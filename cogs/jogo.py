from discord.ext import commands
import discord
import sys
import traceback

# depois usar db para guardar jogadores simultaneos
usuarios_jogando = []


class Jogo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.lugares_acessiveis = [['patio', 'lagoa'], ['patio', 'casa'], ['patio', 'floresta'], ['patio', 'galinheiro']]
        self.onde_esta = {'lagoa': 'banho', 'casa': 'rede', 'floresta': 'betty'}
        self.items = []
        self.lugar_atual = 'patio'

        self.patio = discord.Embed(title='Patio', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
        self.patio.set_image(url='https://i.imgur.com/uVdpzOc.png')
        self.lagoa = discord.Embed(title='Lagoa', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
        self.lagoa.set_image(url='https://i.imgur.com/ppiVZaZ.png')
        self.floresta = discord.Embed(title='Floresta', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
        self.floresta.set_image(url='https://i.imgur.com/MKFUieh.png')
        self.casa = discord.Embed(title='Casa', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
        self.casa.set_image(url='https://i.imgur.com/ogGPewJ.png')
        self.galinheiro = discord.Embed(title='Galinheiro', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
        self.galinheiro.set_image(url='https://i.imgur.com/kDDR9lU.png')

        self.mapas = {'patio' : self.patio, 'lagoa' : self.lagoa, 'floresta' : self.floresta, 'casa' : self.casa, 'galinheiro' : self.galinheiro}

        self.mapa = self.patio
        self.bot_mens = None



    # async def executa_jogo(self, ctx):

    #     comandos = ['ir', 'pegar']

    #     def check(m):
    #         #return  m.channel == ctx.channel and m.author == ctx.author and (m.content.lower().startswith('ir ') or m.content.lower().startswith('pegar '))
    #         return  m.channel == ctx.channel and m.author == ctx.author
    #     finalizado = False
    #     while(not finalizado):
    #         msg = await self.bot.wait_for('message', check=check)
    #         if msg.content.lower().startswith('ir'):
    #             await msg.reply(f'Hello {msg.author.mention}!')
    #         finalizado = True

    async def executa_jogo(self, ctx):
        pass

    def jogando():
        async def predicate(ctx):
            return ctx.author.id in usuarios_jogando
        return commands.check(predicate)

    def nao_jogando():
        async def predicate(ctx):
            return ctx.author.id not in usuarios_jogando
        return commands.check(predicate)

    async def cria_mapa(self):
        self.mapa = self.patio

    async def atualiza_mapa(self):
        await self.embed.edit(embed=self.mapas[self.lugar_atual])

    @commands.command()
    @nao_jogando()
    async def jogar(self, ctx):
        self.lugares_acessiveis = [['patio', 'lagoa'], ['patio', 'casa'], ['patio', 'floresta'], ['patio', 'galinheiro']]
        self.onde_esta = {'lagoa': 'banho', 'casa': 'rede', 'floresta': 'betty'}
        self.items = []
        self.lugar_atual = 'patio'
        msg = await ctx.reply('Utilize os comandos !ir [lugar] ou !pegar[algo]')
        await msg.delete(delay=30)
        self.embed = await ctx.reply(embed=self.mapa)
        await ctx.message.delete()
        await self.atualiza_mapa()
        usuarios_jogando.append(ctx.author.id)

    @commands.command()
    @jogando()
    async def parar(self, ctx):
        usuarios_jogando.remove(ctx.author.id)
        msg = await ctx.reply('Parando jogo')
        await msg.delete(delay=10)
        await self.embed.delete()
        await ctx.message.delete()




    @commands.command(hidden=True)
    @jogando()
    async def ir(self, ctx, *, lugar):
        if self.bot_mens is not None:
            await self.bot_mens.delete()
        if lugar == self.lugar_atual:
            self.bot_mens = await ctx.send('Você fica parado no lugar, incrível')
            return

        if [f'{self.lugar_atual}', f'{lugar}'] in self.lugares_acessiveis or [f'{lugar}', f'{self.lugar_atual}'] in self.lugares_acessiveis:
            if lugar == 'casa':
                if 'banho' not in self.items:
                    self.bot_mens = await ctx.send(f'Tu tá fedendo demais para ir na casa, vá tomar um banho antes')
                    return
            self.bot_mens = await ctx.send(f'Você vai para {lugar}')
            self.lugar_atual = lugar
            await self.atualiza_mapa()
        else:
            self.bot_mens = await ctx.send(f'Não consigo chegar em {lugar}')

        if self.lugar_atual == 'galinheiro' and 'betty' in self.items:
            self.bot_mens = await ctx.send(f'Você capturou a Betty!')
            usuarios_jogando.remove(ctx.author.id)
            await self.embed.delete()
        await ctx.message.delete()

    
    @commands.command(hidden=True)
    @jogando()
    async def pegar(self, ctx, *, objeto):
        if self.bot_mens is not None:
            await self.bot_mens.delete()
        if self.lugar_atual in self.onde_esta:
            if self.onde_esta[self.lugar_atual] == objeto:
                if objeto not in self.items:
                    if objeto == 'betty':
                        if 'rede' in self.items:
                            self.bot_mens = await ctx.send(f'Pegou {objeto}')
                            self.items.append(objeto)
                            return
                        else:
                            self.bot_mens = await ctx.send(f'A Betty corre demais, você vai precisar da rede')
                            return
                    else:
                        self.bot_mens = await ctx.send(f'Pegou {objeto}')
                        self.items.append(objeto)
                        return
                else:
                    self.bot_mens = await ctx.send(f'Você já pegou {objeto}')
                    return
        self.bot_mens = await ctx.send(f'Você não tem telepatia para pegar {objeto}')
        await ctx.message.delete()

    @jogar.error
    async def jogarHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            self.bot_mens = await ctx.reply('Você já está jogando!\nUtilize os comandos !ir [lugar] ou !pegar[algo]')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @ir.error
    @pegar.error
    @parar.error
    async def comandosHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('Você não está jogando!')
        elif isinstance(error, commands.MissingRequiredArgument):
            self.bot_mens = await ctx.reply('O que? Aonde? Como? Hoje no globo repórter')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(Jogo(bot))