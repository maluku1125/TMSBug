import datetime
import discord
from discord.ext import commands
from collections import defaultdict, deque

# 偵測參數：60 秒內、相同內容、出現在 >=3 個不同頻道 → 刪訊息 + 禁言 1 小時
WINDOW_SECONDS = 60
TRIGGER_CHANNELS = 3
TIMEOUT_HOURS = 1


def message_key(message):
    """訊息內容指紋：文字 + 附件(檔名,大小)。同一張圖到處貼也會命中；空訊息回 None。"""
    content = (message.content or '').strip()
    attach_sig = tuple(sorted((a.filename, a.size) for a in message.attachments))
    if not content and not attach_sig:
        return None
    return (content, attach_sig)


class Normal_AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tms_guild_id = int(bot._config["function"]["tmsguildid"])
        self.log_channel_id = int(bot._config["function"]["logchannel"])
        # user_id -> deque[(timestamp, key, channel_id, message)]
        self.recent = defaultdict(deque)

    @commands.Cog.listener()
    async def on_message(self, message):
        # 僅在 TMS 主群作用；略過私訊/bot/webhook
        if message.guild is None or message.guild.id != self.tms_guild_id:
            return
        if message.author.bot:
            return
        # 版主/管理豁免（有管理訊息權限者不偵測）
        perms = getattr(message.author, 'guild_permissions', None)
        if perms and perms.manage_messages:
            return

        key = message_key(message)
        if key is None:
            return

        now = datetime.datetime.now().timestamp()
        dq = self.recent[message.author.id]
        dq.append((now, key, message.channel.id, message))

        # 清除視窗外的舊紀錄
        while dq and now - dq[0][0] > WINDOW_SECONDS:
            dq.popleft()

        # 相同內容出現在幾個不同頻道
        matched = [entry for entry in dq if entry[1] == key]
        hit_channels = {entry[2] for entry in matched}
        if len(hit_channels) < TRIGGER_CHANNELS:
            return

        # 觸發：先清掉該使用者快取，避免重複觸發
        del self.recent[message.author.id]

        # 控制快取規模：使用者數過多時清掉只剩過期紀錄的項目
        if len(self.recent) > 2000:
            stale = [uid for uid, q in self.recent.items() if not q or now - q[-1][0] > WINDOW_SECONDS]
            for uid in stale:
                del self.recent[uid]

        await self._punish(message.author, matched, key, hit_channels)

    async def _punish(self, member, matched, key, hit_channels):
        # 1) 刪除所有命中的訊息
        deleted = 0
        for _, _, _, msg in matched:
            try:
                await msg.delete()
                deleted += 1
            except Exception:
                pass  # 已被刪或無權限

        # 2) 禁言 1 小時
        timeout_error = None
        try:
            await member.timeout(
                datetime.timedelta(hours=TIMEOUT_HOURS),
                reason="1分鐘內於多個頻道發送相同訊息（疑似殭屍帳號）"
            )
        except Exception as e:
            timeout_error = e

        print(f"[AntiSpam] {member} ({member.id}) 跨頻道洗版：刪除{deleted}則、禁言{'成功' if timeout_error is None else f'失敗({timeout_error})'}")

        # 3) 發送 log
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel is None:
            return

        content_text, attach_sig = key
        preview = content_text[:200] if content_text else "(無文字)"
        if attach_sig:
            preview += f"\n📎 附件：{', '.join(name for name, _ in attach_sig)}"

        embed = discord.Embed(
            title="🛡️ 反洗版偵測",
            description=f"{member.mention} (`{member.id}`) 於 {WINDOW_SECONDS} 秒內在 {len(hit_channels)} 個頻道發送相同訊息",
            color=0xff0000,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="訊息內容", value=preview, inline=False)
        embed.add_field(name="出現頻道", value=' '.join(f"<#{cid}>" for cid in hit_channels), inline=False)
        embed.add_field(
            name="處置",
            value=(
                f"🗑️ 已刪除 {deleted}/{len(matched)} 則訊息\n"
                f"🔇 禁言 {TIMEOUT_HOURS} 小時：{'✅ 成功' if timeout_error is None else f'❌ 失敗 ({timeout_error})'}"
            ),
            inline=False
        )
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[AntiSpam] log 發送失敗: {e}")
