"""訊息記錄 Cog —— 將「被刪除」與「被編輯」的訊息轉貼到指定的 Discord 頻道。

不寫入任何本機檔案：資料全程留在 Discord 平台內，管理員直接在頻道中查閱。

設定（Config/TMSBug_config.ini）：
    [function]
    messagelogchannel = <頻道 ID>     ← 未設定則整個功能停用

限制：discord.py 只對「仍在記憶體訊息快取中」的訊息發出 on_message_delete /
on_message_edit 並附帶內容；快取外的舊訊息被刪除時只有 raw 事件、無內容可記。
快取大小由 TMSBug.py 的 max_messages 決定。
"""

import asyncio
import time
import datetime

import discord
from discord.ext import commands

MAX_DESC = 3800              # embed description 上限 4096，留餘裕
MAX_FIELD = 1000             # embed field value 上限 1024，留餘裕
MAX_EMBEDS_PER_MESSAGE = 10  # Discord 單則訊息最多 10 個 embed
FLUSH_INTERVAL = 2.0         # 收集這麼久的事件後一次送出（洗版時會一口氣刪很多則）
MAX_QUEUE = 500              # 佇列上限，超過就丟棄以免積壓


def _trim(text: str, limit: int) -> str:
    if not text:
        return '（無文字內容）'
    return text if len(text) <= limit else text[:limit - 3] + '...'


class Normal_ChatLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = bot._config["function"]
        self.log_guild_id = int(cfg.get("messageloggingguild", cfg.get("tmsguildid")))

        raw = cfg.get("messagelogchannel", "").strip()
        self.log_channel_id = int(raw) if raw.isdigit() else 0

        self._queue = asyncio.Queue(maxsize=MAX_QUEUE)
        self._dropped = 0
        self._task = None

        if not self.log_channel_id:
            print('[MsgLog] ⚠ 未設定 [function] messagelogchannel，刪除/編輯記錄已停用')
        else:
            self._task = asyncio.create_task(self._worker())
            print(f'[MsgLog] 刪除/編輯記錄將送往頻道 {self.log_channel_id}')

    async def cog_unload(self):
        if self._task:
            self._task.cancel()

    # ── 共用判斷 ────────────────────────────────────────────
    def _should_log(self, message) -> bool:
        if not self.log_channel_id:
            return False
        if message.guild is None or message.guild.id != self.log_guild_id:
            return False
        if message.author.bot:
            return False
        # 不記錄記錄頻道本身，避免自我循環
        if message.channel.id == self.log_channel_id:
            return False
        return True

    def _enqueue(self, embed):
        try:
            self._queue.put_nowait(embed)
        except asyncio.QueueFull:
            self._dropped += 1
            if self._dropped % 50 == 1:
                print(f'[MsgLog] ⚠ 佇列已滿，累計丟棄 {self._dropped} 筆')

    # ── 送出（批次）──────────────────────────────────────────
    async def _worker(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                batch = [await self._queue.get()]
                deadline = time.monotonic() + FLUSH_INTERVAL
                while len(batch) < MAX_EMBEDS_PER_MESSAGE:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    try:
                        batch.append(await asyncio.wait_for(self._queue.get(), remaining))
                    except asyncio.TimeoutError:
                        break
                await self._send(batch)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f'[MsgLog] worker 例外：{e}')
                await asyncio.sleep(5)

    async def _send(self, embeds):
        channel = self.bot.get_channel(self.log_channel_id)
        if channel is None:
            print(f'[MsgLog] ⚠ 找不到頻道 {self.log_channel_id}')
            return
        try:
            await channel.send(embeds=embeds,
                               allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException as e:
            print(f'[MsgLog] 送出失敗：{e}')

    # ── embed 組裝 ──────────────────────────────────────────
    @staticmethod
    def _base(message, title, color):
        embed = discord.Embed(
            title=title, color=color,
            timestamp=datetime.datetime.now(datetime.timezone.utc))
        embed.add_field(name='頻道', value=message.channel.mention, inline=True)
        embed.add_field(name='作者',
                        value=f'{message.author.mention}\n`{message.author}`',
                        inline=True)
        embed.set_footer(text=f'作者 ID：{message.author.id}｜訊息 ID：{message.id}')
        return embed

    @staticmethod
    def _attach_field(embed, message):
        parts = []
        if message.attachments:
            # 訊息刪除後 CDN 連結可能失效，僅供短時間內查看
            parts += [f'[{a.filename}]({a.url})' for a in message.attachments]
        if message.stickers:
            parts += [f'貼圖：{s.name}' for s in message.stickers]
        if parts:
            embed.add_field(name='附件／貼圖',
                            value=_trim('\n'.join(parts), MAX_FIELD), inline=False)

    # ── 刪除 ────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not self._should_log(message):
            return
        embed = self._base(message, '🗑️ 訊息已刪除', discord.Color.red())
        embed.description = _trim(message.content, MAX_DESC)
        self._attach_field(embed, message)
        self._enqueue(embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        for message in messages:
            if not self._should_log(message):
                continue
            embed = self._base(message, '🗑️ 訊息已批次刪除', discord.Color.dark_red())
            embed.description = _trim(message.content, MAX_DESC)
            self._attach_field(embed, message)
            self._enqueue(embed)

    # ── 編輯 ────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if not self._should_log(message_after):
            return
        # Discord 在補上連結預覽、釘選等情況也會送出 edit 事件，
        # 此時內容與附件皆未變動，不需記錄。
        if (message_before.content == message_after.content
                and message_before.attachments == message_after.attachments):
            return

        embed = self._base(message_after, '✏️ 訊息已編輯', discord.Color.orange())
        embed.add_field(name='編輯前',
                        value=_trim(message_before.content, MAX_FIELD), inline=False)
        embed.add_field(name='編輯後',
                        value=_trim(message_after.content, MAX_FIELD), inline=False)
        embed.add_field(name='原訊息',
                        value=f'[跳至訊息]({message_after.jump_url})', inline=False)
        self._attach_field(embed, message_after)
        self._enqueue(embed)
