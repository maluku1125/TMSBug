from discord.ext import commands
from functions.AIModels import init_gemini, AIChat_response, AIUnavailable
import aiohttp
import time
from collections import defaultdict

IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
RATE_LIMIT = 3            # 每 RATE_WINDOW 秒內最多請求次數
RATE_WINDOW = 300         # 5 分鐘（秒）
MAX_INPUT_LENGTH = 500    # 輸入最大字數
MAX_IMAGES = 3            # 單則訊息最多處理幾張圖
MAX_IMAGE_MB = 4          # 單張圖片大小上限
IMAGE_TIMEOUT = 15        # 圖片下載逾時（秒）
PRUNE_EVERY = 200         # 每 N 次請求清理一次速率限制表
NO_REPLY = "安息的洞穴盡頭沒有任何回應"


class Normal_AIFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = bot._config["config"]
        fn = bot._config["function"]

        self.enabled = init_gemini(
            cfg.get("gemini"),
            model_name=cfg.get("gemini_model") or None,
            max_tokens=int(cfg.get("gemini_max_tokens", 250)),
            timeout=int(cfg.get("gemini_timeout", 30)),
            thinking=cfg.get("gemini_thinking", ""),
            safety=cfg.get("gemini_safety", "relaxed"),
            media_resolution=cfg.get("gemini_media_resolution", "low"),
        )
        # 允許使用 AI 的伺服器（逗號分隔），未設定則只有主群
        ids = fn.get("aiguilds") or fn.get("tmsguildid", "")
        self.allowed_guilds = {int(x) for x in str(ids).replace(" ", "").split(",") if x}
        # 黑名單使用者（逗號分隔）
        bl = cfg.get("ai_blacklist", "")
        self.blacklist = {int(x) for x in str(bl).replace(" ", "").split(",") if x}

        self._user_requests = defaultdict(list)   # user_id -> [timestamp, ...]
        self._request_counter = 0

    def _prune_requests(self, now):
        """清掉已無有效時間戳的使用者，避免字典無限成長"""
        stale = [uid for uid, ts in self._user_requests.items()
                 if not ts or now - ts[-1] >= RATE_WINDOW]
        for uid in stale:
            del self._user_requests[uid]

    async def _download_images(self, message):
        """下載訊息中的圖片附件（共用連線、限制張數與大小）"""
        images = []
        targets = [a for a in message.attachments
                   if a.content_type and a.content_type.split(';')[0] in IMAGE_CONTENT_TYPES]
        if not targets:
            return images
        timeout = aiohttp.ClientTimeout(total=IMAGE_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for a in targets[:MAX_IMAGES]:
                if a.size > MAX_IMAGE_MB * 1024 * 1024:
                    print(f"AI: 略過過大圖片 {a.filename} ({a.size / 1024 / 1024:.1f}MB)")
                    continue
                try:
                    async with session.get(a.url) as resp:
                        if resp.status == 200:
                            images.append((a.content_type.split(';')[0], await resp.read()))
                except Exception as e:
                    print(f"AI: 圖片下載失敗 {a.filename}: {type(e).__name__}")
        return images

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.enabled or message.guild is None:
            return
        if message.guild.id not in self.allowed_guilds:
            return
        if self.bot.user not in message.mentions:
            return
        if message.author.bot:
            print("AI: Rejected bot message.")
            return
        if message.author.id in self.blacklist:
            print("AI: Rejected blacklisted user.")
            return

        now = time.time()
        uid = message.author.id

        # 定期清理速率限制表
        self._request_counter += 1
        if self._request_counter % PRUNE_EVERY == 0:
            self._prune_requests(now)

        recent = [t for t in self._user_requests[uid] if now - t < RATE_WINDOW]
        self._user_requests[uid] = recent
        if len(recent) >= RATE_LIMIT:
            await message.reply(NO_REPLY, mention_author=False)
            return

        content = (message.content
                   .replace(f'<@!{self.bot.user.id}>', '')
                   .replace(f'<@{self.bot.user.id}>', '')
                   .strip())

        if len(content) > MAX_INPUT_LENGTH:
            await message.reply(NO_REPLY, mention_author=False)
            return

        images = await self._download_images(message)
        if not content and not images:
            return   # 只有 tag 沒內容，不浪費額度

        # 先記錄用量，失敗時退還
        self._user_requests[uid].append(now)

        nick = message.author.nick or message.author.name
        try:
            async with message.channel.typing():
                response = await AIChat_response(nick, uid, content, images)
        except AIUnavailable as e:
            print(f"AI unavailable: {e}")
            self._refund(uid, now)
            await message.reply(NO_REPLY, mention_author=False)
            return
        except Exception as e:
            print(f"AI ERROR: {type(e).__name__}: {e}")
            self._refund(uid, now)
            await message.reply(NO_REPLY, mention_author=False)
            return

        # Discord 單則訊息上限 2000 字，超長時截斷
        if len(response) > 2000:
            response = response[:1997] + "..."
        try:
            await message.reply(response, mention_author=False)
        except Exception as e:
            print(f"AI: 回覆失敗 {type(e).__name__}: {e}")

    def _refund(self, uid, ts):
        """生成失敗時退還該次額度"""
        try:
            self._user_requests[uid].remove(ts)
        except ValueError:
            pass
