import discord
import asyncio
import random
from discord.ext import commands
from discord.ext.commands import MemberConverter

class moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['nick', 'n'])
    async def nickname(self, ctx, member: discord.Member, *, nick = None):
        if not ctx.author.guild_permissions.manage_nicknames:
            await ctx.send("You do not have the permissions to use this command.")
            return
        previous_name = member.display_name
        try:
            await member.edit(nick = nick)
        except:
            await ctx.send("I cannot nick this member.")
            return
        if not nick:
            await ctx.send(f"{previous_name}'s nick was reset.")
        else:
            await ctx.send(f"{previous_name} was nicked {nick}.")

    @nickname.error
    async def nickname_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.nickname {person} {name}`")

    @commands.command(aliases = ['na', 'nicknameall'])
    async def nickall(self, ctx, *, args = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the permissions to use this command.")
            return
        if not args:
            msg = await ctx.send(f"Resetting all nicks... (This may take a while)")
        else:
            msg = await ctx.send(f"Nicknaming everyone to {args}... (This may take a while)")
        if len(ctx.guild.members) > 50:
            await ctx.send("Muteall cannot be used on guilds with over 50 members.")
            return
        for p in ctx.guild.members:
            try:
                await p.edit(nick = args)
            except:
                pass
        await msg.edit(content = "Done!")

    @nickall.error
    async def nickall_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.nickall {name}`")
       
    @commands.command(aliases = ['c', 'purge'])
    async def clear(self, ctx, amount):
        if not amount.isdigit():
            await ctx.send("Please follow format: `y.clear {amount}`")
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have the permissions to use this command.")
            return
        await ctx.channel.purge(limit = int(amount) + 1)

    @clear.error
    async def clear_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.clear {amount}`")

    @commands.command(aliases = ['m'])
    async def mute(self, ctx, *, member):
        if not ctx.author.guild_permissions.manage_permissions:
            await ctx.send("You do not have the permissions to use this command.")
            return
        converter = MemberConverter()
        try:
            member = await converter.convert(ctx, member)
        except:
            await ctx.send("Member not found.")
            return
        await ctx.send(member.display_name + ' was muted.')
        found = False
        for r in ctx.guild.roles:
            if r.name == "Muted":
                role = r
                found = True
        if not found:
            role = await ctx.guild.create_role(name = "Muted", color = discord.Color(0x505050))
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages = False)
        await member.add_roles(role)

    @mute.error
    async def mute_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.mute {person}`")

    @commands.command(aliases = ['um'])
    async def unmute(self, ctx, *, member):
        if not ctx.author.guild_permissions.manage_permissions:
            await ctx.send("You do not have the permissions to use this command.")
            return
        converter = MemberConverter()
        try:
            member = await converter.convert(ctx, member)
        except:
            await ctx.send("Member not found.")
            return
        await ctx.send(member.display_name + ' was unmuted.')
        role = discord.utils.get(member.guild.roles, name = "Muted")
        await member.remove_roles(role)

    @unmute.error
    async def unmute_error(self, ctx, error):
        print(error)
        await ctx.send('Please follow format: `y.unmute {person}`')

    @commands.command(aliases = ['ma'])
    async def muteall(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the permissions to use this command.")
            return
        await ctx.send("All non-admins were muted.")
        found = False
        for r in ctx.guild.roles:
            if r.name == "Muted" and not r.permissions.send_messages:
                role = r
                found = True
        if not found:
            perms = discord.Permissions(send_messages = False)
            role = await ctx.guild.create_role(name = "Muted", permissions = perms)
        if len(ctx.guild.members) > 50:
            await ctx.send("Muteall cannot be used on guilds with over 50 members.")
            return
        for p in ctx.guild.members:
            try:
                await p.add_roles(role)
            except:
                pass

    @commands.command(aliases = ['uma'])
    async def unmuteall(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the permissions to use this command.")
            return
        await ctx.send("All muted members were unmuted.")
        found = False
        for r in ctx.guild.roles:
            if r.name == "Muted" and not r.permissions.send_messages:
                role = r
                found = True
        if not found:
            perms = discord.Permissions(send_messages = False)
            role = await ctx.guild.create_role(name = "Muted", permissions = perms)
        if len(ctx.guild.members) > 50:
            await ctx.send("Muteall cannot be used on guilds with over 50 members.")
            return
        for m in ctx.guild.members:
            for n in m.roles:
                if n == role:
                    await m.remove_roles(n)
                    break

    @commands.command(aliases = ['k', 'yoink'])
    async def kick(self, ctx, *, bad_person):
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("You do not have the permissions to use this command.")
            return
        converter = MemberConverter()
        try:
            member = await converter.convert(ctx, bad_person)
        except:
            await ctx.send("Member not found.")
            return
        try:
            await member.guild.kick(member)
        except:
            await ctx.send("I cannot kick this member.")
            return
        await ctx.send(member.display_name + ' was kicked.')
    
    @kick.error
    async def kick_error(self, ctx, error):
        print(error)
        await ctx.send('Please follow format: `y.kick {person}`')

def setup(client):
    client.add_cog(moderation(client))