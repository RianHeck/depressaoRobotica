from discord.ext import commands
from discord.ui import View, Button
import discord
import sys
import traceback

# depois usar db para guardar jogadores simultaneos
usuarios_jogando = {}

PATIO = discord.Embed(title='Patio', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
PATIO.set_image(url='https://i.imgur.com/uVdpzOc.png')
LAGOA = discord.Embed(title='Lagoa', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
LAGOA.set_image(url='https://i.imgur.com/ppiVZaZ.png')
FLORESTA = discord.Embed(title='Floresta', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
FLORESTA.set_image(url='https://i.imgur.com/MKFUieh.png')
CASA = discord.Embed(title='Casa', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
CASA.set_image(url='https://i.imgur.com/ogGPewJ.png')
GALINHEIRO = discord.Embed(title='Galinheiro', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
GALINHEIRO.set_image(url='https://i.imgur.com/kDDR9lU.png')

LUGARES_ACESSESSIVEIS = [['patio', 'lagoa'], ['patio', 'casa'], ['patio', 'floresta'], ['patio', 'galinheiro']]
ONDE_ESTA = {'lagoa': 'banho', 'casa': 'rede', 'floresta': 'betty'}

class Sessao:
    def __init__(self, contexto : tuple) -> None:
        self.jogadorId = contexto[0]
        self.canal = contexto[1]
        self.view = jogoView(timeout=15, sessao=self)

        usuarios_jogando[contexto] = self

        self.items = []
        self.lugar_atual = 'patio'

        self.mapas = {'patio' : PATIO, 'lagoa' : LAGOA, 'floresta' : FLORESTA, 'casa' : CASA, 'galinheiro' : GALINHEIRO}

        self.mapa = PATIO
        self.bot_mens = None

    async def cria_mapa(self):
        self.mapa = PATIO
        self.embed = await self.canal.send(embed=self.mapa, view=self.view)

    async def atualiza_mapa(self):
        await self.embed.edit(embed=self.mapas[self.lugar_atual], view=self.view)

    async def parar(self):
        if self.bot_mens is not None:
            await self.bot_mens.delete()
        await self.embed.delete()

    async def ir(self, ctx, lugar):
        if self.bot_mens is not None:
            await self.bot_mens.delete()
        if lugar == self.lugar_atual:
            self.bot_mens = await ctx.send('Você fica parado no lugar, incrível')
            return

        if [f'{self.lugar_atual}', f'{lugar}'] in LUGARES_ACESSESSIVEIS or [f'{lugar}', f'{self.lugar_atual}'] in LUGARES_ACESSESSIVEIS:
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

    
    async def pegar(self, ctx, objeto):
        if self.bot_mens is not None:
            await self.bot_mens.delete()
        if self.lugar_atual in ONDE_ESTA:
            if ONDE_ESTA[self.lugar_atual] == objeto:
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

class jogoView(View):
    def __init__(self, *items: discord.ui.Item, timeout: discord.Optional[float] = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.ultimaMens = None
        self.sessao = sessao

    async def atualiza_botoes(self, interaction):
        for x in self.children:
            if x.custom_id != 'pegar' and x.custom_id != 'preto':
                x.disabled = True
        if self.sessao.lugar_atual == 'lagoa':
            botao = [x for x in self.children if x.custom_id=="direita"][0]
            botao.disabled = False
        elif self.sessao.lugar_atual == 'floresta':
            botao = [x for x in self.children if x.custom_id=="baixo"][0]
            botao.disabled = False
        elif self.sessao.lugar_atual == 'casa':
            botao = [x for x in self.children if x.custom_id=="esquerda"][0]
            botao.disabled = False
        elif self.sessao.lugar_atual == 'galinheiro':
            botao = [x for x in self.children if x.custom_id=="cima"][0]
            botao.disabled = False
        else:
            for x in self.children:
                x.disabled = False
        await interaction.edit_original_message(view=self)
        await self.sessao.atualiza_mapa()

    @discord.ui.button(emoji="🛑", custom_id="preto")
    async def button1_callback(self, button, interaction):
        # if self.ultimaMens != None:
        #     await interaction.response.defer()
        #     await self.ultimaMens.edit("nada")
        # else:
        #     await interaction.response.send_message("nada")
        #     self.ultimaMens = await interaction.original_message()
        # await self.stop()
        await interaction.response.defer()
        await self.sessao.parar()
    
    @discord.ui.button(emoji="⬆️", custom_id="cima")
    async def button2_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'patio':
            self.sessao.lugar_atual = 'floresta'
        elif self.sessao.lugar_atual == 'galinheiro':
            self.sessao.lugar_atual = 'patio'
        # await interaction.response.edit_message(content="cima")
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="🖐️", custom_id="pegar")
    async def button3_callback(self, button, interaction):
        if self.sessao.lugar_atual == 'lagoa':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                await interaction.response.edit_message(content="Você toma banho")
            else:
                await interaction.response.edit_message(content="Você já tomou banho")
        elif self.sessao.lugar_atual == 'casa':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                await interaction.response.edit_message(content="Você pega a rede")
            else:
                await interaction.response.edit_message(content="Você já pegou a rede")
        elif self.sessao.lugar_atual == 'floresta':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                if 'rede' in self.sessao.items:
                    self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                    await interaction.response.edit_message(content="Você pega a Betty")
                else:
                    await interaction.response.edit_message(content="A Betty corre demais, você vai precisar da rede")
            else:
                await interaction.response.edit_message(content="Você já pegou a Betty")
        else:
            await interaction.response.edit_message(content="Não tem nada pra pegar aqui")
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="⬅️", row=2, custom_id="esquerda")
    async def button6_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'patio':
            self.sessao.lugar_atual = 'lagoa'
        elif self.sessao.lugar_atual == 'casa':
            self.sessao.lugar_atual = 'patio'
        # await interaction.response.edit_message(content="esquerda")
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="⬇️", row=2, custom_id="baixo")
    async def button7_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'patio':
            if 'betty' in self.sessao.items:
                await self.sessao.parar()
            else:
                self.sessao.lugar_atual = 'galinheiro'
        elif self.sessao.lugar_atual == 'floresta':
            self.sessao.lugar_atual = 'patio'
        # await interaction.response.edit_message(content="baixo")
        await self.atualiza_botoes(interaction)
    
    @discord.ui.button(emoji="➡️", row=2, custom_id="direita")
    async def button8_callback(self, button, interaction):
        if self.sessao.lugar_atual == 'patio':
            if 'banho' in self.sessao.items:
                self.sessao.lugar_atual = 'casa'
            else:
                await interaction.response.edit_message(content='Tu tá fedendo demais para ir na casa, vá tomar um banho antes')
                return
        elif self.sessao.lugar_atual == 'lagoa':
            self.sessao.lugar_atual = 'patio'
        await interaction.response.defer()
        # await interaction.response.edit_message(content="direita")
        await self.atualiza_botoes(interaction)



class Jogo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def jogando():
        async def predicate(ctx):
            return (ctx.author.id, ctx.channel) in usuarios_jogando
        return commands.check(predicate)

    def nao_jogando():
        async def predicate(ctx):
            return (ctx.author.id, ctx.channel) not in usuarios_jogando
        return commands.check(predicate)

    @commands.command()
    @nao_jogando()
    async def jogar(self, ctx):
        # LUGARES_ACESSESSIVEIS = [['patio', 'lagoa'], ['patio', 'casa'], ['patio', 'floresta'], ['patio', 'galinheiro']]
        # ONDE_ESTA = {'lagoa': 'banho', 'casa': 'rede', 'floresta': 'betty'}
        # self.items = []
        # self.lugar_atual = 'patio'
        sessao = Sessao((ctx.author.id, ctx.channel))
        await sessao.cria_mapa()
        # msg = await ctx.reply('Utilize os comandos !ir [lugar] ou !pegar[algo]')
        # await msg.delete(delay=30)
        # self.embed = await ctx.reply(embed=self.mapa)
        await ctx.message.delete()
        # await self.atualiza_mapa()
        # usuarios_jogando[(ctx.author.id, ctx.channel)].append(sessao)
        res = await sessao.view.wait()
        if res:
            delMsg = await ctx.channel.send("É minha vez de jogar!")
            await delMsg.delete(delay=5)
        else:
            await ctx.channel.send("Zerou!")
        await sessao.parar()
        del usuarios_jogando[(ctx.author.id, ctx.channel)]
        del sessao
        

    @commands.command()
    @jogando()
    async def parar(self, ctx):
        #usuarios_jogando.remove((ctx.author.id, ctx.channel))
        sessao = usuarios_jogando[(ctx.author.id, ctx.channel)]
        await sessao.parar()
        del sessao
        del usuarios_jogando[(ctx.author.id, ctx.channel)]
        msg = await ctx.reply('Parando jogo')
        await msg.delete(delay=10)
        # await self.embed.delete()
        await ctx.message.delete()


    @commands.command(hidden=True)
    @jogando()
    async def ir(self, ctx, *, lugar):
        # if self.bot_mens is not None:
        #     await self.bot_mens.delete()
        # if lugar == self.lugar_atual:
        #     self.bot_mens = await ctx.send('Você fica parado no lugar, incrível')
        #     return

        # if [f'{self.lugar_atual}', f'{lugar}'] in LUGARES_ACESSESSIVEIS or [f'{lugar}', f'{self.lugar_atual}'] in LUGARES_ACESSESSIVEIS:
        #     if lugar == 'casa':
        #         if 'banho' not in self.items:
        #             self.bot_mens = await ctx.send(f'Tu tá fedendo demais para ir na casa, vá tomar um banho antes')
        #             return
        #     self.bot_mens = await ctx.send(f'Você vai para {lugar}')
        #     self.lugar_atual = lugar
        #     await self.atualiza_mapa()
        # else:
        #     self.bot_mens = await ctx.send(f'Não consigo chegar em {lugar}')

        # if self.lugar_atual == 'galinheiro' and 'betty' in self.items:
        #     self.bot_mens = await ctx.send(f'Você capturou a Betty!')
        #     usuarios_jogando.remove(ctx.author.id)
        #     await self.embed.delete()
        # await ctx.message.delete()
        sessao = usuarios_jogando[(ctx.author.id, ctx.channel)]
        await sessao.ir(ctx, lugar)

    
    @commands.command(hidden=True)
    @jogando()
    async def pegar(self, ctx, *, objeto):
        # if self.bot_mens is not None:
        #     await self.bot_mens.delete()
        # if self.lugar_atual in ONDE_ESTA:
        #     if ONDE_ESTA[self.lugar_atual] == objeto:
        #         if objeto not in self.items:
        #             if objeto == 'betty':
        #                 if 'rede' in self.items:
        #                     self.bot_mens = await ctx.send(f'Pegou {objeto}')
        #                     self.items.append(objeto)
        #                     return
        #                 else:
        #                     self.bot_mens = await ctx.send(f'A Betty corre demais, você vai precisar da rede')
        #                     return
        #             else:
        #                 self.bot_mens = await ctx.send(f'Pegou {objeto}')
        #                 self.items.append(objeto)
        #                 return
        #         else:
        #             self.bot_mens = await ctx.send(f'Você já pegou {objeto}')
        #             return
        # self.bot_mens = await ctx.send(f'Você não tem telepatia para pegar {objeto}')
        # await ctx.message.delete()
        sessao = usuarios_jogando[(ctx.author.id, ctx.channel)]
        await sessao.pegar(ctx, objeto)


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