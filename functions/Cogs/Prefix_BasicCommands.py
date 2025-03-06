from discord.ext import commands
import random

class Prefix_BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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