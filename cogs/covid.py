import discord
import asyncio
import random
from discord.ext import commands
import datetime
import math
import COVID19Py


class covid(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['corona', 'coronavirus', 'covid'])
    async def covid19(self, ctx):
        covid19 = COVID19Py.COVID19()
        latest = covid19.getLatest()
        await ctx.send(f"Total confirmed cases: {latest['confirmed']:,}\ntotal deaths: {latest['deaths']:,}")

def setup(client):
    client.add_cog(covid(client))