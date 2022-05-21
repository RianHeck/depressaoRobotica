from discord.ext import commands
import discord
from main import prefix, testeID, respostas
from utils.checks import *
from utils.db import *
import sys


sys.path.append("..")

class Basico(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return

        if ctx.content.lower().__contains__('bitches'):
            await ctx.channel.send("  ⣞⢽⢪⢣⢣⢣⢫⡺⡵⣝⡮⣗⢷⢽⢽⢽⣮⡷⡽⣜⣜⢮⢺⣜⢷⢽⢝⡽⣝\n⠸⡸⠜⠕⠕⠁⢁⢇⢏⢽⢺⣪⡳⡝⣎⣏⢯⢞⡿⣟⣷⣳⢯⡷⣽⢽⢯⣳⣫⠇\n  ⠀⠀⢀⢀⢄⢬⢪⡪⡎⣆⡈⠚⠜⠕⠇⠗⠝⢕⢯⢫⣞⣯⣿⣻⡽⣏⢗⣗⠏⠀\n   ⠀⠪⡪⡪⣪⢪⢺⢸⢢⢓⢆⢤⢀⠀⠀⠀⠀⠈⢊⢞⡾⣿⡯⣏⢮⠷⠁\n  ⠀⠀⠀⠈⠊⠆⡃⠕⢕⢇⢇⢇⢇⢇⢏⢎⢎⢆⢄⠀⢑⣽⣿⢝⠲⠉\n  ⠀⠀⠀⠀⠀⡿⠂⠠⠀⡇⢇⠕⢈⣀⠀⠁⠡⠣⡣⡫⣂⣿⠯⢪⠰⠂\n  ⠀⠀⠀⠀⡦⡙⡂⢀⢤⢣⠣⡈⣾⡃⠠⠄⠀⡄⢱⣌⣶⢏⢊⠂\n  ⠀⠀⠀⠀⢝⡲⣜⡮⡏⢎⢌⢂⠙⠢⠐⢀⢘⢵⣽⣿⡿⠁⠁\n  ⠀⠀⠀⠀⠨⣺⡺⡕⡕⡱⡑⡆⡕⡅⡕⡜⡼⢽⡻⠏\n  ⠀⠀⠀⠀⣼⣳⣫⣾⣵⣗⡵⡱⡡⢣⢑⢕⢜⢕⡝\n  ⠀⠀⠀⣴⣿⣾⣿⣿⣿⡿⡽⡑⢌⠪⡢⡣⣣⡟\n  ⠀⠀⠀⡟⡾⣿⢿⢿⢵⣽⣾⣼⣘⢸⢸⣞⡟\n  ⠀⠀⠀⠀⠁⠇⠡⠩⡫⢿⣝⡻⡮⣒⢽⠋⠀")
        
        if ctx.content in respostas:
            await ctx.channel.send(respostas[ctx.content])

    @commands.command(enabled=False)
    async def comandosVelho(self, ctx):

        embedComandos = discord.Embed(
        title=f'{self.bot.user} Comandos', color=0xF0F0F0)

        embedComandos.set_thumbnail(url=self.bot.user.avatar.url)

        embedComandos.add_field(name=f'{prefix}ping', value='Testa o ping do bot e da API do discord', inline=False)
        embedComandos.add_field(name=f'{prefix}roleta [1-6]', value='Uma roleta russa, opcionalmente escreva o número de balas a ser usado', inline=False)
        embedComandos.add_field(name=f'{prefix}roletav/{prefix}r [1-6]', value=f'Roleta russa por comando de voz, use {prefix}carrega para chamar o bot.\nopcionalmente escreva o número de balas a ser usado', inline=False)
        embedComandos.add_field(name=f'{prefix}comandos', value='Mostra uma lista de comandos', inline=False)
        embedComandos.add_field(name=f'{prefix}provas [numero de semanas]', value='Mostra as provas para as próximas semanas, 2 semanas se não especificado', inline=False)
     
        await ctx.reply(embed=embedComandos)


    @commands.command()
    async def comandos(self, ctx):
        await ctx.message.delete()
        page1 = discord.Embed (
            title = 'Comandos Básicos',
            description = f'Page 1/4',
            colour = discord.Colour.dark_teal()
        )
        page1.add_field(name=f'`{prefix}ping`', value='Testa o ping do bot e da API do discord', inline=False)
        page1.add_field(name=f'`{prefix}comandos`', value='Mostra uma lista de comandos', inline=False)
        page1.add_field(name=f'`{prefix}jogar`', value='Um joguinho básico meio familiar', inline=False)
        page1.set_thumbnail(url=self.bot.user.avatar.url)
        page1.set_author(name='GitHub', url='https://github.com/RiruAugusto/depressaoRobotica', icon_url='https://i.imgur.com/97a24aM.png')

        page2 = discord.Embed (
            title = 'Roletas',
            description = f'Page 2/4',
            colour = discord.Colour.blurple()
        )
        page2.add_field(name=f'`{prefix}carrega`', value=f'Chama o bot para o seu canal de voz para usar roletav', inline=False)
        page2.add_field(name=f'`{prefix}descarrega`', value=f'Roleta russa por comando de voz, use {prefix}carrega para chamar o bot.\nopcionalmente escreva o número de balas a ser usado', inline=False)
        page2.add_field(name=f'`{prefix}roleta` [1-6]', value='Uma roleta russa, opcionalmente escreva o número de balas a ser usado', inline=False)
        page2.add_field(name=f'`{prefix}roletav` ou `{prefix}r` [1-6]', value=f'Roleta russa por comando de voz, use {prefix}carrega para chamar o bot.\nopcionalmente escreva o número de balas a ser usado', inline=False)
        page2.set_thumbnail(url=self.bot.user.avatar.url)
        page2.set_author(name='GitHub', url='https://github.com/RiruAugusto/depressaoRobotica', icon_url='https://i.imgur.com/97a24aM.png')


        page3 = discord.Embed (
            title = 'Provas',
            description = f'Page 3/4',
            colour = discord.Colour.dark_red()
        )
        page3.add_field(name=f'`{prefix}provas` [numero de semanas]', value='Mostra as provas para as próximas semanas, 2 semanas se não especificado', inline=False)
        page3.add_field(name=f'`{prefix}horario`', value='Mostra o horário das mensagens automáticas para o canal atual', inline=False)
        page3.set_thumbnail(url=self.bot.user.avatar.url)
        page3.set_author(name='GitHub', url='https://github.com/RiruAugusto/depressaoRobotica', icon_url='https://i.imgur.com/97a24aM.png')


        page4 = discord.Embed (
            title = 'Moderação',
            description = f'Page 4/4',
            colour = discord.Colour.red()
        )
        page4.add_field(name=f'`{prefix}adiciona` [#canal]', value='Adiciona um canal para ter avisos automáticos de provas.\nSe não houver canal, usa o canal atual', inline=False)
        page4.add_field(name=f'`{prefix}remove` [#canal]', value='Remove um canal dos avisos automáticos de provas.\nSe não houver canal, usa o canal atual', inline=False)
        page4.add_field(name=f'`{prefix}sethorario`', value='Muda o horário das mensagens automáticas para o canal atual', inline=False)
        page4.add_field(name=f'`{prefix}addrole` (@role)', value='Permite uma role usar comandos de moderação', inline=False)
        page4.add_field(name=f'`{prefix}remrole` (@role)', value='Impede uma role usar comandos de moderação', inline=False)
        page4.set_thumbnail(url=self.bot.user.avatar.url)
        page4.set_author(name='GitHub', url='https://github.com/RiruAugusto/depressaoRobotica', icon_url='https://i.imgur.com/97a24aM.png')


        
        pages = [page1, page2, page3, page4]

        message = await ctx.send(embed = page1)
        # sim eu to dependendo do meu código da outra cog, me deixa ser feliz
        await dbExecute(f'INSERT INTO {tableMensagens}(id_canal, id_mens) VALUES({ctx.channel.id},{message.id})')
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
                if i < 3:
                    i += 1
                    await message.edit(embed = pages[i])
            elif str(reaction) == '⏭':
                i = 3
                await message.edit(embed = pages[i])
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 40.0, check = check)
                await message.remove_reaction(reaction, user)
            except:
                break

        await message.delete()
        # await message.clear_reactions()

    @commands.command()
    async def ping(self, ctx):
        pingm = await ctx.channel.send('Ping?')
        await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - ctx.message.created_at)[8:-3], round(self.bot.latency*1000)))


    @commands.command()
    @adm()
    async def limpa(self, ctx):

        if ctx.author.id == int(testeID):
            canal = self.bot.get_channel(int(958058492550316113))
            await canal.purge(bulk=False)

def setup(bot):
    bot.add_cog(Basico(bot))