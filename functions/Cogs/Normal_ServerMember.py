from discord.ext import commands
import discord
import datetime

class Normal_ServerMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            print(f'{member} 加入了伺服器')
            print('-'*40)
            now_HMS = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            # created_at 為 UTC-aware，顯示轉台灣時間(+8)，與「加入時間」一致
            if member.created_at:
                created_at_format = (member.created_at + datetime.timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S')
            else:
                created_at_format = '未知'

            # 帳號創建未滿 14 天 → 紅色警示
            account_age = datetime.datetime.now(datetime.timezone.utc) - member.created_at
            is_new_account = account_age < datetime.timedelta(days=14)

            renamechannel = member.guild.get_channel(int(self.bot._config["function"]["membercountchannel"]))
            welcomechannel = member.guild.get_channel(int(self.bot._config["function"]["welcomechannel"]))

            embed = discord.Embed(
                title=f"**歡迎 {member}**",
                description = f'當前人數:{member.guild.member_count}',
                color=0xff0000 if is_new_account else 0x32EBA7,
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
            if is_new_account:
                embed.add_field(
                    name = "⚠️ 新帳號",
                    value = f"創建未滿 14 天（{account_age.days} 天前創建）",
                    inline=False
                )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")
            await welcomechannel.send(f'歡迎 {member.mention} 加入伺服器！\n 可以去頻道最上方<id:customize>，新增或更改自己想要的身分組以使用更多功能喔！', embed=embed) 

            await renamechannel.edit(name=f'全部人數：{member.guild.member_count}')
            print(f'更改了人數')
            print('-'*40)


    @commands.Cog.listener()
    async def on_member_remove(self, member):        
        if member.guild.id == int(self.bot._config["function"]["tmsguildid"]):
            print(f'{member} 離開了伺服器')
            print('-'*40)
            
            renamechannel = member.guild.get_channel(int(self.bot._config["function"]["membercountchannel"]))
            leavechannel = member.guild.get_channel(int(self.bot._config["function"]["leavechannel"]))

            now_HMS = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            # created_at 為 UTC-aware，顯示轉台灣時間(+8)，與「加入時間」一致
            if member.created_at:
                created_at_format = (member.created_at + datetime.timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S')
            else:
                created_at_format = '未知'

            embed = discord.Embed(
                title=f"**{member}離開了**", 
                description = f'當前人數:{member.guild.member_count}', 
                color=0xff0000,
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
            await leavechannel.send(f'{member.mention} 離開了伺服器！', embed=embed) 

            await renamechannel.edit(name=f'全部人數：{member.guild.member_count}') 
            print(f'更改了人數')
            print('-'*40)
