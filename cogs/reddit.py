import discord
import asyncio
import random
from discord.ext import commands
import os
import praw
from prawcore import NotFound

r = praw.Reddit(client_id="6-R1PtP82qhAEQ",
        client_secret=os.getenv('REDDIT_SECRET'),
        user_agent="yoidbot")

class reddit(commands.Cog): 

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['me', 'mem', 'mme', 'meem'])
    async def meme(self, ctx):
        submissions = []
        i = random.randint(1, 200)
        submissions = list(r.subreddit("dankmemes").hot(limit=i))
        submission = submissions[i - 1]
        submission = submissions[random.randint(0, len(submissions) - 1)]
        embed = discord.Embed(
            title = submission.title,
            url = f"https://reddit.com{submission.permalink}",
            color = ctx.author.color,
        )
        embed.set_footer(text = f"{submission.score} points | {submission.num_comments} comments")
        if submission.over_18:
            embed.description = f":warning: NSFW\n\n[{submission.title}](https://reddit.com{submission.permalink})"
            await ctx.send(embed = embed)
            return
        if submission.url.startswith('https://i.redd.it/'):
            embed.set_image(url = submission.url)
            await ctx.send(embed = embed)
        elif submission.url.startswith('https://v.redd.it/'):
            await ctx.send(submission.url)
        else:
            await ctx.send(embed = embed)
            await ctx.send(submission.url)

    @meme.error
    async def meme_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.meme {subreddit}`")

    @commands.command(aliases = ['frie', 'f'])
    async def fries(self, ctx):
        submissions = []
        for submission in r.subreddit("foodporn+food").search("title:fries", limit = 100):
            if submission.score > 100:
                submissions.append(submission)
        submission = submissions[random.randint(0, len(submissions) - 1)]
        embed = discord.Embed(
            title = submission.title,
            url = f"https://reddit.com{submission.permalink}",
            color = ctx.author.color,
        )
        embed.set_footer(text = f"{submission.score} points | {submission.num_comments} comments")
        if submission.url.startswith('https://i.redd.it/'):
            embed.set_image(url = submission.url)
            await ctx.send(embed = embed)
        elif submission.url.startswith('https://v.redd.it/'):
            await ctx.send(submission.url)
        else:
            await ctx.send(embed = embed)
            await ctx.send(submission.url)

    @fries.error
    async def fries_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.fries {subreddit}`")

    @commands.command(aliases = ['r', 'reddi', 'redd', 'red', 're'])
    async def reddit(self, ctx, subreddit):
        submissions = []
        def check_subreddit(subreddit):
            valid = True
            if subreddit == 'all' or subreddit == 'popular':
                return valid
            try:
                r.subreddit(subreddit).subreddit_type
            except:
                valid = False
            return valid
        if not check_subreddit(subreddit):
            await ctx.send("Invalid subreddit.")
            return
        for submission in r.subreddit(subreddit).hot(limit=50):
            submissions.append(submission)
        submission = submissions[random.randint(0, len(submissions) - 1)]
        embed = discord.Embed(
            description = f"[{submission.title}](https://reddit.com{submission.permalink})",
            title = f"r/{subreddit}",
            color = ctx.author.color,
        )
        embed.set_footer(text = f"{submission.score} points | {submission.num_comments} comments")
        if submission.is_self:
            embed.description += f"\n\n{submission.selftext}"
            await ctx.send(embed = embed)
            return
        if submission.over_18 and not ctx.channel.is_nsfw():
            await ctx.send("NSFW commands can only be used in a NSFW channel.")
            return
        if submission.url.startswith('https://i.redd.it/'):
            embed.set_image(url = submission.url)
            await ctx.send(embed = embed)
        elif submission.url.startswith('https://v.redd.it/'):
            await ctx.send(submission.url)
        elif submission.url.startswith('/r/'):
            embed.description += f"\n\nhttps://reddit.com{submission.url}"
            await ctx.send(embed = embed)
        else:
            await ctx.send(embed = embed)
            await ctx.send(submission.url)

    @reddit.error
    async def reddit_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.reddit {subreddit}`")
        
def setup(client):
    client.add_cog(reddit(client))