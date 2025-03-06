from discord.ext import commands
from functions.tinyfunctions import probably

#排除的category
ignore_parent_id = [1061625669513125938,1019792919915413536,1019916578969636956]
        
class Normal_BasicFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        
        if thread.parent_id in ignore_parent_id:
            return
        
        if thread.guild.id != 420666881368784929:
            return
        
        channel = self.bot.get_channel(588950084658528257) 
        await channel.send(f"討論串已建立 \nAt:{thread.parent.mention} \nName: {thread.mention}\nowner: {thread.owner.mention}")