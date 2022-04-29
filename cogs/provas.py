from discord.ext import commands
import datetime
import json
import discord


class Provas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    def diaSemana(self, wDia):
        dias = {0: 'Segunda-feira', 1 : 'Terça-feira', 2 : 'Quarta-feira', 3 : 'Quinta-feira', 4 : 'Sexta-feira', 5 : 'Sábado', 6 : 'Domingo'}
        return dias[wDia]

    async def criaEmbedProvas(self, channel, sem):
        async with channel.typing():
            with open('provasTeste.json', encoding='utf-8') as prov:
                provas = json.load(prov)
            
            hoje = datetime.date.today()
            hojeString = datetime.date.today().strftime('%d/%m/%y')
            diaDaSemana = hoje.weekday()

            embedProvas = discord.Embed(
            title=f'**{self.diaSemana(diaDaSemana)}, {hojeString}**', description=f'Provas para as próximas {sem} semana(s)', color=0x336EFF)

            provasParaPeriodo = []
            # for attribute in provas:

            #         dataProvaRaw = provas[attribute]
            #         dataProva = datetime.date.fromisoformat(dataProvaRaw)
                    
            #         if(dataProva-hoje).days <= (7 * sem) and (dataProva-hoje).days >= 0:
            #             provasParaPeriodo.append((attribute, (datetime.date.fromisoformat(provas[attribute])-hoje).days))


            for materia in provas:
                for provaIndividual in provas[materia]:
                    dataProvaRaw = provaIndividual['data']
                    dataProva = datetime.date.fromisoformat(dataProvaRaw)
                    
                    if(dataProva-hoje).days <= (7 * sem) and (dataProva-hoje).days >= 0:
                        provasParaPeriodo.append((provaIndividual['nome'], (datetime.date.fromisoformat(provaIndividual['data'])-hoje).days, materia, provaIndividual['tipo']))
                        

            provasParaPeriodo = sorted(provasParaPeriodo, key=lambda attribute: attribute[1])

            
            if provasParaPeriodo[0][1] == 0:
                embedProvas.set_image(url='https://i.imgur.com/kaAhqqC.gif')
                embedProvas.color = 0xFF0000
            elif provasParaPeriodo[0][1] == 1:
                embedProvas.set_image(url='https://i.imgur.com/AQhq1Mo.png')
                embedProvas.color = 0xFFFF00
            else:
                embedProvas.set_image(url='https://i.imgur.com/7nqUbE9.gif')

        return embedProvas, provasParaPeriodo

    @commands.command(description='Mostra provas e trabalhos para as próximas semanas, por padrão 2 semanas, mas pode ser mudado pelo argumento, Ex: "!provas 4"',
                      brief='Provas para as próximas semanas')
    async def provas(self, ctx, semanas = 2):

        embedProvas, provasParaPeriodo = await self.criaEmbedProvas(ctx.channel, semanas)

        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()


        for attribute in provasParaPeriodo:
            with open('provas.json', encoding='utf-8') as prov:
                dataProvaRaw = json.load(prov)[attribute[0]]
            hoje = datetime.date.today()
            dataProva = datetime.date.fromisoformat(dataProvaRaw)
            dia = dataProva.strftime('%d/%m/%y')
            diaDaSemana = self.diaSemana(dataProva.weekday())
            if attribute[1] == 0:
                embedProvas.add_field(name=f'•{attribute[0]}', value=f'__->**É HOJE FIOTE** PROVA DE {attribute[0]}, {diaDaSemana}, {dia}__', inline=False)
            elif attribute[1] == 1:
                embedProvas.add_field(name=f'•{attribute[0]}', value=f'->Prova de {attribute[0]}, {diaDaSemana}, {dia} em **{(dataProva-hoje).days} dia**', inline=False)
            else:
                embedProvas.add_field(name=f'•{attribute[0]}', value=f'->Prova de {attribute[0]}, {diaDaSemana}, {dia} em **{(dataProva-hoje).days} dias**', inline=False)


        mensagemJunto = await ctx.channel.send(f'{ctx.author.mention}')
        mensagemEmbed = await ctx.channel.send(embed=embedProvas)

        await mensagemJunto.delete(delay=60)
        await mensagemEmbed.delete(delay=60)


def setup(bot):
    bot.add_cog(Provas(bot))