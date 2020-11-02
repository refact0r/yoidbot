import discord
import asyncio
import random
from discord.ext import commands
import requests
from datetime import datetime
import math
import time
import typing
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()

key = os.getenv('HYPIXEL_KEY')

class hypixel(commands.Cog):

    def __init__(self, client):
        self.client = client

    def get_status(self, uuid):
        status_data = requests.get(f"https://api.hypixel.net/status?key={key}&uuid={uuid}").json()
        if not status_data['session']['online']:
            return ":red_circle:  Offline"
        status = ":green_circle:  Online"
        status += f" - {status_data['session']['gameType'].capitalize()}"
        if status_data['session']['mode'] == "LOBBY":
            status += " Lobby"
        return status

    @commands.command(aliases = ['hypixelstats', 'hs', 'hp'])
    async def hypixel(self, ctx, player = None):
        msg = await ctx.send("Loading...")
        if not player:
            c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
            userdata = c.fetchone()
            if not userdata:
                await ctx.send("Please folow format: `y.hypixel {username}`")
                return
            player = userdata[5]
            uuid = userdata[6]
        else:
            uuid_data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}")
            if uuid_data.status_code != requests.codes.ok:
                await msg.edit(content = "Player not found.")
                return
            userdata = uuid_data.json()
            uuid = userdata['id']
        data = requests.get(f"https://api.hypixel.net/player?key={key}&name={player}").json()
        if not data['player']:
            await ctx.send("Player not found.")
            return
        if 'rank' in data['player'] and data['player']['rank'] != 'NORMAL':
            rank = data['player']['rank']
        elif 'newPackageRank' in data['player']:
            if data['player']['newPackageRank'] == 'MVP_PLUS':
                rank = 'MVP+'
            elif data['player']['newPackageRank'] == 'MVP':
                rank = 'MVP'
            elif data['player']['newPackageRank'] == 'VIP_PLUS':
                rank = 'VIP+'
            else:
                rank = 'VIP'
            if 'monthlyPackageRank' in data['player']:
                rank = 'MVP++'
        else:
            rank = 'Default'
        embed = discord.Embed(
            title = f"{data['player']['displayname']}'s hypixel stats",
            color = ctx.author.color,
            description = ''
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{uuid}?helm")
        embed.add_field(name = 'Status', value = self.get_status(uuid))
        if 'networkExp' in data['player']:
            embed.add_field(name = 'Level', value = int((math.sqrt((2 * data['player']['networkExp']) + 30625) / 50) - 2.5))
        embed.add_field(name = 'Rank', value = rank)
        if 'achievementPoints' in data['player']:
            embed.add_field(name = 'Achievement Points', value = data['player']['achievementPoints'])
        if 'karma' in data['player']:
            embed.add_field(name = 'Karma', value = data['player']['karma'])
        ts = data['player']['firstLogin']/1000
        embed.add_field(name = 'First Login', value = datetime.fromtimestamp(ts).strftime('%b %d %Y'))
        await msg.edit(content = '', embed = embed)

    @hypixel.error
    async def hypixel_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.hypixel {username}`")

    @commands.command(aliases = ['bedwarsstats', 'bw'])
    async def bedwars(self, ctx, *, input = None):
        msg = await ctx.send("Loading...")
        modes = [
            ['solos', 'solo', '1', 's'],
            ['doubles', 'double', '2', 'd'],
            ['3v3v3v3', '3', 'threes', 't'],
            ['4v4v4v4', '4', 'fours', 'f'],
            ['4v4']
        ]
        gamemode = ''
        c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
        userdata = c.fetchone()
        if not input:
            if not userdata[5]:
                await msg.edit(content = "Please follow format: `y.bedwars {username} {gamemode(optional)}`")
                return
            player = userdata[5]
        else:
            args = input.split()
            if not userdata[5]:
                player = args[0]
                if len(args) > 1:
                    gamemode = args[1]
            else:
                if len(args) > 1:
                    player = args[0]
                    gamemode = args[1]
                else:
                    if any(args[0] in mode for mode in modes):
                        player = userdata[5]
                        gamemode = args[0]
                    else:
                        player = args[0]
        data = requests.get(f"https://api.hypixel.net/player?key={key}&name={player}").json()
        if not data['player'] or 'Bedwars' not in data['player']['stats']:
            await msg.edit(content = "Player not found.")
            return
        embed = discord.Embed(
            title = f":bed:  {data['player']['displayname']}'s bedwars stats",
            color = ctx.author.color,
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{data['player']['uuid']}?helm")
        def get(input):
            if input in data['player']['stats']['Bedwars']:
                return data['player']['stats']['Bedwars'][input]
            else:
                return 0
        keys = {
            'games_played': 'games_played_bedwars',
            'winstreak': 'winstreak',
            'kills': 'kills_bedwars',
            'deaths': 'deaths_bedwars',
            'final_kills': 'final_kills_bedwars',
            'final_deaths': 'final_deaths_bedwars',
            'wins': 'wins_bedwars',
            'losses': 'losses_bedwars',
            'beds': 'beds_broken_bedwars',
            'beds_lost': 'beds_lost_bedwars',
            'resources_collected': 'resources_collected_bedwars',
            'items_purchased': 'items_purchased_bedwars',
        }
        def add_prefix(prefix):
            for item in keys:
                keys[item] = prefix + keys[item]
        if not gamemode:
            embed.description = 'Overall'
            embed.add_field(name = 'Level', value = data['player']['achievements']['bedwars_level'])
            embed.add_field(name = 'Coins', value = get('coins'))
        elif gamemode in modes[0]:
            embed.description = 'Solo'
            add_prefix('eight_one_')
        elif gamemode in modes[1]:
            embed.description = 'Doubles'
            add_prefix('eight_two_')
        elif gamemode in modes[2]:
            embed.description = '3v3v3v3'
            add_prefix('four_three_')
        elif gamemode in modes[3]:
            embed.description = '4v4v4v4'
            add_prefix('four_four_')
        elif gamemode in modes[4]:
            embed.description = '4v4'
            add_prefix('two_four_')
        else:
            await msg.edit(content = "Please enter a valid gamemode.")
            return
        embed.add_field(name = 'Games Played', value = get(keys['games_played']))
        embed.add_field(name = 'Winstreak', value = get(keys['winstreak']))
        k = get(keys['kills'])
        d = get(keys['deaths'])
        if d != 0:
            kdr = '{:.2f}'.format(k/d)
        else:
            kdr = k
        stats = f"**{k}** kills | **{d}** deaths | **{kdr}** KDR\n"
        fk = get(keys['final_kills'])
        fd = get(keys['final_deaths'])
        if fd != 0:
            fkdr = '{:.2f}'.format(fk/fd)
        else:
            fkdr = fk
        stats += f"**{fk}** final kills | **{fd}** final deaths | **{fkdr}** FKDR\n"
        w = get(keys['wins'])
        l = get(keys['losses'])
        if l != 0:
            wlr = '{:.2f}'.format(w/l)
        else:
            wlr = w
        stats += f"**{w}** wins | **{l}** losses | **{wlr}** WLR\n"
        b = get(keys['beds'])
        bl = get(keys['beds_lost'])
        if bl != 0:
            blr = '{:.2f}'.format(b/bl)
        else:
            blr = b
        stats += f"**{b}** beds broken | **{bl}** beds lost | **{blr}** BLR\n"
        rc = get(keys['resources_collected'])
        ip = get(keys['items_purchased'])
        stats2 = f"**{rc}** resources collected\n **{ip}** items purchased"
        embed.add_field(name = 'General Stats', value = stats, inline = False)
        embed.add_field(name = 'Other Stats', value = stats2, inline = False)
        await msg.edit(content = '', embed = embed)

    @bedwars.error
    async def bedwars_error(self, ctx, error):
        print(error)
        if type(error) == discord.ext.commands.errors.CommandInvokeError:
            await ctx.send("Could not get data.")
        else:
            await ctx.send("Please follow format: `y.bedwars {username} {gamemode(optional)}`")

    @commands.command(aliases = ['skywarsstats', 'sw'])
    async def skywars(self, ctx, *, input = None):
        msg = await ctx.send("Loading...")
        modes = [
            ['solonormal', 'solosnormal', 'sn', '1n'],
            ['soloinsane', 'solosinsane', 'si', '1i'],
            ['doublenormal', 'doublesnormal', 'dn', '2n'],
            ['doubleinsane', 'doublesinsane', 'di', '2i', '2sinsane', '2insane'],
            ['solo', 'solos', '1', '1s', 's'],
            ['double', 'doubles', '2', '2s', 'd'],
        ]
        gamemode = ''
        c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
        userdata = c.fetchone()
        if not input:
            if not userdata[5]:
                await msg.edit(content = "Please follow format: `y.skywars {username} {gamemode(optional)}`")
                return
            player = userdata[5]
        else:
            args = input.split()
            if not userdata[5]:
                player = args[0]
                if len(args) > 1:
                    gamemode = ''.join(args[1:])
            else:
                if len(args) > 1:
                    if any(''.join(args) in mode for mode in modes):
                        player = userdata[5]
                        gamemode = ''.join(args)
                    else:
                        player = args[0]
                        gamemode = ''.join(args[1:])
                else:
                    if any(''.join(args) in mode for mode in modes):
                        player = userdata[5]
                        gamemode = ''.join(args)
                    else:
                        player = args[0]
        data = requests.get(f"https://api.hypixel.net/player?key={key}&name={player}").json()
        if not data['player'] or 'SkyWars' not in data['player']['stats']:
            await msg.edit(content = "Player not found.")
            return
        embed = discord.Embed(
            title = f":crossed_swords:  {data['player']['displayname']}'s skywars stats",
            color = ctx.author.color,
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{data['player']['uuid']}?helm")
        def get(input):
            if input in data['player']['stats']['SkyWars']:
                return data['player']['stats']['SkyWars'][input]
            else:
                return 0
        keys = {
            'kills': 'kills',
            'deaths': 'deaths',
            'wins': 'wins',
            'losses': 'losses',
        }
        def sw_lvl(xp):
            xps = [0, 20, 70, 150, 250, 500, 1000, 2000, 3500, 6000, 10000, 15000]
            if xp >= 15000:
                return (xp - 15000) / 10000. + 12
            else:
                for i in range(len(xps)):
                    if xp < xps[i]:
                        return i
        def add_postfix(postfix):
            for item in keys:
                keys[item] = keys[item] + postfix
        if not gamemode:
            embed.description = 'Overall'
            embed.add_field(name = 'Level', value = sw_lvl(get('skywars_experience')))
            embed.add_field(name = 'Coins', value = get('coins'))
            embed.add_field(name = 'Souls', value = get('souls'))
            embed.add_field(name = 'Winstreak', value = get('win_streak'))
        elif gamemode in modes[0]:
            embed.description = 'Solo Normal'
            add_postfix('_solo_normal')
        elif gamemode in modes[1]:
            embed.description = 'Solo Insane'
            add_postfix('_solo_insane')
        elif gamemode in modes[2]:
            embed.description = 'Doubles Normal'
            add_postfix('_team_normal')
        elif gamemode in modes[3]:
            embed.description = 'Doubles Insane'
            add_postfix('_team_insane')
        elif gamemode in modes[4]:
            embed.description = 'Solo'
            add_postfix('_solo')
        elif gamemode in modes[5]:
            embed.description = 'Doubles'
            add_postfix('_team')
        else:
            await msg.edit(content = "Please enter a valid gamemode.")
            return
        w = get(keys['wins'])
        l = get(keys['losses'])
        embed.add_field(name = 'Games Played', value = w + l)
        k = get(keys['kills'])
        d = get(keys['deaths'])
        if d != 0:
            kdr = '{:.2f}'.format(k/d)
        else:
            kdr = k
        stats = f"**{k}** kills | **{d}** deaths | **{kdr}** KDR\n"
        if l != 0:
            wlr = '{:.2f}'.format(w/l)
        else:
            wlr = w
        stats += f"**{w}** wins | **{l}** losses | **{wlr}** WLR\n"
        embed.add_field(name = 'Stats', value = stats, inline = False)
        await msg.edit(content = '', embed = embed)

    @skywars.error
    async def skywars_error(self, ctx, error):
        print(error)
        if type(error) == discord.ext.commands.errors.CommandInvokeError:
            await ctx.send("Could not get data.")
        else:
            await ctx.send("Please follow format: `y.skywars {username} {gamemode(optional)}`")

    @commands.command(aliases = ['d', 'duelsstats', 'duel'])
    async def duels(self, ctx, *, input = None):
        msg = await ctx.send("Loading...")
        modes = [
            ['classic', 'c'],
            ['bridge', 'bridge1', 'bridge1v1', 'br', 'br1'],
            ['bridge2', 'bridge2v2', 'br2'],
            ['bridge4', 'bridge4v4', 'br4'],
            ['uhc', 'uhc1v1', 'uhc1', 'u', 'u1'],
            ['uhc2', 'uhc2v2', 'u2'],
            ['uhc4', 'uhc4v4', 'u4'],
            ['bow', 'b'],
            ['sumo', 's'],
            ['op', 'op1v1', 'op1', 'o1', 'o'],
            ['bowspleef', 'bs'],
            ['skywars', 'skywars1v1', 'skywars1', 'sw', 'sw1'],
            ['nodebuff', 'n'],
            ['blitz', 'bl'],
            ['combo', 'co'],
            ['megawalls', 'megawalls1v1', 'megawalls1', 'm', 'm1']
        ]
        gamemode = ''
        c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
        userdata = c.fetchone()
        if not input:
            if not userdata[5]:
                await msg.edit(content = "Please follow format: `y.skywars {username} {gamemode(optional)}`")
                return
            player = userdata[5]
        else:
            args = input.split()
            if not userdata[5]:
                player = args[0]
                if len(args) > 1:
                    gamemode = ''.join(args[1:])
            else:
                if len(args) > 1:
                    if any(''.join(args) in mode for mode in modes):
                        player = userdata[5]
                        gamemode = ''.join(args)
                    else:
                        player = args[0]
                        gamemode = ''.join(args[1:])
                else:
                    if any(''.join(args) in mode for mode in modes):
                        player = userdata[5]
                        gamemode = ''.join(args)
                    else:
                        player = args[0]
        data = requests.get(f"https://api.hypixel.net/player?key={key}&name={player}").json()
        if not data['player'] or 'Duels' not in data['player']['stats']:
            await msg.edit(content = "Player not found.")
            return
        embed = discord.Embed(
            title = f":crossed_swords:  {data['player']['displayname']}'s duels stats",
            color = ctx.author.color,
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{data['player']['uuid']}?helm")
        def get(input):
            if input in data['player']['stats']['Duels']:
                return data['player']['stats']['Duels'][input]
            else:
                return 0
        stats = ''
        otherstats = ''
        prefixes = {
            'wins': '_wins',
            'losses': '_losses',
        }
        postfixes = {
            'winstreak': 'current_winstreak_mode_',
            'best_winstreak': 'best_winstreak_mode_'
        }
        def add_mode(mode):
            for item in prefixes:
                prefixes[item] = mode + prefixes[item]
            for item in postfixes:
                postfixes[item] = postfixes[item] + mode
        def add_kills_stats(mode):
            k = get(mode + '_kills')
            d = get(mode + '_deaths')
            if d != 0:
                kdr = '{:.2f}'.format(k/d)
            else:
                kdr = k
            return f"**{k}** kills | **{d}** deaths | **{kdr}** KDR\n"
        if not gamemode:
            await msg.edit(content = "Please follow format: `y.duels {username} {gamemode}`")
            return
        elif gamemode in modes[0]:
            embed.description = 'Classic Duels'
            add_mode('classic_duel')
        elif gamemode in modes[1]:
            embed.description = 'Bridge 1v1'
            add_mode('bridge_duel')
            stats += add_kills_stats('bridge_duel_bridge')
        elif gamemode in modes[2]:
            embed.description = 'Bridge 2v2'
            add_mode('bridge_doubles')
            stats += add_kills_stats('bridge_doubles_bridge')
        elif gamemode in modes[3]:
            embed.description = 'Bridge 4v4'
            add_mode('bridge_four')
            stats += add_kills_stats('bridge_four_bridge')
        elif gamemode in modes[4]:
            embed.description = 'UHC 1v1'
            add_mode('uhc_duel')
        elif gamemode in modes[5]:
            embed.description = 'UHC 2v2'
            add_mode('uhc_doubles')
            stats += add_kills_stats('uhc_doubles')
        elif gamemode in modes[6]:
            embed.description = 'UHC 4v4'
            add_mode('uhc_four')
            stats += add_kills_stats('uhc_four')
        elif gamemode in modes[7]:
            embed.description = 'Bow Duels'
            add_mode('bow_duel')
        elif gamemode in modes[8]:
            embed.description = 'Sumo Duels'
            add_mode('sumo_duel')
        else:
            await msg.edit(content = "Please enter a valid gamemode.")
            return
        embed.add_field(name = 'Winstreak', value = get(postfixes['winstreak']))
        embed.add_field(name = 'Best Winstreak', value = get(postfixes['best_winstreak']))
        w = get(prefixes['wins'])
        l = get(prefixes['losses'])
        embed.add_field(name = 'Games Played', value = w + l)
        if l != 0:
            wlr = '{:.2f}'.format(w/l)
        else:
            wlr = w
        stats += f"**{w}** wins | **{l}** losses | **{wlr}** WLR\n"
        embed.add_field(name = 'Stats', value = stats, inline = False)
        await msg.edit(content = '', embed = embed)

    @skywars.error
    async def duels_error(self, ctx, error):
        print(error)
        if type(error) == discord.ext.commands.errors.CommandInvokeError:
            await ctx.send("Could not get data.")
        else:
            await ctx.send("Please follow format: `y.duels {username} {type} {gamemode(optional)}`")
    
    @commands.command(aliases = ['flist', 'hypixelfriends', 'hfl'])
    async def hypixelflist(self, ctx, player = None):
        msg = await ctx.send("Loading...")
        if not player:
            c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
            userdata = c.fetchone()
            if not userdata:
                await msg.edit(content = "Please follow format: `y.hypixelflist {username}`")
                return
            uuid = userdata[6]
            username = userdata[5]
        else:
            data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}")
            if data.status_code != requests.codes.ok:
                await msg.edit(content = "Player not found.")
                return
            userdata = data.json()
            uuid = userdata['id']
            username = userdata['name']
        data = requests.get(f"https://api.hypixel.net/friends?key={key}&uuid={uuid}").json()
        if not data['success']:
            await msg.edit(content = "Player not found.")
            return
        flist = ''
        counter = 0
        online_counter = 0
        for f in data['records']:
            f_uuid = f['uuidReceiver']
            if f_uuid == uuid:
                f_uuid = f['uuidSender']
            friend = requests.get(f"https://api.hypixel.net/player?key={key}&uuid={f_uuid}").json()
            if not friend['player']:
                continue
            if 'lastLogin' not in friend['player'] or 'lastLogout' not in friend['player']:
                continue 
            if friend['player']['lastLogin'] > friend['player']['lastLogout']:
                flist += f"{friend['player']['displayname']}\n"
                online_counter += 1
            counter += 1
        if not flist:
            flist = "None"
        embed = discord.Embed(
            title = f":busts_in_silhouette:  {username}'s hypixel friends",
            color = ctx.author.color,
            description = f"Total friends: {counter}\n Online friends: {online_counter}"
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{uuid}?helm")
        embed.add_field(name = "Online Friends", value = flist)
        await msg.edit(content = '', embed = embed)

    @hypixelflist.error
    async def hypxielflist_error(self, ctx, error):
        if type(error) == discord.ext.commands.errors.CommandInvokeError:
            await ctx.send("Could not get data.")
        else:
            await ctx.send("Please follow format: `y.hypixelflist {username}`")

    @commands.command(aliases = ['sb', 'skyblock'])
    async def skyblockstats(self, ctx, *, input = None):
        msg = await ctx.send("Loading...")
        cute_names = [
            "Apple",
            "Banana",
            "Blueberry",
            "Coconut",
            "Cucumber",
            "Grapes",
            "Kiwi",
            "Lemon",
            "Lime",
            "Mango",
            "Orange",
            "Papaya",
            "Peach",
            "Pear",
            "Pineapple",
            "Pomegranate",
            "Raspberry",
            "Strawberry",
            "Tomato",
            "Watermelon",
            "Zucchini"
        ]
        c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
        userdata = c.fetchone()
        profile_name = ''
        if not input:
            if not userdata[5]:
                await msg.edit(content = "Please follow format: `y.skyblock {username} {gamemode(optional)}`")
                return
            username = userdata[5]
            uuid = userdata[6]
        else:
            args = input.split()
            if args[0] not in cute_names:
                uuid_data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{args[0]}")
                if uuid_data.status_code != requests.codes.ok:
                    await msg.edit(content = "Player not found.")
                    return
                uuid_data = uuid_data.json()
                username = uuid_data['name']
                uuid = uuid_data['id']
                if len(args) > 1:
                    profile_name = args[1]
            else:
                if userdata[5]:
                    username = userdata[5]
                    uuid = userdata[6]
                    profile_name = args[0]
                else:
                    await msg.edit(content = "Player not found.")
                    return

        skylea_data = requests.get(f"https://sky.lea.moe/api/v2/profile/{uuid}").json()
        if 'profiles' not in skylea_data:
            await msg.edit(content = "No skyblock data for this player.")
            return
        profile = ''
        for p in skylea_data['profiles']:
            if profile_name:
                if skylea_data['profiles'][p]['cute_name'].lower() == profile_name.lower():
                    profile = skylea_data['profiles'][p]
                    break
            else:
                if skylea_data['profiles'][p]['current']:
                    profile = skylea_data['profiles'][p]
                    break
        if not profile:
            await msg.edit(content = f"Could not find a profile with name: `{profile_name}`")
        embed = discord.Embed(
            title = f"{username}'s skyblock stats",
            color = ctx.author.color,
            description = f"""
                **Status:** {self.get_status(uuid)}
                **Profile:** {profile['cute_name']}
                **Last Update:** {profile['data']['last_updated']['text']} ({datetime.fromtimestamp(profile['data']['last_updated']['unix'] / 1000.0).strftime('%m/%d/%Y').lstrip("0")})
                **First Joined:** {profile['data']['first_join']['text']} ({datetime.fromtimestamp(profile['data']['first_join']['unix'] / 1000.0).strftime('%m/%d/%Y').lstrip("0")})
            """,
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{uuid}?helm")
        if 'bank' in profile['data']:
            embed.add_field(name = ":bank:  Bank Balance", value = round(profile['data']['bank']))
        else:
            embed.add_field(name = ":bank:  Bank Balance", value = 0)
        if 'purse' in profile['data']:
            embed.add_field(name = ":moneybag:  Purse", value = round(profile['data']['purse']))
        if 'fairy_souls' in profile['data']:
            embed.add_field(name = ":rainbow:  Fairy Souls", value = f"{profile['data']['fairy_souls']['collected']}/{profile['data']['fairy_souls']['total']}")
        stats = {
            "health": ":heart:  Health",
            "defense": ":shield:  Defense",
            "effective_health": ":two_hearts:  Effective Health",
            "strength": ":muscle:  Strength",
            "speed": ":dash:  Speed",
            "crit_chance": ":game_die:  Crit Chance",
            "crit_damage": ":skull_crossbones:  Crit Damage",
            "bonus_attack_speed": ":crossed_swords:  Attack Speed",
            "intelligence": ":brain:  Intelligence",
            "pet_luck": ":parrot:  Pet Luck",
            "sea_creature_chance": ":fishing_pole_and_fish:  Sea Creature Chance",
            "magic_find": ":sparkles:  Magic Find"
        }
        percentages = {
            "speed",
            "crit_chance",
            "crit_damage",
            "bonus_attack_speed",
            "sea_creature_chance"
        }
        if 'stats' in profile['data']:
            for s in stats:
                if s in percentages:
                    embed.add_field(name = stats[s], value = f"{profile['data']['stats'][s]}%")
                else:
                    embed.add_field(name = stats[s], value = profile['data']['stats'][s])
        await msg.edit(content = '', embed = embed)
    
    @skyblockstats.error
    async def skyblockstats_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.skyblockstats {username} {profile(optional)}`")

    @commands.command(aliases = ['sb2', 'skyblock2'])
    async def skyblockstats2(self, ctx, *, input = None):
        msg = await ctx.send("Loading...")
        cute_names = [
            "Apple",
            "Banana",
            "Blueberry",
            "Coconut",
            "Cucumber",
            "Grapes",
            "Kiwi",
            "Lemon",
            "Lime",
            "Mango",
            "Orange",
            "Papaya",
            "Peach",
            "Pear",
            "Pineapple",
            "Pomegranate",
            "Raspberry",
            "Strawberry",
            "Tomato",
            "Watermelon",
            "Zucchini"
        ]
        c.execute("SELECT * FROM userxp WHERE id = %s;", (ctx.author.id,))
        userdata = c.fetchone()
        profile_name = ''
        if not input:
            if not userdata[5]:
                await msg.edit(content = "Please follow format: `y.skyblock {username} {gamemode(optional)}`")
                return
            username = userdata[5]
            uuid = userdata[6]
        else:
            args = input.split()
            if args[0] not in cute_names:
                uuid_data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{args[0]}")
                if uuid_data.status_code != requests.codes.ok:
                    await msg.edit(content = "Player not found.")
                    return
                uuid_data = uuid_data.json()
                username = uuid_data['name']
                uuid = uuid_data['id']
                if len(args) > 1:
                    profile_name = args[1]
            else:
                if userdata[5]:
                    username = userdata[5]
                    uuid = userdata[6]
                    profile_name = args[0]
                else:
                    await msg.edit(content = "Player not found.")
                    return

        skylea_data = requests.get(f"https://sky.lea.moe/api/v2/profile/{uuid}").json()
        if 'profiles' not in skylea_data:
            await msg.edit(content = "No skyblock data for this player.")
            return
        profile = ''
        for p in skylea_data['profiles']:
            if profile_name:
                if skylea_data['profiles'][p]['cute_name'].lower() == profile_name.lower():
                    profile = skylea_data['profiles'][p]
                    break
            else:
                if skylea_data['profiles'][p]['current']:
                    profile = skylea_data['profiles'][p]
                    break
        if not profile:
            await msg.edit(content = f"Could not find a profile with name: `{profile_name}`")
        embed = discord.Embed(
            title = f"{username}'s skyblock stats",
            color = ctx.author.color,
            description = f"""
                **Status:** {self.get_status(uuid)}
                **Profile:** {profile['cute_name']}
                **Last Update:** {profile['data']['last_updated']['text']} ({datetime.fromtimestamp(profile['data']['last_updated']['unix'] / 1000.0).strftime('%m/%d/%Y').lstrip("0")})
                **First Joined:** {profile['data']['first_join']['text']} ({datetime.fromtimestamp(profile['data']['first_join']['unix'] / 1000.0).strftime('%m/%d/%Y').lstrip("0")})
            """,
        )
        embed.set_thumbnail(url = f"https://crafatar.com/avatars/{uuid}?helm")
        if 'bank' in profile['data']:
            embed.add_field(name = ":bank:  Bank Balance", value = round(profile['data']['bank']))
        else:
            embed.add_field(name = ":bank:  Bank Balance", value = 0)
        if 'purse' in profile['data']:
            embed.add_field(name = ":moneybag:  Purse", value = round(profile['data']['purse']))
        if 'fairy_souls' in profile['data']:
            embed.add_field(name = ":rainbow:  Fairy Souls", value = f"{profile['data']['fairy_souls']['collected']}/{profile['data']['fairy_souls']['total']}")
        stats = {
            "health": ":heart:  Health",
            "defense": ":shield:  Defense",
            "effective_health": ":two_hearts:  Effective Health",
            "strength": ":muscle:  Strength",
            "speed": ":dash:  Speed",
            "crit_chance": ":game_die:  Crit Chance",
            "crit_damage": ":skull_crossbones:  Crit Damage",
            "bonus_attack_speed": ":crossed_swords:  Attack Speed",
            "intelligence": ":brain:  Intelligence",
            "pet_luck": ":parrot:  Pet Luck",
            "sea_creature_chance": ":fishing_pole_and_fish:  Sea Creature Chance",
            "magic_find": ":sparkles:  Magic Find"
        }
        percentages = {
            "speed",
            "crit_chance",
            "crit_damage",
            "bonus_attack_speed",
            "sea_creature_chance"
        }
        if 'stats' in profile['data']:
            for s in stats:
                if s in percentages:
                    embed.add_field(name = stats[s], value = f"{profile['data']['stats'][s]}%")
                else:
                    embed.add_field(name = stats[s], value = profile['data']['stats'][s])
        await msg.edit(content = '', embed = embed)

def setup(client):
    client.add_cog(hypixel(client))