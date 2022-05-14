import sys
import os
from discord.ext import commands
import json
import discord
from dotenv import load_dotenv

if os.path.dirname(sys.argv[0]) != '':
    os.chdir(os.path.dirname(sys.argv[0]))

load_dotenv()

with open('config.json') as conf:
    config = json.load(conf)

# TOKEN = config['TOKEN']
TOKEN = os.getenv('TOKEN')

prefix = config['prefix']
arquivoEmbeds = config['arquivoEmbeds']
arquivoEmbedsAuto = config['arquivoEmbedsAuto']
testeID = config['testeID']
arquivoProvas = config['arquivoProvas']
arquivoRespostas = config['arquivoRespostas']

OWNER_ID = 236901700475027456

avisosAutomaticos = True # para debug, primariamente

with open(arquivoRespostas, encoding='utf-8') as data:
    respostas = json.load(data)

if TOKEN == '' or TOKEN == None:
    print('Sem token do Bot')
    raise RuntimeError('Sem token do Bot')
if prefix == '':
    prefix = '!'

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix,intents=intents, caseInensitive=True)


@bot.event
async def on_ready():
        print(f'Conectado como {bot.user}')
        await bot.change_presence(activity=discord.Game(f'"{prefix}comandos" para ajuda'))

        print(f'Bot foi iniciado, com {len(bot.users)} usuários, em {len(bot.guilds)} servers.')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f'Carregado cogs.{filename[:-3]}')

bot.run(TOKEN)
