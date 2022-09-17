from discord.ext import commands
import discord

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Errors(bot))
