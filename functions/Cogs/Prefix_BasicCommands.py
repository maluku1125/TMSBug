from discord.ext import commands

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
