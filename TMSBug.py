import datetime
import discord
from discord.ext import commands
import time
import configparser
import asyncio

from functions.chatlog import chat_log_save, get_speak_count
from functions.CreateBossDataEmbed import Create_Boss_Data_Embed, boss_aliases
from functions.tinyfunctions import probably
from functions.CreateMemoEmbed import CreateFarmingEmbed, CreateCombatEmbed
from functions.Cogs.Prefix_BasicCommands import Prefix_BasicCommands
from functions.Cogs.Slash_BasicCommands import Slash_BasicCommands
from functions.Cogs.Slash_RequestUnionRank import Slash_RequestUnionRank
from functions.Cogs.Slash_CreateBossDataEmbed import Slash_CreateBossDataEmbed
from functions.Cogs.Slash_CreatePrizeEmbed import Slash_CreatePrizeEmbed
from functions.Cogs.Slash_CreateSolErdaFragmentEmbed import Slash_CreateSolErdaFragmentEmbed
from functions.Cogs.Slash_RequestMapleEvents import Slash_RequestMapleEvents
from functions.AIModels import AIChat_response

try:
    _TMSBot_CONF = configparser.ConfigParser()
    config_path = 'C:\\Users\\User\\Desktop\\DiscordBot\\Config\\TMSBug_config.ini'
    _TMSBot_CONF.read(config_path, encoding="utf-8")
except FileNotFoundError:
    print("`config.ini` file missing.")
    #sys.exit(1)

discord.voice_client.VoiceClient.warn_nacl = False


def resolve_intents() -> discord.Intents:
    "Resolves configured intents to discord format"
    intents = discord.Intents.default()
    intents.members = _TMSBot_CONF.getboolean("intents", "members", fallback=False)
    intents.presences = _TMSBot_CONF.getboolean("intents", "presences", fallback=False)
    intents.message_content = _TMSBot_CONF.getboolean("intents", "message_content", fallback=False)
    return intents

class TMSBot(commands.AutoShardedBot):

    def __init__(self, config, intents):
        allowed_mentions = discord.AllowedMentions(
            roles=True, everyone=False, users=True, replied_user=False
        )
        super().__init__(
            self_bot=True,
            command_prefix=commands.when_mentioned_or(
                config["bot"]["prefix"].strip('"')
            ),
            description=config["bot"]["description"],
            pm_help=True,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents,
            activity=discord.Activity(
                type=int(config["bot"]["activity_type"]), name=config["bot"]["activity"]
            ),
        )
      
        # setup from config
        self._config = config
        self.color = discord.Color.from_str(config["bot"]["color"])
        self.name = config["bot"]["name"]
        self.session = None
        self.uptime = None
        self.time_date = ''
        self.noticeguilds = []
        
        print('-'*25)
        print('TMSBot is Loading')
        print('-'*25)
        print(f'ChatLog Count = {get_speak_count()}')
        self.speak_count = get_speak_count()
        if self.speak_count != 0 :
            self.time_date = datetime.datetime.now().strftime('%m%d')
            print('-'*25)
            print(f'ChatLog Date = {self.time_date}')

    async def on_ready(self):       

        await self.add_cog(Prefix_BasicCommands(self))
        print('Cogs:Prefix_BasicCommands loaded')
        await self.add_cog(Slash_BasicCommands(self))
        print('Cogs:Slash_BasicCommands loaded')
        await self.add_cog(Slash_RequestUnionRank(self))
        print('Cogs:Slash_RequestUnionRank loaded')
        await self.add_cog(Slash_CreateBossDataEmbed(self))
        print('Cogs:Slash_CreateBossDataEmbed loaded')
        await self.add_cog(Slash_CreatePrizeEmbed(self))
        print('Cogs:Slash_CreatePrizeEmbed loaded')
        await self.add_cog(Slash_CreateSolErdaFragmentEmbed(self))
        print('Cogs:Slash_CreateSolErdaFragmentEmbed loaded')
        await self.add_cog(Slash_RequestMapleEvents(self))
        print('Cogs:Slash_RequestMapleEvents loaded')


        dev_guild_id = self._config["bot"]["dev_guild"]
        print('slash command is now loading')
        print(f'devguild : {dev_guild_id}')
        
        if dev_guild_id:
            dev_guild = self.get_guild(int(dev_guild_id))
            self.tree.copy_global_to(guild=dev_guild)
            slash = await self.tree.sync(guild=dev_guild)
            print(f"Loaded slash command to dev guild")
        else:
            slash = await self.tree.sync()
            print(f"Loaded slash command to global guild")

        print(f"Total Slash Command Loaded:{len(slash)}")

        print('-'*25)
        print('TMSBot is Online')
        print('-'*25)


    async def on_message(self, message, /):
        
        await self.process_commands(message)

        if datetime.datetime.now().strftime('%m%d') != self.time_date:
            self.time_date = datetime.datetime.now().strftime('%m%d')
            self.speak_count = 0
        
        # 略自己
        if message.author == self.user:
            return
        now_HMS = datetime.datetime.now().strftime('%H:%M:%S')

        if message.guild.id != int(self._config["function"]["tmsguildid"]):
            if message.guild not in self.noticeguilds:
                await message.channel.send(f'```邪惡的蟲蟲將在5/18回到TMS新楓之谷群了，\n但我可以派出我的分身TMSBug_v2來到【{message.guild}】，\n看到這訊息的冒險者阿，趕緊聯絡負責召喚魔法的管理員進行召喚吧！```[召喚蟲蟲分身!](https://reurl.cc/aLj8V9)')
                self.noticeguilds.append(message.guild)
                print(f'在{message.guild}發送了換蟲通知')

        #TMS server only function
        if message.guild.id == int(self._config["function"]["tmsguildid"]):
            if message.author.bot != True :
                self.speak_count += 1        
                print(f'{now_HMS} #{self.speak_count},Channel：{message.channel}, User：{message.author}')
                print("Content：", message.content, message.stickers, message.attachments)
                print('-'*40)
            else:
                print(f'{now_HMS} #BOTSpeak,Channel：{message.channel}, User：{message.author}')
                print("Content：", message.content, message.stickers, message.attachments)
                print('-'*40)

            #非和協會地
            if self.user in message.mentions:
                if '我要入會地' in message.content:
                    if message.channel.id == 656213444621631508:
                            
                        thread_id = 1225733037782859776  # 討論串 ID
                        thread = self.get_channel(thread_id)

                        await thread.send(f'{message.author.mention} hi，你到會地了')
                        await message.delete()
                    else:
                        await message.delete()

            #   Chat AI
            # 檢查消息是否提及了機器人
            if self.user in message.mentions:

                if "我要入會地" in message.content:
                    return

                # 獲取消息的內容，並去除提及機器人的部分
                content = message.content.replace(f'<@!{self.user.id}>', '').strip()

                await message.channel.typing()            
                if message.author.nick == None:
                    response = AIChat_response(message.author.name, content)       
                else:  
                    response = AIChat_response(message.author.nick, content)            
                await message.channel.send(response)

            #Chat Log
            #----------------------------------------
            #write
        
            if message.author.bot != True :
                chat_log_save(self.speak_count, message.channel, message.author, message.content, message.attachments, message.stickers)
        
            #read
            if message.content == 'chatlog' :
                for r in message.author.roles:
                    if r.id == 477757173863153665:
                        
                        date = time.strftime('%Y%m%d', time.localtime(time.time()))

                        await message.channel.send(file = discord.File(f'C:\\Users\\User\\Desktop\\DiscordChatlog\\ChatLog\\{date}_TMS新楓之谷_Chatlog.csv'))
                        return
        
            #Count ServerMember
            #----------------------------------------
            if message.content == 'count':
                await message.channel.send(f'伺服器總人數：{message.guild.member_count}')

                renamechannel = message.guild.get_channel(int(self._config["function"]["membercountchannel"]))
                await renamechannel.edit(name=f'全部人數：{message.guild.member_count}')

            #Count DailySpeak
            #----------------------------------------
            if message.content == 'speakcount':
                await message.channel.send(f'今日總訊息數:{self.speak_count}')

            #Random img17
            #----------------------------------------
            if probably(0.001):
                await message.add_reaction('<:img17:588950160399269889>')
                print(message.channel, ':', message.author, '隨機加上img17表情')
            
            #Flat img17
            #----------------------------------------
            if message.content == '<:ban:597267067581890571>' or message.content == '<:ban_g:927438410182963232>' or message.content == '<:ban_w:927423587911077990>':
                await message.add_reaction('<:img17_flat:839749212152528916>')

    
        #MEMO資訊
        if message.content == '練等備忘' or message.content == '鍊等備忘':
            embed = CreateFarmingEmbed()
            await message.channel.send(embed=embed)
            print(f'{now_HMS}, Guild：{message.channel.guild}, User：{message.author} ,FarmingMemo')
            print('-'*40)

        if message.content == '打王備忘' or message.content == 'BOSS備忘' or message.content == 'Boss備忘' or message.content == 'boss備忘':
            embed = CreateCombatEmbed()
            await message.channel.send(embed=embed)
            print(f'{now_HMS}, Guild：{message.channel.guild}, User：{message.author} ,CombatMemo')
            print('-'*40)


    async def on_reaction_add(self, reaction, user):
        print(f'{user}, {reaction}')
        #TMS server only function
        if reaction.message.guild.id == int(self._config["function"]["tmsguildid"]):
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

        
    async def on_member_join(self, member):
        if member.guild.id == int(self._config["function"]["tmsguildid"]):
            print(f'{member} 加入了伺服器')
            print('-'*40)
            
            renamechannel = member.guild.get_channel(int(self._config["function"]["membercountchannel"]))
            await renamechannel.edit(name=f'全部人數：{member.guild.member_count}')
            print(f'更改了人數')
            print('-'*40)
    
    async def on_member_remove(self, member):
        if member.guild.id == int(self._config["function"]["tmsguildid"]):
            print(f'{member} 離開了伺服器')
            print('-'*40)
            
            renamechannel = member.guild.get_channel(int(self._config["function"]["membercountchannel"]))
            await renamechannel.edit(name=f'全部人數：{member.guild.member_count}')
            print(f'更改了人數')
            print('-'*40)

    async def on_message_edit(self, message_before, message_after):
    
        #Chat Log
        #----------------------------------------
        if message_after.guild.id == int(self._config["function"]["messageloggingguild"]):
            if message_after.author.bot != True :
                chat_log_save('Edit_Before', message_before.channel, message_before.author, message_before.content, message_before.attachments, message_before.stickers)
                chat_log_save('Edit_After', message_after.channel, message_after.author, message_after.content, message_after.attachments, message_after.stickers)

                print(f'Edit_Before, Channel：{message_before.channel}, User：{message_before.author}')
                print("Content：", message_before.content, message_before.stickers, message_before.attachments)
                print(f'Edit_After, Channel：{message_after.channel}, User：{message_after.author}')
                print("Content：", message_after.content, message_after.stickers, message_after.attachments)
                print('-'*40) 

async def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    tmsbot = TMSBot(config=_TMSBot_CONF, intents=resolve_intents())

    await tmsbot.start(_TMSBot_CONF["discord"]["token"], reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())