"""訊息記錄 Cog —— 僅記錄「被刪除」與「被編輯」的訊息。

一般聊天不再落地。只有事後無法從 Discord 取回的內容（已刪除／編輯前的版本）
才會寫入加密記錄，供管理員處理糾紛時查核。

限制：discord.py 只對「仍在記憶體訊息快取中」的訊息發出 on_message_delete /
on_message_edit 並附帶內容；快取外的舊訊息被刪除時只有 raw 事件、無內容可記，
因此無法記錄。快取大小由 TMSBug.py 的 max_messages 決定。
"""

from discord.ext import commands
import datetime

from functions.chatlog import chat_log_save


class Normal_ChatLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = bot._config["function"]
        self.log_guild_id = int(cfg.get("messageloggingguild",
                                        cfg.get("tmsguildid")))

    def _should_log(self, message) -> bool:
        """只記錄指定伺服器內、真人使用者的訊息"""
        if message.guild is None or message.guild.id != self.log_guild_id:
            return False
        if message.author.bot:
            return False
        return True

    @staticmethod
    def _print(event, message):
        now_HMS = datetime.datetime.now().strftime('%H:%M:%S')
        print(f'{now_HMS} [{event}] Channel：{message.channel}, User：{message.author}')
        print("Content：", message.content, message.stickers, message.attachments)
        print('-' * 30)

    # ── 刪除 ────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not self._should_log(message):
            return
        chat_log_save('Delete', message.channel, message.author, message.content,
                      message.attachments, message.stickers, message.id)
        self._print('Delete', message)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        for message in messages:
            if not self._should_log(message):
                continue
            chat_log_save('BulkDelete', message.channel, message.author, message.content,
                          message.attachments, message.stickers, message.id)
            self._print('BulkDelete', message)

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

        chat_log_save('Edit_Before', message_before.channel, message_before.author,
                      message_before.content, message_before.attachments,
                      message_before.stickers, message_before.id)
        chat_log_save('Edit_After', message_after.channel, message_after.author,
                      message_after.content, message_after.attachments,
                      message_after.stickers, message_after.id)
        self._print('Edit_Before', message_before)
        self._print('Edit_After', message_after)
