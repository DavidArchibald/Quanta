#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands

import datetime
import os
import sys
import time

import asyncio
import subprocess

from ..helpers import bot_states
from ..helpers.helper_functions import confirm_action

states = bot_states.BotStates()


class DeveloperCommands:
    """Commands just for the developer, mainly for testing."""

    icon = "<:quantacode:473976436051673091>"

    def __init__(self, database):
        self.database = database

    @commands.command(hidden=True, aliases=["speak"], usage="say [message]")
    @commands.has_role("Quanta's Owner")
    async def say(self, ctx: commands.Context, *, text: str):
        """Says what you say!

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            text {str} -- The text for the bot to say.
        """

        await ctx.message.delete()
        await ctx.send(text)

    @commands.command(hidden=True, aliases=["stop", "shutdown", "end"], usage="kill")
    @commands.has_role("Quanta's Owner")
    async def kill(self, ctx: commands.Context):
        """Bye bye Quanta...

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        confirm = await confirm_action(ctx)
        if not confirm:
            return

        await ctx.send("Goodbye...")
        await ctx.bot.logout()

    @commands.command(
        hidden=True, aliases=["guildinfo", "guild-info"], usage="guildinfo"
    )
    @commands.has_role("Quanta's Owner")
    async def guild_info(self, ctx: commands.Context):
        """Retrieve info about this guild.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        guild = ctx.guild
        embed = discord.Embed()

        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Name", value=guild.name)
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Created at", value=guild.created_at.strftime("%x"))
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Channels", value=len(guild.channels))
        embed.add_field(
            name="Roles", value=len(guild.role_hierarchy) - 1
        )  # Remove @everyone
        embed.add_field(name="Emoji", value=len(guild.emojis))
        embed.add_field(name="Region", value=guild.region.name)
        embed.add_field(
            name="Icon URL", value=guild.icon_url or "This guild has no icon."
        )

        await ctx.send(embed=embed)

    @commands.command(
        hidden=True, aliases=["force", "dev"], usage="sudo (quiet) [command] [*args]"
    )
    @commands.has_role("Quanta's Owner")
    async def sudo(self, ctx: commands.Context, *args):
        """Force a command to be run without perms from the user.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            quiet {bool} -- Whether to run silently or not.

        """

    @commands.command(hidden=True, aliases=["run"], usage="eval [code]")
    async def eval(self, ctx: commands.Context, quiet: bool = False):
        """Runs arbitrary code.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        pass

    async def __local_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def update(self, ctx: commands.Context):
        """Loads changes and then reruns the bot.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """
        try:
            git_update = await asyncio.create_subprocess_exec(
                "git help", loop=ctx.bot.loop
            )
        except NotImplementedError:
            await states.error(
                ctx,
                "The OS this script is running on does not support running commands on their command line through Python.",
            )
            return
        stdout, stderr = await git_update.communicate()
        result = stdout.decode().strip()
        print(result)
