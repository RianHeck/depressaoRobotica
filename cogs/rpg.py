from __future__ import annotations
from random import choices, randint, random, choice
from discord.ext import commands
from discord.ui import View, Button
import discord
import sys
import traceback
import time
from utils.db import *
from main import prefix


# fazer rpg simples que nem simpleMMO
# ganhar moedas ao matar bichos
# usar moedas pra upar ou taxar outras pessoas no server
# outro jogo dá bonus ou algo assim
# economia em db
# prova de calc amanha e trabalho de humanas;

# rpg em c do prof

usuarios_jogando = {}

DINHEIRO = 0

def jogando():
    async def predicate(ctx):
        return (ctx.author, ctx.channel) in usuarios_jogando
    return commands.check(predicate)

def nao_jogando():
    async def predicate(ctx):
        return (ctx.author, ctx.channel) not in usuarios_jogando
    return commands.check(predicate)

class Personagem():
    def __init__(self) -> None:
        # usar db para pegar os status e itens
        self.hp = 100
        self.dmg = 10
        self.defa = 2
        self.items = []
        self.descricao = None
        self.nome = None
        self.imagem_url = None

    def attack(self, outro : Inimigo):
        dano_causado = randint(0, self.dmg) - outro.defa
        if dano_causado < 0:
            dano_causado = 0
        dano_sofrido = randint(0, outro.dmg) - self.defa
        if dano_sofrido < 0:
            dano_sofrido = 0
        outro.hp -= dano_causado
        self.hp -= dano_sofrido
        return dano_causado, dano_sofrido

class Inimigo():
    def __init__(self, nome, descricao, hp, dmg, defa) -> None:
        # usar db para pegar os status e itens
        self.nome = nome
        self.descricao = descricao
        self.hp = hp
        self.dmg = dmg
        self.defa = defa
        self.imagem_url = None

MINOTAURO = Inimigo(nome='Minotauro', descricao='O grande minotauro, o inimigo mais forte do andar.', 
                    hp=100, dmg=12, defa=7)
MINOTAURO.imagem_url = 'https://i.imgur.com/uVdpzOc.png'

GOBLIN = Inimigo(nome='Goblin', descricao='Um goblin qualquer, estranhamente com medo de armaduras de aço.', 
                    hp=40, dmg=4, defa=1)
GOBLIN.imagem_url = 'https://i.imgur.com/kDDR9lU.png'


def cria_embed(inimigo : Inimigo):
    embed = discord.Embed(title=inimigo.nome, description=inimigo.descricao)
    embed.set_image(url=inimigo.imagem_url)
    return embed


# class Inimigo(Personagem):
#     def __init__(self) -> None:
#         super().__init__()
#         self.descricao


class Sessao():
    def __init__(self, contexto : tuple) -> None:
        self.jogador = contexto[0]
        self.canal = contexto[1]
        self.view = rpgView(timeout=20, sessao=self)
        self.inimigos = [MINOTAURO, GOBLIN]
        self.embed_atual = None
        self.personagem_jogador = Personagem()

        usuarios_jogando[contexto] = self

    async def comeca(self):
        await self.escolhe_inimigo()

    async def escolhe_inimigo(self):
        # variar chances de acordo com o nivel
        self.inimigo = choices(self.inimigos, weights=(20, 80), k=1)
        self.embed_atual = cria_embed(self.inimigo[0])
        self.embed = await self.canal.send(embed=self.embed_atual, view=self.view)

    async def parar(self):
        self.view.clear_items()
        await self.embed.edit(embed=self.embed_atual, view=self.view)
        self.view.stop()
        del usuarios_jogando[(self.jogador, self.canal)]

class rpgView(View):
    def __init__(self, *items: discord.ui.Item, timeout: discord.Optional[float] = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.sessao = sessao

    @discord.ui.button(emoji="⚔️", custom_id="atacar")
    async def attack_callback(self, button, interaction):
        await interaction.response.defer()
        self.sessao.embed_atual.clear_fields()
        dano_causado, dano_sofrido = self.sessao.personagem_jogador.attack(self.sessao.inimigo[0])
        if self.sessao.inimigo[0].hp <= 0:
            await self.sessao.canal.send(f'Matou {self.sessao.inimigo[0].nome}!')
            self.sessao.embed_atual.set_image(url=discord.Embed.Empty)
            dinheiro = randint(0, 10)
            global DINHEIRO
            DINHEIRO += dinheiro
            self.sessao.embed_atual.add_field(name=f'Morto por {self.sessao.jogador.name}', value=f'Ganhou {dinheiro} moedas de ouro.')
            await self.sessao.parar()
        else:
            self.sessao.embed_atual.add_field(name='Você atacou!', value=f'Causou {dano_causado}, hp inimigo = {self.sessao.inimigo[0].hp}')
            self.sessao.embed_atual.add_field(name=f'{self.sessao.inimigo[0].nome} atacou!', value=f'Causou {dano_sofrido}, seu hp = {self.sessao.personagem_jogador.hp}')
            await self.sessao.embed.edit(embed=self.sessao.embed_atual, view=self)

class Rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @nao_jogando()
    async def luta(self, ctx):
        sessao = Sessao((ctx.author, ctx.channel))
        await sessao.comeca()

    @commands.command()
    async def din(self, ctx):
        await ctx.send(f'Você tem {DINHEIRO} moedas de ouro')



async def setup(bot):
    await bot.add_cog(Rpg(bot))
