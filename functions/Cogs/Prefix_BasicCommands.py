from discord.ext import commands
import random
import discord
import time

class Prefix_BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_role_id = 597092130388836362 
        self.delete_message_count = 0
        self.delete_message_timestamp = time.time()

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

        # 檢查是否超過使用次數限制
        current_time = time.time()
        if current_time - self.delete_message_timestamp > 1200:  # 10 分鐘
            self.delete_message_count = 0
            self.delete_message_timestamp = current_time

        if self.delete_message_count >= 30:
            await ctx.send("在 20 分鐘內只能使用 30 次此指令。")
            return

        self.delete_message_count += 1

        try:
            message = await ctx.channel.fetch_message(messageid)
            await message.delete()
            await ctx.send(f"訊息 {messageid} 已刪除。")
        except discord.NotFound:
            await ctx.send(f"找不到訊息 {messageid}。")
        except discord.Forbidden:
            await ctx.send(f"沒有權限刪除訊息 {messageid}。")
        except discord.HTTPException as e:
            await ctx.send(f"刪除訊息 {messageid} 時發生錯誤：{e}")
