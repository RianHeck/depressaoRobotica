import datetime
import discord
import json
import random
from discord.ext import tasks
from discord.ext import commands
from discord.utils import get
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import locale
from sys import platform
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# importando respostas basicas = fala algo : responde algo
with open('links.json', encoding='utf-8') as data:
    response_object = json.load(data)

# importando configurações pessoais por um json

with open('config.json', 'r') as conf:
    confs = json.load(conf)
    # btoken = confs['token']
    prefix = confs['prefix']
    IDCanalProvas = confs['canalDeProvas']
    testeID = confs['testeID']

TOKEN = os.getenv('TOKEN')

avisosAutomaticos = True

if TOKEN == '' or TOKEN == None:
    print('Sem token do Bot')
    raise RuntimeError('Sem token do Bot')
if prefix == '':
    prefix = '!'
if IDCanalProvas == '':
    avisosAutomaticos = False
    print('Sem ID do canal para avisos automáticos, não haverão mensagens automáticas')

def diaSemana(wDia):
    dias = {0: 'Segunda-feira', 1 : 'Terça-feira', 2 : 'Quarta-feira', 3 : 'Quinta-feira', 4 : 'Sexta-feira', 5 : 'Sábado', 6 : 'Domingo'}
    return dias[wDia]

def plataformaWindows():
    if platform.startswith("win32"):
        return True
    else:
        return False

def leRoles():
    with open('roles.txt', 'r+', encoding='utf-8') as f:
        roles = f.read()
        return roles.split(',')


def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


def load_json(filename):
    try:
        with open(filename, encoding='utf-8') as inF:
            arquivo = json.load(inF)
            return arquivo
    except ValueError:
        return []
    except FileNotFoundError:
        raise KeyError()
        
def write_json(filename, content):
    novo = load_json(filename)
    novo.append(content)
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(novo, outF, ensure_ascii=True, indent=4)


def delete_item(filename, item):
    content = load_json(filename)
    if item in content:
        content.remove(item)
    else:
        return -1
    with open(filename, 'w', encoding='utf-8') as outF:
        json.dump(content, outF, ensure_ascii=True, indent=4)


# pemitindo o bot ver outras pessoas, e mais algumas coisas da API que eu com certeza entendo
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    
    if avisosAutomaticos:
        canal = bot.get_channel(int(IDCanalProvas))
        if canal in bot.get_all_channels():
            if canal.permissions_for(canal.guild.me).read_messages and canal.permissions_for(canal.guild.me).send_messages:
                if not plataformaWindows:
                    aviso_provas.start(IDCanalProvas)
            else:
                print('Não consigo mandar mesnagens no canal de aviso de provas')
        else:
            print('Não encontrei o canal indicado para os avisos de provas')
    
    print(f'Conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(f'"{prefix}comandos" para ajuda'))
  
    print(f'Bot foi iniciado, com {len(bot.users)} usuários, em {len(bot.guilds)} servers.')

    print('Verificando e deletando embeds deixados para trás')
    embeds = load_json('embeds.json')

    for embed in embeds:
        canal = bot.get_channel(embed[1])
        try:
            msg = await canal.fetch_message(embed[0])
            await msg.delete()
            delete_item('embeds.json', embed)
        except discord.errors.NotFound:
            delete_item('embeds.json', embed)
            print(f'Deletada uma mensagem desaparecida em {canal.guild}/{canal} do arquivo')
        else:
            print(f'Deletada uma mensagem em {canal.guild}/{canal}')


@bot.event
async def on_voice_state_update(member, before, after):
    
    if member.id != bot.user.id:
        return

    elif after.channel is not None:
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time >= 300:
                await voice.disconnect()
                await canalConectado.send('Cansei de segurar o revólver')
            if not voice.is_connected():
                break

@bot.event
async def on_message_delete(message):
    embeds = load_json('embeds.json')
    for embed in embeds:
        if message.id == embed[0]:
            delete_item('embeds.json', embed)

# @bot.event
# async def on_typing(ch, us, wh):
#     await ch.send(f'FALA LOGO {us.mention}')
    
@bot.command()
async def ping(ctx):
    pingm = await ctx.channel.send('Ping?')
    await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - ctx.message.created_at)[8:-3], round(bot.latency*1000)))


@slash.slash(name='roleta',
            description='Roleta por texto',
            #guild_ids=[317781355113086976, 477183409572282379],
            guild_ids=[317781355113086976],
            options=[
                create_option(
                    name='balas',
                    description='Número de balas',
                    required=False,
                    option_type=3
                )
            ])

@bot.command()
async def roleta(ctx, *, balas='1'):
    
    heya = bot.get_emoji(895327381437448204)
    gun = bot.get_emoji(895329552518217798)

    if gun not in ctx.guild.emojis:
        gun = ':gun:'
    if heya not in ctx.guild.emojis:
        heya = ':smiley:'
    


    try:
        balas = int(balas)
    except ValueError: 
        mes = await ctx.reply(f'Me fala quando conseguir colocar "{balas}" balas no revólver')
        await mes.delete(delay=10)
        return

    n = random.randint(1, 6)
    if balas < 0:
        await ctx.reply('Muito corajoso você')
    elif balas == 0:
        await ctx.reply(f'{heya} Sobreviveu! Que surpresa né?')
    elif balas > 6:
        await ctx.reply('Você é corajoso até demais')
    elif balas == 6:
        await ctx.reply(f'{gun} Morreu! Achei o suicida')
    elif n <= balas:
        await ctx.reply(f'{gun} Morreu!')
    else:
        await ctx.reply(f'{heya} Sobreviveu!')

@bot.command()
async def comandos(ctx):

    embedComandos = discord.Embed(
    title=f'{bot.user} Comandos', color=0xF0F0F0)

    embedComandos.set_thumbnail(url=bot.user.avatar_url)

    embedComandos.add_field(name=f'{prefix}ping', value='Testa o ping do bot e da API do discord', inline=False)
    embedComandos.add_field(name=f'{prefix}roleta (1-6)', value='Uma roleta russa, opcionalmente escreva o número de balas a ser usado', inline=False)
    embedComandos.add_field(name=f'{prefix}roletav/{prefix}r (1-6)', value=f'Roleta russa por comando de voz, use {prefix}carrega para chamar o bot.\nopcionalmente escreva o número de balas a ser usado', inline=False)
    embedComandos.add_field(name=f'{prefix}comandos', value='Mostra uma lista de comandos', inline=False)
    embedComandos.add_field(name=f'{prefix}provas (numero de semanas)', value='Mostra as provas para as próximas semanas, 2 semanas se não especificado', inline=False)
    
    await ctx.reply(embed=embedComandos)

    # await ctx.reply(f'**{bot.user}**\n{prefix}ping, {prefix}roleta (numero de balas), {prefix}comandos, {prefix}provas, {prefix}roletav')

@bot.command(aliases=['carregar'])
async def carrega(ctx):

    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()

    if ctx.author.voice is None:
            await ctx.channel.send("Você não está conectado em nenhum canal de voz")
            return

    global canalConectado
    canalConectado = ctx.channel
    

    if not is_connected(ctx):
        roletaVC = await ctx.author.voice.channel.connect()
        # roletaVC = await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
        await ctx.channel.send(f'Conectado em {roletaVC.channel}')

    else:
        roletaVC = ctx.message.guild.voice_client
        await roletaVC.move_to(ctx.author.voice.channel)
        #roletaVC = await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)


    # await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
    # roletaVC = ctx.message.guild.voice_client

    roletaVC.play(discord.FFmpegPCMAudio("audio/reload.mp3"))

@bot.command(aliases=['descarregar'])
async def descarrega(ctx):

    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()

    if is_connected(ctx):
        await ctx.message.guild.voice_client.disconnect()
    else:
        await ctx.channel.send('Não estou conectado em nenhum canal')


@bot.command(aliases=['r', 'rpg'])
async def roletav(ctx, *, argumentos='1'):

    if not ctx.message.guild.voice_client:
        await ctx.channel.send(f'Não estou conectado a nenhum canal, use {prefix}carrega')
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
        return

    if ctx.author.voice is None:
            await ctx.channel.send("Você não está conectado em nenhum canal de voz")
            return

    consegueMover = ctx.author.voice.channel.permissions_for(ctx.guild.me).move_members

    roletaVC = ctx.message.guild.voice_client

    if ctx.author.voice.channel == ctx.message.guild.voice_client.channel:
        if ctx.voice_client.is_playing():
            mes = await ctx.reply('Calma, tem bala pra todo mundo!:)')
            await mes.delete(delay=10)
        else:
            try:
                balas = int(argumentos)
            except ValueError: 
                mes = await ctx.reply(f'Me fala quando conseguir colocar "{argumentos}" balas no revólver')
                await mes.delete(delay=10)
                return

            n = random.randint(1, 6)
            if balas < 0:
                roletaVC.play(discord.FFmpegPCMAudio("audio/uepa.mp3"))
                await asyncio.sleep(1)
                mes = await ctx.reply('Muito corajoso você')
                await mes.delete(delay=10)
            elif balas == 0:
                roletaVC.play(discord.FFmpegPCMAudio("audio/uepa.mp3"))
            elif balas > 6:
                mes = await ctx.reply('Você é corajoso até demais')
                await mes.delete(delay=10)
            elif balas == 6:
                if ctx.invoked_with == 'rpg':
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiroG.mp3"))
                else:
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiro.mp3"))
                await asyncio.sleep(1)
                if consegueMover:
                    await ctx.message.author.move_to(None)
                else:
                    await ctx.reply('Muito forte')
            elif n <= balas:
                if ctx.invoked_with == 'rpg':
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiroG.mp3"))
                else:
                    roletaVC.play(discord.FFmpegPCMAudio("audio/tiro.mp3"))
                await asyncio.sleep(1)
                if consegueMover:
                    await ctx.message.author.move_to(None)
                else:
                    await ctx.reply('Muito forte')
            else:
                roletaVC.play(discord.FFmpegPCMAudio("audio/falha.mp3"))
                await asyncio.sleep(1.5)
                roletaVC.play(discord.FFmpegPCMAudio("audio/tambor.mp3"))

    else:
        await roletaVC.move_to(ctx.author.voice.channel)
    
    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()


# @bot.command()
# async def adiciona(ctx, roleNova):

#     roles = leRoles()
#     if roles == ['']:
#         roles.clear()
#     roles.append(roleNova)

#     roles = ','.join(roles)

#     with open('roles.txt', 'r+', encoding='utf-8') as f:
#         f.seek(0)
#         f.write(roles)
#     await ctx.channel.send(leRoles())

# @bot.command()
# async def remove(ctx, roleRemove):

#     roles = leRoles()
#     if roleRemove in roles:
#         roles.remove(roleRemove)

#     roles = ','.join(roles)
#     print(roles)

#     with open('roles.txt', 'r+', encoding='utf-8') as f:
#         f.seek(0)
#         f.write(roles)
#     await ctx.channel.send(leRoles())    


async def criaEmbedProvas(sem):

    with open('provasTeste.json', encoding='utf-8') as prov:
        provas = json.load(prov)
    
    hoje = datetime.date.today()
    hojeString = datetime.date.today().strftime('%d/%m/%y')
    diaDaSemana = hoje.weekday()

    embedProvas = discord.Embed(
    title=f'**{diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para as próximas {sem} semana(s)', color=0x336EFF)

    provasParaPeriodo = []
    for materia in provas:
        for provaIndividual in provas[materia]:
            dataProvaRaw = provaIndividual['data']
            dataProva = datetime.date.fromisoformat(dataProvaRaw)
            
            if(dataProva-hoje).days <= (7 * sem) and (dataProva-hoje).days >= 0:
                provasParaPeriodo.append({'nome': provaIndividual['nome'],
                                          'diasParaProva': (datetime.date.fromisoformat(provaIndividual['data'])-hoje).days,
                                          'materia': materia,
                                          'data': dataProva,
                                          'tipo': provaIndividual['tipo']})
                

    provasParaPeriodo = sorted(provasParaPeriodo, key=lambda attribute: attribute['diasParaProva'])

    
    if provasParaPeriodo[0]['diasParaProva'] == 0:
        embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
        embedProvas.color = 0xFF0000
    elif provasParaPeriodo[0]['diasParaProva'] == 1:
        embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
        embedProvas.color = 0xFFFF00
    else:
        embedProvas.set_image(url='https://i.imgur.com/zkGm9j2.jpg')

    # aumentar tamanho horizontal
    # footer = "\u2800" * 100
    # footer = footer + "|"
    # print(footer)
    # embedProvas.set_footer(text=footer)

    return embedProvas, provasParaPeriodo

@bot.command()
async def provas(ctx, sem = 2):

# criar lista de materias baseadas nas roles da pessoa
# if attribute['materia'] in listaMateriasEspecificas:
#     (1)
# mandar somente essas para comando !provas
    async with ctx.channel.typing():

        embedProvas, provasParaPeriodo = await criaEmbedProvas(sem)

        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()

        for prova in provasParaPeriodo:
            dataProva = prova['data']
            dia = dataProva.strftime('%d/%m/%y')
            diaDaSemana = diaSemana(dataProva.weekday())
            # aqui (1)
            if prova['diasParaProva'] == 0:
                embedProvas.add_field(name=f'•{prova["nome"]}',
                                      value=f'__->**É HOJE FIOTE** PROVA DE {prova["nome"]}, {diaDaSemana}, {dia}__', inline=False)
            elif prova['diasParaProva'] == 1:
                embedProvas.add_field(name=f'•{prova["nome"]}',
                                      value=f'->Prova de {prova["nome"]}, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dia**', inline=False)
            else:
                embedProvas.add_field(name=f'•{prova["nome"]}',
                                      value=f'->Prova de {prova["nome"]}, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dias**', inline=False)


        # mensagemJunto = await ctx.channel.send(f'{ctx.author.mention}')
        mensagemEmbed = await ctx.channel.send(content=f'{ctx.author.mention}', embed=embedProvas)
        write_json('embeds.json', (mensagemEmbed.id, ctx.channel.id))

        await mensagemEmbed.delete(delay=60)
        # delete_item('embeds.json', (mensagemEmbed.id, ctx.channel.id))
        
        

@bot.command()
async def reseta(ctx):

    # depois revisitar esse codigo, ele nao eh amigavel com varios servers
    # especificar o server e canal

    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()

    if ctx.author.id == int(testeID):
        aviso_provas.cancel()
        await asyncio.sleep(1)
        aviso_provas.start(IDCanalProvas)
    elif not avisosAutomaticos:
        await ctx.reply('Avisos automáticos desligados')
    else:
        await ctx.reply('Você não possui permissão para usar esse comando!')

@bot.command()
async def manda(ctx, *, mens):

    if ctx.author.id == testeID:
        canal = bot.get_channel(int(958058492550316113))
        await canal.send(mens)


@bot.command()
async def limpa(ctx):

    if ctx.author.id == testeID:
        canal = bot.get_channel(int(958058492550316113))
        await canal.purge(bulk=False)

@bot.event
async def on_message(ctx):
    if ctx.author.bot:
        return

    if ctx.content.lower().__contains__('bitches'):
        await ctx.channel.send("  ⣞⢽⢪⢣⢣⢣⢫⡺⡵⣝⡮⣗⢷⢽⢽⢽⣮⡷⡽⣜⣜⢮⢺⣜⢷⢽⢝⡽⣝\n⠸⡸⠜⠕⠕⠁⢁⢇⢏⢽⢺⣪⡳⡝⣎⣏⢯⢞⡿⣟⣷⣳⢯⡷⣽⢽⢯⣳⣫⠇\n  ⠀⠀⢀⢀⢄⢬⢪⡪⡎⣆⡈⠚⠜⠕⠇⠗⠝⢕⢯⢫⣞⣯⣿⣻⡽⣏⢗⣗⠏⠀\n   ⠀⠪⡪⡪⣪⢪⢺⢸⢢⢓⢆⢤⢀⠀⠀⠀⠀⠈⢊⢞⡾⣿⡯⣏⢮⠷⠁\n  ⠀⠀⠀⠈⠊⠆⡃⠕⢕⢇⢇⢇⢇⢇⢏⢎⢎⢆⢄⠀⢑⣽⣿⢝⠲⠉\n  ⠀⠀⠀⠀⠀⡿⠂⠠⠀⡇⢇⠕⢈⣀⠀⠁⠡⠣⡣⡫⣂⣿⠯⢪⠰⠂\n  ⠀⠀⠀⠀⡦⡙⡂⢀⢤⢣⠣⡈⣾⡃⠠⠄⠀⡄⢱⣌⣶⢏⢊⠂\n  ⠀⠀⠀⠀⢝⡲⣜⡮⡏⢎⢌⢂⠙⠢⠐⢀⢘⢵⣽⣿⡿⠁⠁\n  ⠀⠀⠀⠀⠨⣺⡺⡕⡕⡱⡑⡆⡕⡅⡕⡜⡼⢽⡻⠏\n  ⠀⠀⠀⠀⣼⣳⣫⣾⣵⣗⡵⡱⡡⢣⢑⢕⢜⢕⡝\n  ⠀⠀⠀⣴⣿⣾⣿⣿⣿⡿⡽⡑⢌⠪⡢⡣⣣⡟\n  ⠀⠀⠀⡟⡾⣿⢿⢿⢵⣽⣾⣼⣘⢸⢸⣞⡟\n  ⠀⠀⠀⠀⠁⠇⠡⠩⡫⢿⣝⡻⡮⣒⢽⠋⠀")
    
    if ctx.content in response_object:
        await ctx.channel.send(response_object[ctx.content])

    # if ctx.content == (f'{prefix}ajuda'):
    #     await ctx.s

    if bot.user.mentioned_in(ctx):
        await comandos(ctx)
    
    await bot.process_commands(ctx)


@tasks.loop(seconds=60*60*24) # a cada 1 dia
async def aviso_provas(ID):

    with open('provas.json', encoding='utf-8') as prov:
        provas = json.load(prov)

    canalProvas = bot.get_channel(int(ID))
    sem = 2 # quantidade de semanas para verificar

    # deleta as mensagens passadas do bot
    async for message in canalProvas.history(limit=2):
        if message.author == bot.user:
            # print(message)
            await message.delete()

    async with canalProvas.typing():

        embedProvas, provasParaPeriodo = await criaEmbedProvas(canalProvas, sem)

        for attribute in provasParaPeriodo:  

            with open('provas.json', encoding='utf-8') as prov:
                dataProvaRaw = json.load(prov)[attribute[0]]
            hoje = datetime.date.today()
            dataProva = datetime.date.fromisoformat(dataProvaRaw)
            dia = dataProva.strftime('%d/%m/%y')
            diaDaSemana = diaSemana(dataProva.weekday())
            if attribute[1] == 0:
                embedProvas.add_field(name=f'•{attribute[0]}', value=f'__->**É HOJE RAPAZIADA** PROVA DE {attribute[0]}, {diaDaSemana}, {dia}__', inline=False)
            elif attribute[1] == 1:
                embedProvas.add_field(name=f'•{attribute[0]}', value=f'->Prova de {attribute[0]}, {diaDaSemana}, {dia} em **{(dataProva-hoje).days} dia**', inline=False)
            else:
                embedProvas.add_field(name=f'•{attribute[0]}', value=f'->Prova de {attribute[0]}, {diaDaSemana}, {dia} em **{(dataProva-hoje).days} dias**', inline=False)

        await canalProvas.send('@everyone')
        await canalProvas.send(embed=embedProvas)

bot.run(TOKEN)

