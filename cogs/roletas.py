from discord.ext import commands
import random
import discord
import asyncio
from discord.utils import get
from main import prefix

# IMPLEMENTAR CHECKS NO LUGAR DOS IFS

class Roletas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    async def deleta_mensagem(self, ctx):
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()

    def is_connected(self, ctx):
        voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()


    @commands.command(brief='roleta russa 1-6')
    async def roleta(self, ctx, *, balas='1'):
        
        heya = self.bot.get_emoji(895327381437448204)
        gun = self.bot.get_emoji(895329552518217798)

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


    @commands.command(aliases=['carregar'], brief='chama o bot para canal de voz')
    async def carrega(self, ctx):

        await self.deleta_mensagem(ctx)

        if ctx.author.voice is None:
                await ctx.channel.send("Você não está conectado em nenhum canal de voz")
                return

        global canalConectado
        canalConectado = ctx.channel
        

        if not self.is_connected(ctx):
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


    @commands.command(aliases=['descarregar'], brief='desconecta bot do canal de voz')
    async def descarrega(self, ctx):

        await self.deleta_mensagem(ctx)

        if self.is_connected(ctx):
            await ctx.message.guild.voice_client.disconnect()
        else:
            await ctx.channel.send('Não estou conectado em nenhum canal')


    @commands.command(aliases=['r', 'rpg'], brief='roleta russa por canal de voz')
    async def roletav(self, ctx, *, argumentos='1'):

        if not self.is_connected(ctx):
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
        
        await self.deleta_mensagem(ctx)

def setup(bot):
    bot.add_cog(Roletas(bot))