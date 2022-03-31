import datetime
import discord
import json
import random
from discord.ext import tasks
from discord.ext import commands
import locale
from sys import platform

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

if btoken == '':
    print('Sem token do Bot')
    raise Exception('Sem token do Bot')
if prefix == '':
    prefix = '!'
if IDCanalProvas == '':
    avisosAutomaticos = False
    print('Sem ID do canal para avisos automáticos, não haveram mensagens automáticas')

def diaSemana(wDia):
    dias = {0: 'Segunda-feira', 1 : 'Terça-feira', 2 : 'Quarta-feira', 3 : 'Quinta-feira', 4 : 'Sexta-feira', 5 : 'Sábado', 6 : 'Domingo'}
    return dias[wDia]


# pemitindo o bot ver outras pessoas, e mais algumas coisas da API que eu com certeza entendo
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game('"!comandos" para ajuda'))
  
    print(f'Bot foi iniciado, com {len(bot.users)} usuários, em {len(bot.guilds)} servers.')

    # nao rodar as mensagens de prova automaticas
    # se o host for windows
    # (provavelmente é teste)

    
@bot.command()
async def ping(ctx):
    pingm = await ctx.channel.send('Ping?')
    await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - ctx.message.created_at)[8:-3], round(bot.latency*1000)))

@bot.command()
async def roleta(ctx, *, argumentos=''):
    
    if argumentos == '':
        n = random.randint(0, 5)
        if n == 0:
            await ctx.reply('Morreu!')
        else:
            await ctx.reply('Sobreviveu!')
    
    else:
        try:
            balas = int(argumentos)
        except ValueError as ve: 
            await ctx.reply(f'Me fala quando conseguir colocar "{argumentos}" balas no revólver')
            return

        n = random.randint(1, 6)
        if balas < 0:
            await ctx.reply('Muito corajoso você')
        elif balas == 0:
            await ctx.reply('Sobreviveu! Que surpresa né?')
        elif balas > 6:
            await ctx.reply('Você é corajoso até demais')
        elif balas == 6:
            await ctx.reply('Achei o suicida')
        elif n <= balas:
            await ctx.reply('Morreu!')
        else:
            await ctx.reply('Sobreviveu!')

@bot.command()
async def comandos(ctx):
    await ctx.reply(f'**{bot.user}**\n!ping, !roleta (numero de balas), !comandos, !provas')


@bot.command()
async def provas(ctx):
    prov = open('provas.json', "r")
    provas = json.load(prov)
    prov.close()

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

"""
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(prefix):
        comando, argumentos = trata_argumentos(message, False)

        if comando == 'ping':
            pingm = await manda('Ping?')
            await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - message.created_at)[8:-3], round(client.latency*1000)))

        elif comando == 'comandos':
            await manda(f'**{client.user}** \n !ping, !roleta (numero de balas), !comandos, !provas')

        elif comando == 'roleta':
            comando, argumentos = trata_argumentos(message, True)
            if argumentos=="":
                n = random.randint(0, 5)
                if n == 0:
                    await manda('Morreu!')
                else:
                    await manda('Sobreviveu!')
            elif(argumentos=="role"):
                n = random.randint(0, 4)
                if n == 0:
                    await manda('Top!')
                elif n == 1:
                    await manda('Jungle!')
                elif n == 2:
                    await manda('Mid!')
                elif n == 3:
                    await manda('Adc!')
                elif n == 4:
                    await manda('Sup!')
            else:
                n = random.randint(1, 6)
                try:
                    balas = int(argumentos)
                except ValueError as ve:                
                    await manda(f'Me fala quando conseguir colocar "{argumentos}" balas no revólver')
                if balas < 0:
                    await manda('Muito corajoso você')
                elif balas == 0:
                    await manda('Sobreviveu! Que surpresa né?')
                elif balas > 6:
                    await manda('Você é corajoso até demais')
                elif balas == 6:
                    await manda('Achei o suicida')
                elif n <= balas:
                    await manda('Morreu!')
                else:
                    await manda('Sobreviveu!')

        elif comando == 'provas':
            prov = open('provas.json', "r")
            provas = json.load(prov)
            prov.close()

            await message.delete()
            
            hoje = datetime.date.today()
            hojeString = datetime.date.today().strftime('%d/%m/%y')
            diaDaSemana = hoje.weekday()

            embedProvas = discord.Embed(
            title=f'**{diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para a semana', color=0x336EFF)

            embedProvas.set_image(url='https://i.imgur.com/7nqUbE9.gif')

            for attribute in provas:
                    value = provas[attribute]
                    diaDaProva = datetime.date.fromisoformat(value)

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


            mensagemJunto = await manda(f'{message.author.mention}')
            mensagemEmbed = await message.channel.send(embed=embedProvas)
            await mensagemJunto.delete(delay=60)
            await mensagemEmbed.delete(delay=60)

        elif comando == 'deleta' and message.author.id == testeID:
            canalProvas = client.get_channel(IDCanalProvas)
            await canalProvas.purge(limit=int(argumentos))

        # SE QUISER ADICIONAR ALGUM COMANDO:
        # elif(comando == 'nome do comando' and argumentos == 'argumentos se tiver'):
        # o comando await manda('') manda uma mensagem
        # e é isso, não é muito complicado, só desorganizado
    
    if message.content in response_object:
        await manda(response_object[message.content])

"""
"""
@tasks.loop(seconds=60*60*24) # a cada 1 dia
async def aviso_provas(IDcanalProvas):
    prov = open('provas.json', "r")
    provas = json.load(prov)
    prov.close()

    canalProvas = client.get_channel(int(IDcanalProvas))

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
            
"""
bot.run(btoken)

