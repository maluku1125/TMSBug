from discord.ext import commands
from functions.tinyfunctions import probably
from functions.AIModels import init_gemini, AIChat_response
import aiohttp
import time
from collections import defaultdict

blacklist = [1132722596010528809,0]

IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
RATE_LIMIT = 3          # 每 5 分鐘最多請求次數
RATE_WINDOW = 300       # 5 分鐘（秒）
MAX_INPUT_LENGTH = 500  # 輸入最大字數

class Normal_AIFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_gemini(bot._config["config"]["gemini"])
        self._user_requests = defaultdict(list)  # user_id -> [timestamp, ...]

    async def _download_images(self, message):
        """從訊息中下載圖片附件"""
        images = []
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.split(';')[0] in IMAGE_CONTENT_TYPES:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            images.append((attachment.content_type.split(';')[0], data))
        return images

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild is None:
            return

        if message.guild.id == int(self.bot._config["function"]["tmsguildid"]) or message.guild.id == 807885362583830568:

            if self.bot.user in message.mentions :
                
                if message.author.bot == True:
                    print("AI: Rejected bot message.")
                    return
                
                if message.author.id in blacklist:
                    print("AI: Rejected blacklisted user.")
                    return                

                # 速率限制：同一人每 5 分鐘 3 次
                now = time.time()
                uid = message.author.id
                self._user_requests[uid] = [t for t in self._user_requests[uid] if now - t < RATE_WINDOW]
                if len(self._user_requests[uid]) >= RATE_LIMIT:
                    await message.channel.send("安息的洞穴盡頭沒有任何回應")
                    return

                # 獲取消息的內容，並去除提及機器人的部分
                content = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()

                # 輸入字數限制
                if len(content) > MAX_INPUT_LENGTH:
                    await message.channel.send("安息的洞穴盡頭沒有任何回應")
                    return

                # 記錄此次請求
                self._user_requests[uid].append(now)

                # 下載圖片附件
                images = await self._download_images(message)

                await message.channel.typing()
                try:
                    if message.author.nick == None:
                        response = await AIChat_response(message.author.name, message.author.id, content, images)       
                    else:
                        response = await AIChat_response(message.author.nick, message.author.id, content, images) 

                    await message.channel.send(response)
                except Exception as e:
                    print(f"AI ERROR: {type(e).__name__}: {e}")