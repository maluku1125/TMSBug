from discord.ext import commands
from functions.tinyfunctions import probably
from functions.AIModels import AIChat_response

class Normal_AIFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild.id == int(self.bot._config["function"]["tmsguildid"]):

            if self.bot.user in message.mentions or probably(0.001):
  
                if "我要入會地" in message.content:
                    return

                # 獲取消息的內容，並去除提及機器人的部分
                content = message.content.replace(f'<@!{self.bot.user.id}>', '').strip()

                await message.channel.typing()            
                if message.author.nick == None:
                    response = AIChat_response(message.author.name, content)       
                else:  
                    response = AIChat_response(message.author.nick, content)            
                await message.channel.send(response)