from discord.ext import commands

class Normal_SearchGamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        #TMS server only function
        if reaction.message.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            if str(reaction) == '<:Bahamut:1237775873239679067>':                
                if reaction.count > 1:
                    print(f'{user}替{reaction.message.author}查詢了巴哈，但是第二次')
                    return                
                if reaction.message.content == None:
                    print(f'{user}替{reaction.message.author}查詢了巴哈，但是沒有內容')
                    return
                content_without_spaces = reaction.message.content.replace(' ', '')
                content_without_spaces = content_without_spaces.replace('　', '')

                if reaction.message.author.bot or user.bot: 
                    print(f'{user}替{reaction.message.author}查詢了{content_without_spaces}，但是是機器人')
                    return               

                print(f'{user}替{reaction.message.author}查詢了{content_without_spaces}')
                print('-'*40)
                reaction_channel = reaction.message.channel
                await reaction_channel.send(f'{reaction.message.author.mention}，{user.mention}幫你查詢了[你問的內容](https://forum.gamer.com.tw/search.php?bsn=7650&q={content_without_spaces}&exact=0&advancedSearch=1&page=1)')
