from distutils import archive_util
from datetime import datetime, timedelta
import discord
import json
import random
from discord.ext import tasks
import locale


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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

@client.event
async def on_ready():
    print('Conectado como {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('"!comandos" para ajuda'))
    # await client.change_presence(status=discord.Status.offline)
    print('Bot foi iniciado, com {} usuários, em {} servers.' .format(len(client.users), len(client.guilds)))
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
            data = datetime.now().strftime('%d/%m/%y')
            data = datetime.strptime(data, '%d/%m/%y')
            for attribute in provas:
                    value = provas[attribute]
                    a = datetime.strptime(value, '%d-%m-%y')
                    if(a-data) <= timedelta(days=7):
                        dia = a.strftime('%A, %d/%m/%y')
                        msg = f'{message.author.mention} Prova de {attribute}, no dia {dia} em {(a-data).days} dias'
                        await message.channel.send(msg)
        
        # SE QUISER ADICIONAR ALGUM COMANDO:
        # elif(comando == 'nome do comando' and argumentos == 'argumentos se tiver'):
        # o comando await manda('') manda uma mensagem
        # e é isso, não é muito complicado, só desorganizado
    
    if message.content in response_object:
        await manda(response_object[message.content])


@tasks.loop(seconds=60*60*24) # a cada 1 dia
async def aviso_provas():
    data = datetime.now().strftime('%d/%m/%y')
    data = datetime.strptime(data, '%d/%m/%y')
    for attribute in provas:
            value = provas[attribute]
            a = datetime.strptime(value, '%d-%m-%y')
            if(a-data) <= timedelta(days=0):
                canalProvas = client.get_channel(958058492550316113)
                dia = a.strftime('%A, %d/%m/%y')
                msg = f'@everyone @everyone @everyone @everyone @everyone\n **É HOJE RAPAZIADA** PROVA DE {attribute}, {dia}'
                await canalProvas.send(msg)
            
            elif(a-data) <= timedelta(days=7):
                canalProvas = client.get_channel(958058492550316113)
                dia = a.strftime('%A, %d/%m/%y')
                msg = f'@everyone Prova de {attribute}, {dia} em {(a-data).days} dias'
                await canalProvas.send(msg)
    

client.run(btoken)

