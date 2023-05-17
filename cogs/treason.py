from discord.ext import commands
from discord.ui import View, Button
import discord
from utils.db import *
from main import prefix
from random import choice

canais_jogando = {}

class Sessao():
    def __init__(self, contexto : tuple) -> None:
        self.host = contexto[0]
        self.canal = contexto[1]
        self.view = treasonView(timeout=300, sessao=self)
        
    
    async def comeca(self):
        await self.view.comeca()

class treasonView(View):
    def __init__(self, *items: discord.ui.Item, timeout: float = 180, sessao : Sessao):
        super().__init__(*items, timeout=timeout)
        self.sessao = sessao
        self.embed = discord.Embed(title='Coup', description='Todo mundo mente nessa porra')
        self.embedMensagem = 0
        self.acaoAtual = None
        self.playerAlvo = None
        self.botoes = []
        self.jogadores = []
        self.acoesBotoes = [self.taxar_callback, self.roubar_callback, self.assassinar_callback, self.trocar_callback, self.renda_callback, self.auxilio_callback, self.coup_callback]
        # self.estadoAtual = {'jogadores' : [], 'acaoAtual' : None, 'playerAlvo' : None}
        self.mensagemLobby = {}


    async def comeca(self):
        await self.lobby()
        res = await self.wait()
        if res:
            await self.encerra()

    async def lobby(self):
        self.clear_items()

        botaoComecar = Button(label='Comecar', custom_id='comecar')
        botaoComecar.callback = self.comecar_callback
        self.add_item(botaoComecar)

        botaoEntrar = Button(label='Entrar', custom_id='entrar')
        botaoEntrar.callback = self.entrar_callback
        self.add_item(botaoEntrar)

        botaoSair = Button(label='Sair', custom_id='sair')
        botaoSair.callback = self.sair_callback
        self.add_item(botaoSair)

        self.embed.add_field(name='Jogadores', value='')
        await self.embedComeco()

    async def entrar_callback(self, interaction):
        if interaction.user in self.jogadores:
            await interaction.response.send_message('Você já entrou!', ephemeral=True, delete_after=3)
        
        else:
            self.jogadores.append(interaction.user)
            
            if(len(self.jogadores) == 0):
                self.embed.set_field_at(index=0, name='Jogadores', value='')
            else:
                self.embed.set_field_at(index=0, name='Jogadores', value=f'{f"{chr(10)}".join(player.name for player in self.jogadores)}')
                # print(f'{f"{chr(10)}".join(player.name for player in self.jogadores)}')
            
            await self.embedMensagem.edit(embed=self.embed, view=self)
            await interaction.response.defer()

    async def sair_callback(self, interaction):
        if interaction.user in self.jogadores:
            self.jogadores.remove(interaction.user)

            if(len(self.jogadores) == 0):
                self.embed.set_field_at(index=0, name='Jogadores', value='')
                # print('vazio')
            else:
                self.embed.set_field_at(index=0, name='Jogadores', value=f'{f"{chr(10)}".join(player.name for player in self.jogadores)}')
                # print(f'{f"{chr(10)}".join(player.name for player in self.jogadores)}')
            
            await self.embedMensagem.edit(embed=self.embed, view=self)
            await interaction.response.defer()

        else:
            await interaction.response.send_message('Você não está no jogo!', ephemeral=True, delete_after=3)


    # async def sair_callback(self, interaction):
    #     if interaction.user in self.jogadores:
    #         self.jogadores.remove(interaction.user)
    #         if interaction.user not in self.mensagemLobby.keys():
    #             #self.mensagemLobby[interaction.user] = await interaction.response.send_message(f'{interaction.user.name} saiu do jogo!')
    #             await interaction.response.defer()
    #         else:
    #             # print(type(self.mensagemLobby))
    #             # await self.mensagemLobby[interaction.user].edit_original_response(content=f'{interaction.user.name} saiu do jogo!')

    #             if(len(self.jogadores) == 0):
    #                 self.embed.set_field_at(index=0, name='Jogadores', value='')
    #             else:
    #                 self.embed.set_field_at(index=0, name='Jogadores', value=f'{f"{chr(10)}".join(player.name for player in self.jogadores)}')
    #             print(f'{f"{chr(10)}".join(player.name for player in self.jogadores)}')
    #             await self.embedMensagem.edit(embed=self.embed, view=self)
    #             await interaction.response.defer()
    #     else:
    #         await interaction.response.send_message('Você não está no jogo!', ephemeral=True, delete_after=3)

    async def comecar_callback(self, interaction):
        await interaction.response.defer()
        if len(self.jogadores) == 0:
            pass
        else:
            await self.criarBotoesJogadores()
            await self.escolherAcao()
            await self.embedComeco()

    async def encerra(self):
        self.clear_items()
        self.embed.clear_fields()
        await self.embedMensagem.edit(embed=self.embed, view=self)
        self.stop()
        del self.sessao
        del self

    async def embedComeco(self):
        if self.embedMensagem == 0:
            self.embedMensagem = await self.sessao.canal.send(embed=self.embed, view=self)
        else:
            await self.embedMensagem.edit(embed=self.embed, view=self)

    async def criarBotoesJogadores(self):
        self.botoes = []
        for i in range(len(self.jogadores)):
            botao = Button(label=f'{self.jogadores[i].name}', custom_id=f'{self.jogadores[i].name}')
            botao.callback = self.player_callback
            self.botoes.append(botao)

    async def player_callback(self, interaction):
        self.playerAlvo = interaction.custom_id
        #print(interaction.to_dict())
        #await interaction.channel.send(f'{interaction.custom_id}')
        # await interaction.response.send_message(f'{interaction.user.name} taxou {self.playerAlvo}')
        await self.executarAcao(interaction)

    async def executarAcao(self, interaction):
        if self.acaoAtual == 'taxar':
            await interaction.response.send_message(f'{interaction.user.name} taxou {self.playerAlvo}')
        elif self.acaoAtual == 'roubar':
            await interaction.response.send_message(f'{interaction.user.name} roubou {self.playerAlvo}')
        elif self.acaoAtual == 'assassinar':
            await interaction.response.send_message(f'{interaction.user.name} assassinou {self.playerAlvo}')
        elif self.acaoAtual == 'trocar':
            await interaction.response.send_message(f'{interaction.user.name} trocou suas roles')
        elif self.acaoAtual == 'renda':
            await interaction.response.send_message(f'{interaction.user.name} pegou 1$')
        elif self.acaoAtual == 'auxilio':
            await interaction.response.send_message(f'{interaction.user.name} pegou 2$')
        elif self.acaoAtual == 'coup':
            await interaction.response.send_message(f'{interaction.user.name} fez um coup contra {self.playerAlvo}')
        await self.escolherAcao()

    async def escolherAcao(self):
        self.clear_items()
        for i in range(len(self.acoesBotoes)):
            self.add_item(self.acoesBotoes[i])
        await self.embedMensagem.edit(embed=self.embed, view=self)

    async def escolherJogador(self):
        # unificar as funcoes de escolher e usar if pra decidir que botoes mostrar
        self.clear_items()
        for i in range(len(self.botoes)):
            self.add_item(self.botoes[i])
        await self.embedMensagem.edit(embed=self.embed, view=self)


    # IMPORTANTE
    # construir check que verifica qual jogador esta na vez
    # terminar (comecar kk) o lobby para os jogadores entrarem

    # FABIO
    # guardar mensagens criadas de acoes em uma lista
    # as mensagens servem como um historico
    # ao final do jogo excluir as mensagens

    @discord.ui.button(label='Taxar', custom_id="taxar", emoji='💰')
    async def taxar_callback(self, button, interaction):
        self.acaoAtual = interaction.custom_id
        #self.acaoAtual = 'taxar'
        await self.escolherJogador()
        await interaction.response.defer()

    @discord.ui.button(label='Roubar', custom_id="roubar", emoji='🫳')
    async def roubar_callback(self, button, interaction):
        self.acaoAtual = 'roubar'
        await self.escolherJogador()
        await interaction.response.defer()
    
    @discord.ui.button(label='Assassinar', custom_id="assassinar", emoji='🔪')
    async def assassinar_callback(self, button, interaction):
        self.acaoAtual = 'assassinar'
        await self.escolherJogador()
        await interaction.response.defer()
    
    @discord.ui.button(label='Trocar', custom_id="trocar", emoji='🔄')
    async def trocar_callback(self, button, interaction):
        self.acaoAtual = 'trocar'
        await self.executarAcao(interaction)
        # await interaction.response.defer()
    
    @discord.ui.button(label='Renda', custom_id="renda", emoji='🪙')
    async def renda_callback(self, button, interaction):
        self.acaoAtual = 'renda'
        await self.executarAcao(interaction)
        # await interaction.response.defer()
    
    @discord.ui.button(label='Auxílio Estrangeiro', custom_id="auxilio", emoji='🪙')
    async def auxilio_callback(self, button, interaction):
        self.acaoAtual = 'auxilio'
        await self.executarAcao(interaction)
        # await interaction.response.defer()

    @discord.ui.button(label='Coup', custom_id="coup", emoji='🔫')
    async def coup_callback(self, button, interaction):
        self.acaoAtual = 'coup'
        await self.escolherJogador()
        await interaction.response.defer()

class Treason(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles = ['assassin', 'contessa', 'captain', 'duke', 'inquisitor']
        self.deque = []
        self.montarDeque()

    def montarDeque(self):
        for i in range(0, 3):
            self.deque.extend(self.roles)
        self.embaralhar()

    def embaralhar(self):
        embaralhado = []
        for i in range(len(self.deque)):
            escolhido = choice(self.deque)
            self.deque.remove(escolhido)
            embaralhado.append(escolhido)
        self.deque = embaralhado

    @commands.command()
    async def fala(self, ctx):
        await ctx.reply('qualquer coisa', ephemeral=True)

    @commands.command()
    async def coup(self, ctx):
        sessao = Sessao((ctx.author, ctx.channel))
        await sessao.comeca()



def setup(bot):
    bot.add_cog(Treason(bot))