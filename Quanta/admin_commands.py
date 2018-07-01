import discord
from discord.ext import commands

import helper_functions
from helper_functions import HelperCommands

from helper_functions import GetUserConverter

import asyncio

helperCommands = HelperCommands()

class AdminCommands:
    """Special commands just for Admins."""

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, limit: int = 100, user: GetUserConverter = "all"):
        """Deletes a number of messages by a user.
        
        Arguments:
            ctx {commands.context} -- Information about where the command was run.
        
        Keyword Arguments:
            limit {int} -- The max number of messages to purge (default: {100})
            user {GetUserConverter} -- Fuzzy user getting (default: {"all"})
        """

        await ctx.message.delete()
        
        if user == None or user.casefold() == "all":
            await ctx.channel.purge(limit=limit)
        
        def check_user(message):
            return user == None or user.casefold() == "all" or message.author == user
        
        await ctx.channel.purge(limit=limit, check=check_user)

    @commands.command(aliases=["clearall", "clear_all", "clear-all"])
    @commands.has_permissions(manage_messages=True)
    async def clearAll(self, ctx: commands.Context):
        """Remove all messsages.
        
        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        await ctx.message.delete()
        confirm=await helperCommands.confirmAction(ctx)
        if not confirm:
            return
        
        async for message in ctx.channel.history(limit=None):
            await message.delete()
        #print(len(await ctx.channel.history(limit=None).flatten()))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.context, user: GetUserConverter, reason=""):
        """Kick a user.
        
        Arguments:
            ctx {commands.context} -- Information about where a command was run.
            user {GetUserConverter} -- Fuzzy user getting.
        
        Keyword Arguments:
            reason {str} -- Why the user is being kicked (default: {""})
        """

        await ctx.kick(user)
        await ctx.send("kicked {0}".format(user))
