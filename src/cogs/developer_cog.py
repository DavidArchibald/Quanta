#!/usr/bin/env python3

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

from ..constants import emojis

exit_handler = exit_handling.get_exit_handler()

states = bot_states.BotStates()


class DeveloperCommands:
    """Commands just for the developer, mainly for testing."""

    icon = "<:quantacode:473976436051673091>"

    def __init__(self, database):
        self.database = database
        self._last_result = None

    @commands.command(hidden=True, aliases=["speak"], usage="say [message]")
    async def say(self, ctx: commands.Context, *, text: str):
        """Says what you say!

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            text {str} -- The text for the bot to say.
        """

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
            wait {str} -- How long to wait until killing.
        """

        if isinstance(wait, str) and wait.casefold() in ("now", "immediately", "force"):
            wait = 0

        try:
            wait = int(wait)
        except ValueError:
            await ctx.send(f'Invalid argument "{wait}" for wait.')
            return

        confirm, message = await confirm_action(ctx)
        if not confirm:
            await message.edit(content="")
            return

        await message.edit(content="Shutting down...")

        await message.add_reaction(emojis.loading)

        exit_handler.terminate()  # This won't close it because this command will still be running.

        for _ in range(0, wait):
            commands_running = exit_handler.get_commands_running() - 1
            if commands_running == 0:
                try:
                    await message.clear_reactions()
                except discord.HTTPException:
                    await message.remove_reaction(emojis.loading, ctx.bot.user)
                await message.edit(content="Goodbye!")
                sys.exit(0)
            await asyncio.sleep(1)

        if commands_running > 0:
            s = "s" if commands_running != 1 else ""
            if commands_running != 0:
                logging.warn(
                    f"Forcing shutdown! {commands_running} command{s} left hanging."
                )
                try:
                    await message.clear_reactions()
                except discord.HTTPException:
                    await message.remove_reaction(emojis.loading, ctx.bot.user)
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
    async def eval(self, ctx: commands.Context, *, code: str):
        """Runs arbitrary code.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        environment = {
            "bot": ctx.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        environment.update(globals())

        code = cleanup_code(code)

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
        result = f"```diff\n{error}\n{output}```"
        if len(result) > 1000:
            result_truncated = "\n**---Output Truncated---**"
            result = result[1000 - len(result_truncated)] + result_truncated
        await ctx.send(result)

    async def __local_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)


def cleanup_code(content):
    """Removes codeblocks from string.

    Arguments:
        content {str} -- String with potential codeblocks.
    """

    code_languages = [
        "asciidoc",
        "autohotkey",
        "bash",
        "coffeescript",
        "cpp",
        "cs",
        "css",
        "diff",
        "fix",
        "glsl",
        "ini",
        "json",
        "md",
        "markdown",
        "ml",
        "prolog",
        "py",
        "python",
        "tex",
        "xl",
        "xml",
    ]

    if content.startswith("```") and content.endswith("```"):
        content = content[3:-3]
        content_lines = content.split("\n")
        if content_lines[0].trim().casefold() in code_languages:
            content = content_lines[1:].join("\n")

    if content.startswith("`") and content.endswith("`"):
        content = content[1:-1]

    return content


def setup(bot, database):
    bot.add_cog(DeveloperCommands(database))
