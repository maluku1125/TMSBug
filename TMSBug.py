import datetime
import discord
from discord.ext import commands
import time
import configparser
import asyncio

from functions.chatlog import chat_log_save, get_speak_count
from functions.tinyfunctions import probably
from functions.Cogs.Prefix_BasicCommands import Prefix_BasicCommands
from functions.Cogs.Slash_BasicCommands import Slash_BasicCommands
from functions.Cogs.Normal_ChatLogging import Normal_ChatLogging
from functions.Cogs.Normal_ListenMessage import Normal_ListenMessage
from functions.Cogs.Normal_AIFunctions import Normal_AIFunctions
from functions.Cogs.Normal_SearchGamer import Normal_SearchGamer
from functions.Cogs.Normal_AdminFunctions import Normal_AdminFunctions
from functions.Cogs.Normal_ServerMember import Normal_ServerMember
from functions.Cogs.Normal_BasicFunctions import Normal_BasicFunctions
from functions.Cogs.Loop_ServerCheck import Loop_ServerCheck


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
            # activity=discord.Activity(
            #     type=int(config["bot"]["activity_type"]), name=config["bot"]["activity"]
            # ),
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
        await self.add_cog(Normal_ListenMessage(self))
        print('Cogs:Normal_ListenMessage loaded')
        await self.add_cog(Normal_ChatLogging(self))
        print('Cogs:Normal_ChatLogging loaded')
        await self.add_cog(Normal_AIFunctions(self))
        print('Cogs:Normal_AIFunctions loaded')
        await self.add_cog(Normal_SearchGamer(self))
        print('Cogs:Normal_SearchGamer loaded')
        await self.add_cog(Normal_AdminFunctions(self))
        print('Cogs:Normal_AdminFunctions loaded')
        await self.add_cog(Loop_ServerCheck(self))
        print('Cogs:Loop_ServerCheck loaded')
        await self.add_cog(Normal_ServerMember(self))
        print('Cogs:Normal_ServerMember loaded')
        await self.add_cog(Normal_BasicFunctions(self))
        print('Cogs:Normal_BasicFunctions loaded')


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

async def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    tmsbot = TMSBot(config=_TMSBot_CONF, intents=resolve_intents())

    await tmsbot.start(_TMSBot_CONF["discord"]["token"], reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())