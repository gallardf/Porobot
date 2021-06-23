import asyncio
import os
import numpy as np
from discord.ext import commands
from random import randint

bot = commands.Bot(command_prefix='.')

porolist = dict()
inventaires = dict()
cooldowns = dict()
cd = dict()
player = dict()
tout = dict()

PS = {'casse dalle': [1, 1], 'porosnax lidl': [2, 5], 'porosnax': [3, 15], 'porosnax dopant': [4, 25],
      'porosnax rassasiant': [5, 50], 'porosnax deluxe': [6, 200]}

if os.path.exists('C:/Users/Max/PycharmProjects/Porobot/sauvegarde.npy'):
    tout = np.load('sauvegarde.npy', allow_pickle=True).item()
    print(tout)
    porolist = tout['porolist']
    inventaires = tout['inventaires']
    cooldowns = tout['cooldowns']
    player = tout['player']
    cd = tout['cd']

else:
    porolist = dict()
    inventaires = dict()
    cooldowns = dict()
    cd = dict()
    player = dict()
    tout = {'porolist': porolist, 'inventaires': inventaires, 'cooldowns': cooldowns, 'cd': cd, 'player': player}
    np.save('sauvegarde.npy', tout)


@bot.command()
async def save(porolist, inventaires, cooldowns, cd):
    global tout
    tout = {'porolist': porolist, 'inventaires': inventaires, 'cooldowns': cooldowns, 'cd': cd, 'player': player}
    np.save('sauvegarde.npy', tout)


@bot.command()
async def level():
    for serv in porolist:
        if porolist[serv][1] >= porolist[serv][2]:
            porolist[serv][0] += 1
            porolist[serv][1] = porolist[serv][1] - porolist[serv][2]
            porolist[serv][2] = int(((porolist[serv][0]) ** 1.25) * 100)
            channel = bot.get_channel(porolist[serv][3])
            await channel.send('***Bravo votre Poro vient de passer niveau ' + str(porolist[serv][0]) + '!***')
            await channel.send(
                '***Il lui faut maintenant ' + str(porolist[serv][2]) + ' points de bouffe pour level up!***')


# Réparation de fichier cooldown#####
# for serv in cooldowns:
#    for id in cooldowns[serv]:
#        cooldowns[serv][id] = True
# save(porolist, inventaires, cooldowns, cd)


@bot.command()
async def cdreset():
    for serv in porolist:
        if cd[serv] != cooldowns[serv]:
            channel = bot.get_channel(porolist[serv][3])
            await channel.send('Vous pouvez .coffret de nouveau')
            cd[serv] = dict(cooldowns[serv])


@bot.event
async def on_ready():
    global cpt
    cpt = 1799
    while True:
        await level()
        await save(porolist, inventaires, cooldowns, cd)
        await asyncio.sleep(1)
        cpt += 1
        if cpt == 1800:
            await cdreset()
            cpt = 1


@bot.command()
async def aide(ctx):
    await ctx.send('*Liste des commandes (et alias):*'
                   '\n.start pour faire naître le poro (a faire dans le channel consacré a ce bot)  '
                   '\n.inventaire (.i) a faire au début pour créer son inventaire et le regarder '
                   '\n.coffret (.c) pour avoir une chance de drop des porosnax appétissants (30min cd)'
                   '\n.feed *ID* (.f *ID*) pour donner a manger au poro '
                   '\n.poro pour check le profile du Poro')


@bot.command()
async def start(ctx):
    serv = ctx.guild.id
    channel = ctx.message.channel.id
    if serv in porolist:
        await ctx.send('Le Poro est déjà présent dans ce monde')

    else:
        porolist[serv] = [1, 0, 100, channel]  # Level/Bouffe/Bouffe Max/Main channel du serv
        inventaires[serv] = {'kaki': 9999999}
        cooldowns[serv] = {'kaki': 9999999}
        global cd
        cd[serv] = {'kaki': 9999999}
        await ctx.send('Le Poro vient de naître')


@bot.command()
async def i(ctx):
    persid = ctx.message.author.id
    serv = ctx.guild.id
    if persid in inventaires[serv]:
        msg = ''
        for i in inventaires[serv][persid]:
            if inventaires[serv][persid][i] > 0:
                msg += '\n' + str(PS[i][0]) + ': ' + str(i) + ': ' + str(inventaires[serv][persid][i])

        if msg == '':
            msg = 'Ton inventaire contient:\nRIEN'

        else:
            msg = 'Ton inventaire contient:' + msg

        await ctx.send(msg)

    else:
        inventaires[serv][persid] = {'casse dalle': 0, 'porosnax lidl': 0, 'porosnax': 0,
                                     'porosnax dopant': 0, 'porosnax rassasiant': 0, 'porosnax deluxe': 0}
        player[persid] = ctx.message.author.name
        await ctx.send('Ton inventaire a été créé')
        cooldowns[serv][persid] = True
        cd[serv][persid] = True


@bot.command()
async def coffret(ctx):
    persid = ctx.message.author.id
    serv = ctx.guild.id
    try:
        if cd[serv][persid]:
            cd[serv][persid] = False
            inv = inventaires[serv][persid]
            r = randint(1, 1000)
            if r <= 590:  # 59%
                inv['porosnax lidl'] += 1
                await ctx.send("Tu as gagné un porosnax lidl, coup dur frère")

            elif r <= 790:  # 20%
                inv['porosnax'] += 1
                await ctx.send("Tu as gagné un porosnax, tout de plus normal")

            elif r <= 939:  # 14.9%
                inv['casse dalle'] += 1
                await ctx.send("Un casse dalle, Pour une (toute) petite faim")

            elif r <= 989:  # 5%
                inv['porosnax dopant'] += 1
                await ctx.send("Tu as gagné un porosnax dopant, son FOV va augmenter!")

            elif r <= 999:  # 1%
                inv['porosnax rassasiant'] += 1
                await ctx.send("Tu as gagné un porosnax rassasiant, il va bien se Khalass")

            elif r <= 1000:  # 0.1%
                inv['porosnax deluxe'] += 1
                await ctx.send("Tu as gagné un porosnax Delux, LA CHATTE LA CHATTE LA CHATTE QU'IL A")
        else:
            await ctx.send('Reviens dans ' + str(cpt // 60) + 'min')
    except:
        await ctx.send('Fait .i et re-essaies si ca ne fonctionne toujours pas ping Moumix')


@bot.command()
async def c(ctx):
    persid = ctx.message.author.id
    serv = ctx.guild.id
    try:
        if cd[serv][persid]:
            cd[serv][persid] = False
            inv = inventaires[serv][persid]
            r = randint(1, 1000)
            if r <= 590:  # 59%
                inv['porosnax lidl'] += 1
                await ctx.send("Tu as gagné un porosnax lidl, coup dur frère")

            elif r <= 790:  # 20%
                inv['porosnax'] += 1
                await ctx.send("Tu as gagné un porosnax, tout de plus normal")

            elif r <= 939:  # 14.9%
                inv['casse dalle'] += 1
                await ctx.send("Un casse dalle, Pour une (toute) petite faim")

            elif r <= 989:  # 5%
                inv['porosnax dopant'] += 1
                await ctx.send("Tu as gagné un porosnax dopant, son FOV va augmenter!")

            elif r <= 999:  # 1%
                inv['porosnax rassasiant'] += 1
                await ctx.send("Tu as gagné un porosnax rassasiant, il va bien se Khalass")

            elif r <= 1000:  # 0.1%
                inv['porosnax deluxe'] += 1
                await ctx.send("Tu as gagné un porosnax Delux, LA CHATTE LA CHATTE LA CHATTE QU'IL A")
        else:
            await ctx.send('Reviens dans ' + str((1800 - cpt) // 60) + ' min')

    except:
        await ctx.send('Fait .i et re-essaies si ca ne fonctionne toujours pas ping Moumix')


@bot.command()
async def cds(ctx):
    serv = ctx.guild.id
    if ctx.message.author.id == 161126402861694976:
        msg = ''
        for name in cooldowns[serv]:
            if type(name) == int:
                msg += str(player[name]) + ': ' + str(cd[serv][name]) + '\n'
        await ctx.send(msg)


@bot.command()
async def feed(ctx):
    serv = ctx.guild.id
    poro = porolist[serv]
    persid = ctx.message.author.id
    inv = inventaires[serv][persid]
    arg = ctx.message.content[6:]
    ps = ''

    if arg == '':
        await ctx.send("Veuillez rentrer l'ID du porosnax a donner au Poro")

    else:
        arg = int(arg)
        for k in PS:
            if PS[k][0] == arg:
                ps = k
        if arg in [1, 2, 3, 4, 5, 6] and inv[ps] > 0:
            poro[1] += PS[ps][1]
            inv[ps] -= 1
            await ctx.send("Le poro s'est bien Khalass")
        elif arg not in [1, 2, 3, 4, 5, 6]:
            await ctx.send("ID de porosnax non valable")
        elif inv[ps] == 0:
            await ctx.send("Tu n'as aucun porosnax de ce type")


@bot.command()
async def f(ctx):
    serv = ctx.guild.id
    poro = porolist[serv]
    persid = ctx.message.author.id
    inv = inventaires[serv][persid]
    arg = ctx.message.content[3:]
    ps = ''

    if arg == '':
        await ctx.send("Veuillez rentrer l'ID du porosnax a donner au Poro")

    else:
        arg = int(arg)
        for k in PS:
            if PS[k][0] == arg:
                ps = k
        if arg in [1, 2, 3, 4, 5, 6] and inv[ps] > 0:
            poro[1] += PS[ps][1]
            inv[ps] -= 1
            await ctx.send("Le poro s'est bien Khalass")
        elif arg not in [1, 2, 3, 4, 5, 6]:
            await ctx.send("ID de porosnax non valable")
        elif inv[ps] == 0:
            await ctx.send("Tu n'as aucun porosnax de ce type")


@bot.command()
async def poro(ctx):
    serv = ctx.guild.id
    poro = porolist[serv]
    msg = 'Le poro est level ' + str(poro[0]) + '\nIl a ' + str(
        poro[1]) + '/' + str(poro[2]) + ' points de bouffe'
    await ctx.send(msg)


@bot.command()
async def flo(ctx):
    await ctx.send('Le Roi des Beew')


@bot.command()
async def aytox(ctx):
    await ctx.send('https://lolpros.gg/player/aytox')


@bot.command()
async def kaki(ctx):
    await ctx.send('la légende')


@bot.command()
async def arno(ctx):
    await ctx.send('veut une HK bien fraiche')


@bot.command()
async def nebs(ctx):
    await ctx.send('le roi des weebs')


@bot.command()
async def erwan(ctx):
    await ctx.send('hardstuck platine')


@bot.command()
async def moumix(ctx):
    await ctx.send('cringe ARAM player')


@bot.command()
async def amine(ctx):
    await ctx.send('le raciste/homophobe')


@bot.command()
async def merguezls(ctx):
    await ctx.send('Marseillais n°2')


@bot.command()
async def croaa(ctx):
    await ctx.send('Stop spam fdp')


@bot.command()
async def derasiel(ctx):
    await ctx.send('le plus beau de tout les trap')


bot.run('ODU1OTE1NTE4MTE1NTc3ODc2.YM5bcQ.EUjFXFcRfud4vB8nRnjq1dtmeLA')
