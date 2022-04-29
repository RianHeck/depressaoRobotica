from discord.ext import commands
import discord
from main import prefix

class Basico(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Conectado como {self.bot.user}')
        await self.bot.change_presence(activity=discord.Game(f'"{prefix}comandos" para ajuda'))

        print(f'Bot foi iniciado, com {len(self.bot.users)} usuários, em {len(self.bot.guilds)} servers.')

def setup(bot):
    bot.add_cog(Basico(bot))