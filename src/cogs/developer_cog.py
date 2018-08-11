#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands

import datetime
import os
import sys
import time
import logging

import asyncio
import subprocess

from ..helpers import bot_states
from ..helpers.helper_functions import confirm_action
from ..handlers import exit_handling

states = bot_states.BotStates()


class DeveloperCommands:
    """Commands just for the developer, mainly for testing."""

    icon = "<:quantacode:473976436051673091>"

    def __init__(self, database):
        self.database = database

    @commands.command(hidden=True, aliases=["speak"], usage="say [message]")
    async def say(self, ctx: commands.Context, *, text: str):
        """Says what you say!

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            text {str} -- The text for the bot to say.
        """

        await ctx.message.delete()
        await ctx.send(text)

    @commands.command(
        hidden=True,
        aliases=["stop", "shutdown", "end", "terminate"],
        usage="kill (wait)",
    )
    async def kill(self, ctx: commands.Context, wait: str = 30):
        """Bye bye Quanta...

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            force {boolean} -- Forces the command
        """

        if isinstance(wait, str) and wait.casefold() in ("now", "immediately", "force"):
            wait = 0

        try:
            wait = int(wait)
        except:
            ctx.send('Invalid argument "wait"')
            return

        confirm, message = await confirm_action(ctx)
        if not confirm:
            return

        await message.edit(content="Goodbye!")
        exit_handling.terminate()

        for _ in range(0, wait):
            commands_running = exit_handling.get_commands_running() - 1
            if commands_running == 0:
                try:
                    sys.exit(0)
                except SystemExit:
                    pass
            await asyncio.sleep(1)

        if commands_running > 0:
            s = "s" if commands_running != 1 else ""
            if commands_running != 0:
                logging.warn(
                    f"Forcing shutdown! {commands_running} command{s} left hanging."
                )
                await message.edit(
                    content=f"{commands_running} command{s} aborted to allow shutdown."
                )
            await ctx.bot.logout()
            sys.exit(0)

    @commands.command(
        hidden=True, aliases=["guildinfo", "guild-info"], usage="guildinfo"
    )
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
    @commands.is_owner()
    async def sudo(self, ctx: commands.Context, command=None, *, arguments=""):
        """Force a command to be run without perms from the user.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            quiet {bool} -- Whether to run silently or not.

        """

        new_message = ctx.message
        new_message.content = f"{ctx.prefix}{command} {arguments}"

        new_ctx = await ctx.bot.get_context(new_message)
        await new_ctx.command._parse_arguments(new_ctx)  # Parses the arguments
        await new_ctx.command.call_before_hooks(new_ctx)  # Calls command hooks

        await new_ctx.command.callback(*new_ctx.args, **new_ctx.kwargs)

    @commands.command(hidden=True, aliases=["run"], usage="eval [code]")
    async def eval(self, ctx: commands.Context, quiet: bool = False):
        """Runs arbitrary code.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """
        print(ctx, quiet)

        pass

    @commands.command(hidden=True)
    async def update(self, ctx: commands.Context):
        """Loads changes and then reruns the bot.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """
        try:
            git_update = await asyncio.create_subprocess_shell(
                "git pull origin master",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                loop=ctx.bot.loop,
            )
        except NotImplementedError:
            await states.error(
                ctx,
                "The OS this script is running on does not support running commands on their command line through Python.",
            )
            return
        stdout, stderr = await git_update.communicate()
        error = stderr.decode().strip()
        output = stdout.decode().strip()
        result = f"```css\n{error}\n{output}```"
        if len(result) > 1000:
            result_truncated = "\n**---Output Truncated---**"
            result_truncated_length = 23
            result = result[1000 - result_truncated_length] + result_truncated
        await ctx.send(result)

    async def __local_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)


def setup(bot, database):
    bot.add_cog(DeveloperCommands(database))
