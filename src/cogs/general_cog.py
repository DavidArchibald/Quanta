#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands

from ..helpers import simple_paginator
from ..helpers.simple_paginator import SimplePaginator

import inspect
import re
import textwrap


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
            ping_time = ctx.bot.latency
        elif isinstance(round_to, str) and round_to.isdigit():
            ping_time = round(ctx.bot.latency, int(round_to))
        else:
            ping_time = round(ctx.bot.latency, 4)

        await ctx.send(f"Pong! | {ping_time} seconds")

    @commands.command(aliases=["commands"], usage="help (command)")
    async def help(self, ctx: commands.Context, command=None):
        """Show a complete list of commands you can use. Or information about a specific one.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            command -- a command to get specific help about. (default: {None})
        """
        if command is None:
            embed = discord.Embed(
                title="<:quantabadge:473675013786959891> **Help**",
                color=0xf1c40f,  # gold
                description=textwrap.dedent(
                    """
                    Quanta is a multipurpose bot for simplifying your life.
                    """
                ),
            )
            for name, cog in ctx.bot.cogs.items():
                name = re.sub(
                    "([a-z])(?=[A-Z])", r"\1 ", name
                )  # Turns PascalCase to Title Case
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
                    description += f"**{command_usage}**\n"
                if description:
                    header = name
                    if icon is not None:
                        header = f"{icon} {name}"
                    embed.add_field(name=header, value=description, inline=True)

            embed.add_field(
                name="\u200B",
                value=textwrap.dedent(
                    f"""**Commands are written in the format command [required] (optional)**

                    To see more information about a specific command use {ctx.prefix}help (command)
                    """
                ),
            )
        else:
            print(dir(ctx))

        await ctx.send(embed=embed)
