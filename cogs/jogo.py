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
        self.view = jogoView(timeout=20, sessao=self)

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
        self.view.stop()
        del usuarios_jogando[(self.jogadorId, self.canal)]


class jogoView(View):
    def __init__(self, *items: discord.ui.Item, timeout: discord.Optional[float] = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.ultimaMens = None
        self.sessao = sessao

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        await self.sessao.parar()
        await self.sessao.canal.send('Deu ruim! Fale com o maluco que mantém o GitHub.\nhttps://github.com/RiruAugusto/depressaoRobotica')
        return await super().on_error(error, item, interaction)

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
        self.sessao.mapas[self.sessao.lugar_atual].clear_fields()

    @discord.ui.button(emoji="🛑", custom_id="preto")
    async def button1_callback(self, button, interaction):
        await interaction.response.defer()
        parando = await self.sessao.canal.send('Parando jogo.')
        await parando.delete(delay=5)
        await self.sessao.parar()
    
    @discord.ui.button(emoji="⬆️", custom_id="cima")
    async def button2_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'patio':
            self.sessao.lugar_atual = 'floresta'
        elif self.sessao.lugar_atual == 'galinheiro':
            self.sessao.lugar_atual = 'patio'
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="🖐️", custom_id="pegar")
    async def button3_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'lagoa':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você toma banho', value='Agora você pode ir para a casa da dona Jocelina!')
                # await interaction.response.edit_message(content="Você toma banho")
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você já tomou banho', value='Vai lá pegar a rede na casa!')
                # await interaction.response.edit_message(content="Você já tomou banho")
        elif self.sessao.lugar_atual == 'casa':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você pega a rede', value='Dá pra pegar a Betty na floresta agora!')
                # await interaction.response.edit_message(content="Você pega a rede")
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você já pegou a rede', value='Tenta pegar a Betty na floresta!')
                # await interaction.response.edit_message(content="Você já pegou a rede")
        elif self.sessao.lugar_atual == 'floresta':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                if 'rede' in self.sessao.items:
                    self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                    self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você pega a Betty', value='Leva ela de volta pro galinheiro!')
                    # await interaction.response.edit_message(content="Você pega a Betty")
                else:
                    self.sessao.mapas[self.sessao.lugar_atual].add_field(name='A Betty corre demais, você vai precisar da rede', value='A dona Jocelina tem uma na casa dela!')
                    # await interaction.response.edit_message(content="A Betty corre demais, você vai precisar da rede")
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você já pegou a Betty', value='Só levar ela pro galinheiro!')
                # await interaction.response.edit_message(content="Você já pegou a Betty")
        else:
            self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você tenta pegar o vento...', value='Realmente não tem nada de interessante aqui pra pegar.')
            # await interaction.response.edit_message(content="Não tem nada pra pegar aqui")
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
                return
            else:
                self.sessao.lugar_atual = 'galinheiro'
        elif self.sessao.lugar_atual == 'floresta':
            self.sessao.lugar_atual = 'patio'
        # await interaction.response.edit_message(content="baixo")
        await self.atualiza_botoes(interaction)
    
    @discord.ui.button(emoji="➡️", row=2, custom_id="direita")
    async def button8_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'patio':
            if 'banho' in self.sessao.items:
                self.sessao.lugar_atual = 'casa'
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Tu tá fedendo demais para ir na casa, vá tomar um banho antes', value='Dá pra tomar banho no lago.')
                # await interaction.response.edit_message(content='Tu tá fedendo demais para ir na casa, vá tomar um banho antes')
        elif self.sessao.lugar_atual == 'lagoa':
            self.sessao.lugar_atual = 'patio'
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
        sessao = Sessao((ctx.author.id, ctx.channel))
        await sessao.cria_mapa()
        if not ctx.channel.type == discord.ChannelType.private:
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        res = await sessao.view.wait()
        if res:
            delMsg = await ctx.channel.send("É minha vez de jogar!(Jogador Ocioso)")
            await delMsg.delete(delay=5)
            await sessao.parar()
        else:
            if 'betty' in sessao.items:
                await ctx.channel.send(f'{ctx.author.mention} Zerou!')
        del sessao
        

    @commands.command(enabled=False)
    @jogando()
    async def parar(self, ctx):
        sessao = usuarios_jogando[(ctx.author.id, ctx.channel)]
        await sessao.parar()
        del sessao
        del usuarios_jogando[(ctx.author.id, ctx.channel)]
        msg = await ctx.reply('Parando jogo')
        await msg.delete(delay=10)
        await ctx.message.delete()

    @jogar.error
    async def jogarHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            self.bot_mens = await ctx.reply('Você já está jogando!')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @parar.error
    async def comandosHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('Você não está jogando!')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(Jogo(bot))