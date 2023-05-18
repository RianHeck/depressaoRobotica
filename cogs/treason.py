from discord.ext import commands
from discord.ui import View, Button
import discord
from utils.db import *
from main import prefix
from random import choice, shuffle

canais_jogando = {}

def estaNaVez(jogadores : list, vez : int):
    async def predicate(interaction : discord.Interaction):
        if jogadores.index(interaction.user) == vez:
            return True
        else:
            return False
            
    return commands.check(predicate) 


class Jogador():
    def __init__(self) -> None:
        self.dinheiro = 2
        self.numeroDeInfluencia = 2
        self.influencias = {}


class Sessao():
    def __init__(self, contexto : tuple) -> None:
        self.host = contexto[0]
        self.canal = contexto[1]
        self.view = treasonView(timeout=30, sessao=self)
        
    
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
        self.objetoJogadores = {}
        self.vez = 0
        self.acoesBotoes = [self.taxar_callback, self.roubar_callback, self.assassinar_callback, self.trocar_callback, self.renda_callback, self.auxilio_callback, self.coup_callback]
        # self.estadoAtual = {'jogadores' : [], 'acaoAtual' : None, 'playerAlvo' : None}
        self.mensagemLobby = {}
        self.listaMensagensBot = []
        self.roles = ['assassin', 'contessa', 'captain', 'duke', 'inquisitor']
        self.deque = []

    def montarDeque(self):
        for i in range(0, 3):
            self.deque.extend(self.roles)
        shuffle(self.deque)

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

        botaoEncerrar = Button(label='Encerrar', custom_id='encerrar')
        botaoEncerrar.callback = self.encerrar_callback
        self.add_item(botaoEncerrar)

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
            self.montarDeque()
            self.darCartas()
            for jogador in self.jogadores:
                await interaction.channel.send(f'{jogador.name} : {" e ".join(role for role in self.objetoJogadores[jogador].keys())}')
            await self.escolherAcao()
            await self.embedComeco()

    async def encerrar_callback(self, interaction):
        await interaction.response.defer()
        await self.encerra()

    def darCartas(self):
        for jogador in self.jogadores:
            carta1 = choice(self.deque)
            self.deque.remove(carta1)
            carta2 = choice(self.deque)
            self.deque.remove(carta2)

            self.objetoJogadores[jogador] = {carta1 : False, carta2 : False}

    async def encerra(self):
        self.clear_items()
        self.embed.clear_fields()
        await self.embedMensagem.edit(embed=self.embed, view=self)
        for mensagem in self.listaMensagensBot:
            await mensagem.delete_original_message()
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
        if self.jogadores.index(interaction.user) != self.vez:
            await interaction.response.send_message('Espere sua vez!', ephemeral=True, delete_after=3)
            return False
               
        self.playerAlvo = interaction.custom_id
        #print(interaction.to_dict())
        #await interaction.channel.send(f'{interaction.custom_id}')
        # await interaction.response.send_message(f'{interaction.user.name} taxou {self.playerAlvo}')
        await self.executarAcao(interaction)

    # @estaNaVez(self.jogadores)
    async def executarAcao(self, interaction):
        if self.jogadores.index(interaction.user) != self.vez:
            await interaction.response.send_message('Espere sua vez!', ephemeral=True, delete_after=3)
            return False
        
        if self.acaoAtual == 'taxar':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} pegou 3$ como imposto'))
        elif self.acaoAtual == 'roubar':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} extorquiu {self.playerAlvo}'))
        elif self.acaoAtual == 'assassinar':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} assassinou {self.playerAlvo}'))
        elif self.acaoAtual == 'trocar':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} trocou suas roles'))
        elif self.acaoAtual == 'renda':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} pegou 1$'))
        elif self.acaoAtual == 'auxilio':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} pegou 2$'))
        elif self.acaoAtual == 'coup':
            self.listaMensagensBot.append(await interaction.response.send_message(f'{interaction.user.name} fez um coup contra {self.playerAlvo}'))
        
        self.vez = (self.vez+1)%(len(self.jogadores))
        await self.escolherAcao()

    async def escolherAcao(self):
        self.clear_items()
        for i in range(len(self.acoesBotoes)):
            self.add_item(self.acoesBotoes[i])
        await self.embedMensagem.edit(embed=self.embed, view=self)

    async def escolherJogador(self, interaction):
        # unificar as funcoes de escolher e usar if pra decidir que botoes mostrar
        if self.jogadores.index(interaction.user) != self.vez:
            await interaction.response.send_message('Espere sua vez!', ephemeral=True, delete_after=3)
            return False
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
        await self.executarAcao(interaction)
        
    @discord.ui.button(label='Roubar', custom_id="roubar", emoji='🫳')
    async def roubar_callback(self, button, interaction):
        self.acaoAtual = 'roubar'
        await self.escolherJogador(interaction)
        await interaction.response.defer()
    
    @discord.ui.button(label='Assassinar', custom_id="assassinar", emoji='🔪')
    async def assassinar_callback(self, button, interaction):
        self.acaoAtual = 'assassinar'
        await self.escolherJogador(interaction)
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
        await self.escolherJogador(interaction)
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