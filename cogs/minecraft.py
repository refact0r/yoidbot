import discord
import asyncio
import random
from discord.ext import commands
import requests
import datetime
import math
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()

class minecraft(commands.Cog):

    def __init__(self, client):
        self.client = client

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    @commands.command(aliases = ['bucket', 'bc', 'bcv'])
    @is_in_guild(710654601304473610)
    async def bucketcraft(self, ctx):
        msg = await ctx.send("Loading...")
        data = requests.get("https://api.mcsrvstat.us/2/bucketcraftsmp.us.to").json()
        embed = discord.Embed(
            title = "bucketcraft",
            color = ctx.author.color,
        )
        embed.set_thumbnail(url = "https://api.mcsrvstat.us/icon/bucketcraftsmp.us.to")
        if data['online']:
            embed.add_field(name = "Status", value = ":green_circle: Online")
            embed.add_field(name = "Players Online", value = f"{data['players']['online']}/{data['players']['max']}")
            list = ''
            if "list" in data['players']:
                for p in data['players']['list']:
                    list += f'{p}\n'
                embed.add_field(name = "Players", value = list, inline = False)
            else:
                embed.add_field(name = "Players", value = "None", inline = False)
        else:
            embed.add_field(name = "Status", value = ":red_circle: Offline")
        await msg.edit(content = '', embed = embed)

    @commands.command(aliases = ['mc', 'mcs', 'minecraftserver'])
    async def mcserver(self, ctx, ip):
        msg = await ctx.send("Loading...")
        data = requests.get(f"https://api.mcsrvstat.us/2/{ip}").json()
        if not data['ip']:
            await ctx.send("That server does not exist.")
            return
        embed = discord.Embed(
            title = ip,
            color = ctx.author.color,
        )
        if len(f"https://api.mcsrvstat.us/icon/{ip}") < 2048:
            embed.set_thumbnail(url = f"https://api.mcsrvstat.us/icon/{ip}")
        if data['online']:
            embed.add_field(name = "Status", value = ":green_circle: Online")
            version = data['version']
            if 'software' in data:
                version = f"{data['software']} {version}"
            embed.add_field(name = "Version", value = version)
            embed.add_field(name = "Players Online", value = f"{data['players']['online']}/{data['players']['max']}", inline = False)
            if 'list' in data['players']:
                list = ''
                for p in data['players']['list']:
                    list += f'{p}\n'
                if len(list) < 1024:
                    embed.add_field(name = "Players", value = list, inline = False)
        else:
            embed.add_field(name = "Status", value = ":red_circle: Offline")
        await msg.edit(content = '', embed = embed)

    @mcserver.error
    async def mcserver_error(self, ctx, error):
        await ctx.send("Please follow format: `y.server {ip}`")

    @commands.command(aliases = ['mcskin', 'minecraft skin'])
    async def skin(self, ctx, username = None):
        if not username:
            c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
            userdata = c.fetchone()
            if not userdata:
                await ctx.send("Please follow format: `y.skin {username}`")
                return
            uuid = userdata[6]
            username = userdata[5]
        else:
            data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            if data.status_code != requests.codes.ok:
                await ctx.send("Player not found.")
                return
            userdata = data.json()
            uuid = userdata['id']
            username = userdata['name']
        embed = discord.Embed(
            title = f"{username}'s minecraft skin",
            color = ctx.author.color
        )    
        embed.set_image(url = f"https://crafatar.com/renders/body/{uuid}?overlay")
        await ctx.send(embed = embed)

    @skin.error
    async def skin_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.skin {username}`")

    @commands.command(aliases = ['lmc', 'linkmc'])
    async def linkminecraft(self, ctx, username):
        data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if data.status_code != requests.codes.ok:
            await ctx.send("Player not found.")
            return
        userdata = data.json()
        c.execute("UPDATE userxp SET mc_username = %s, mc_uuid = %s WHERE id = %s;", (userdata['name'], userdata['id'], ctx.author.id))
        conn.commit()
        await ctx.send(f"Minecraft account linked! Username: `{userdata['name']}`, UUID: `{userdata['id']}`")

    @linkminecraft.error
    async def linkminecraft_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.linkmc {username}`")

    @commands.command(aliases = ['ulmc', 'unlinkmc'])
    async def unlinkminecraft(self, ctx):
        c.execute("UPDATE userxp SET mc_username = null, mc_uuid = null WHERE id = %s;",(ctx.author.id,))
        conn.commit()
        await ctx.send(f"Minecraft account unlinked.")

def setup(client):
    client.add_cog(minecraft(client))