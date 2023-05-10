from discord.ext import commands
import discord
from utils import db


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Errors(bot))
