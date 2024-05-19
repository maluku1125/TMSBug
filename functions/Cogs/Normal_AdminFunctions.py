from discord.ext import commands
import discord
import datetime 

class Normal_AdminFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        # 略自己
        if message.author == self.bot.user:
            return        
        # TMS admin only function
        if message.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            for r in message.author.roles:
                if r.id == 477757173863153665:                    
                    if message.content == 'serverinfo':
                        print(f'{message.author} is asking for server info')

                        embed = discord.Embed(
                            title=f"**{message.guild}**", 
                            description = f'Member Count: {message.guild.member_count}', 
                            color=0x32EBA7,
                            )
                        created_at = message.guild.created_at
                        formatted_date = created_at.strftime('%Y-%m-%d')
                        embed.add_field(
                            name="**Basic Info**",
                            value = f"```"
                                    f"Owner: {message.guild.owner}\n"
                                    f"Since: {formatted_date}\n```",                            
                        )                        
                        embed.add_field(
                            name="**Premium**",
                            value = f"```"
                                    f"Premium Tier      : {message.guild.premium_tier}\n"
                                    f"Subscription count: {message.guild.premium_subscription_count}\n```",
                        )

                        embed.add_field(
                            name="**Channels**",
                            value = f"```"
                                    f"Total Channels Count: {len(message.guild.channels)}\n"
                                    f"Text Channels Count : {len(message.guild.text_channels)}\n"
                                    f"Voice Channels Count: {len(message.guild.voice_channels)}\n"
                                    f"Threads Count       : {len(message.guild.threads)}\n```",
                            inline=False
                        )
                        embed.add_field(
                            name="**Emojis & Stickers**",
                            value = f"```"
                                    f"Emojis Count  : {len(message.guild.emojis)}\n"
                                    f"Stickers Count: {len(message.guild.stickers)}\n```",
                            inline=False
                        )



                        embed.set_thumbnail(url=message.guild.icon)
                        

                        await message.channel.send(embed=embed)



                        
                        
                
                 
                
                         

            