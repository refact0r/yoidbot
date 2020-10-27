import discord
import os
import random
import asyncio
from discord.ext import commands
import math
from datetime import datetime
import time
import psycopg2
import wikipedia
import string
import json

bot_token = os.getenv('BOT_TOKEN')

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()
#c.execute("ALTER TABLE userxp ADD COLUMN mc_uuid TEXT;")
#c.execute("CREATE TABLE userxp (id BIGINT, name TEXT, xp INT, level INT, badges INT[], mc_username TEXT, mc_uuid TEXT);")
#c.execute("CREATE TABLE guilds (guild_id BIGINT, prefixes TEXT[]);") 
#c.execute("DELETE FROM guilds;")
#c.execute("INSERT INTO guilds VALUES (100, %s);", (["y!"],))
#c.execute("UPDATE userxp SET badges = %s WHERE id = 508863359777505290;", ([2, 8],))
'''
with open('dataclips.json', 'r') as myfile:
	data = json.load(myfile)
	for i in data['values']:
		c.execute("UPDATE userxp SET mc_username = %s, mc_uuid = %s WHERE id = %s;", (i[5], i[6], i[0]))
'''
conn.commit()

default_prefixes = ['y.', 'yoidbot please ', 'Y.']

async def determine_prefix(bot, message):
	guild = message.guild
	if guild:
		c.execute("SELECT * FROM guilds WHERE guild_id = %s;", (guild.id,))
		data = c.fetchone()
		if data and data[1]:
			return data[1] + ['yoidbot please ']
	return default_prefixes

client = commands.Bot(command_prefix = determine_prefix)

for file in os.listdir('./cogs'):
	if file.endswith('.py'):
		client.load_extension(f'cogs.{file[:-3]}')

client.remove_command('help')

@client.event
async def on_ready():
	await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "y.help"))
	print('bot has connected to discord')
	for guild in client.guilds:
		print(guild.name)

@client.command(aliases = ['ap'])
@commands.has_permissions(manage_guild = True)
@commands.guild_only()
async def addprefix(ctx, *, prefix):
	' '.join(prefix)
	if prefix[0] == '"' and prefix[-1] == '"':
		prefix = prefix[1:-1]
	c.execute("SELECT * FROM guilds WHERE guild_id = %s;", (ctx.guild.id,))
	data = c.fetchone()
	if not data:
		c.execute("INSERT INTO guilds VALUES (%s, %s);", (ctx.guild.id, [prefix]))
	else:
		if prefix in data[1]:
			await ctx.send("This server already has that prefix.")
		c.execute("UPDATE guilds SET prefixes = prefixes || %s WHERE guild_id = %s;", ([prefix], ctx.guild.id))
	conn.commit()
	await ctx.send(f"Added prefix `{prefix}`")

@addprefix.error
async def addprefix_error(ctx, error):
	if type(error) == discord.ext.commands.errors.MissingPermissions:
		await ctx.send("You do not have the permissions to use this command.")
	else:	
		await ctx.send("Please follow format: `y.addprefix {prefix}` (use quotes around prefix if prefix has space at the end)")

@client.command(aliases = ['rp'])
@commands.has_permissions(manage_guild = True)
@commands.guild_only()
async def removeprefix(ctx, *, prefix):
	' '.join(prefix)
	if prefix[0] == '"' and prefix[-1] == '"':
		prefix = prefix[1:-1]
	c.execute("SELECT * FROM guilds WHERE guild_id = %s;", (ctx.guild.id,))
	data = c.fetchone()
	if not data:
		await ctx.send("This server does not have any custom prefixes set.")
		return
	if prefix not in data[1]:
		await ctx.send("This server does not have this prefix.")
		return
	s = f"Removed prefix `{prefix}`"
	if len(data[1]) <= 1:
		c.execute("DELETE FROM guilds WHERE guild_id = %s;", (ctx.guild.id,))
		s += "\nPrefixes were reset to the default prefixes (`y.`, `Y.`)."
	else:
		c.execute("UPDATE guilds SET prefixes = array_remove(prefixes, %s) WHERE guild_id = %s;", (prefix, ctx.guild.id))
	conn.commit()
	await ctx.send(s)

@removeprefix.error
async def removeprefix_error(ctx, error):
	if type(error) == discord.ext.commands.errors.MissingPermissions:
		await ctx.send("You do not have the permissions to use this command.")
	else:	
		await ctx.send("Please follow format: `y.addprefix {prefix}` (use quotes around prefix if prefix has space at the end)")

@client.command(aliases = ['pr'])
@commands.guild_only()
async def prefixes(ctx):
	c.execute("SELECT * FROM guilds WHERE guild_id = %s;", (ctx.guild.id,))
	data = c.fetchone()
	prefixes = ''
	if not data:
		prefixes = "This server does not have any custom prefixes.\nTo add a custom prefix, do `y.addprefix {prefix}`.\n\nThese are the default prefixes:\n"
		data2 = default_prefixes
	else:
		data2 = data[1]
	for i in data2:
		prefixes += f"`{i}`\n"
	
	embed = discord.Embed(
		title = f"{ctx.guild.name}'s prefixes",
		description = prefixes,
		color = ctx.author.color
	)
	await ctx.send(embed = embed)

@client.command(aliases = ['close', 'stop', 'die'])
@commands.is_owner()
async def shutdown(ctx):
	await ctx.send("Bot shutting down...")
	await client.close()

@client.command(aliases = ['h'])
async def help(ctx, command = None):
	file = open('help.json', 'r')
	data = json.load(file)
	if command:
		for category in data:
			if command in data[category]['commands']:
				command_data = data[category]['commands'][command]
				aliases = ''
				for c in client.commands:
					if c.name == command or command in c.aliases:
						for a in [c.name] + c.aliases:
							if command != a:
								aliases += f"`{a}`, "
						break
				embed = discord.Embed(
					title = command,
					color = ctx.author.color,
				)
				usage = ''
				if command_data['usage']:
					usage = ' ' + command_data['usage']
				embed.add_field(name = "Usage", value = f"`y.{command}{usage}`", inline = False)
				if aliases:
					embed.add_field(name = "Other Names", value = aliases[:-2], inline = False)
				embed.add_field(name = "Description", value = f"{command_data['long']}", inline = False)
				await ctx.send(embed = embed)
				return
		await ctx.send("Could not find that command.")
		return
	pages = [["Useful"], ["Levels", "Moderation", "Reddit"], ["Games", "Minecraft", "Hypixel"]]
	def generate(page):
		embed = discord.Embed(
			title = 'Help',
			color = ctx.author.color,
			description = "Use the reactions below to go to the next page.\nIf you want to get further help, report issues, or suggest new ideas, join the Yoidbot discord: https://discord.gg/NPVFbnF"
		)
		for category in page:
			commands = ''
			for c in data[category]['commands']:
				usage = ''
				if data[category]['commands'][c]['usage']:
					usage = ' ' + data[category]['commands'][c]['usage']
				commands += f"`y.{c}{usage}` - {data[category]['commands'][c]['brief']}\n"
			embed.add_field(name = f"{data[category]['emoji']} {category}", value = commands, inline = False)
		return embed
	embeds = [generate(p) for p in pages]
	for i in range(len(embeds)):
		embeds[i].set_footer(text = f"Page {i + 1}/{len(embeds)}")
	msg = await ctx.send(embed = embeds[0])
	await msg.add_reaction('◀️')
	await msg.add_reaction('▶️')
	current = 0
	def check(reaction, user):
		return reaction.message.id == msg.id and user != client.user
	while True:
		try:
			reaction, user = await client.wait_for('reaction_add', timeout = 300.0, check = check)
		except asyncio.TimeoutError:
			return
		try:
			await reaction.remove(user)
		except:
			pass
		if reaction.emoji == '◀️':
			if current == 0:
				current = len(embeds) - 1
			else:
				current -= 1
		elif reaction.emoji == '▶️':
			if current == len(embeds) - 1:
				current = 0
			else:
				current += 1
		await msg.edit(embed = embeds[current])

@client.command()
async def hi(ctx):
    await ctx.send(f'Hello, {ctx.author.display_name}!')

@client.command()
async def invite(ctx):
	await ctx.send("https://discord.com/api/oauth2/authorize?client_id=680466714777223183&permissions=8&scope=bot")

@client.command(aliases = ['p'])
async def ping(ctx):
	before = time.monotonic()
	message = await ctx.send("Pong!")
	ping = int((time.monotonic() - before) * 1000)
	await message.edit(content = f"Pong! `{ping}ms`")
	c.execute("SELECT * FROM ping ORDER BY type;")
	data = c.fetchall()
	if ping < data[0][1]:
		c.execute("UPDATE ping SET time = %s, person = %s WHERE type = 0;", (ping, ctx.author.name))
		conn.commit()
	if ping > data[1][1]:
		c.execute("UPDATE ping SET time = %s, person = %s WHERE type = 1;", (ping, ctx.author.name))
		conn.commit()

@client.command(aliases = ['pl'])
async def pingleaderboard(ctx):
	c.execute("SELECT * FROM ping ORDER BY type;")
	data = c.fetchall()
	await ctx.send(f'lowest: {data[0][1]}ms by {data[0][2]}\nhighest: {data[1][1]}ms by {data[1][2]}')

@client.command(aliases = ['s'])
async def say(ctx, *, message):
	await ctx.send(f'{message}')

@say.error
async def say_error(ctx, error):
	await ctx.send('Please follow format: `y.say {message}`')

@client.command(aliases = ['sp'])
async def spam(ctx, *, message):
	s = message.split()
	if int(s[-1]) > 20:
		await ctx.send('You cannot spam that much.')
	else:
		out = message[0:len(message) - len(s[-1]) - 1]
		await ctx.send((out + '\n') * int(s[-1]))

@spam.error
async def spam_error(ctx, error):
	await ctx.send('Please follow format: `y.spam {message} {amount}`')

@client.command(aliases = ['8ball', '8b'])
async def eightball(ctx):
	answers = [
		"As I see it, yes.",
		"Ask again later.",
		"Better not tell you now.",
		"Cannot predict now.",
		"Concentrate and ask again.",
		"Don’t count on it.",
		"It is certain.",
		"It is decidedly so.",
		"Most likely.",
		"My reply is no.",
		"My sources say no.",
		"Outlook not so good.",
		"Outlook good.",
		"Reply hazy, try again.",
		"Signs point to yes.",
		"Very doubtful.",
		"Without a doubt.",
		"Yes.",
		"Yes – definitely.",
		"You may rely on it.",
	]
	await ctx.send(":8ball: " + random.choice(answers))

@client.command(aliases = ['cf'])
async def coinflip(ctx):
	rand = random.randint(0, 1)
	if rand:
		await ctx.send("Heads!")
	else:
		await ctx.send("Tails!")

@client.command()
async def speakthetruth(ctx):
	truth = [
		'subscribe to https://www.youtube.com/channel/UCbpHaJIAapKyQGT8qleP2lg',
		'subscribe to https://www.youtube.com/channel/UCEANNnWCyRCbkk-DHEMbgtA',
		'subscribe to https://www.youtube.com/channel/UCfjfrAYcwqXk13xeLZlftSw',
		'subscribe to https://www.youtube.com/channel/UCQwgWTzqnHUPsWoOEbgJOZQ',
	]
	await ctx.send(truth[random.randint(0, len(truth) - 1)])

@client.command(aliases = ['wikipedia', 'w'])
async def wiki(ctx, *, subject):
	' '.join(subject)
	suggest = wikipedia.suggest(subject)
	if not suggest:
		suggest = subject
	summary = ''
	try:
		summary = wikipedia.summary(suggest, sentences = 4)
	except wikipedia.exceptions.DisambiguationError as e:
		suggest = e.options[0]
	except wikipedia.exceptions.PageError as e:
		await ctx.send(f'"{subject}" does not match any pages.')
		return
	num = 4
	while len(summary) > 1000 or not summary:
		num -= 1
		summary = wikipedia.summary(suggest, sentences = num)
	page = wikipedia.page(suggest)
	summary = f"{page.url}\n\n{summary}"
	embed = discord.Embed(
		title = page.title,
		color = ctx.author.color,
		description = summary
	)
	if page.images[0]:
		embed.set_image(url = page.images[0])
	await ctx.send(embed = embed)

@wiki.error
async def wiki_error(ctx, error):
	await ctx.send("Please follow format: `y.wikipedia {subject}`")

@client.command(aliases = ['server', 'si'])
async def serverinfo(ctx):
	embed = discord.Embed(
		title = f":desktop:  {ctx.guild.name} info",
		color = ctx.author.color,
		description = "_ _"
	)
	embed.set_thumbnail(url = ctx.guild.icon_url)
	owner = ctx.guild.owner
	if owner.display_name != owner.name:
		name = owner.display_name + f" ({owner.name})"
	else:
		name = owner.name
	embed.add_field(name = ":bust_in_silhouette:  Owner", value = name)
	embed.add_field(name = ":date:  Date Created", value = ctx.guild.created_at.strftime("%B %d, %Y"))
	public = 'Private'
	if 'PUBLIC' in ctx.guild.features:
		public = 'Public'
	embed.add_field(name = ":wrench:  Server Type", value = public, inline = False)
	if ctx.guild.premium_subscription_count:
		embed.add_field(name = ":gem:  Nitro Level", value = f"Level {ctx.guild.premium_tier} ({ctx.guild.premium_subscription_count} boosts)")
	total = 0
	member = 0
	bot = 0
	online = 0
	dnd = 0
	idle = 0
	offline = 0
	for m in ctx.guild.members:
		total += 1
		if m.bot:
			bot += 1
		else:
			member += 1
		if m.status == discord.Status.online:
			online += 1
		elif m.status == discord.Status.dnd:
			dnd += 1
		elif m.status == discord.Status.idle:
			idle += 1
		else:
			offline += 1
	if total == 1:
		totalS = ''
	else:
		totalS = 's'
	if bot == 1:
		botS = ''
	else:
		botS = 's'
	if member == 1:
		memberS = ''
	else:
		memberS = 's'
	embed.add_field(name = ":busts_in_silhouette:  Members", value = f"**{total}** total member{totalS}\n**{bot}** bot{botS}\n**{member}** member{memberS}")
	embed.add_field(name = ":green_circle:  Member Status", value = f"**{online}** online\n**{idle}** idle\n**{dnd}** do not disturb\n**{offline}** offline")
	text = 0
	voice = 0
	category = 0
	for c in ctx.guild.channels:
		if c.type == discord.ChannelType.text:
			text += 1
		elif c.type == discord.ChannelType.voice:
			voice += 1
		else:
			category += 1
	if category == 1:
		categoryS = 'y'
	else:
		categoryS = 'ies'
	if text == 1:
		textS = ''
	else:
		textS = 's'
	if voice == 1:
		voiceS = ''
	else:
		voiceS = 's'
	embed.add_field(name = ":page_facing_up:  Channels", value = f"**{category}** categor{categoryS}\n**{text}** text channel{textS}\n**{voice}** voice channel{voiceS}", inline = False)
	await ctx.send(embed = embed)

client.run(bot_token)
