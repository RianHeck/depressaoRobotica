from discord.ext import commands
from discord.ui import View, Button
import discord
import sys
import traceback
import time
from utils.db import *
from main import prefix

sys.path.append("..")

# COMANDO PARA VERIFICAR SE A PESSOA CERTA ESTA COM
# OS CARGOS PACIFISTA E GENOCIDA
# TAXAR PESSOA QUE ESTA COM O CARGO ERRONEAMENTE

# GUARDAR TAMBEM A DATA EM QUE O HIGHSCORE FOI ALCANCADO
# COLOCAR MANUAL PARA OS QUE JÁ TEM

# depois usar db para guardar jogadores simultaneos
usuarios_jogando = {}

PATIO = discord.Embed(title='Patio', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
PATIO.set_image(url='https://i.imgur.com/uVdpzOc.png')
# FILE_PATIO = discord.File('images/patio.png', filename='patio.png')
# PATIO.set_image(url='attachment://patio.png')

LAGOA = discord.Embed(title='Lagoa', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
LAGOA.set_image(url='https://i.imgur.com/ppiVZaZ.png')
# FILE_LAGOA = discord.File('images/lagoa.png', filename='lagoa.png')
# LAGOA.set_image(url='attachment://lagoa.png')

FLORESTA = discord.Embed(title='Floresta', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
FLORESTA.set_image(url='https://i.imgur.com/MKFUieh.png')
# FILE_FLORESTA = discord.File('images/floresta.png', filename='floresta.png')
# FLORESTA.set_image(url='attachment://floresta.png')

CASA = discord.Embed(title='Casa', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
CASA.set_image(url='https://i.imgur.com/ogGPewJ.png')
# FILE_CASA = discord.File('images/casa.png', filename='casa.png')
# CASA.set_image(url='attachment://casa.png')

GALINHEIRO = discord.Embed(title='Galinheiro', description='**LUGARES**: patio, lagoa, floresta, casa, galinheiro\n**ITEMS**: banho, rede, betty')
GALINHEIRO.set_image(url='https://i.imgur.com/kDDR9lU.png')
# FILE_GALINHEIRO = discord.File('images/galinheiro.png', filename='galinheiro.png')
# GALINHEIRO.set_image(url='attachment://galinheiro.png')

LUGARES_ACESSESSIVEIS = [['patio', 'lagoa'], ['patio', 'casa'], ['patio', 'floresta'], ['patio', 'galinheiro']]
ONDE_ESTA = {'lagoa': 'banho', 'casa': 'rede', 'floresta': 'betty'}

def jogando():
    async def predicate(ctx):
        return (ctx.author, ctx.channel) in usuarios_jogando
    return commands.check(predicate)

def nao_jogando():
    async def predicate(ctx):
        return (ctx.author, ctx.channel) not in usuarios_jogando
    return commands.check(predicate)

def tem_roleG():
    async def predicate(ctx):
        guilda = ctx.guild
        roleG_id = await dbReturn(f'SELECT * FROM {tableWR} WHERE (id_guilda = {guilda.id} AND tipo = "genocide")')
        if len(roleG_id) != 0:
            roleG = guilda.get_role(roleG_id[0][1])
            if roleG in ctx.author.roles:
                return True
        return False
    return commands.check(predicate)

def tem_roleP():
    async def predicate(ctx):
        guilda = ctx.guild
        roleP_id = await dbReturn(f'SELECT * FROM {tableWR} WHERE (id_guilda = {guilda.id} AND tipo = "pacifist")')
        if len(roleP_id) != 0:
            roleP = guilda.get_role(roleP_id[0][1])
            if roleP in ctx.author.roles:
                return True
        return False
    return commands.check(predicate)

async def scoreboardGuildaAll(guilda):
        scoreboard = await dbReturn(f'SELECT * FROM {tableScoreboard} WHERE id_guilda = {guilda.id};')
        return scoreboard

async def scoreboardGuildaPacifist(guilda):
    scoreboard = await dbReturn(f'SELECT * FROM {tableScoreboard} WHERE (id_guilda = {guilda.id} AND tipo = "pacifist");')
    return scoreboard

async def scoreboardGuildaGenocide(guilda):
    scoreboard = await dbReturn(f'SELECT * FROM {tableScoreboard} WHERE (id_guilda = {guilda.id} AND tipo = "genocide");')
    return scoreboard


async def retornaScoreboard(guilda, tipo):
    if tipo == 'genocide':
        scoreboard = await scoreboardGuildaGenocide(guilda)
    elif tipo == 'pacifist':
        scoreboard = await scoreboardGuildaPacifist(guilda)
    elif tipo == 'any':
        scoreboard = await scoreboardGuildaAll(guilda)
    scoreboard = sorted(scoreboard, key=lambda score: score[3])
    return scoreboard

class Sessao:
    def __init__(self, contexto : tuple) -> None:
        self.startTime = time.time()
        self.endTime = 0
        self.totalTime = 0
        self.insistencia = 0
        self.jogador = contexto[0]
        self.canal = contexto[1]
        self.view = jogoView(timeout=20, sessao=self)

        usuarios_jogando[contexto] = self

        self.items = []
        self.lugar_atual = 'patio'

        self.mapas = {'patio' : PATIO, 'lagoa' : LAGOA, 'floresta' : FLORESTA, 'casa' : CASA, 'galinheiro' : GALINHEIRO}
        # self.imagens = {'patio' : FILE_PATIO, 'lagoa' : FILE_LAGOA, 'floresta' : FILE_FLORESTA, 'casa' : FILE_CASA, 'galinheiro' : FILE_GALINHEIRO}

        self.bot_mens = None

    async def comeca_jogo(self, ctx):
        await self.cria_mapa()
        if not ctx.channel.type == discord.ChannelType.private:
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        res = await self.view.wait()
        if res:
            await ctx.channel.send('É minha vez de jogar!(Jogador Ocioso)', delete_after=5)
            await self.parar()
        # else:
        #     if 'betty' in self.items:
        #         await ctx.channel.send(f'{ctx.author.mention} Zerou!')
        del self.view
        del self

    async def cria_mapa(self):
        # self.embed = await self.canal.send(embed=self.mapas[self.lugar_atual], file=self.imagens[self.lugar_atual], view=self.view)
        self.embed = await self.canal.send(embed=self.mapas[self.lugar_atual], view=self.view)

    async def atualiza_mapa(self):
        # await self.embed.edit(embed=self.mapas[self.lugar_atual], file=self.imagens[self.lugar_atual], view=self.view)
        await self.embed.edit(embed=self.mapas[self.lugar_atual], view=self.view)

    async def parar(self):
        if self.bot_mens is not None:
            await self.bot_mens.delete()
        await self.embed.delete()
        self.view.stop()
        del usuarios_jogando[(self.jogador, self.canal)]


    async def insereScore(self, tipo):
        if not self.canal.type == discord.ChannelType.private:
            guilda = self.canal.guild
            usuario = self.jogador
            tempo = self.totalTime

            # criar checks pra verificar se a pessoa tem as roles
            # pacifista ou genocida e ter comandos so pra elas

            # depois revisar esse pesadelo de codigo
            # quando tiver tempo
            score = await retornaScoreboard(guilda, tipo)
            role_id = await dbReturn(f'SELECT * FROM {tableWR} WHERE (id_guilda = {guilda.id} AND tipo = "{tipo}")')
            if len(role_id) != 0:
                role = guilda.get_role(role_id[0][1])
                if role is not None:
                    if len(score) != 0:
                        top = score[0][3]
                        if tempo < top:
                            if len(role.members) != 0:
                                usuarioVelho = role.members[0]
                                await usuarioVelho.remove_roles(role)
                                await self.canal.send(f'NOVO WR SUUUUUUUUUUUUUUUUUUUU\n {usuarioVelho.mention} - **{tipo.capitalize()}%** em `{top}s` -> {usuario.mention} - **{tipo.capitalize()}%** em `{tempo}s`')
                            else:
                                await self.canal.send(f'NOVO WR SUUUUUUUUUUUUUUUUUUUU\n {usuario.mention} fez **{tipo.capitalize()}%** em `{tempo}s`')
                            await usuario.add_roles(role)
                    else:
                        if len(role.members) != 0:
                            usuarioVelho = role.members[0]
                            await usuarioVelho.remove_roles(role)
                        await self.canal.send(f'NOVO WR SUUUUUUUUUUUUUUUUUUUU\n {usuario.mention} fez **{tipo.capitalize()}%** em `{tempo}s`')
                        await usuario.add_roles(role)


            jaAdicionado = await dbReturn(f'SELECT * FROM {tableScoreboard} WHERE (id_guilda = {guilda.id} AND id_usuario = {usuario.id} AND tipo = "{tipo}");')
            if len(jaAdicionado) != 0:
                tempoVelho = jaAdicionado[0][3]
                # talvez verificar tambem se eh recorde em any%
                # preguica
                if tempo < tempoVelho:
                    await self.canal.send(f'Novo recorde pessoal em **{tipo.capitalize()}%**! (`{tempoVelho}s` -> `{tempo}s`)')
                    await dbExecute(f'UPDATE {tableScoreboard} SET tempo = {tempo} WHERE (id_guilda = {guilda.id} AND id_usuario = {usuario.id} AND tipo = "{tipo}");')
            else:
                await dbExecute(f'INSERT INTO {tableScoreboard}(id_guilda, id_usuario, tipo, tempo) VALUES({guilda.id},{usuario.id},"{tipo}",{tempo});')
        
        # await Jogo.atualizaRoles(top, tempo, tipo)
            


class jogoView(View):
    def __init__(self, *items: discord.ui.Item, timeout: float = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.ultimaMens = None
        self.sessao = sessao

    async def interaction_check(self, interaction):
        if interaction.user == self.sessao.jogador:
            return True
        else:
            await self.sessao.canal.send(content=f'Alguém ta querendo jogar coop')
            # await interaction.response.send_message('Tá querendo acabar com o jogo do amiguinho né?', ephemeral=True)
            return False


    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        await self.sessao.parar()
        await self.sessao.canal.send('Deu ruim! Fale com o maluco que mantém o GitHub.\nhttps://github.com/RiruAugusto/depressaoRobotica', delete_after=60)
        await self.sessao.canal.send(content=f'Erro:\n{error}', delete_after=15)
        return await super().on_error(error, item, interaction)

    async def atualiza_botoes(self, interaction):
        if self.sessao.lugar_atual == 'lagoa':
            for x in self.children:
                if x.custom_id == 'pegar' or x.custom_id == 'parar' or x.custom_id=='direita':
                    x.disabled = False
                else:
                    x.disabled = True
        elif self.sessao.lugar_atual == 'floresta':
            for x in self.children:
                if x.custom_id == 'pegar' or x.custom_id == 'parar' or x.custom_id=='baixo':
                    x.disabled = False
                else:
                    x.disabled = True
        elif self.sessao.lugar_atual == 'casa':
            for x in self.children:
                if x.custom_id == 'pegar' or x.custom_id == 'parar' or x.custom_id=='esquerda':
                    x.disabled = False
                else:
                    x.disabled = True
        elif self.sessao.lugar_atual == 'galinheiro':
            for x in self.children:
                if x.custom_id == 'pegar' or x.custom_id == 'parar' or x.custom_id=='cima':
                    x.disabled = False
                else:
                    x.disabled = True
        else:
            for x in self.children:
                x.disabled = False
        await interaction.edit_original_message(view=self)
        await self.sessao.atualiza_mapa()
        self.sessao.mapas[self.sessao.lugar_atual].clear_fields()

    @discord.ui.button(emoji="🛑", custom_id="parar")
    async def button1_callback(self, button, interaction):
        await interaction.response.defer()
        await self.sessao.canal.send('Parando jogo.', delete_after=5)
        await self.sessao.parar()
    
    @discord.ui.button(emoji="⬆️", custom_id="cima")
    async def button2_callback(self, button, interaction):
        await interaction.response.defer()
        self.sessao.insistencia = 0
        if self.sessao.lugar_atual == 'patio':
            self.sessao.lugar_atual = 'floresta'
        elif self.sessao.lugar_atual == 'galinheiro':
            self.sessao.lugar_atual = 'patio'
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="🖐️", custom_id="pegar")
    async def button3_callback(self, button, interaction):
        await interaction.response.defer()
        if self.sessao.lugar_atual == 'patio':
            if 'glock' in self.sessao.items:
                    self.sessao.mapas[self.sessao.lugar_atual].add_field(name='AGORA VAI LÁ NA FLORESTA', value='NÃO ERA ISSO QUE TU QUERIA?')
            elif self.sessao.insistencia == 0:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você tenta pegar o vento...', value='Realmente não tem nada de interessante aqui pra pegar.')
                self.sessao.insistencia = 1
            elif self.sessao.insistencia == 1:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você insiste em pegar o vento...', value='Tô falando que não tem nada de interessante aqui pra pegar.')
                self.sessao.insistencia = 2
            elif self.sessao.insistencia == 2:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='TÁ BOM, TOMA AQUI UMA GLOCK', value='VAI PEGAR AQUELA GALINHA NA FLORESTA.')
                self.sessao.items.append('glock')
        elif self.sessao.lugar_atual == 'lagoa':
            if 'glock' in self.sessao.items:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='AGORA VAI LÁ NA FLORESTA', value='NÃO ERA ISSO QUE TU QUERIA?')
            elif ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você toma banho', value='Agora você pode ir para a casa da dona Jocelina!')
                # await interaction.response.edit_message(content="Você toma banho")
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você já tomou banho', value='Vai lá pegar a rede na casa!')
                # await interaction.response.edit_message(content="Você já tomou banho")
        elif self.sessao.lugar_atual == 'casa':
            if 'glock' in self.sessao.items:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='AGORA VAI LÁ NA FLORESTA', value='NÃO ERA ISSO QUE TU QUERIA?')
            elif ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                self.sessao.items.append(ONDE_ESTA[self.sessao.lugar_atual])
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você pega a rede', value='Dá pra pegar a Betty na floresta agora!')
                # await interaction.response.edit_message(content="Você pega a rede")
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você já pegou a rede', value='Tenta pegar a Betty na floresta!')
                # await interaction.response.edit_message(content="Você já pegou a rede")
        elif self.sessao.lugar_atual == 'floresta':
            if ONDE_ESTA[self.sessao.lugar_atual] not in self.sessao.items:
                if 'glock' in self.sessao.items:
                    self.sessao.endTime = time.time()
                    self.sessao.totalTime = round(self.sessao.endTime-self.sessao.startTime, 3)
                    await self.sessao.canal.send(f'{self.sessao.jogador.mention} METEU UM BALAÇO NA BETTY! ZEROU EM {self.sessao.totalTime}S.')
                    await self.sessao.insereScore('genocide')
                    await self.sessao.parar()
                    return
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
            if 'glock' in self.sessao.items:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='AGORA VAI LÁ NA FLORESTA', value='NÃO ERA ISSO QUE TU QUERIA?')
            else:
                self.sessao.mapas[self.sessao.lugar_atual].add_field(name='Você tenta pegar o vento...', value='Realmente não tem nada de interessante aqui pra pegar.')
            # await interaction.response.edit_message(content="Não tem nada pra pegar aqui")
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="⬅️", row=2, custom_id="esquerda")
    async def button6_callback(self, button, interaction):
        await interaction.response.defer()
        self.sessao.insistencia = 0
        if self.sessao.lugar_atual == 'patio':
            self.sessao.lugar_atual = 'lagoa'
        elif self.sessao.lugar_atual == 'casa':
            self.sessao.lugar_atual = 'patio'
        # await interaction.response.edit_message(content="esquerda")
        await self.atualiza_botoes(interaction)

    @discord.ui.button(emoji="⬇️", row=2, custom_id="baixo")
    async def button7_callback(self, button, interaction):
        await interaction.response.defer()
        self.sessao.insistencia = 0
        if self.sessao.lugar_atual == 'patio':
            if 'betty' in self.sessao.items:
                self.sessao.endTime = time.time()
                self.sessao.totalTime = round(self.sessao.endTime-self.sessao.startTime, 3)
                if self.sessao.totalTime < 25:
                    await self.sessao.canal.send(f'Muito rápido! Parábens {self.sessao.jogador.mention}! Você terminou em {self.sessao.totalTime}s.')
                else:
                    await self.sessao.canal.send(f'Parábens {self.sessao.jogador.mention}! Você terminou em {self.sessao.totalTime}s.')
                await self.sessao.insereScore('pacifist')
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
        self.sessao.insistencia = 0
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


    # tabelas any%, pacifist% e genocide%(bioshock%)
    # tabela local da guilda e tabela global

    @commands.Cog.listener()
    async def on_ready(self):
        await dbExecute(f'''CREATE TABLE IF NOT EXISTS {tableScoreboard}(
                            id_guilda INT,
                            id_usuario INT,
                            tipo TEXT,
                            tempo INT
                        );
                        '''
        )
        await dbExecute(f'''CREATE TABLE IF NOT EXISTS {tableWR}(
                            id_guilda INT,
                            id_role INT,
                            tipo TEXT
                        );
                        '''
        )
        # fazer isso em um comando para adm
        for guild in self.bot.guilds:
            jaAdicionado = await dbReturn(f'SELECT * FROM {tableWR} WHERE (id_guilda = {guild.id});')
            if len(jaAdicionado) == 0:
                try:
                    roleG = await guild.create_role(name='Genocida', color=0xcc0000)
                    print(f'Criando cargo "Genocida" em {guild} com id {roleG.id}')
                    roleP = await guild.create_role(name='Pacifista', color=0xffffff)
                    print(f'Criando cargo "Pacifista" em {guild} com id {roleP.id}')
                    await dbExecute(f'INSERT INTO {tableWR}(id_guilda, id_role, tipo) VALUES({guild.id},{roleG.id},"genocide");')
                    await dbExecute(f'INSERT INTO {tableWR}(id_guilda, id_role, tipo) VALUES({guild.id},{roleP.id},"pacifist");')
                except discord.Forbidden:
                    continue

    @commands.command(name='scoreboard')
    @commands.guild_only()
    async def scoreboard(self, ctx):

        # sim, eu to fazendo 3 consultas que podiam ser 1
        # me deixa
        scoreboard = await retornaScoreboard(ctx.guild, 'any')
        scoreboardGenocide = await retornaScoreboard(ctx.guild, 'genocide')
        scoreboardPacifist = await retornaScoreboard(ctx.guild, 'pacifist')
        
        page1 = discord.Embed (
            title = 'Scoreboard do jogo para essa Guilda!',
            description = f'Any%',
            colour = discord.Colour.dark_teal()
        )
        page1.set_image(url='https://i.imgur.com/27HsA8G.jpg')
        page1.set_footer(text=f'Se você suspeita que as roles estão com as pessoas erradas, use {prefix}cobra')
        for i in range (5):
            try:
                jogador = self.bot.get_user(scoreboard[i][1])
                tipo = scoreboard[i][2]
                tempo = scoreboard[i][3]
                page1.add_field(name=f'{i+1}º {jogador} - `{tempo}s` ({tipo.capitalize()}%)', value='\u200b', inline=False)
            except IndexError:
                break

        page2 = discord.Embed (
            title = 'Scoreboard do jogo para essa Guilda!',
            description = f'Genocide%',
            colour = discord.Colour.blurple()
        )
        page2.set_image(url='https://i.imgur.com/4V4LwDj.png')
        page2.set_footer(text=f'Se você suspeita que as roles estão com as pessoas erradas, use {prefix}cobra')
        for i in range (5):
            try:
                jogador = self.bot.get_user(scoreboardGenocide[i][1])
                tempo = scoreboardGenocide[i][3]
                page2.add_field(name=f'{i+1}º {jogador} - `{tempo}s`', value='\u200b', inline=False)
            except IndexError:
                break

        page3 = discord.Embed (
            title = 'Scoreboard do jogo para essa Guilda!',
            description = f'Pacifist%',
            colour = discord.Colour.dark_red()
        )
        page3.set_image(url='https://i.imgur.com/6sYrnGj.png')
        page3.set_footer(text=f'Se você suspeita que as roles estão com as pessoas erradas, use {prefix}cobra')
        for i in range (5):
            try:
                jogador = self.bot.get_user(scoreboardPacifist[i][1])
                tempo = scoreboardPacifist[i][3]
                page3.add_field(name=f'{i+1}º {jogador} - `{tempo}s`', value='\u200b', inline=False)
            except IndexError:
                break


        pages = [page1, page2, page3]

        message = await ctx.send(embed = page1)

        await message.add_reaction('⏮')
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        await message.add_reaction('⏭')

        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None

        while True:
            if str(reaction) == '⏮':
                i = 0
                await message.edit(embed = pages[i])
            elif str(reaction) == '◀':
                if i > 0:
                    i -= 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '▶':
                if i < 2:
                    i += 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '⏭':
                i = 2
                await message.edit(embed = pages[i])
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 40.0, check = check)
                await message.remove_reaction(reaction, user)
            except:
                break

        # await message.delete()
        await message.clear_reactions()

    @commands.command()
    @commands.guild_only()
    async def pb(self, ctx):
        guilda = ctx.guild

        score = await dbReturn(f'SELECT * FROM {tableScoreboard} WHERE (id_guilda = {guilda.id} AND id_usuario = {ctx.author.id});')
        if len(score) != 0:
            mens = ''
            for i in range(len(score)):
                mens += f'`{score[i][3]}s` em {score[i][2].capitalize()}%\n'
            await ctx.reply(mens, delete_after=30)
        else:
            await ctx.reply(f'Você ainda não completou o jogo. Jogue usando o comando {prefix}jogar', delete_after=30)

    @commands.command(aliases=['cobrar'])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def cobra(self, ctx):
        # separar a verificação em outra função, e retorna 1 se
        # corrigiu genocide, 2 se corrigiu pacifist e 0 se tudo tranquilo
        # reutilizar a função aqui e antes das funções apenas para as roles (!teste)
        guilda = ctx.guild
        tranquilo = True
        scoreboardG = await retornaScoreboard(guilda, 'genocide')
        scoreboardP = await retornaScoreboard(guilda, 'pacifist')
        roleG_id = await dbReturn(f'SELECT * FROM {tableWR} WHERE (id_guilda = {guilda.id} AND tipo = "genocide")')
        roleP_id = await dbReturn(f'SELECT * FROM {tableWR} WHERE (id_guilda = {guilda.id} AND tipo = "pacifist")')
        if len(scoreboardG) != 0 and len(roleG_id) != 0:
            roleG = guilda.get_role(roleG_id[0][1])
            top1_score = scoreboardG[0]
            top1_id = top1_score[1]
            #top1_user = self.bot.get_user(top1_id)
            for member in guilda.members:
                if member.id == top1_id:
                    top1_member = member
            if roleG not in top1_member.roles:
                tranquilo = False
                await ctx.send(f'{top1_member.mention} não estava com a role Genocida, e deveria ter!')
                await top1_member.add_roles(roleG)
            
            for member in roleG.members:
                if member != top1_member:
                    tranquilo = False   
                    await ctx.send(f'{member.mention} estava com a role Genocida, e não deveria ter!')
                    await member.remove_roles(roleG)
        else:
            tranquilo = False
            await ctx.send(f'Ninguém jogou ainda, ou o bot não conseguiu criar a role Genocida!')
        if len(scoreboardP) != 0 and len(roleP_id) != 0:
            roleP = guilda.get_role(roleP_id[0][1])
            top1_score = scoreboardP[0]
            top1_id = top1_score[1]
            #top1_user = self.bot.get_user(top1_id)
            for member in guilda.members:
                if member.id == top1_id:
                    top1_member = member
            if roleP not in top1_member.roles:
                tranquilo = False  
                await ctx.send(f'{top1_member.mention} não estava com a role Pacifista, e deveria ter!')
                await top1_member.add_roles(roleP)
            
            for member in roleP.members:
                if member != top1_member:
                    tranquilo = False  
                    await ctx.send(f'{member.mention} estava com a role Pacifista, e não deveria ter!')
                    await member.remove_roles(roleP)
        else:
            tranquilo = False
            await ctx.send(f'Ninguém jogou ainda, ou o bot não conseguiu criar a role Pacifista!')

        if tranquilo:
            await ctx.send(f'Tudo parece estar correto!')

    @commands.command(enabled=False)
    @tem_roleG()
    async def teste(self, ctx):
        await ctx.send('você é genocida')

    @cobra.error
    async def cobraHandler(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('Não tenho permissão para gerenciar roles!')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.command(aliases=['Jogar', 'pegagalinha'])
    @nao_jogando()
    # @commands.max_concurrency(1)
    async def jogar(self, ctx):
        sessao = Sessao((ctx.author, ctx.channel))
        await sessao.comeca_jogo(ctx)
        

    @commands.command(enabled=False)
    @jogando()
    async def parar(self, ctx):
        sessao = usuarios_jogando[(ctx.author, ctx.channel)]
        await sessao.parar()
        del sessao
        del usuarios_jogando[(ctx.author, ctx.channel)]
        await ctx.reply('Parando jogo', delete_after=10)
        await ctx.message.delete()

    @teste.error
    async def jogoRolesHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f'Você não tem a role necessária. Se você tem o recorde, use {prefix}cobra')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @jogar.error
    async def jogarHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            self.bot_mens = await ctx.reply('Você já está jogando!')
            await self.bot_mens.delete(delay=5)
        elif isinstance(error, commands.MaxConcurrencyReached):
            self.bot_mens = await ctx.reply('Espere, alguém está jogando!')
            await self.bot_mens.delete(delay=5)
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

    @scoreboard.error
    @pb.error
    async def dmHandler(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.reply('Esse comando só pode ser usado em uma guilda!')
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

async def setup(bot):
    await bot.add_cog(Jogo(bot))
