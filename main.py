import os
from discord.ext import commands
import json
import discord

with open('config.json') as conf:
    config = json.load(conf)

token = config['token']

prefix = '!'

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=prefix,intents=intents, caseInensitive=True)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(token)