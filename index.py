from distutils import archive_util
import datetime
import discord
import json
import random
from discord.ext import tasks
import locale
from sys import platform

# não sei se ainda é necessário, mas vou deixar porque não faz tanto mal
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# parar de usar locale, usar weekday e cadeia de ifs
# https://stackoverflow.com/questions/34076198/how-do-i-convert-the-weekday-of-a-particular-date
# tipo isso


# importando respostas basicas = fala algo : responde algo

data = open('links.json', "r")
response_object = json.load(data)

prov = open('provas.json', "r")
provas = json.load(prov)
# importando o token por um json

# importando o token por um json

with open('config.json', 'r') as conf:
    confs = json.load(conf)
    btoken = confs['token']

# colocando o prefixo no próprio arquivo, porque eu nao sei mexer no git
prefix = '!'

# pemitindo o bot ver outras pessoas, e mais algumas coisas da API que eu com certeza entendo
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

# funcao para tratar o input dos comandos, separando o prefixo dos comandos e dos argumentos(caso haja algum)
def trata_argumentos(message, raw):
    args = message.content[len(prefix):]
    args2 = args.strip().split()

    if raw:
        argumentoslist = str(args2[1:])
    else:
        argumentoslist = str(args2[1:]).lower()

    comandolist = str(args2[:1]).lower()
    comando = "".join(str(x) for x in comandolist)[2:len(comandolist) - 2]
    argumentos = "".join(str(x) for x in argumentoslist)[2:len(argumentoslist) - 2].replace("\'", "").replace(",", "")
    return comando, argumentos


def diaSemana(wDia):
    dias = {0: 'Segunda-feira', 1 : 'Terça-feira', 2 : 'Quarta-feira', 3 : 'Quinta-feira', 4 : 'Sexta-feira', 5 : 'Sábado', 6 : 'Domingo'}
    return dias[wDia]


def plataformaWindows():
    if platform.startswith("win32"):
        return True
    else:
        return False


@client.event
async def on_ready():
    print('Conectado como {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('"!comandos" para ajuda'))
    # await client.change_presence(status=discord.Status.offline)
    print('Bot foi iniciado, com {} usuários, em {} servers.' .format(len(client.users), len(client.guilds)))

    # nao rodar as mensagens de prova automaticas
    # se o host for windows
    # (provavelmente é teste)
    if not plataformaWindows:
        aviso_provas.start() 

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # pequena funcao anônima para encurtar a mesma funcao de sempre
    manda = lambda mens: message.channel.send(f'{mens}')

    if message.content.startswith(prefix):
        comando, argumentos = trata_argumentos(message, 0)

        if comando == 'ping':
            pingm = await manda('Ping?')
            await pingm.edit(content = 'Pong! Latência de {0} ms. Latência de API {1} ms'.format(str(pingm.created_at - message.created_at)[8:-3], round(client.latency*1000)))

        elif comando == 'comandos':
            await manda(f'**{client.user}** \n !ping, !roleta (numero de balas), !comandos, !provas')

        elif comando == 'roleta':
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
                if n <= int(argumentos):
                    await manda('Morreu!')
                else:
                    await manda('Sobreviveu!')

        elif comando == 'provas':
            hoje = datetime.date.today()
            hojeString = datetime.date.today().strftime('%d/%m/%y')
            diaDaSemana = hoje.weekday()

            await manda(f'**{diaSemana(diaDaSemana)}, {hojeString}**\n-----------------------------------')

            for attribute in provas:
                    value = provas[attribute]
                    diaDaProva = datetime.date.fromisoformat(value)

                    if(diaDaProva-hoje).days == 0:
                        dia = diaDaProva.strftime('%d/%m/%y')
                        diaDaSemana = diaSemana(diaDaProva.weekday())
                        msg = f'->{message.author.mention} **É HOJE FIOTE** PROVA DE {attribute}, {diaDaSemana}, {dia}'
                        await manda(msg)
                    
                    elif(diaDaProva-hoje).days <= 7 and (diaDaProva-hoje).days > 0:
                        dia = diaDaProva.strftime('%d/%m/%y')
                        diaDaSemana = diaSemana(diaDaProva.weekday())
                        msg = f'->{message.author.mention} Prova de {attribute}, {diaDaSemana}, {dia} em {(diaDaProva-hoje).days} dias'
                        await manda(msg)

            await manda('-----------------------------------')


        elif comando == 'deleta':
            canalProvas = client.get_channel(958058492550316113)
            await canalProvas.purge(limit=2)

        # SE QUISER ADICIONAR ALGUM COMANDO:
        # elif(comando == 'nome do comando' and argumentos == 'argumentos se tiver'):
        # o comando await manda('') manda uma mensagem
        # e é isso, não é muito complicado, só desorganizado
    
    if message.content in response_object:
        await manda(response_object[message.content])


@tasks.loop(seconds=60*60*24) # a cada 1 dia
async def aviso_provas():
    canalProvas = client.get_channel(958058492550316113)

    await canalProvas.purge(bulk=False)

    hoje = datetime.date.today()
    hojeString = datetime.date.today().strftime('%d/%m/%y')
    diaDaSemana = hoje.weekday()
    
    await canalProvas.send(f'**{diaSemana(diaDaSemana)}, {hojeString}**\n-----------------------------------')

    for attribute in provas:
            value = provas[attribute]

            diaDaProva = datetime.date.fromisoformat(value)

            if(diaDaProva-hoje).days == 0:
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                msg = f'->@everyone @everyone @everyone @everyone @everyone\n**É HOJE RAPAZIADA** PROVA DE {attribute}, {diaDaSemana}, {dia}'
                await canalProvas.send(msg)
            
            elif(diaDaProva-hoje).days <= 7 and (diaDaProva-hoje).days > 0:
                dia = diaDaProva.strftime('%d/%m/%y')
                diaDaSemana = diaSemana(diaDaProva.weekday())
                msg = f'->@everyone Prova de {attribute}, {diaDaSemana}, {dia} em {(diaDaProva-hoje).days} dias'
                await canalProvas.send(msg)

    await canalProvas.send('-----------------------------------')

client.run(btoken)

