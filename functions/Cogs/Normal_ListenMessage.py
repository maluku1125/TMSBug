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
            
            # Flat img17
            if message.content == '<:ban:597267067581890571>' or message.content == '<:ban_g:927438410182963232>' or message.content == '<:ban_w:927423587911077990>':
                await message.add_reaction('<:img17_flat:839749212152528916>')

            # 非和協會地            
            if self.bot.user in message.mentions:
                if '我要入會地' in message.content:
                    if message.channel.id == 656213444621631508:
                            
                        thread_id = 1225733037782859776  # 討論串 ID
                        thread = self.bot.get_channel(thread_id)

                        # await thread.send(f'{message.author.mention} hi，你到會地了')
                        await message.delete()
                        await message.author.send('https://discord.gg/H2nU6DbZBA \n歡迎加入公會DC')  # 傳送私訊
                    else:
                        await message.delete()
