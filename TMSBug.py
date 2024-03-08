import datetime
import discord
from discord.ext import commands
import time
import configparser
import asyncio

from functions.chatlog import chat_log_save, get_speak_count
from functions.getprize import  use_apple, use_fashionbox, prizechannelblacklist
from functions.CreateBossDataEmbed import Create_Boss_Data_Embed, boss_aliases
from functions.CreatePrizeEmbed import Create_FashionBox_embed, Create_Apple_embed
from functions.tinyfunctions import probably
from functions.CreateMemoEmbed import CreateFarmingEmbed, CreateCombatEmbed
from functions.tinyfunctions import RollDice
from functions.Cogs.Discord_Commands import DiscordCommands
from functions.Cogs.SlashCommands import SlashCommands

try:
    _TMSBot_CONF = configparser.ConfigParser()
    config_path = 'C:\\Users\\User\\Desktop\\maplestory_discordbot\\config.ini'
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

        
        await self.add_cog(DiscordCommands(self))
        print('Cogs:DiscordCommands loaded')
        await self.add_cog(SlashCommands(self))
        print('Cogs:SlashCommands loaded')


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

                        await message.channel.send(file = discord.File(f'C:\\Users\\User\\Desktop\\DiscordChatlog\\ChatLog\\{date}_TMS新楓之谷testver_Chatlog.csv'))
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
            sent_message = await message.channel.send(embed=embed)
            print(f'{now_HMS}, Guild：{message.channel.guild}, User：{message.author} ,FarmingMemo')
            print('-'*40)

        if message.content == '打王備忘' or message.content == 'BOSS備忘' or message.content == 'Boss備忘' or message.content == 'boss備忘':
            embed = CreateCombatEmbed()
            sent_message = await message.channel.send(embed=embed)
            print(f'{now_HMS}, Guild：{message.channel.guild}, User：{message.author} ,CombatMemo')
            print('-'*40)

        #BOSS資訊    
        #----------------------------------------        
        if message.content in boss_aliases:    

            if message.content == '蟲蟲':
                await message.channel.send(f'叫我嗎?')
            else:
                await message.add_reaction('<:img17:588950160399269889>')
                embed, num_subtitles= Create_Boss_Data_Embed(message.content, 0)
                if probably(0.02):
                    embed, num_subtitles= Create_Boss_Data_Embed("蟲蟲", 0)  
                sent_message = await message.channel.send(embed=embed)
                await sent_message.add_reaction('🔄')
                await sent_message.add_reaction('❌')

            Bossmode = [0]   # 將 Bossmode 定義為全域變數

            @self.event
            async def on_reaction_add(reaction, user):
                if user == self.user:
                    return  # 忽略機器人自身的反應

                if reaction.message.author != self.user:
                    return  # 忽略機器人所發送訊息以外的反應

                if reaction.message.id != sent_message.id:
                    return  # 忽略其他訊息的反應

                if reaction.emoji == '🔄':
                    await reaction.remove(user)  # 刪除使用者加上的反應                
                    await asyncio.wait_for(switch_boss_mode(), timeout=10)  # 等待使用者反應，設定超時時間為 10 秒    
                if reaction.emoji == '❌':
                    await sent_message.delete()
                                

            async def switch_boss_mode():
                Bossmode[0] = (Bossmode[0] + 1) % num_subtitles

                embed, _ = Create_Boss_Data_Embed(message.content, Bossmode[0])    
                await sent_message.edit(embed=embed)

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