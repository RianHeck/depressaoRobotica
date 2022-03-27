import discord
import json
import random
# from dict import comandos

data = open('links.json', "r")
links = json.load(data)

response_object = links

with open('config.json', 'r') as conf:
    confs = json.load(conf)
    btoken = confs['token']

# importando o token por um json

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

        elif comando == 'roleta' and argumentos == "":
            n = random.randint(0, 5)
            if n == 0:
                await manda('Morreu!')
            else:
                await manda('Sobreviveu!')

        elif comando == 'roleta' and argumentos == "role":
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
        
     
    if ';-;' in message.content:
        await manda(';-;')
    
    if message.content in response_object:
        await manda(response_object[message.content])

client.run(btoken)

