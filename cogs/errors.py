from discord.ext import commands
import discord

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Errors(bot))
