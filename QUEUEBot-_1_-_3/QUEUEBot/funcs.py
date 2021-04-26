import discord
from discord.ext import commands
from config import settings
import datetime
import asyncio

def toTime(time):
    return(f"{time // 60}:{time - (time // 60) * 60}")

def fromTime(time):
    try:
        st = list(map(int, time.split(':')))
        if len(st) != 2:
           raise ValueError()
    except:
        return None
    return st[0] * 60 + st[1]

def fromDate(date):
	try:
		st = list(map(int, date.split('.')))
		if len(st) != 2:
			raise ValueError()
	except:
		return None
	return st
