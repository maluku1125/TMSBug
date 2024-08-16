from discord.ext import commands
from functions.tinyfunctions import probably
from functions.AIModels import AIChat_response, AIChat_response_admin

blacklist = [1132722596010528809,0]

class Normal_AIFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild.id == int(self.bot._config["function"]["tmsguildid"]) or message.guild.id == 807885362583830568:

            if self.bot.user in message.mentions :
  
                if "我要入會地" in message.content:
                    return
                
                if message.author.bot == True:
                    print("AI: Rejected bot message.")
                    return
                
                if message.author.id in blacklist:
                    print("AI: Rejected blacklisted user.")
                    return                

                # 獲取消息的內容，並去除提及機器人的部分
                content = message.content.replace(f'<@!{self.bot.user.id}>', '').strip()

                await message.channel.typing()   
                if message.channel.id == 1251595101080125440:  
                    response = AIChat_response_admin(content)      
                elif message.author.nick == None:
                    response = AIChat_response(message.author.name, content)       
                else:  
                    response = AIChat_response(message.author.nick, content) 

                await message.channel.send(response)