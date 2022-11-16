from discord.ext import commands
import discord
from main import OWNER_ID
from utils import db

def permissao():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        has_role = False
        roles = db.dbReturn(f'SELECT * FROM {db.tablePermissoes} WHERE id_guilda = {ctx.channel.id}')
        if roles is not None:
            for role in roles:
                role = ctx.guild.get_role(role)
                if not role:
                    continue
                if role in ctx.author.roles:
                    has_role = True
                    break
        if has_role or ctx.author.guild_permissions.administrator:
                return True
        else:
            return False
            
    return commands.check(predicate) 

def adm():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def eu():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        else:
            return False
    return commands.check(predicate)