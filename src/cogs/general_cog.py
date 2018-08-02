import discord
from discord.ext import commands

from ..helpers import simple_paginator
from ..helpers.simple_paginator import SimplePaginator

import inspect
import textwrap
import re


class GeneralCommands:
    """Commands for everyone."""

    icon = "<:quantaperson:473983023797370880>"

    def __init__(self, database):
        self.database = database

    @commands.command(usage="ping")
    async def ping(self, ctx: commands.Context, round_to=4):
        """Returns the bot latency.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.

        Keyword Arguments:
            exact {int} -- How many digits to round the bot latency to. (default: {4})
        """

        # Check digits is a string then casefold
        if isinstance(round_to, str) and (
            round_to.casefold() == "true" or round_to.casefold() == "exact"
        ):
            pingTime = ctx.bot.latency
        elif isinstance(round_to, str) and round_to.isdigit():
            pingTime = round(ctx.bot.latency, int(round_to))
        else:
            pingTime = round(ctx.bot.latency, 4)

        await ctx.send("Pong! | {0} seconds".format(pingTime))

    @commands.command(aliases=["commands"], usage="help (command)")
    async def help(self, ctx: commands.Context, command=None):
        """Show a complete list of commands you can use. Or information about a specific one.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            command -- a command to get specific help about. (default: {None})
        """
        embed = discord.Embed(
            title="<:quantabadge:473675013786959891> **Help**",
            color=0xf1c40f,  # gold
            description="Quanta is a multipurpose bot for simplifying your life.",
        )
        for name, cog in ctx.bot.cogs.items():
            name = re.sub("([a-z])(?=[A-Z])", r"\1 ", name)
            members = inspect.getmembers(cog)
            description = ""
            icon = getattr(cog, "icon", None)
            for _, member in members:
                if not isinstance(member, commands.Command):
                    continue
                command = member
                command_usage = member.usage
                if command.hidden == True:
                    continue
                description += "**{}**\n".format(command_usage)
            if description:
                header = name
                if icon is not None:
                    header = "{} {}".format(icon, name)
                embed.add_field(name=header, value=description, inline=True)
        await ctx.send(embed=embed)
