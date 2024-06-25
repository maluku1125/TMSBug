from discord.ext import commands
import discord
import datetime

class Normal_ServerMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(member)

        if member.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            print(f'{member} 加入了伺服器')
            print('-'*40)
            
            renamechannel = member.guild.get_channel(int(self.bot._config["function"]["membercountchannel"]))
            await renamechannel.edit(name=f'全部人數：{member.guild.member_count}')
            print(f'更改了人數')
            print('-'*40)

            welcomechannel = member.guild.get_channel(int(self.bot._config["function"]["welcomechannel"]))
            print(f'歡迎頻道：{welcomechannel}')

            now_HMS = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            created_at_format = member.created_at.strftime('%Y/%m/%d %H:%M:%S') if member.joined_at else '未知'

            print(member.guild.member_count)
            print(created_at_format)
            print(now_HMS)
            print(member.display_avatar.url)

            embed = discord.Embed(
                title=f"**歡迎 {member}**", 
                description = f'當前人數:{member.guild.member_count}', 
                color=0x32EBA7,
                )  
            embed.add_field(
                name = "**創建時間**",
                value = f"{created_at_format}",         
                inline=True                   
            )
            embed.add_field(
                name = "**加入時間**",
                value = f"{now_HMS}", 
                inline=True                           
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")
            print(f'已創建embed')
            await welcomechannel.send(f'歡迎 {member.mention} 加入伺服器！\n 可以去頻道最上方<id:customize>，新增或更改自己想要的身分組以使用更多功能喔！', embed=embed) 



    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(member)
        if member.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            print(f'{member} 離開了伺服器')
            print('-'*40)
            
            renamechannel = member.guild.get_channel(int(self.bot._config["function"]["membercountchannel"]))
            leavechannel = member.guild.get_channel(int(self.bot._config["function"]["leavechannel"]))

            now_HMS = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            created_at_format = member.created_at.strftime('%Y/%m/%d %H:%M:%S') if member.joined_at else '未知'

            embed = discord.Embed(
                title=f"**{member}離開了**", 
                description = f'當前人數:{member.guild.member_count}', 
                color=0x32EBA7,
                )  
            embed.add_field(
                name = "**創建時間**",
                value = f"{created_at_format}",         
                inline=True                   
            )
            embed.add_field(
                name = "**加入時間**",
                value = f"{now_HMS}", 
                inline=True                           
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")

            await renamechannel.edit(name=f'全部人數：{member.guild.member_count}')

            await leavechannel.send(f'{member.mention} 離開了伺服器！', embed=embed) 


            print(f'更改了人數')
            print('-'*40)