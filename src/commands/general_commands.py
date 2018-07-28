import discord
from discord.ext import commands

from ..helpers import simple_paginator
from ..helpers.simple_paginator import SimplePaginator

import inspect
import textwrap

class GeneralCommands:
    """Commands for everyone."""

    def __init__(self, database):
        self.database = database

    @commands.command()
    async def ping(self, ctx: commands.Context, round_to=4):
        """Returns the bot latency.
        
        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
        
        Keyword Arguments:
            exact {int} -- How many digits to round the bot latency to. (default: {4})
        """

        # Check digits is a string then casefold
        if isinstance(round_to, str) and (round_to.casefold() == "true" or round_to.casefold() == "exact"):
            pingTime = ctx.bot.latency
        elif isinstance(round_to, str) and round_to.isdigit():
            pingTime = round(ctx.bot.latency, int(round_to))
        else:
            pingTime = round(ctx.bot.latency, 4) #fallback

        await ctx.send("Pong! | {0} seconds".format(pingTime))
    
    @commands.command(aliases=["h", "commands"])
    async def help(self, ctx: commands.Context, command=None):
        """Show a complete list of commands you can use. Or information about a specific one.
        
        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            command -- a command to get specific help about. (default: {None})
        """
        embed = discord.Embed(
            title = "__Help__",
            color = 0xf1c40f, # gold
            description = "hi this is a description for help because logic"
        )
        print(ctx.bot.cogs)
        for name, cog in ctx.bot.cogs.items():
            print(ctx.bot.cogs.values())
            members = inspect.getmembers(cog)
            description = ""
            for memberName, member in members:
                if not isinstance(member, commands.Command):
                    continue
                command = member # just a stylistic thing, no need for it.
                commandName = memberName
                if command.hidden == True:
                    continue
                description += "**{}**\n".format(commandName)
                #description += "    \n".join(textwrap.wrap(command.help.split('\n')[0], width=22)) + "\n"
            if description:
                embed.add_field(name = name, value = description, inline = True)
        await ctx.send(embed = embed)
