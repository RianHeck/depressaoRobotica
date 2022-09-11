import asyncio
import sys
import os
from discord.ext import commands
import json
import discord
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

if os.path.dirname(sys.argv[0]) != '':
    os.chdir(os.path.dirname(sys.argv[0]))

load_dotenv()
if len(sys.argv) != 1:
    if sys.argv[1] == '-d':
        # imprime duas vezes????
        print('--------MODO DE DEBUG--------')
        TOKEN = os.getenv('DEBUGTOKEN')
    else:
        print('opcao invalida')
        sys.exit(1)
else:
    TOKEN = os.getenv('TOKEN')


with open('config.json') as conf:
    config = json.load(conf)


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
bot = commands.Bot(command_prefix=prefix,intents=intents, help_command=None)
bot.owner_id = OWNER_ID

@bot.event
async def on_ready():
       print(f'Conectado como {bot.user}')
       await bot.change_presence(activity=discord.Game(f'"{prefix}comandos" para ajuda'))

       print(f'Bot foi iniciado, com {len(bot.users)} usuários, em {len(bot.guilds)} servers.')

async def load_extensions():
	for filename in os.listdir('./cogs'):
    		if filename.endswith('.py') and filename != '__init__.py':
       			await bot.load_extension(f'cogs.{filename[:-3]}')
        		print(f'Carregado cogs.{filename[:-3]}')

async def main():
	await load_extensions()
	await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
