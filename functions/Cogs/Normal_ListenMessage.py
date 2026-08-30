from discord.ext import commands
from functions.tinyfunctions import probably

class Normal_ListenMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # 略自己
        if message.author == self.bot.user:
            return
        
        # TMS only function
        if message.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            
            # Random img17

            if probably(0.001):
                await message.add_reaction('<:img17:588950160399269889>')
                print(message.channel, ':', message.author, '隨機加上img17表情')
