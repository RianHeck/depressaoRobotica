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
from utils.json import load_json

# fazer rpg simples que nem simpleMMO
# ganhar moedas ao matar bichos
# usar moedas pra upar ou taxar outras pessoas no server
# outro jogo dá bonus ou algo assim
# economia em db
# prova de calc amanha e trabalho de humanas;

# rpg em c do prof

# ativar e desativar pvp próprio com cooldown de 2 horas
# ter embed ou reaction de confirmação

# roubar moedas ao ganhar pvp, quantidade máxima por dia ou
# algo assim

# mercante? trade entre players (talvez muito difícil)?

usuarios_jogando = {}

DINHEIRO = 0

arquivoItems = 'json/itemsRPG.json'

def jogando():
    async def predicate(ctx):
        return (ctx.author, ctx.channel) in usuarios_jogando
    return commands.check(predicate)

def nao_jogando():
    async def predicate(ctx):
        return (ctx.author, ctx.channel) not in usuarios_jogando
    return commands.check(predicate)

# carregar o json no init, recarregar via comando se precisar
# parar de reabrir ele toda vez que consultar
async def carrega_items():
    arquivo = load_json(arquivoItems)
    return arquivo

async def traduz_item(item):
    arquivo = await carrega_items()
    try:
        item_traduzido = arquivo[item]
    except KeyError:
        return -1
    else:
        return item_traduzido
    # nomes = [arquivo[item][0]['nome'] for item in arquivo]

    # await ctx.send(f'Todos os items:\n{", ".join(nomes)}')

class Personagem():
    def __init__(self, hp, dmg, defa, items) -> None:
        # usar db para pegar os status e itens
        self.hp = hp
        self.dmg = dmg
        self.defa = defa
        self.items = items
        # self.nome = None
        #self.descricao = None
        #self.imagem_url = None

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
        
MINOTAURO = {'nome' : 'Minotauro', 'descricao' : 'O grande minotauro, o inimigo mais forte do andar.',
             'hp' : 100, 'dmg' : 12, 'defa' : 7, 
             'imagem_url' : 'https://i.imgur.com/EMOGjSp.png'}

GOBLIN = {'nome' : 'Goblin', 'descricao' : 'Um goblin qualquer, estranhamente com medo de armaduras de aço.',
             'hp' : 40, 'dmg' : 4, 'defa' : 1, 
             'imagem_url' : 'https://i.imgur.com/inZND3P.png'}


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
        # self.personagem_jogador = Personagem()

        usuarios_jogando[contexto] = self

    async def comeca(self, ctx):
        self.db_usuario = (dbReturnDict(f'SELECT * FROM {tableRPG} WHERE id_usuario = {ctx.author.id};'))
        if len(self.db_usuario) == 0:
            self.personagem_jogador = await self.cria_personagem()
            self.db_usuario = self.personagem_jogador.__dict__
        else:
            self.db_usuario = self.db_usuario[0]
            items = self.db_usuario['items'].split(';')
            self.personagem_jogador = await self.cria_personagem(hp=self.db_usuario['hp'], dmg=self.db_usuario['dmg'], defa=self.db_usuario['defa'], items=items)

        await self.escolhe_inimigo()
        if not ctx.channel.type == discord.ChannelType.private:
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        res = await self.view.wait()
        if res:
            await ctx.channel.send('É minha vez de jogar!(Jogador Ocioso)', delete_after=5)
            await self.parar()
        del self.view

    # meio inútil, depois revisar
    async def cria_personagem(self, hp=100, dmg=10, defa=2, items=[]):
        personagem = Personagem(hp, dmg, defa, items)
        return personagem

    def cria_inimigo(self, inimigo):
        objeto = Inimigo(nome=inimigo['nome'], descricao=inimigo['descricao'], hp=inimigo['hp'], dmg=inimigo['dmg'], defa=inimigo['defa'])
        if inimigo['imagem_url'] is not None:
            objeto.imagem_url = inimigo['imagem_url']
        return objeto

    async def escolhe_inimigo(self):
        # variar chances de acordo com o nivel
        escolha_inimigo = choices(self.inimigos, weights=(20, 80), k=1)
        self.inimigo = self.cria_inimigo(escolha_inimigo[0])
        self.embed_atual = cria_embed(self.inimigo)
        self.embed_mensagem = await self.canal.send(embed=self.embed_atual, view=self.view)

    async def parar(self):
        self.view.clear_items()
        await self.embed_mensagem.edit(embed=self.embed_atual, view=self.view)
        self.view.stop()
        del usuarios_jogando[(self.jogador, self.canal)]
        await self.embed_mensagem.delete()
        del self

class rpgView(View):
    def __init__(self, *items: discord.ui.Item, timeout: discord.Optional[float] = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.sessao = sessao

    @discord.ui.button(emoji="⚔️", custom_id="atacar")
    async def attack_callback(self, button, interaction):
        await interaction.response.defer()
        self.sessao.embed_atual.clear_fields()
        dano_causado, dano_sofrido = self.sessao.personagem_jogador.attack(self.sessao.inimigo)
        if self.sessao.inimigo.hp <= 0:
            await self.sessao.canal.send(f'{self.sessao.jogador.mention} matou {self.sessao.inimigo.nome}!')
            self.sessao.embed_atual.set_image(url=discord.Embed.Empty)
            dinheiro = randint(0, 10)
            global DINHEIRO
            DINHEIRO += dinheiro
            self.sessao.embed_atual.add_field(name=f'Morto por {self.sessao.jogador.name}', value=f'Ganhou {dinheiro} moedas de ouro.')
            await self.sessao.parar()
        else:
            self.sessao.embed_atual.add_field(name='Você atacou!', value=f'Causou {dano_causado}, hp inimigo = {self.sessao.inimigo.hp}')
            self.sessao.embed_atual.add_field(name=f'{self.sessao.inimigo.nome} atacou!', value=f'Causou {dano_sofrido}, seu hp = {self.sessao.personagem_jogador.hp}')
            await self.sessao.embed_mensagem.edit(embed=self.sessao.embed_atual, view=self)

    @discord.ui.button(emoji="🛑", custom_id="parar")
    async def parar_callback(self, button, interaction):
        await interaction.response.defer()
        await self.sessao.parar()

class Rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        dbExecute(f'''CREATE TABLE IF NOT EXISTS {tableRPG}(
                            id_usuario INT PRIMARY KEY,
                            hp INT,
                            dmg INT,
                            defa INT,
                            items TEXT,
                            moedas INT
                        );
                        '''
        )

    @commands.command()
    async def coloca(self, ctx, hp, dmg, defa):
        moedas = 42
        dbExecute(f'''INSERT INTO {tableRPG}(id_usuario, hp, dmg, defa, items, moedas) VALUES({ctx.author.id},{hp},{dmg}, {defa}, "espada;escudo", {moedas})
                            ON CONFLICT(id_usuario) DO UPDATE SET hp=excluded.hp, dmg=excluded.dmg, defa=excluded.defa, items=excluded.items, moedas=excluded.moedas;''')

    # APENAS ACESSAR A DB EM UM LUGAR POR VEZ
    # ENQUANTO TIVER JOGANDO, NÃO PODER EXECUTAR OUTROS COMANDOS QUE
    # ACESSEM TAMBÉM
    @commands.command()
    async def tira(self, ctx, palavra):
        db_usuario = (dbReturnDict(f'SELECT * FROM {tableRPG} WHERE id_usuario = {ctx.author.id};'))
        if len(db_usuario) == 0:
            await ctx.send('Você não tem um personagem criado!')
            return
        db_usuario = db_usuario[0]
        usuario = self.bot.get_user(db_usuario['id_usuario'])
        # items = db_usuario['items'].split(';')
        items = db_usuario['items'].replace(';', ', ')
        await ctx.send(f"{usuario.name}\nhp: {db_usuario['hp']}, dano: {db_usuario['dmg']}, defesa: {db_usuario['defa']}, items: {items}, moedas: {db_usuario['moedas']}")
        arquivo = await carrega_items()
        nomes = [arquivo[item]['nome'] for item in arquivo]
        await ctx.send(f'Todos os items:\n{", ".join(nomes)}')
        item = await traduz_item(palavra.lower())
        if item == -1:
            await ctx.send('item não existe')
        else:
            await ctx.send(item)
        
        # await ctx.send(items)

    @commands.command()
    async def status(self, ctx, item):
        item_traduzido = await traduz_item(item.lower())
        if item_traduzido == -1:
            await ctx.send('item não existe')
        else:
            mensagem = ''
            for status in item_traduzido:
                mensagem += (f'{status.capitalize()} : {item_traduzido[status]}\n')
            await ctx.send(f'{mensagem}')

    @commands.command()
    @nao_jogando()
    async def luta(self, ctx):
        sessao = Sessao((ctx.author, ctx.channel))
        await sessao.comeca(ctx)

    @commands.command()
    async def din(self, ctx):
        sessao = usuarios_jogando[(ctx.author, ctx.channel)]
        await ctx.send(f'Você tem {DINHEIRO} moedas de ouro')
        await ctx.send(f'{sessao.personagem_jogador.__dict__}')



def setup(bot):
    bot.add_cog(Rpg(bot))
