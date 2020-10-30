import discord
from discord.ext import commands
import math
import psycopg2
import os
import typing

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()
#c.execute("UPDATE userxp SET badges = '{1, 8}' WHERE name = '<y>';")
conn.commit()
c.execute("SELECT * FROM userxp WHERE name = '<y>';")
print(c.fetchone())
c.execute("SELECT * FROM userxp ORDER BY xp DESC LIMIT 3;")
third = c.fetchall()[2][2]

class levels(commands.Cog):

    def __init__(self, client):
        self.client = client

    def find_level(self, xp):
    	return int(math.floor((math.sqrt(20 * xp + 25) - 5) / 10))

    def find_xp(self, level):
        return 5 * level * level + (5 * level)

    place_badges = [
        [":crown:", "first place"],
        [":second_place:", "second place"],
        [":third_place:", "third place"],
    ]
    level_badges = [
        [":small_blue_diamond:", 1],
        [":large_blue_diamond:", 5],
        [":diamond_shape_with_a_dot_inside:", 10],
        [":beginner:", 20],
        [":reminder_ribbon:", 30],
        [":military_medal:", 40],
        [":sparkles:", 50],
        [":star2:", 60],
        [":rosette:", 70],
        [":trident:", 80],
        [":trophy:", 100],
    ]
    badges = [
        [":1234:", "win a game of 2048"],
        [":regional_indicator_x:", "win a game of tictactoe"],
    ]

    def find_badge(self, level):
        for i in range(len(self.level_badges)):
            if level < self.level_badges[i][1]:
                return i
        return i
    
    prev = {}

    @commands.Cog.listener()
    async def on_message(self, msg):
        id = msg.author.id
        if msg.author.bot or msg.author.id == 680466714777223183:
            return
        c.execute("SELECT * FROM userxp WHERE id = %s;", (id,))
        data = c.fetchone()
        if not data:
            c.execute("INSERT INTO userxp VALUES (%s, %s, %s, %s, %s);", (id, msg.author.name, 1, 0, [0, 0]))
            conn.commit()
            self.prev[msg.channel.id] = id
            return
        level = self.find_level(data[2])
        badge_id = self.find_badge(level)
        level_badge = ''
        if badge_id:
            level_badge = self.level_badges[badge_id - 1][0]
        print(f"lvl: {level}, badge_id: {badge_id}, level_badge: {level_badge}\n{data}")
        if level != data[3]:
            congrat_string = f"Congratulations {msg.author.display_name}, you are now level {level}!"
            if badge_id != data[4][1]:
                congrat_string += f" You also earned the badge {level_badge}"
            await msg.channel.send(congrat_string)
        badges = data[4]
        badges[1] = badge_id
        if data[2] > third:
            c.execute("SELECT * FROM userxp ORDER BY xp DESC LIMIT 3;")
            top = c.fetchall()
            for i in range(len(top)):
                if top[i][0] == id:
                    print("top 3")
                    if data[4][0] != i + 1:
                        badges[0] = i + 1
                        print("update")
                        c.execute("UPDATE userxp SET badges[0] = 0 WHERE badges[0] > 0;")
                        conn.commit()
                        for j in range(len(top)):
                            c.execute("SELECT badges FROM userxp WHERE id = %s;", (top[j][0],))
                            b = list(c.fetchone())[0]
                            b[0] = j + 1
                            c.execute("UPDATE userxp SET badges = %s WHERE id = %s;", (b, top[j][0]))
                            conn.commit()
                    break
        new = data[2] + 1
        if msg.channel.id in self.prev:
            if self.prev[msg.channel.id] == id:
                new = data[2]
        c.execute("UPDATE userxp SET xp = %s, level = %s, name = %s, badges = %s WHERE id = %s;", (new, level, msg.author.name, badges, id))
        conn.commit()
        self.prev[msg.channel.id] = id

    @commands.command(aliases = ['lb'])
    async def leaderboard(self, ctx):
        c.execute("SELECT * FROM userxp ORDER BY xp DESC;")
        all = c.fetchall()
        content = ''
        counter = 1
        within = False
        author = ''
        for i in all:
            if ctx.guild.fetch_member(i[0]):
                name = i[1]
                if counter <= 20:
                    if i[0] == ctx.author.id:
                        within = True
                        name = '**' + name + '**'
                    if counter == 1:
                        content += f'**{counter}** - :crown: __{name}__ - level {i[3]} - {i[2]} xp\n'
                    elif counter == 2:
                        content += f'**{counter}** - :second_place: __{name}__ - level {i[3]} - {i[2]} xp\n'
                    elif counter == 3:
                        content += f'**{counter}** - :third_place: __{name}__ - level {i[3]} - {i[2]} xp\n'
                    else:
                        content += f'**{counter}** - __{name}__ - level {i[3]} - {i[2]} xp\n'
                else:
                    if i[0] == ctx.author.id:
                        author = f'**{counter}** - __**{name}**__ - level {i[3]} - {i[2]} xp\n'
                        break
                counter += 1
        if not within:
            content += "**------------------------------------------------------------**\n" + author
        embed = discord.Embed(
            title = f"{ctx.guild.name}'s leaderboard",
            color = ctx.author.color,
            description = content
        )
        embed.set_thumbnail(url = ctx.guild.icon_url)
        await ctx.send(embed = embed)

    @commands.command(aliases = ['glb'])
    async def globalleaderboard(self, ctx):
        c.execute("SELECT * FROM userxp ORDER BY xp DESC;")
        all = c.fetchall()
        content = ''
        counter = 1
        within = False
        author = ''
        for i in all:
            name = i[1]
            if counter <= 20:
                if i[0] == ctx.author.id:
                    within = True
                    name = '**' + name + '**'
                if counter == 1:
                    content += f'**{counter}** - :crown: __{name}__ - level {i[3]} - {i[2]} xp\n'
                elif counter == 2:
                    content += f'**{counter}** - :second_place: __{name}__ - level {i[3]} - {i[2]} xp\n'
                elif counter == 3:
                    content += f'**{counter}** - :third_place: __{name}__ - level {i[3]} - {i[2]} xp\n'
                else:
                    content += f'**{counter}** - __{name}__ - level {i[3]} - {i[2]} xp\n'
            else:
                if i[0] == ctx.author.id:
                    author = f'**{counter}** - __**{name}**__ - level {i[3]} - {i[2]} xp\n'
                    break
            counter += 1
        if not within:
            content += "**------------------------------------------------------------**\n" + author
        embed = discord.Embed(
            title = f"global leaderboard",
            color = ctx.author.color,
            description = content
        )
        await ctx.send(embed = embed)

    @commands.command(aliases = ['lvl'])
    async def level(self, ctx, *, author: typing.Optional[discord.Member] = None):
        if not author:
            author = ctx.author
        c.execute("SELECT * FROM userxp WHERE id = %s;", (author.id,))
        data = c.fetchone()
        print(data)
        if not data:
            c.execute("INSERT INTO userxp VALUES (%s, %s, %s, %s);", (author.id, author.name, 1, 0))
            conn.commit()
        level = self.find_level(data[2])
        a = int(self.find_xp(level))
        title = f'level {level}\n'
        stuff = f'total xp: **{data[2]}**\n'
        stuff += f'**{data[2] - a}**/**{(data[3] + 1) * 10}** xp\n'
        stuff += f'level {level} `'
        x = int(round((data[2] - a) / ((level + 1) / 2)))
        stuff += '|' * x
        stuff += '-' * (20 - x)
        stuff += f'` level {level + 1}'
        if author.display_name != author.name:
            name = author.display_name + f" ({author.name})"
        else:
            name = author.name
        badges = ''
        if data[4][0]:
            badges += ' ' + self.place_badges[data[4][0] - 1][0]
        if data[4][1]:
            badges += ' ' + self.level_badges[data[4][1] - 1][0]
        if data[4][2:]:
            for i in data[4][2:]:
                badges += ' ' + self.badges[i - 1][0]
        badges = badges.strip()
        embed = discord.Embed(
            title = name,
            color = author.color,
            description = badges
        )
        embed.add_field(name = title, value = stuff)
        embed.set_thumbnail(url = author.avatar_url)
        await ctx.send(embed = embed)

    @commands.command(aliases = ['badges'])
    async def badge(self, ctx):
        embed = discord.Embed(
            title = "All Badges",
            color = ctx.author.color
        )
        level = ''
        place = ''
        for i in self.place_badges:
            place += f"{i[0]} - {i[1]}\n"
        embed.add_field(name = "Place Badges", value = place, inline = False)
        for j in self.level_badges:
            level += f"{j[0]} - level {j[1]}\n"
        embed.add_field(name = "Level Badges", value = level)
        normal = ''
        for k in self.badges:
            normal += f"{k[0]} - {k[1]}\n"
        embed.add_field(name = "Normal Badges", value = normal)
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(levels(client))