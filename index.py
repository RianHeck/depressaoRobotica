import datetime
import discord
import json
import random
from discord.ext import tasks
from discord.ext import commands
import locale
from sys import platform
import os

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# importando respostas basicas = fala algo : responde algo

data = open('links.json', 'r')
response_object = json.load(data)

# importando configurações pessoais por um json

with open('config.json', 'r') as conf:
    confs = json.load(conf)
    btoken = confs['token']
    prefix = confs['prefix']
    IDCanalProvas = confs['canalDeProvas']
    testeID = confs['testeID']

avisosAutomaticos = True

if btoken == '' or btoken == None:
    print('Sem token do Bot')
    raise RuntimeError('Sem token do Bot')
if prefix == '':
    prefix = '!'
if IDCanalProvas == '':
    avisosAutomaticos = False
    print('Sem ID do canal para avisos automáticos, não haveram mensagens automáticas')

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
        

# pemitindo o bot ver outras pessoas, e mais algumas coisas da API que eu com certeza entendo
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

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

    # nao rodar as mensagens de prova automaticas
    # se o host for windows
    # (provavelmente é teste)
    # if not plataformaWindows and avisosAutomaticos:
    #     aviso_provas.start(IDCanalProvas)

# @bot.event
# async def on_typing(ch, us, wh):
#     await ch.send(f'FALA LOGO {us.mention}')
    
@bot.command()
async def ping(ctx):
    pingm = await ctx.channel.send('Ping?')
    await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - ctx.message.created_at)[8:-3], round(bot.latency*1000)))

@bot.command()
async def roleta(ctx, *, argumentos='1'):
    
    heya = bot.get_emoji(895327381437448204)
    gun = bot.get_emoji(895329552518217798)

    # if gun not in ctx.guild.emojis:
    #     gun = ':gun:'
    # if heya not in ctx.guild.emojis:
    #     heya = ':smiley:'

    try:
        balas = int(argumentos)
    except ValueError: 
        await ctx.reply(f'Me fala quando conseguir colocar "{argumentos}" balas no revólver')
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
    await ctx.reply(f'**{bot.user}**\n{prefix}ping, {prefix}roleta (numero de balas), {prefix}comandos, {prefix}provas')

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


@bot.command()
async def provas(ctx):
    prov = open('provas.json', "r")
    provas = json.load(prov)
    prov.close()


    if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
        await ctx.message.delete()
    
    hoje = datetime.date.today()
    hojeString = datetime.date.today().strftime('%d/%m/%y')
    diaDaSemana = hoje.weekday()

    embedProvas = discord.Embed(
    title=f'**{diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para a semana', color=0x336EFF)

    embedProvas.set_image(url='https://i.imgur.com/7nqUbE9.gif')

    for attribute in provas:
            value = provas[attribute]
            diaDaProva = datetime.date.fromisoformat(value)

            if(diaDaProva-hoje).days == 1:
                embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
                embedProvas.color = 0xFFFF00

            if(diaDaProva-hoje).days == 0:
                embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
                embedProvas.color = 0xFF0000
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'__->**É HOJE FIOTE** PROVA DE {attribute}, {diaDaSemana}, {dia}__', inline=False)
            
            elif(diaDaProva-hoje).days <= 7 and (diaDaProva-hoje).days > 0:
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'->Prova de {attribute}, {diaDaSemana}, {dia} em **{(diaDaProva-hoje).days} dias**', inline=False)


    mensagemJunto = await ctx.channel.send(f'{ctx.author.mention}')
    mensagemEmbed = await ctx.channel.send(embed=embedProvas)
    await mensagemJunto.delete(delay=60)
    await mensagemEmbed.delete(delay=60)

# @bot.command
# async def reseta(ctx):

#     # depois revisitar esse codigo, ele nao eh amigavel com varios servers
#     # especificar o server e canal
#     if ctx.author.id == testeID:
#         aviso_provas.cancel()
#         aviso_provas.start(IDCanalProvas)
#     else:
#         ctx.reply('você não possui permissão para usar esse comando!')

@bot.event
async def on_message(ctx):
    if ctx.author.bot:
        return

    if ctx.content.lower().__contains__('bitches'):
        await ctx.channel.send("  ⣞⢽⢪⢣⢣⢣⢫⡺⡵⣝⡮⣗⢷⢽⢽⢽⣮⡷⡽⣜⣜⢮⢺⣜⢷⢽⢝⡽⣝\n⠸⡸⠜⠕⠕⠁⢁⢇⢏⢽⢺⣪⡳⡝⣎⣏⢯⢞⡿⣟⣷⣳⢯⡷⣽⢽⢯⣳⣫⠇\n  ⠀⠀⢀⢀⢄⢬⢪⡪⡎⣆⡈⠚⠜⠕⠇⠗⠝⢕⢯⢫⣞⣯⣿⣻⡽⣏⢗⣗⠏⠀\n   ⠀⠪⡪⡪⣪⢪⢺⢸⢢⢓⢆⢤⢀⠀⠀⠀⠀⠈⢊⢞⡾⣿⡯⣏⢮⠷⠁\n  ⠀⠀⠀⠈⠊⠆⡃⠕⢕⢇⢇⢇⢇⢇⢏⢎⢎⢆⢄⠀⢑⣽⣿⢝⠲⠉\n  ⠀⠀⠀⠀⠀⡿⠂⠠⠀⡇⢇⠕⢈⣀⠀⠁⠡⠣⡣⡫⣂⣿⠯⢪⠰⠂\n  ⠀⠀⠀⠀⡦⡙⡂⢀⢤⢣⠣⡈⣾⡃⠠⠄⠀⡄⢱⣌⣶⢏⢊⠂\n  ⠀⠀⠀⠀⢝⡲⣜⡮⡏⢎⢌⢂⠙⠢⠐⢀⢘⢵⣽⣿⡿⠁⠁\n  ⠀⠀⠀⠀⠨⣺⡺⡕⡕⡱⡑⡆⡕⡅⡕⡜⡼⢽⡻⠏\n  ⠀⠀⠀⠀⣼⣳⣫⣾⣵⣗⡵⡱⡡⢣⢑⢕⢜⢕⡝\n  ⠀⠀⠀⣴⣿⣾⣿⣿⣿⡿⡽⡑⢌⠪⡢⡣⣣⡟\n  ⠀⠀⠀⡟⡾⣿⢿⢿⢵⣽⣾⣼⣘⢸⢸⣞⡟\n  ⠀⠀⠀⠀⠁⠇⠡⠩⡫⢿⣝⡻⡮⣒⢽⠋⠀")
    
    if ctx.content in response_object:
        await ctx.channel.send(response_object[ctx.content])

    if bot.user.mentioned_in(ctx):
        await ctx.reply(f'**{bot.user}**\n{prefix}ping, {prefix}roleta (numero de balas), {prefix}comandos, {prefix}provas')
    
    await bot.process_commands(ctx)

@tasks.loop(seconds=60*60*24) # a cada 1 dia
async def aviso_provas(IDcanalProvas):
    prov = open('provas.json', "r")
    provas = json.load(prov)
    prov.close()

    canalProvas = bot.get_channel(int(IDcanalProvas))

    # verificar se as mensagens sao do bot antes de deletar
    await canalProvas.purge(limit=2, bulk=False)

    hoje = datetime.date.today()
    hojeString = datetime.date.today().strftime('%d/%m/%y')
    diaDaSemana = hoje.weekday()
    
    embedProvas = discord.Embed(
            title=f'**{diaSemana(diaDaSemana)}, {hojeString}**', description='Provas para a semana', color=0x336EFF)
    
    embedProvas.set_image(url='https://i.imgur.com/7nqUbE9.gif')

    for attribute in provas:
            value = provas[attribute]

            diaDaProva = datetime.date.fromisoformat(value)

            if(diaDaProva-hoje).days == 1:
                embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
                embedProvas.color = 0xFFFF00

            if(diaDaProva-hoje).days == 0:
                embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
                embedProvas.color = 0xFF0000
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'__->**É HOJE RAPAZIADA** PROVA DE {attribute}, {diaDaSemana}, {dia}__', inline=False)

            elif(diaDaProva-hoje).days <= 7 and (diaDaProva-hoje).days > 0:
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                embedProvas.add_field(name=f'•{attribute}', value=f'->Prova de {attribute}, {diaDaSemana}, {dia} em **{(diaDaProva-hoje).days} dias**', inline=False)

    await canalProvas.send('@everyone')
    await canalProvas.send(embed=embedProvas)

bot.run(btoken)

