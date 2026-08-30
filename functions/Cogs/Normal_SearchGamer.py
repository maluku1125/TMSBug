"""
Normal_SearchGamer.py
=====================
以訊息右鍵選單「查巴哈」為指定訊息產生巴哈姆特楓之谷板的搜尋連結。

原本以「對訊息按巴哈表情」觸發，需讀取 reaction.message.content，
而該訊息不屬於 Message Content Intent 的例外情形；改為訊息右鍵選單後，
屬於官方例外「右鍵選單指令所作用的訊息」，即使未取得該 Intent 仍可正常運作。
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.errors import NotFound
from urllib.parse import quote
import logging

FORUM_URL = ("https://forum.gamer.com.tw/search.php"
             "?bsn=7650&q={q}&exact=0&advancedSearch=1&page=1")
MAX_QUERY_LEN = 100


class Normal_SearchGamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tms_guild_id = int(bot._config["function"]["tmsguildid"])
        # Context menu 無法用裝飾器定義在 Cog 內，需手動建立並註冊
        self.search_menu = app_commands.ContextMenu(
            name="查巴哈",
            callback=self.search_context,
        )
        bot.tree.add_command(self.search_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.search_menu.name, type=self.search_menu.type)

    async def search_context(self, interaction: discord.Interaction, message: discord.Message):
        if interaction.guild is None or interaction.guild.id != self.tms_guild_id:
            await interaction.response.send_message("此指令僅能在 TMS 伺服器中使用。", ephemeral=True)
            return

        if message.author.bot:
            await interaction.response.send_message("不能查詢機器人的訊息。", ephemeral=True)
            return

        keyword = (message.content or '').replace(' ', '').replace('　', '')
        if not keyword:
            await interaction.response.send_message("這則訊息沒有文字內容可供查詢。", ephemeral=True)
            return
        if len(keyword) > MAX_QUERY_LEN:
            keyword = keyword[:MAX_QUERY_LEN]

        url = FORUM_URL.format(q=quote(keyword, safe=''))
        print(f'{interaction.user} 替 {message.author} 查詢了 {keyword}')
        print('-' * 40)

        try:
            await interaction.response.send_message(
                f'{message.author.mention}，{interaction.user.mention}'
                f'幫你查詢了[你問的內容]({url})')
        except NotFound:
            logging.warning("search_gamer: Interaction expired before response")
