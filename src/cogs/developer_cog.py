#!/usr/bin/env python3

import discord
from discord.ext import commands

import time

import logging

import asyncio

import contextlib
import io
import re

import textwrap
import tabulate

from typing import Union, Optional

from ..helpers import embed_builder
from ..helpers.helper_functions import confirm_action

from ..handlers import exit_handling

from ..globals import emojis, variables

exit_handler = exit_handling.get_exit_handler()
build_embed = embed_builder.EmbedBuilder()


class DeveloperCommands:
    """Commands just for the developer, mainly for testing."""

    icon = "<:quantacode:473976436051673091>"

    def __init__(self) -> None:
        self.database = variables.database
        self._last_result: Optional[str] = None

    @commands.command(name="Say", aliases=["speak"], usage="say [message]", hidden=True)
    async def say(self, ctx: commands.Context, *, text: str):
        """Says what you say!

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            text {str} -- The text for the bot to say.
        """

        await ctx.send(text)

    @commands.command(
        name="Kill",
        aliases=["stop", "shutdown", "end", "terminate"],
        usage="kill (wait)",
        hidden=True,
    )
    async def kill(self, ctx: commands.Context, wait: Union[str, int] = 30):
        """Bye bye Quanta...

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            wait {str} -- How long to wait until killing.
        """
        message: discord.Message = None
        shutting_down = "Shutting down..."
        if isinstance(wait, str) and wait.casefold() in ("now", "immediately", "force"):
            wait = 0
            commands_running = exit_handler.get_commands_running()
            if commands_running > 0:
                confirm, message = await confirm_action(
                    ctx,
                    message=(
                        f"This will leave {commands_running} commands hanging. "
                        "Are you sure you want to force shutdown?",
                    ),
                )
                if not confirm:
                    await message.edit(content="I'll keep runnin' then.")
                    return

        if message is not None:
            await message.edit(content=shutting_down)
        else:
            message = await ctx.send(shutting_down)

        try:
            wait = int(wait)
        except ValueError:
            await ctx.send(f'Invalid argument "{wait}" for wait.')
            return

        await message.add_reaction(emojis.loading)

        # This won't terminate it for 30 seconds
        # Because this command will still be running.
        await exit_handler.graceful_terminate()

        for _ in range(0, wait):
            commands_running = exit_handler.get_commands_running() - 1
            if commands_running == 0:
                try:
                    await message.clear_reactions()
                except discord.HTTPException:
                    await message.remove_reaction(emojis.loading, ctx.bot.user)
                await message.edit(content="Goodbye!")
                await ctx.bot.logout()
                return
            await asyncio.sleep(1)

        if commands_running > 0:
            s = "s" if commands_running != 1 else ""
            try:
                await message.clear_reactions()
            except discord.HTTPException:
                await message.remove_reaction(emojis.loading, ctx.bot.user)
            logging.warn(
                f"Forcing shutdown! {commands_running} command{s} left hanging."
            )
            await message.edit(
                content=f"{commands_running} command{s} aborted to allow shutdown."
            )
        else:
            await message.edit(content="Goodbye!")

        await ctx.bot.logout()

    @commands.command(
        name="GuildInfo", aliases=["guild-info"], usage="guildinfo", hidden=True
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
        name="Sudo",
        aliases=["force", "dev"],
        usage="sudo [command] (command_args)",
        hidden=True,
    )
    async def sudo(
        self, ctx: commands.Context, command: str = None, *, arguments: str = ""
    ):
        """Force a command to be run without perms from the user.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            command {str} -- The command to run.
            arguments {str} -- The command's arguments.
        """

        new_message = ctx.message
        new_message.content = f"{ctx.prefix}{command} {arguments}"

        new_ctx = await ctx.bot.get_context(new_message)
        await new_ctx.command._parse_arguments(new_ctx)  # Parses the arguments
        await new_ctx.command.call_before_hooks(new_ctx)  # Calls command hooks

        await new_ctx.command.callback(*new_ctx.args, **new_ctx.kwargs)

    @commands.command(name="Eval", aliases=["run"], usage="eval [code]", hidden=True)
    async def eval(self, ctx: commands.Context, *, code: str):
        """Runs arbitrary code.
        Unsafe for anyone but the owner to be able to use.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        await ctx.message.add_reaction(emojis.loading)

        environment = {
            "author": ctx.author,
            "bot": ctx.bot,
            "channel": ctx.channel,
            "ctx": ctx,
            "database": self.database,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
            **globals(),
        }

        code = cleanup_code(code, "python")
        indented_code = textwrap.indent(code, "  ")
        code_with_wrapper = f"async def _eval_wrapper():\n{indented_code}"

        try:
            exec(code_with_wrapper, environment)
        except Exception as exception:
            exception_embed = discord.Embed(
                colour=0xFF0000,
                title=exception.__class__.__name__,
                description=f"```python\n{exception}```",
            )
            await ctx.send(embed=exception_embed)
            await ctx.message.add_reaction(emojis.no)
            await ctx.message.remove_reaction(emojis.loading, ctx.bot.user)
            return

        eval_wrapper = environment["_eval_wrapper"]
        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                return_value = await eval_wrapper()
        except Exception as exception:
            exception_embed = discord.Embed(
                colour=0xFF0000,
                title=exception.__class__.__name__,
                description=f"```python\n{exception}```"
                if str(exception) != ""
                else "No description was given.",
            )
            await ctx.send(embed=exception_embed)
            await ctx.message.add_reaction(emojis.no)
            await ctx.message.remove_reaction(emojis.loading, ctx.bot.user)
        else:
            output = stdout.getvalue()
            return_value = return_value or ""

            if output != "" or return_value != "":
                result = f"{output}\n{return_value}".strip()
                try:
                    await ctx.send(f"```python\n{result}```")
                except discord.HTTPException:
                    await ctx.message.add_reaction(emojis.no)
                    await ctx.message.remove_reaction(emojis.loading, ctx.bot.user)
                    return
                self._last_result = result

            await ctx.message.add_reaction(emojis.yes)
            await ctx.message.remove_reaction(emojis.loading, ctx.bot.user)

    @commands.command(name="Await", hidden=True)
    async def _await(self, ctx: commands.Context, *, coroutine: str):
        """Evaluates a coroutine.
        Await is intended for use on only one coroutine.
        However it would be impractical to force this.
        Unsafe for anyone but the owner to be able to use.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            coroutine {str} -- A string form of a coroutine to evaluate
        """

        coroutine = coroutine.strip()
        if (
            coroutine.startswith("`")
            and coroutine.endswith("`")
            and coroutine.find("`", 1, -1) == -1
        ):
            coroutine = coroutine[1:-1]
        coroutine = f"await {coroutine}"
        # The `commands.Command` decorator wraps a method.
        # This means it can't be called directly.
        # However `method.callback` still points to the original function.
        await self.eval.callback(self, ctx, code=coroutine)  # pylint: disable=E1101

    @commands.command(name="Print", hidden=True)
    async def _print(self, ctx: commands.Context, *, function: str):
        """Evaluates a coroutine.
        Await is intended for use on only one coroutine.
        However it would be impractical to force this.
        Unsafe for anyone but the owner to be able to use.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            coroutine {str} -- A string form of a coroutine to evaluate
        """

        function = function.strip()
        if (
            function.startswith("`")
            and function.endswith("`")
            and function.find("`", 1, -1) == -1
        ):
            function = function[1:-1]
        function = f"print({function})"
        # See `_await` for an explanation.
        await self.eval.callback(self, ctx, code=function)  # pylint: disable=E1101

    @commands.command(name="SQL", hidden=True)
    async def sql(self, ctx: commands.Context, *, query):
        title = "SQL Query"
        description_emojis = f"{emojis.empty} " * 19 + "\n"
        description_success = "**The query succeeded.**"
        description_result = None

        query = cleanup_code(query, "sql")
        async with self.database.acquire() as connection:
            statements = 1 + query.count(";")
            if query.endswith(";"):
                statements -= 1

            has_multiple_statements = statements > 1

            if has_multiple_statements:
                strategy = connection.execute
            else:
                strategy = connection.fetch
            try:
                start_time = time.perf_counter()
                result = await strategy(query)
                elapsed_time = (time.perf_counter() - start_time) * 1000
            except Exception as error:
                await ctx.send(embed=build_embed.error(error))
                return

            elapsed_time_str = f"Elapsed Time: {elapsed_time:.2f}ms"

            if not has_multiple_statements:
                keys = None
                values = []
                for item in result:
                    # print([x for x in item.items()])
                    # print(item.items())
                    if keys is None:
                        keys = list(item.keys())
                    values.extend(item.values())

                incomplete_description_result = f"**The query returned .**"
                ascii_table_truncated = "\n\nResults trimmed."
                max_length = (
                    6000
                    - len(title)
                    - len(elapsed_time_str)
                    - len(incomplete_description_result)
                    - len(ascii_table_truncated)
                    - len(description_emojis)
                )
                ascii_table = tabulate.tabulate(values, keys, tablefmt="grid")
                if len(ascii_table) > max_length:
                    ascii_table = ascii_table[:max_length]
                    table_row = re.compile(r"(\+[+-]+\+)")
                    row_count = len(re.findall(table_row, ascii_table)) - 1
                    if row_count < 0:
                        values = []
                    else:
                        values = values[:row_count]

                    ascii_table = tabulate.tabulate(values, keys, tablefmt="grid")

                    ascii_table += ascii_table_truncated
                description_result = f"**The query returned:**\n```{ascii_table}```"

            await ctx.send(
                embed=build_embed.success(
                    title=title,
                    description=(description_result or description_success)
                    + description_emojis,
                    footer=elapsed_time_str,
                )
            )

    @commands.group(name="Git", case_insensitive=True)
    async def git(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Call a subcommand.")

    @git.command(name="Pull")
    async def pull(self, ctx: commands.Context):
        # See `_await` for an explanation.
        await self.update.callback(self, ctx)  # pylint: disable=E1101

    @commands.command(name="Update", hidden=True)
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
            await ctx.send(
                embed=build_embed.error(
                    (
                        "The OS this script is running on does not support running "
                        "commands on their command line through Python.",
                    )
                )
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

    async def __local_check(self, ctx: commands.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)


def cleanup_code(content: str, language: str = None) -> str:
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

    if (
        content.startswith("```")
        and content.endswith("```")
        and content.find("```", 3, -3) == -1
    ):
        content = content[3:-3]
        content_lines = content.split("\n")
        code_line = content_lines[0]
        if language is not None:
            if language in code_line.casefold():
                content = "\n".join(content_lines[1:])
        elif code_line.casefold() in code_languages:
            content = "\n".join(content_lines[1:])

    if content.startswith("`") and content.endswith("`") and content.find("`", 1, -1):
        content = content[1:-1]

    return content


def setup(bot: commands.Bot):
    bot.add_cog(DeveloperCommands())
