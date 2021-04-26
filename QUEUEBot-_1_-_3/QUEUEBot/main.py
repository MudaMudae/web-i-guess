import discord
from discord.ext import commands
from config import settings
import datetime
import asyncio
from funcs import *

bot = commands.Bot(command_prefix=settings['prefix'])
q = [[[] for i in range(3)] for i in range(
    7)]  # очередь хранится в формате {time, +- 1, man, polise}, где -1 - начало приёма, 1 - конец приёма, man - человек, записавшийся в очередь и polise - номер полиса
doctors = ['Стоматолог', 'Терапевт', 'Морг']
t = []
time_to_work = [('7:30', '19:00'),
                ('7:30', '19:00'),
                ('7:30', '19:00'),
                ('7:30', '19:00'),
                ('7:30', '19:00'),
                ('9:00', '15:00'),
                ('9:00', '15:00')]


@bot.command()
async def showQ(ctx):
    await ctx.send(str(q))


@bot.command()
async def add(ctx, s, f, day, doc, polise):
    author = ctx.message.author
    try:
        day = datetime.date(datetime.datetime.now().year, *fromDate(day)[::-1])
    except:
        await ctx.send(f'Неверный формат даты')
        return

    dtime = (day - datetime.datetime.now().date()).days
    if not (0 <= dtime <= 6):
        await ctx.send(f'Неверная дата')
        return

    if doc not in doctors:
        await ctx.send(f"Запись к этому доктору пока не поддерживается")
        return

    docI = doctors.index(doc)
    global q

    for i in q[dtime][docI]:
        if author == i[2]:
            await ctx.send(f"Вы уже записаны в поликлинику")
            return

    start, finish = fromTime(s), fromTime(f)
    if not start or not finish:
        await ctx.send(f'Неверный формат времени')
        return

    if finish - start < 5:
        await ctx.send(f'Невозможно занять очередь меньше, чем на 5 минут')
        return

    if finish - start > 25:
        await ctx.send(f"Невозможно занять очередь больше, чем на 25 миинут")
        return

    for i in range(len(q[dtime][docI])):
        if q[dtime][docI][i][0] > start:
            if q[dtime][docI][i][0] < finish:
                await ctx.send(f'Невозможно занять очередь на уже занятом времени')
                return
            else:
                break

    q[dtime][docI].append((start, -1, author, polise))
    q[dtime][docI].append((finish, 1, author, polise))
    q[dtime][docI] = sorted(q[dtime][docI], key=lambda x: x[0])
    await ctx.send(f'Вы зарегистрировались в поликлинику')


@bot.command()
async def getTime(ctx, doc):
    global q

    if doc not in doctors:
        await ctx.send(f"Запись к этому доктору пока не поддерживается")
        return

    docI = doctors.index(doc)
    for i in range(7):
        tmp = q[i][docI]
        tmp = [[fromTime(time_to_work[i][0]), 1]] + tmp + [[fromTime(time_to_work[i][1]), -1]]
        for k in range(len(tmp) - 1):
            if tmp[k][1] == 1 and tmp[k + 1][0] - tmp[k][0] != 0:
                s, f = toTime(tmp[k][0]), toTime(tmp[k + 1][0])
                await ctx.send(f"{(datetime.date.today() + datetime.timedelta(days=i)).strftime('%d.%m')} {s}-{f}")


@bot.command()
async def delQ(ctx, doc):
    author = ctx.message.author
    global q

    if doc not in doctors:
        await ctx.send(f"Запись к этому доктору пока не поддерживается")
        return

    docI = doctors.index(doc)

    for i in range(7):
        for k in range(len(q[i][docI]) - 1):
            if author == q[i][docI][k][2]:
                q[i][docI].pop(k + 1)
                q[i][docI].pop(k)

    await ctx.send(f"Вы успешно были удалены из очереди")


@bot.command()
async def time(ctx):
    author = ctx.message.author
    global q

    for i in range(7):
        for j in range(3):
            for k in range(len(q[i][j]) - 1):
                if author == q[i][j][k][2]:
                    await ctx.send(
                        f"Вы записаны {(datetime.date.today() + datetime.timedelta(days=i)).strftime('%d.%m')} к {doctors[j]} на {toTime(q[i][j][k][0])}-{toTime(q[i][j][k + 1][0])}")
                    break


@bot.command()
async def F(ctx):
    exit(0)


@bot.command()
async def Work(ctx):
    # t2 = []
    # for i in range(len(doctors)):
    #     t2.append(asyncio.create_task(Doc(i, ctx)))
    #     await t2[i]
    # for i in range(len(doctors)):
    #      t.append(open('text.txt', 'r'))
    global q
    while 1:
        tmp = fromTime(datetime.datetime.now().strftime("%H:%M")) * 60 + datetime.datetime.now().second
        if 86395 <= tmp <= 5:
            q.pop(0)
            q.append([[] for i in range(3)])
        await asyncio.sleep(5)


@bot.command()
async def Doc(ctx, j):
    global q
    j = int(j)
    await ctx.send(f'{doctors[j]} работает!')
    while 1:
        while len(q[0][j]) == 0:
            await asyncio.sleep(5)
        tmp = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
        await ctx.send(f"Следующий в очереди к {doctors[j]}:{q[0][j][0][2].mention}!")
        tmp2 = q[0][j][0][2]
        while ((q[0][j][1][0] - tmp) * 60) != 0:
            await asyncio.sleep(10)
        if q[0][j][0][2] == tmp2:
            q[0][j].pop(1)
            q[0][j].pop(0)
            await ctx.send(f"Очередь к {doctors[j]} продвинулась")


@bot.command()
async def kill_patient(ctx, j):
    global q
    j = int(j)
    if j >= len(doctors):
        await ctx.send(f"Такого докутах нет!")
        return
    if len(q[0][j]) == 0:
        await ctx.send(f"Очередь пуста")
        return

    q[0][j].pop(1)
    q[0][j].pop(0)
    await ctx.send(f"Очередь к {doctors[j]} продвинулась")


@bot.command()
async def move_all(ctx, j):
    global q
    j = int(j)
    if j >= len(doctors):
        await ctx.send(f"Такого докутах нет!")
        return
    if len(q[0][j]) == 0:
        await ctx.send(f"Очередь пуста")
        return

    tmp = q[0][j][0][0] - (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
    for i in range(len(q[0][j])):
        q[0][j][i] = (q[0][j][i][0] - tmp, q[0][j][i][1], q[0][j][i][2], q[0][j][i][3])

    await ctx.send(f"Очередь сдвинута на {tmp} минут!")


@bot.command()
async def move_by_n(ctx, j, tmp):
    global q
    j = int(j)
    tmp = int(tmp)
    if j >= len(doctors):
        await ctx.send(f"Такого докутах нет!")
        return
    if len(q[0][j]) == 0:
        await ctx.send(f"Очередь пуста")
        return

    for i in range(len(q[0][j])):
        q[0][j][i] = (q[0][j][i][0] + tmp, q[0][j][i][1], q[0][j][i][2], q[0][j][i][3])

    await ctx.send(f"Очередь сдвинута на {tmp} минут!")


@bot.command()
async def advice(ctx, j):
    await ctx.send(f"Рекомендованное время посещения - 13 минут!")


bot.run(settings['token'])