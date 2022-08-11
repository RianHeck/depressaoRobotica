import traceback
from discord.ext import commands, tasks
import datetime
import sys
import discord
from main import avisosAutomaticos, arquivoProvas
from utils.db import *
from utils.json import *
from utils.checks import *

sys.path.append("..")

class Provas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        embeds = await returnTable(tableMensagens)
        for embed in embeds:
            if message.id == embed[1]:
                await dbExecute(f'''DELETE FROM {tableMensagens}
                                WHERE id_canal = {message.channel.id};''')
                # await delete_item(arquivoEmbeds, embed)

    @commands.Cog.listener()
    async def on_ready(self):

        if self.aviso_provas.is_running():
            self.aviso_provas.stop()

        if avisosAutomaticos:
            # canal = self.bot.get_channel(int(IDCanalProvas))

            # VERIFICAR SE AS TABLES EXISTEM, SE NÃO EXCLUIR 1 MENSAGEM DO BOT NO CANAL
            # DE AVISOS

            await dbExecute(f'''CREATE TABLE IF NOT EXISTS {tableAvisos}(
                                id_canal INT,
                                id_mens INT DEFAULT 0,
                                tempo_envio TEXT DEFAULT '07:00:00'
                            );
                            '''
            )
            
            await dbExecute(f'''CREATE TABLE IF NOT EXISTS {tableMensagens}(
                                id_canal INT,
                                id_mens INT DEFAULT 0
                            );
                            '''
            )

            await dbExecute(f'''CREATE TABLE IF NOT EXISTS {tablePermissoes}(
                                id_guilda INT,
                                id_role INT DEFAULT 0
                            );
                            '''
            )

            # arrumar isso aqui
            self.aviso_provas.start()
        
        print('Verificando e deletando embeds deixados para trás')
        # embeds = await load_json(arquivoEmbeds)
        embeds = await returnTable(tableMensagens)
        for embed in embeds:
            canal = self.bot.get_channel(embed[0])
            try:
                msg = await canal.fetch_message(embed[1])
                await msg.delete()
                #await delete_item(arquivoEmbeds, embed)
            except discord.errors.NotFound:
                #await delete_item(arquivoEmbeds, embed)
                print(f'Deletada uma mensagem desaparecida em {canal.guild}/{canal} do arquivo')
            else:
                print(f'Deletada uma mensagem em {canal.guild}/{canal}')
            finally:
                await dbExecute(f'''DELETE FROM {tableMensagens}
                            WHERE id_canal = {canal.id};''')

    
    def diaSemana(self, wDia):
        dias = {0: 'Segunda-feira', 1 : 'Terça-feira', 2 : 'Quarta-feira', 3 : 'Quinta-feira', 4 : 'Sexta-feira', 5 : 'Sábado', 6 : 'Domingo'}
        return dias[wDia]

    async def criaEmbedProvas(self, sem):

        # with open('provasTeste.json', encoding='utf-8') as prov:
            # provas = json.load(prov)
        
        provas = await load_json(arquivoProvas)

        hoje = datetime.date.today()
        hojeString = datetime.date.today().strftime('%d/%m/%y')
        diaDaSemana = hoje.weekday()

        FIM = datetime.date(2022, 12, 21)
        diasParaFim = (FIM-hoje).days

        if diasParaFim == 0:
            embedProvas = discord.Embed(
            title=f'**{self.diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para as próximas {sem} semana(s)\nACABO RAPAZIADA, É ISSO. ATÉ AGOSTO!', color=0x336EFF)
        else:
            embedProvas = discord.Embed(
            title=f'**{self.diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para as próximas {sem} semana(s)\nFaltam {diasParaFim} dias para o fim do semestre.', color=0x336EFF)

        provasParaPeriodo = []
        for materia in provas:
            for provaIndividual in provas[materia]:
                dataProvaRaw = provaIndividual['data']
                dataProva = datetime.date.fromisoformat(dataProvaRaw)
                
                if(dataProva-hoje).days <= (7 * sem) and (dataProva-hoje).days >= 0:
                    provasParaPeriodo.append({'nome': provaIndividual['nome'],
                                            'diasParaProva': (datetime.date.fromisoformat(provaIndividual['data'])-hoje).days,
                                            'materia': materia,
                                            'data': dataProva
                                            })
                    

        provasParaPeriodo = sorted(provasParaPeriodo, key=lambda prova: prova['diasParaProva'])

        
        if provasParaPeriodo[0]['diasParaProva'] == 0:
            embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
            embedProvas.color = 0xFF0000
        elif provasParaPeriodo[0]['diasParaProva'] == 1:
            embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
            embedProvas.color = 0xFFFF00
        else:
            embedProvas.set_image(url='https://i.imgur.com/zkGm9j2.jpg')

        # aumentar tamanho horizontal
        # footer = "\u2800" * 100
        # footer = footer + "|"
        # print(footer)
        # embedProvas.set_footer(text=footer)

        return embedProvas, provasParaPeriodo


    @commands.command(description='Mostra provas e trabalhos para as próximas semanas, por padrão 2 semanas, mas pode ser mudado pelo argumento, Ex: "!provas 4"',
                      brief='Provas para as próximas semanas')
    async def provas(self, ctx, semanas = 2):

        async with ctx.channel.typing():

            embedProvas, provasParaPeriodo = await self.criaEmbedProvas(semanas)

            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                    await ctx.message.delete()

            for prova in provasParaPeriodo:
                dataProva = prova['data']
                dia = dataProva.strftime('%d/%m/%y')
                diaDaSemana = self.diaSemana(dataProva.weekday())
                # aqui (1)
                if prova['diasParaProva'] == 0:
                    embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                        value=f'__->**É HOJE FIOTE** **{prova["nome"].upper()}** DE **{prova["materia"].upper()}**, {diaDaSemana}, {dia}__', inline=False)
                elif prova['diasParaProva'] == 1:
                    embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                        value=f'->**{prova["nome"]}** de **{prova["materia"]}**, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dia**', inline=False)
                else:
                    embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                        value=f'->**{prova["nome"]}** de **{prova["materia"]}**, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dias**', inline=False)


            # mensagemJunto = await ctx.channel.send(f'{ctx.author.mention}')
            mensagemEmbed = await ctx.channel.send(content=f'{ctx.author.mention}', embed=embedProvas)
            #await write_json(arquivoEmbeds, (mensagemEmbed.id, ctx.channel.id))
            await dbExecute(f'INSERT INTO {tableMensagens}(id_canal, id_mens) VALUES({ctx.channel.id},{mensagemEmbed.id})')

            await mensagemEmbed.delete(delay=60)
            # delete_item(arquivoEmbeds, (mensagemEmbed.id, ctx.channel.id))

    @commands.command(name='adiciona')
    @permissao()
    async def adicionaAvisos(self, ctx, canal : discord.TextChannel = -1):
        if canal == -1:
            canal = ctx.channel
        
        jaAdicionado = await dbReturn(f'SELECT id_canal FROM {tableAvisos} WHERE id_canal = "{canal.id}"')

        if not jaAdicionado:

            await dbExecute(f'''INSERT INTO {tableAvisos}(id_canal,id_mens) 
                            SELECT {canal.id}, 0
                            WHERE NOT EXISTS(SELECT 1 FROM {tableAvisos} WHERE id_canal = {canal.id});
                            ''')
            horario = await dbReturn(f'SELECT tempo_envio FROM {tableAvisos} WHERE id_canal = {canal.id}')
            await ctx.send(f'Canal {canal} adicionado aos avisos automáticos, horário padrão: {horario[0][0]}')
        else:
            await ctx.send(f'O canal {canal} já foi adicionado')

    @commands.command(name='remove')
    @permissao()
    async def removeAvisos(self, ctx, canal : discord.TextChannel = -1):
        if canal == -1:
            canal = ctx.channel

        # if canal.permissions_for(ctx.guild.me).manage_messages:
        #     await ctx.message.delete()

        mensagem = await dbReturn(f'SELECT * FROM {tableAvisos} WHERE id_canal = {canal.id}')
        if mensagem:
            if mensagem[0][1] != 0:
                try:
                    msg = await canal.fetch_message(mensagem[0][1])
                    await msg.delete()
                    # await self.delete_item(arquivoEmbedsAuto, mensagem)
                except discord.errors.NotFound:
                    print(f'Deletada uma mensagem automática desaparecida em {canal.guild}/{canal} do arquivo')
                else:
                    print(f'Deletada uma mensagem automática em {canal.guild}/{canal}')
                finally:
                    await dbExecute(f'UPDATE {tableAvisos} SET id_mens = 0 WHERE id_mens = {mensagem[0][1]}')
        
            await dbExecute(f'DELETE FROM {tableAvisos} WHERE id_canal = {canal.id};')
            await ctx.send(f'Canal {canal} removido dos avisos automáticos')
        else:
            await ctx.send(f'Canal **{canal}** não está adicionado aos avisos automáticos')

    
    @commands.command(name='horario')
    async def showHorario(self, ctx):
        canal = ctx.channel

        # if canal.permissions_for(ctx.guild.me).manage_messages:
        #             await ctx.message.delete()

        jaAdicionado = await dbReturn(f'SELECT id_canal FROM {tableAvisos} WHERE id_canal = {canal.id}')

        if jaAdicionado:
            horario = await dbReturn(f'SELECT tempo_envio FROM {tableAvisos} WHERE id_canal = {canal.id}')

            mensagem = await ctx.send(f'O horário configurado é `{horario[0][0]}` para **{canal}**')
            await mensagem.delete(delay=60)
        else:
            await ctx.send(f'Canal **{canal}** não adicionado para avisos automáticos')

    @commands.command(name='sethorario')
    #@commands.has_permissions(administrator=True)
    # criar check próprio para verificar roles ou adms.
    # guardar isso em db
    # @commands.has_role(958866992432050246)
    @permissao()
    async def updateHorario(self, ctx, horario, canal : discord.TextChannel = -1):
        if canal == -1:
            canal = ctx.channel

        # não pegar canal por argumento, usar ctx.channel
        # gerenciar permissões com roles, apenas adms e tal
        # talvez permitir apenas um canal de avisos por guilda
        # !horario para verificar e !setHorario para mudar

        # if canal.permissions_for(ctx.guild.me).manage_messages:
        #             await ctx.message.delete()

        jaAdicionado = await dbReturn(f'SELECT id_canal FROM {tableAvisos} WHERE id_canal = "{canal.id}"')

        if jaAdicionado:

            try:
                horarioFormatado = datetime.time.fromisoformat(horario)
            except ValueError:
                await ctx.send('Horário inválido')
                return

            await dbExecute(f'''UPDATE {tableAvisos} SET tempo_envio = '{horarioFormatado}' WHERE id_canal = {canal.id};
                            ''')
            horarioFormatadoStr = datetime.time.isoformat(horarioFormatado, timespec='auto')
            mensagem = await ctx.send(f'Horário setado para {horarioFormatadoStr} para avisos automáticos em **{canal}**')
            await mensagem.delete(delay=60)
        else:
            await ctx.send(f'Canal **{canal}** não adicionado para avisos automáticos')

    @commands.command(name='addrole')
    @adm()
    async def addRole(self, ctx, *, role : discord.role.Role):
        guilda = ctx.guild
        
        if not role:
            await ctx.send('Role inválida')
            return

        jaAdicionado = await dbReturn(f'SELECT id_role FROM {tablePermissoes} WHERE id_role = "{role.id}"')

        if not jaAdicionado:

            await dbExecute(f'''INSERT INTO {tablePermissoes}(id_guilda,id_role) 
                            SELECT {guilda.id}, {role.id}
                            WHERE NOT EXISTS(SELECT 1 FROM {tablePermissoes} WHERE id_guilda = {guilda.id});
                            ''')
            await ctx.send(f'Role {role} adicionada')
        else:
            await ctx.send(f'A role **{role}** já foi adicionada')

    @commands.command(name='remrole')
    @adm()
    async def remRole(self, ctx, *, role : discord.role.Role):
        
        if not role:
            await ctx.send('Role inválida')
            return

        jaAdicionado = await dbReturn(f'SELECT id_role FROM {tablePermissoes} WHERE id_role = "{role.id}"')

        if jaAdicionado:

            await dbExecute(f'DELETE FROM {tablePermissoes} WHERE id_role = {role.id};')
            await ctx.send(f'Role {role} removida')
        else:
            await ctx.send(f'A role **{role}** não foi adicionada')

    # @commands.command()
    # async def tipo(self, ctx, coisa : discord.role.Role):
        
    #     #role = ctx.guild.get_role()
    #     await ctx.send(type(coisa))

    # @remRole.error
    # async def remroleHandler(self, ctx, error):
    #     if isinstance(error, commands.CheckFailure):
    #         await ctx.send('Você não tem permissão')
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send('Digite uma role')
    #     if isinstance(error, commands.RoleNotFound):
    #         await ctx.send('Role não encontrada')

    @remRole.error
    @addRole.error
    async def roleHandler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            # await ctx.send('Você não tem permissão')
            Embed = discord.Embed(color=0x336EFF)
            Embed.set_image(url='https://i.imgur.com/C7webPo.png')
            await ctx.send(embed=Embed)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Digite uma role')
        if isinstance(error, commands.RoleNotFound):
            await ctx.send('Role não encontrada')
        # else:
        #     print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        #     traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @adicionaAvisos.error
    @removeAvisos.error
    async def avisosHandler(self, ctx, error):
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send('Canal não encontrado')

    @updateHorario.error
    async def updateHorarioHandler(self, ctx, error):
        if isinstance(error, (commands.MissingPermissions, commands.MissingRole, commands.CheckFailure)):
            await ctx.send('Você não tem permissão')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Digite um horário')
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send('Canal não encontrado')

    @commands.command(name='showall')
    @eu()
    async def showAll(self, ctx):
        mensagens = await returnTable(tableAvisos) 
        for mensagem in mensagens:
            canal = self.bot.get_channel(mensagem[0])
            # usar try catch para notificar ou excluir canais que não vejo (None)
            if canal is not None:
                await ctx.send(f'{canal.guild}/{canal} às {mensagem[2]}')

    @commands.command(name='reseta')
    @adm()
    # @commands.cooldown(1, 15, commands.BucketType.user)
    async def reseta(self, ctx, canalProvas : discord.TextChannel = -1):
            if canalProvas == -1:
                canalProvas = ctx.channel

            mensagem = await dbReturn(f'SELECT id_mens FROM {tableAvisos} WHERE id_canal = "{canalProvas.id}"')
            if not mensagem:
                await ctx.send(f'Canal **{canalProvas}** não adicionado para avisos automáticos')
                return
            if mensagem[0][0] != 0:
                try:
                    msg = await canalProvas.fetch_message(mensagem[0][0])
                    await msg.delete()
                except discord.errors.NotFound:
                    print(f'Deletada uma mensagem automática desaparecida em {canalProvas.guild}/{canalProvas} do arquivo')
                else:
                    print(f'Deletada uma mensagem automática em {canalProvas.guild}/{canalProvas}')
                finally:
                    await dbExecute(f'UPDATE {tableAvisos} SET id_mens = 0 WHERE id_mens = {mensagem[0][0]}')

            sem = 2 # quantidade de semanas para verificar
            print(f'Enviando provas task manual para {canalProvas}|{canalProvas.guild} por {ctx.author}')

            async with canalProvas.typing():
                embedProvas, provasParaPeriodo = await self.criaEmbedProvas(sem)

                for prova in provasParaPeriodo:
                    dataProva = prova['data']
                    dia = dataProva.strftime('%d/%m/%y')
                    diaDaSemana = self.diaSemana(dataProva.weekday())
                    if prova['diasParaProva'] == 0:
                        embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                                value=f'__->**É HOJE RAPAZIADA** **{prova["nome"].upper()}** DE **{prova["materia"].upper()}**, {diaDaSemana}, {dia}__', inline=False)
                    elif prova['diasParaProva'] == 1:
                        embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                                value=f'->**{prova["nome"]}** de **{prova["materia"]}**, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dia**', inline=False)
                    else:
                        embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                                value=f'->**{prova["nome"]}** de **{prova["materia"]}**, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dias**', inline=False)

            mensagemEmbed = await canalProvas.send(content='@everyone', embed=embedProvas)

            await dbExecute(f'UPDATE {tableAvisos} SET id_mens = {mensagemEmbed.id} WHERE id_canal = {canalProvas.id}')


    @reseta.error
    async def resetaHandler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply('Calma aí, você só pode usar esse comando a cada 15 segundos!')
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply('Você não tem permissão para executar esse comando')
        elif isinstance(error,commands.ChannelNotFound):
            await ctx.reply('Não encontrei esse canal')
        # else:
        #     print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        #     traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @tasks.loop(minutes=1) # verifica a cada 1 minuto
    async def aviso_provas(self):
        mensagens = await returnTable(tableAvisos)
        for mensagem in mensagens:
            canalProvas = self.bot.get_channel(mensagem[0])

            if canalProvas is None:
                continue

            agora = datetime.datetime.now().time().replace(microsecond=0)
            tempo_setado = datetime.time.fromisoformat(mensagem[2])
            
            diferenca = datetime.datetime.combine(datetime.date.min, agora) - datetime.datetime.combine(datetime.date.min, tempo_setado)
            t1 = datetime.timedelta(minutes=1)
            t2 = datetime.timedelta(seconds=0)

            if(diferenca >= t2 and diferenca < t1):
                if mensagem[1] != 0:
                    try:
                        msg = await canalProvas.fetch_message(mensagem[1])
                        await msg.delete()
                    except discord.errors.NotFound:
                        print(f'Deletada uma mensagem automática desaparecida em {canalProvas.guild}/{canalProvas} do arquivo')
                    else:
                        print(f'Deletada uma mensagem automática em {canalProvas.guild}/{canalProvas}')
                    finally:
                        await dbExecute(f'UPDATE {tableAvisos} SET id_mens = 0 WHERE id_mens = {mensagem[1]}')

                sem = 2 # quantidade de semanas para verificar
                print(f'Enviando provas task para {canalProvas}|{canalProvas.guild}')

                async with canalProvas.typing():
                    embedProvas, provasParaPeriodo = await self.criaEmbedProvas(sem)

                    for prova in provasParaPeriodo:
                        dataProva = prova['data']
                        dia = dataProva.strftime('%d/%m/%y')
                        diaDaSemana = self.diaSemana(dataProva.weekday())
                        if prova['diasParaProva'] == 0:
                            embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                                    value=f'__->**É HOJE RAPAZIADA** **{prova["nome"].upper()}** DE **{prova["materia"].upper()}**, {diaDaSemana}, {dia}__', inline=False)
                        elif prova['diasParaProva'] == 1:
                            embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                                    value=f'->**{prova["nome"]}** de **{prova["materia"]}**, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dia**', inline=False)
                        else:
                            embedProvas.add_field(name=f'•**{prova["materia"]}**',
                                                    value=f'->**{prova["nome"]}** de **{prova["materia"]}**, {diaDaSemana}, {dia} em **{prova["diasParaProva"]} dias**', inline=False)

                mensagemEmbed = await canalProvas.send(content='@everyone', embed=embedProvas)

                await dbExecute(f'UPDATE {tableAvisos} SET id_mens = {mensagemEmbed.id} WHERE id_canal = {canalProvas.id}')


def setup(bot):
    bot.add_cog(Provas(bot))
