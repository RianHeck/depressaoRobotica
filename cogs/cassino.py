from random import randint
import discord
from discord.ext import commands
from discord.ui import View
from utils.db import *
from utils.json import *
from utils.checks import *
import asyncio
from numpy import interp

sys.path.append("..")

usuarios_jogando = {}

class Sessao():
    def __init__(self, contexto : tuple) -> None:
        self.jogador = contexto[0]
        self.canal = contexto[1]
        self.view = cassinoView(timeout=20, sessao=self)
        usuarios_jogando[contexto] = self
    
    async def comeca(self):
        await self.view.comeca()

class cassinoView(View):
    def __init__(self, *items: discord.ui.Item, timeout: float = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.sessao = sessao
        self.embedMensagem = 0
        self.pontosJogador = 0
        self.pontosBot = 0
        self.rodada = 1
        self.cartasPegas = [0] * 14
        self.embed = discord.Embed(title='Blackjack', description='Chegue o mais próximo de 21!')

    def resetarDeque(self):
        for i in range(1, 14):
            self.cartasPegas[i] = 0

    async def pegaCarta(self):
        if self.cartasPegas.count(4) == 13:
            await self.sessao.canal.send("Acabaram as cartas. Como isso aconteceu?")
            return 
        carta = randint(1, 13)
        while(self.cartasPegas[carta] == 4):
            carta = randint(1, 13)
        self.cartasPegas[carta] += 1
        return carta
    
    async def comeca(self):
        self.totalCartasJogador = 0
        self.totalCartasBot = 0
        self.resetarDeque()
        self.ultimaCarta = 0
        self.vezDoJogador = True
        await self.embedComeco()
        res = await self.wait()
        if res:
            await self.encerra()
        # self.embedMensagem = await self.sessao.canal.send(embed=self.embed, view=self)
        # if self.embedMensagem == 0:
        #     self.embedMensagem = await self.sessao.canal.send(embed=self.embed, view=self)
        # await self.atualizaEmbed()

    async def encerra(self):
        self.clear_items()
        self.embed.clear_fields()
        self.embed.add_field(name='Jogo Encerrado', value='\u200b', inline=False)
        self.embed.add_field(name='Pontos', value=f'Seus Pontos {self.sessao.jogador.mention}: {self.pontosJogador}\nPontos Bot: {self.pontosBot}', inline=False)
        await self.embedMensagem.edit(embed=self.embed, view=self)
        self.stop()
        del usuarios_jogando[(self.sessao.jogador, self.sessao.canal)]
        del self.sessao
        del self

    async def embedComeco(self):
        self.embed.clear_fields()
        self.embed.add_field(name='**Sua Vez**', value=f'**Rodada {self.rodada}**', inline=False)
        self.embed.add_field(name='Pontos', value=f'Seus Pontos: {self.pontosJogador}\nPontos Bot: {self.pontosBot}', inline=False)
        self.embed.add_field(name='Quantidade de Cartas Suas', value=f'`{self.totalCartasJogador}`')
        self.embed.add_field(name='Quantidade de Cartas Bot', value=f'`{self.totalCartasBot}`')
        if self.embedMensagem == 0:
            self.embedMensagem = await self.sessao.canal.send(embed=self.embed, view=self)
        else:
            await self.embedMensagem.edit(embed=self.embed, view=self)

    async def atualizaEmbed(self):
        self.embed.clear_fields()
        if self.vezDoJogador:
            self.embed.add_field(name='**Sua Vez**', value=f'**Rodada {self.rodada}**', inline=False)
            self.embed.add_field(name='Pontos', value=f'Seus Pontos: {self.pontosJogador}\nPontos Bot: {self.pontosBot}', inline=False)
            self.embed.add_field(name='Quantidade de Cartas Suas', value=f'`{self.totalCartasJogador}`')
            self.embed.add_field(name='Quantidade de Cartas Bot', value=f'`{self.totalCartasBot}`')
            self.embed.add_field(name=f'Você retirou um `{self.ultimaCarta}`', value='\u200b', inline=False)
        else:
            self.embed.add_field(name='**Vez do Bot**', value=f'**Rodada {self.rodada}**', inline=False)
            self.embed.add_field(name='Pontos', value=f'Seus Pontos: {self.pontosJogador}\nPontos Bot: {self.pontosBot}', inline=False)
            self.embed.add_field(name='Quantidade de Cartas Suas', value=f'`{self.totalCartasJogador}`')
            self.embed.add_field(name='Quantidade de Cartas Bot', value=f'`{self.totalCartasBot}`')
            self.embed.add_field(name=f'O Bot retirou um `{self.ultimaCarta}`', value='\u200b', inline=False)
        await self.embedMensagem.edit(embed=self.embed, view=self)

    async def finalizaRodada(self):
        self.embed.clear_fields()
        self.embed.add_field(name='**Fim da rodada**', value=f'**Rodada {self.rodada}**', inline=False)
        self.embed.add_field(name='Suas Cartas', value=f'`{self.totalCartasJogador}`')
        self.embed.add_field(name='Cartas do Bot', value=f'`{self.totalCartasBot}`')

        if self.totalCartasJogador > 21 and self.totalCartasBot > 21:
            self.embed.add_field(name='Ninguém ganhou!', value='\u200b', inline=False)

        elif self.totalCartasBot > 21:
            self.pontosJogador += 1
            self.embed.add_field(name='Você ganhou!', value='\u200b', inline=False)

        elif self.totalCartasJogador > 21:
            self.pontosBot += 1
            self.embed.add_field(name='O bot ganhou!', value='\u200b', inline=False)

        elif self.totalCartasBot > self.totalCartasJogador:
            self.pontosBot += 1
            self.embed.add_field(name='O bot ganhou!', value='\u200b', inline=False)

        elif self.totalCartasBot < self.totalCartasJogador:
            self.pontosJogador += 1
            self.embed.add_field(name='Você ganhou!', value='\u200b', inline=False)

        elif self.totalCartasBot == self.totalCartasJogador:
            self.pontosBot += 1
            self.pontosJogador += 1
            self.embed.add_field(name='Os dois ganharam!', value='\u200b', inline=False)


        await self.embedMensagem.edit(embed=self.embed, view=self)
        self.resetarDeque()
        self.rodada += 1


    # async def jogadaBot(self):
    #     await asyncio.sleep(1)
    #     while(1):
    #         if (21 - self.totalCartasBot) >= 13:
    #             chance = 100
    #         else:
    #             chance = interp(21 - self.totalCartasBot, [0, 21], [0, 100])
    #         numero = randint(0, 99)
    #         if ((numero > chance) or (self.totalCartasBot > self.totalCartasJogador and self.totalCartasJogador < 21)) and not (self.totalCartasBot < self.totalCartasJogador) or (self.totalCartasJogador > 21):
    #             break
    #         self.ultimaCarta = randint(1, 13)
    #         self.totalCartasBot += self.ultimaCarta
    #         if self.totalCartasBot >= 21:
    #             break
    #         else:
    #             await self.atualizaEmbed()
    #             await asyncio.sleep(1)
        
    #     await self.finalizaRodada()
    #     await asyncio.sleep(2)
    #     await self.comeca()

    async def jogadaBot(self):
        await asyncio.sleep(1)
        while(self.totalCartasBot < 21 and self.totalCartasBot < self.totalCartasJogador and self.totalCartasJogador <= 21):
            self.ultimaCarta = await self.pegaCarta()
            self.totalCartasBot += self.ultimaCarta
            await self.atualizaEmbed()
            await asyncio.sleep(1)
        
        await self.finalizaRodada()
        await asyncio.sleep(2)
        await self.comeca()

    @discord.ui.button(label='Pedir Carta', custom_id="pedir_carta", style=discord.ButtonStyle.primary)
    async def pedir_callback(self, button, interaction):
        if not self.vezDoJogador:
            await interaction.response.send_message('Vez do Bot, espera', ephemeral=True)
            await interaction.delete_original_message(delay=2)
            return
        await interaction.response.defer()
        self.ultimaCarta = await self.pegaCarta()
        self.totalCartasJogador += self.ultimaCarta
        await self.atualizaEmbed()
        # if self.totalCartasJogador >= 21:
        #     self.vezDoJogador = False
        #     await self.jogadaBot()

    @discord.ui.button(label="Parar de Pedir", custom_id="parar_de_pedir", style=discord.ButtonStyle.secondary)
    async def parar_callback(self, button, interaction):
        if not self.vezDoJogador:
            await interaction.response.send_message('Vez do Bot, espera', ephemeral=True)
            await interaction.delete_original_message(delay=2)
            return
        await interaction.response.defer()
        self.vezDoJogador = False
        await self.jogadaBot()

    @discord.ui.button(label="Encerrar Jogo", custom_id="encerrar", style=discord.ButtonStyle.danger)
    async def encerrar_callback(self, button, interaction):
        await self.encerra()

class Cassino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kassino(self, ctx):
        sessao = Sessao((ctx.author, ctx.channel))
        await sessao.comeca()


async def setup(bot):
    await bot.add_cog(Cassino(bot))
