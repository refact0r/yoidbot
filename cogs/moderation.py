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
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.manage_nicknames:
            await ctx.send("You do not have the permissions to use this command.")
            return
        if nick and len(nick) < 2:
            await ctx.send("That nickname is too short. It must be 2 characters or more.")
            return
        if nick and len(nick) > 32:
            await ctx.send("That nickname is too long. It must be 32 characters or less.")
            return
        previous_name = member.display_name
        try:
            await member.edit(nick = nick)
        except Exception:
            print(Exception)
            await ctx.send("I cannot nickname this member.")
            return
        if not nick:
            await ctx.send(f"{previous_name}'s nickname was reset.")
        else:
            await ctx.send(f"{previous_name} was nicknamed {nick}.")

    @nickname.error
    async def nickname_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.nickname {person} {name}`")

    @commands.command(aliases = ['na', 'nicknameall'])
    async def nickall(self, ctx, *, args = None):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the permissions to use this command.")
            return
        if len(ctx.guild.members) > 50:
            await ctx.send("Nickall cannot be used on guilds with over 50 members.")
            return
        if not args:
            msg = await ctx.send(f"Resetting all nicks... (This may take a while)")
        else:
            if len(args) < 2:
                await ctx.send("That nickname is too short. It must be 2 characters or more.")
                return
            if len(args) > 32:
                await ctx.send("That nickname is too long. It must be 32 characters or less.")
                return
            msg = await ctx.send(f"Nicknaming everyone to {args}... (This may take a while)")
        for p in ctx.guild.members:
            try:
                await p.edit(nick = args)
            except Exception:
                print(Exception)
                pass
        if args:
            await msg.edit(content = f"All members were nicknamed {args}.")
        else:
            await msg.edit(content = f"All nicks were reset.")

    @nickall.error
    async def nickall_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.nickall {name}`")
       
    @commands.command(aliases = ['c', 'purge'])
    async def clear(self, ctx, amount):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
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
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.manage_permissions:
            await ctx.send("You do not have the permissions to use this command.")
            return
        converter = MemberConverter()
        try:
            member = await converter.convert(ctx, member)
        except Exception:
            print(Exception)
            await ctx.send("Member not found.")
            return
        found = False
        role = None
        for r in ctx.guild.roles:
            if r.name == "Muted":
                role = r
                found = True
        if not found:
            role = await ctx.guild.create_role(name = "Muted", color = discord.Color(0x505050))
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages = False)
        await member.add_roles(role)
        await ctx.send(member.display_name + ' was muted.')

    @mute.error
    async def mute_error(self, ctx, error):
        print(error)
        await ctx.send("Please follow format: `y.mute {person}`")

    @commands.command(aliases = ['um'])
    async def unmute(self, ctx, *, member):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.manage_permissions:
            await ctx.send("You do not have the permissions to use this command.")
            return
        converter = MemberConverter()
        try:
            member = await converter.convert(ctx, member)
        except Exception:
            print(Exception)
            await ctx.send("Member not found.")
            return
        role = discord.utils.get(member.guild.roles, name = "Muted")
        await member.remove_roles(role)
        await ctx.send(member.display_name + ' was unmuted.')

    @unmute.error
    async def unmute_error(self, ctx, error):
        print(error)
        await ctx.send('Please follow format: `y.unmute {person}`')

    @commands.command(aliases = ['ma'])
    async def muteall(self, ctx):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the permissions to use this command.")
            return
        if len(ctx.guild.members) > 50:
            await ctx.send("Muteall cannot be used on guilds with over 50 members.")
            return
        msg = await ctx.send("Muting all members... (This may take a while)")
        found = False
        role = None
        for r in ctx.guild.roles:
            if r.name == "Muted" and not r.permissions.send_messages:
                role = r
                found = True
        if not found:
            perms = discord.Permissions(send_messages = False)
            role = await ctx.guild.create_role(name = "Muted", permissions = perms)
        for p in ctx.guild.members:
            try:
                await p.add_roles(role)
            except Exception:
                print(Exception)
                pass
        await msg.edit(content = "All members were muted.")

    @commands.command(aliases = ['uma'])
    async def unmuteall(self, ctx):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You do not have the permissions to use this command.")
            return
        if len(ctx.guild.members) > 50:
            await ctx.send("Muteall cannot be used on guilds with over 50 members.")
            return
        msg = await ctx.send("Unmuting all members... (This may take a while)")
        found = False
        role = None
        for r in ctx.guild.roles:
            if r.name == "Muted" and not r.permissions.send_messages:
                role = r
                found = True
        if not found:
            perms = discord.Permissions(send_messages = False)
            role = await ctx.guild.create_role(name = "Muted", permissions = perms)
        for m in ctx.guild.members:
            for n in m.roles:
                if n == role:
                    await m.remove_roles(n)
                    break
        await msg.edit(content = "All members were unmuted.")

    @commands.command(aliases = ['k', 'yoink'])
    async def kick(self, ctx, *, bad_person):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send("You do not have the permissions to use this command.")
            return
        converter = MemberConverter()
        try:
            member = await converter.convert(ctx, bad_person)
        except Exception:
            print(Exception)
            await ctx.send("Member not found.")
            return
        try:
            await member.guild.kick(member)
        except Exception:
            print(Exception)
            await ctx.send("I cannot kick this member.")
            return
        await ctx.send(member.display_name + ' was kicked.')
    
    @kick.error
    async def kick_error(self, ctx, error):
        print(error)
        await ctx.send('Please follow format: `y.kick {person}`')

def setup(client):
    client.add_cog(moderation(client))