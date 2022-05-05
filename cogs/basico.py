from discord.ext import commands
import discord
from main import prefix, testeID

class Basico(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Conectado como {self.bot.user}')
        await self.bot.change_presence(activity=discord.Game(f'"{prefix}comandos" para ajuda'))

        print(f'Bot foi iniciado, com {len(self.bot.users)} usuários, em {len(self.bot.guilds)} servers.')

    @commands.command()
    async def limpa(self, ctx):

        if ctx.author.id == int(testeID):
            canal = self.bot.get_channel(int(958058492550316113))
            await canal.purge(bulk=False)

def setup(bot):
    bot.add_cog(Basico(bot))