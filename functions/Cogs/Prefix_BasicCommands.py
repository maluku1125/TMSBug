from discord.ext import commands
import random
import discord
import time

class Prefix_BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 從 config.ini [function] 讀取（缺少鍵時退回原寫死值）
        self.allowed_role_id = int(bot._config["function"].get("delmsgrole", 1067162303411269672))
        self.log_channel_id = int(bot._config["function"].get("logchannel", 588950084658528257))
        self.delete_message_count = 0
        self.delete_message_timestamp = time.time()
        self.delete_message_enabled = True
        self.delete_message_locktime = time.time()
        
    @commands.command()
    async def hi(self, ctx: commands.Context):
        await ctx.send("Hello, world!")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        bot_latency = round(self.bot.latency * 1000)
        await ctx.send(f"pong, latency is {bot_latency} ms.")
        
    @commands.command()
    async def randnumber(self, ctx: commands.Context, n: int, m: int):
        if n > m:
            await ctx.send("抽的數量不能大於總數")
            return
        if n < 1 or m < 1:
            await ctx.send("n 和 m 必須是正整數")
            return

        # 使用 random.sample() 隨機選擇 n 個數字
        result = random.sample(range(1, m + 1), n)
        await ctx.send(f"隨機選出的數字: {result}")
        
    @commands.command()
    async def delmsg(self, ctx: commands.Context, messageid: int):
        # 檢查使用者是否具有特定身分組
        if not any(role.id == self.allowed_role_id for role in ctx.author.roles):
            await ctx.send("你沒有權限使用這個指令。")
            return
        
        if not self.delete_message_enabled:
            if time.time() - self.delete_message_locktime < 86400:
                await ctx.send(f"此指令暫時禁用，{86400 - int(time.time() - self.delete_message_locktime)} 秒後解鎖。")
                return
            else:
                self.delete_message_enabled = True

        # 檢查是否超過使用次數限制
        current_time = time.time()
        if current_time - self.delete_message_timestamp > 1800:  # 10 分鐘
            self.delete_message_count = 0
            self.delete_message_timestamp = current_time

        if self.delete_message_count >= 10:
            await ctx.send("在 30 分鐘內只能使用 10 次此指令。")
            self.delete_message_enabled = False
            self.delete_message_locktime = time.time()
            return

        self.delete_message_count += 1
        
        await ctx.message.delete()

        try:
            message = await ctx.channel.fetch_message(messageid)
            if message.channel.id != ctx.channel.id:
                await ctx.send("你只能刪除當前頻道的訊息")
                return 
            
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel:
                embed = discord.Embed(title="訊息刪除備份", color=discord.Color.red())
                embed.add_field(name="頻道", value=ctx.channel.name, inline=False)
                embed.add_field(name="訊息ID", value=message.id, inline=False)
                embed.add_field(name="訊息內容", value=message.content, inline=False)
                embed.add_field(name="刪除者", value=ctx.author.display_name, inline=False)
                embed.add_field(name="原發送者", value=message.author.display_name, inline=False)
                
                if message.attachments:
                    for attachment in message.attachments:
                        embed.add_field(name="附件", value=attachment.url, inline=False)
                
                await log_channel.send(embed=embed)
                       
            await message.delete()  
            await ctx.send(f"訊息 {messageid} 已刪除，刪除者：{ctx.author.display_name}")
                  
        except discord.NotFound:
            await ctx.send(f"找不到訊息 {messageid}")
        except discord.Forbidden:
            await ctx.send(f"沒有權限刪除訊息 {messageid}。")
        except discord.HTTPException as e:
            await ctx.send(f"刪除訊息 {messageid} 時發生錯誤：{e}")
