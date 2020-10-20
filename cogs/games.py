import discord
import asyncio
import random
from discord.ext import commands
import datetime
import math
import requests
import urllib.request, json
import html
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()

class games(commands.Cog):

    def __init__(self, client):
        self.client = client

    def add_xp(self, id, amount):
        c.execute("SELECT * FROM userxp WHERE id = %s;", (id,))
        data = c.fetchone()
        if not data:
            return
        xp = int(math.ceil(data[3] * amount))
        if xp < 5:
            xp = 5
        c.execute("UPDATE userxp SET xp = %s WHERE id = %s;", (data[2] + xp, id))
        conn.commit()

    def add_xp2(self, id, amount):
        c.execute("SELECT * FROM userxp WHERE id = %s;", (id,))
        data = c.fetchone()
        if not data:
            return
        c.execute("UPDATE userxp SET xp = %s WHERE id = %s;", (data[2] +  amount, id))
        conn.commit()

    def add_badge(self, id, badge_id):
        c.execute("UPDATE userxp SET badges = array_append(badges, %s) WHERE id = %s;", (badge_id, id))
        conn.commit()

    @commands.command(aliases = ['t'])
    @commands.cooldown(5, 30, commands.BucketType.channel)
    @commands.max_concurrency(1, commands.BucketType.channel, wait = False)
    async def trivia(self, ctx):
        data = requests.get(f'https://opentdb.com/api.php?amount=1').json()
        results = data['results'][0]
        embed = discord.Embed(
            title = ":question:  Trivia",
            description = f"Category: {results['category']} | Difficulty: {results['difficulty'].capitalize()}",
            color = ctx.author.color
        )
        embed2 = embed
        def decode(answers):
            new = []
            for i in answers:
                new.append(html.unescape(i))
            return new
        if results['type'] == 'boolean':
            if results['correct_answer'] == "False":
                answers = results['incorrect_answers'] + [results['correct_answer']]
            else:
                answers = [results['correct_answer']] + results['incorrect_answers']
            answers = decode(answers)
            embed.add_field(name = html.unescape(results['question']), value = f"True or False")
            available_commands = ['true', 'false', 't', 'f']
        else:
            pos = random.randint(0, 3)
            if pos == 3:
                answers = results['incorrect_answers'] + [results['correct_answer']]
            else:
                answers = results['incorrect_answers'][0:pos] + [results['correct_answer']] + results['incorrect_answers'][pos:]
            answers = decode(answers)
            embed.add_field(name = html.unescape(results['question']), value = f"A) {answers[0]}\nB) {answers[1]}\nC) {answers[2]}\nD) {answers[3]}")
            available_commands = ['a', 'b', 'c', 'd'] + [x.lower() for x in answers]
        question = await ctx.send(embed = embed)
        correct_answer = html.unescape(results['correct_answer'])
        def check(m):
            return m.channel == ctx.channel and m.content.lower() in available_commands and not m.author.bot
        try:
            msg = await self.client.wait_for('message', timeout = 30.0, check = check)
        except asyncio.TimeoutError:
            return
        correct = False
        if results['type'] == 'boolean':
            if msg.content.lower() == correct_answer.lower() or msg.content.lower() == correct_answer.lower()[0]:
                correct = True
            answer_string = f"The answer was **{correct_answer}**"
        else:
            letters = ['a', 'b', 'c', 'd']
            if msg.content.lower() == correct_answer.lower() or msg.content.lower() == letters[pos]:
                correct = True
            answer_string = f"The answer was **{letters[pos].upper()}) {correct_answer}**"
        if correct:
            name = ":white_check_mark:  Correct"
            if results['difficulty'] == 'easy':
                self.add_xp(ctx.author.id, 0.25)
            elif results['difficulty'] == 'medium':
                self.add_xp(ctx.author.id, 0.5)
            else:
                self.add_xp(ctx.author.id, 1)
        else:
            name = ":x:  Incorrect"
        embed2.clear_fields()
        embed2.add_field(name = name, value = answer_string)
        await question.edit(embed = embed2)

    @trivia.error
    async def trivia_error(self, ctx, error):
        await ctx.send(error)

    #@commands.max_concurrency(1, commands.BucketType.channel, wait = False)
    @commands.command(aliases = ['hang', 'hm'])
    async def hangman(self, ctx):
        with open('words3.txt') as f:
            word = random.choice(f.readlines()).rstrip("\n")
        hang = [
            "**```    ____",
            "   |    |",
            "   |    ",
            "   |   ",
            "   |    ",
            "   |   ",
            "___|__________```**"
        ]
        empty = '\n'.join(hang)
        man = [['@', 2], [' |', 3], ['\\', 3, 7], ['/', 3], ['|', 4], ['/', 5], [' \\', 5]]
        string = [':blue_square:' for i in word]
        embed = discord.Embed(
            title = "Hangman",
            color = ctx.author.color,
            description = f"Type a letter in chat to guess.\n\n**{' '.join(string)}**\n\n{empty}",
        )
        incorrect = 0
        original = await ctx.send(embed = embed)
        guessed = []
        incorrect_guessed = []
        already_guessed = None
        def check(m):
            return m.channel == ctx.channel and m.content.isalpha() and len(m.content) == 1 and m.author == ctx.author
        while incorrect < len(man) and ':blue_square:' in string:
            try:
                msg = await self.client.wait_for('message', timeout = 120.0, check = check)
                letter = msg.content.lower()
            except asyncio.TimeoutError:
                await ctx.send("Game timed out.")
                return
            if already_guessed:
                await already_guessed.delete()
                already_guessed = None
            if letter in guessed:
                already_guessed = await ctx.send("You have already guessed that letter.")
                await msg.delete()
                continue
            guessed += letter
            if letter not in word:
                incorrect_guessed += letter
                if embed.fields:
                    embed.set_field_at(0, name = "Incorrect letters:", value = ', '.join(incorrect_guessed))
                else:
                    embed.add_field(name = "Incorrect letters:", value = ', '.join(incorrect_guessed))
                part = man[incorrect]
                if len(part) > 2:
                    hang[part[1]] = hang[part[1]][0:part[2]] + part[0] + hang[part[1]][part[2] + 1:]
                else:
                    hang[part[1]] += part[0]
                incorrect += 1
            else:
                for j in range(len(word)):
                    if letter  == word[j]:
                        string[j] = word[j]
            new = '\n'.join(hang)
            if ':blue_square:' not in string:
                embed.description = f"You guessed the word!\n\n**{' '.join(string)}**\n\n{new}"
                self.add_xp(ctx.author.id, 0.5)
            elif incorrect == len(man):
                embed.description = f"You've been hanged! The word was \n\n**{' '.join([k for k in word])}**\n\n{new}"
            else:
                embed.description = f"Type a letter in chat to guess.\n\n**{' '.join(string)}**\n\n{new}"
            await msg.delete()
            await original.edit(embed = embed)

    @hangman.error
    async def hangman_error(self, ctx, error):
        await ctx.send(error)

    @commands.command(aliases = ['ttt'])
    async def tictactoe(self, ctx, *, opponent: discord.Member):
        if opponent.id == ctx.author.id:
            await ctx.send("You played yourself. Oh wait, you can't.")
            return
        if opponent.bot:
            await ctx.send("You played a bot. Oh wait, you can't.")
            return
        await ctx.send('Tictactoe has started. Type the number of the square you want to go in. Type "end_game" to end the game.')
        player1 = ctx.author
        player2 = opponent

        commands = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'end_game']

        def check(m):
            return m.channel == ctx.channel and (m.content in commands) and not m.author.bot

        def endgame(board):
            for k in range(3):
                if board[k][0] == board[k][1] and board[k][1] == board[k][2]:
                    if board[k][0] > 0:
                        return board[k][0]
                elif board[0][k] == board[1][k] and board[1][k] == board[2][k]:
                    if board[0][k] > 0:
                        return board[0][k]
            if (board[0][0] == board[1][1] and board[1][1] == board[2][2]) or (board[0][2] == board[1][1] and board[1][1] == board[2][0]):
                if board[1][1] > 0:
                    return board[1][1]
            counter = 0
            for l in range(3):
                for m in range(3):
                    if board[l][m] == 0:
                        counter += 1
            if counter == 0:
                return 3
            else:
                return 0

        board = [[0] * 3 for n in range(3)]
        end = False
        player = 1
        while not end:
            out = '```'
            for i in range(3):
                for j in range(3):
                    out += ' '
                    if board[i][j] == 0:
                        out += str(i * 3 + j + 1)
                    elif board[i][j] == 1:
                        out += 'X'
                    elif board[i][j] == 2:
                        out += 'O'
                    out += ' '
                    if j != 2:
                        out += '|'
                out += '\n'
                if i != 2:
                    out += '---+---+---\n'
            out += '```'
            await ctx.send(out)
            result = endgame(board)
            if result != 0:
                if result == 1:
                    await ctx.send(f'{player1.display_name} wins!')
                    self.add_xp(player1.id, 0.5)
                    self.add_badge(player1.id, 2)
                    return
                elif result == 2:
                    await ctx.send(f'{player2.display_name} wins!')
                    self.add_xp(player2.id, 0.5)
                    self.add_badge(player1.id, 2)
                    return
                else:
                    await ctx.send('Tie!')
                    self.add_xp(player1.id, 0.25)
                    self.add_xp(player2.id, 0.25)
                    return
            if player == 1:
                await ctx.send("{0}'s turn".format(player1.display_name))
            else:
                await ctx.send("{0}'s turn".format(player2.display_name))
            valid = False
            while not valid:
                try:
                    msg = await self.client.wait_for('message', timeout = 300.0, check = check)
                except asyncio.TimeoutError:
                    await ctx.send('Game timed out.')
                    return
                if (player == 1 and msg.author == player1) or (player == 2 and msg.author == player2):
                    if msg.content == 'end_game':
                        await ctx.send('Game ended.')
                        return
                    input = int(msg.content)
                    a = int((input - 1) / 3)
                    b = int((input - 1) % 3)
                    if board[a][b] == 0:
                        board[a][b] = player
                        player = 3 - player
                        valid = True
	
    @tictactoe.error
    async def tictactoe_error(self, ctx, error):
        print(error)
        await ctx.send('Please follow format: `y.tictactoe {opponent}`')

    @commands.command(aliases = ['2048'])
    @commands.max_concurrency(1, commands.BucketType.channel, wait = False)
    async def twentyfortyeight(self, ctx):
        available_commands = ['w', 'a', 's', 'd', 'end_game']
        await ctx.send('2048 has started. Use WASD keys to move. Type "end_game" to end the game.')
        
        def moveNumbers(input, board):
            up = False
            down = False
            left = False
            right = False
            alreadyMoved = [[False] * 4 for n in range(4)]
            if input == 'w':
                up = True
            elif input == 's':
                down = True
            elif input == 'a':
                left = True
            else:
                right = True
            for k in range(4):
                for l in range(4):
                    stop = False
                    limit = 0
                    if down or right:
                        limit = 3
                    a = 0
                    b = 0
                    if up:
                        a = l
                        b = k
                    elif down:
                        a = 3 - l
                        b = k
                    elif left:
                        a = k
                        b = l
                    else:
                        a = k
                        b = 3 - l
                    while not stop:
                        if up or down:
                            c = a - 1
                            if down:
                                c = a + 1
                            if a == limit:
                                stop = True
                            else:
                                if board[c][b] == 0:
                                    board[c][b] = board[a][b]
                                    board[a][b] = 0
                                    a = c
                                elif board[c][b] == board[a][b] and alreadyMoved[c][b] != True:
                                    board[c][b] = board[c][b] * 2
                                    board[a][b] = 0
                                    alreadyMoved[c][b] = True
                                    stop = True
                                else:
                                    stop = True
                        else:
                            c = b - 1
                            if right:
                                c = b + 1
                            if b == limit:
                                stop = True
                            else:
                                if board[a][c] == 0:
                                    board[a][c] = board[a][b]
                                    board[a][b] = 0
                                    b = c
                                elif board[a][c] == board[a][b] and alreadyMoved[a][c] != True:
                                    board[a][c] = board[a][c] * 2
                                    board[a][b] = 0
                                    alreadyMoved[a][c] = True
                                    stop = True
                                else:
                                    stop = True
        
        end = False
        win = False
        start = True
        board = [[0] * 4 for n in range(4)]
        empty2 = 0
        empty = 0
        emptyX = []
        emptyY = []
        input = ''
        counter = 0
        while not end:
            canMove = False
            empty2 = 0
            if start:
                randX = random.randint(0, 3)
                randY = random.randint(0, 3)
                board[randX][randY] = 2
            out = '``` -------------------\n'
            for i in range(4):
                for j in range(4):
                    if i == 0:
                        if j == 0:
                            if board[i][j] == board[i + 1][j] or board[i][j] == board[i][j + 1]:
                                canMove = True
                        elif j == 3:
                            if board[i][j] == board[i + 1][j] or board[i][j] == board[i][j - 1]:
                                    canMove = True
                        else:
                            if board[i][j] == board[i + 1][j] or board[i][j] == board[i][j + 1] or board[i][j] == board[i][j - 1]:
                                    canMove = True
                    elif i == 3:
                        if j == 0:
                            if board[i][j] == board[i - 1][j] or board[i][j] == board[i][j + 1]:
                                canMove = True
                        elif j == 3:
                            if board[i][j] == board[i - 1][j] or board[i][j] == board[i][j - 1]:
                                canMove = True
                        else:
                            if board[i][j] == board[i][j + 1] or board[i][j] == board[i - 1][j] or board[i][j] == board[i][j - 1]:
                                canMove = True
                    else:
                        if j == 0:
                            if board[i][j] == board[i - 1][j] or board[i][j] == board[i][j + 1] or board[i][j] == board[i + 1][j]:
                                canMove = True
                        elif j == 3:
                            if board[i][j] == board[i - 1][j] or board[i][j] == board[i][j - 1] or board[i][j] == board[i + 1][j]:
                                canMove = True
                        else:
                            if board[i][j] == board[i][j + 1] or board[i][j] == board[i - 1][j] or board[i][j] == board[i][j - 1] or board[i][j] == board[i + 1][j]:
                                canMove = True
                    if board[i][j] == 2048:
                        win = True
                    if board[i][j] == 0:
                        empty2 += 1
                        out += '|    '
                    elif board[i][j] > 0 and board[i][j] < 10:
                        out += '|  ' + str(board[i][j]) + ' '
                    elif board[i][j] >= 10 and board[i][j] < 100:
                        out += '| ' + str(board[i][j]) + ' '
                    elif board[i][j] >= 100 and board[i][j] < 1000:
                        out += '| ' + str(board[i][j])
                    elif board[i][j] >= 1000 and board[i][j] < 10000:
                        out += '|' + str(board[i][j])
                out += '|\n'
                if i != 3:
                    out += '|----+----+----+----|\n'
            out += ' -------------------```'
            if start:
                msg2 = await ctx.send(out)
            else:
                await msg2.edit(content = out)
            if win:
                await ctx.send('You won!')
                self.add_xp(ctx.author.id, 10)
                self.add_badge(ctx.author.id, 1)
                return
            elif empty2 == 0 and not canMove:
                await ctx.send('Game over.')
                self.add_xp2(ctx.author.id, counter)
                return
            valid = False
            while not valid:
                try:
                    msg = await self.client.wait_for('message', timeout = 300.0)
                except asyncio.TimeoutError:
                    await ctx.send('Game timed out.')
                    return
                if msg.channel == ctx.channel and msg.author == ctx.author:
                    if msg.content in available_commands:
                        content = msg.content
                        if content == 'end_game':
                            await ctx.send('Game ended.')
                            print(counter)
                            return
                        valid = True
                    await msg.delete()
            board2 = [row[:] for row in board]
            moveNumbers(content, board)
            for k in range(4):
                for l in range(4):
                    if board[k][l] == 0:
                        empty += 1
                        emptyX.append(k)
                        emptyY.append(l)

            if board != board2 and empty != 0:
                pos = random.randint(0, empty - 1)
                board[emptyX[pos]][emptyY[pos]] = 2 + (random.randint(0, 1) * 2)
                counter += 1
            empty = 0
            emptyX = []
            emptyY = []
            start = False

    @twentyfortyeight.error
    async def twentyfortyeight_error(self, ctx, error):
        await ctx.send(error)

def setup(client):
    client.add_cog(games(client))