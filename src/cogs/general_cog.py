#!/usr/bin/env python3

import asyncio
import aiohttp
import discord
from discord.ext import commands

import copy
import datetime
import os
import textwrap
import math
import random
import re
import urllib

import logging
import traceback

from fuzzywuzzy import process

import humanize

import html
import ujson
import jsonschema
import xml.etree.cElementTree
import yaml

from ..globals import emojis, latency, uptime
from ..helpers import session_helper
from ..helpers.helper_functions import confirm_action, wait_for_reactions


class GeneralCommands:
    """Commands for everyone."""

    icon = "<:quantaperson:473983023797370880>"

    def __init__(self, bot: commands.Bot, loop=None) -> None:
        config_path = os.path.join(os.path.dirname(__file__), "../secrets/config.yaml")
        with open(config_path, "r") as config_file:
            try:
                config = yaml.safe_load(config_file)
            except yaml.YAMLError:
                pass

        if config is not None:
            wolfram_scheme = {
                "type": "object",
                "properties": {
                    "wolfram_alpha": {
                        "type": "object",
                        "properties": {"app_id": {"type": "string"}},
                    }
                },
            }

            try:
                jsonschema.validate(config, wolfram_scheme)
            except jsonschema.exceptions.ValidationError:
                logging.warning(
                    (
                        "The secrets config doesn't have "
                        "valid wolfram_alpha configuration."
                        "Wolfram Alpha based commands will be disabled."
                    )
                )
                logging.warning(
                    f"The following exception was suppressed:\n{traceback.format_exc()}"
                )
            else:
                wolfram_alpha = config["wolfram_alpha"]
                self._app_id = wolfram_alpha["app_id"]

        self._trivia = []
        self._trivia_count = 25
        self._trivia_minimum = 5
        self._trivia_packet_size = 5
        self._trivia_task = None
        self._trivia_lock = asyncio.Lock()

        self.loop = loop or asyncio.get_event_loop()

    async def on_ready(self):
        await self.load_trivia()

    @commands.command(name="Ping", usage="ping")
    async def ping(self, ctx, round_to=4):
        """Returns the bot latency.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.

        Keyword Arguments:
            round_to {int} -- How many digits to round the bot latency. (default: {4})
        """

        # Check digits is a string then casefold
        if isinstance(round_to, str) and (
            round_to.casefold() == "true" or round_to.casefold() == "exact"
        ):
            latency_time = ctx.bot.latency
        elif isinstance(round_to, str) and round_to.isdigit():
            latency_time = round(ctx.bot.latency, int(round_to))
        else:
            latency_time = round(ctx.bot.latency, 4)

        if latency_time < 1:
            message = random.choice(latency.fast_latency)(latency_time)
        else:
            message = random.choice(latency.slow_latency)(latency_time)

        if message is not None:
            await ctx.send(message)

    @commands.command(
        name="Help", aliases=["commands", "command"], usage="help (command)"
    )
    async def help(self, ctx, *, command_name=None):
        """Show a complete list of commands you can use. Or information about a specific one.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            command_name {str} -- A command to get specific help. (default: {None})
        """
        if command_name is None:
            embed = discord.Embed(
                title="<:quantabadge:473675013786959891> **Help**",
                color=0x551A8B,  # silver
                description=textwrap.dedent(
                    """
                    Quanta is a multipurpose bot for simplifying your life.
                    """
                ),
            )
            for name, cog in ctx.bot.cogs.items():
                title_case_name = re.sub(
                    "([a-z])(?=[A-Z])", r"\1 ", name
                )  # Turns PascalCase to Title Case
                description = ""
                cog_commands = ctx.bot.get_cog_commands(name)
                icon = getattr(cog, "icon", None)
                for cog_command in cog_commands:
                    command_usage = (
                        cog_command.usage
                        if cog_command.usage is not None
                        else cog_command.name
                    )
                    if cog_command.hidden is True:
                        continue
                    description += f"**{command_usage}**\n"
                if description:
                    header = title_case_name
                    if icon is not None:
                        header = f"{icon} {title_case_name}"
                    embed.add_field(name=header, value=description, inline=True)

            embed.add_field(
                name="\u200B",
                value=(
                    "**Commands are written in the format"
                    "command [required] (optional)**\n\n"
                    f"To see more information about a specific command use {ctx.prefix}"
                    "help (command)"
                ),
            )
        else:
            command = ctx.bot.get_command(command_name)

            if command is None:
                all_command_names = [
                    name
                    for command in ctx.bot.commands
                    if command.hidden is not True
                    for name in (*command.aliases, command.name)
                ]

                closest_command_name, closest_ratio = process.extractOne(
                    command_name, all_command_names
                )
                could_not_find = (
                    "I couldn't find that command, sorry!"
                    f"Check {ctx.prefix}help for a list of the commands I have."
                )
                if closest_ratio < 80:
                    await ctx.send(could_not_find)
                    return
                else:
                    confirm, message = await confirm_action(
                        ctx, f"Do you mean my command {closest_command_name}?"
                    )
                    if not confirm:
                        await message.edit(content=could_not_find)
                        return

                    await message.edit(
                        content=(
                            "Here's the information about my command"
                            f"{closest_command_name}."
                        )
                    )
                    command_name = closest_command_name
                    command = ctx.bot.get_command(closest_command_name)
                    if command is None:
                        # This shouldn't ever happen.
                        await message.edit(
                            content=(
                                "Something went wrong when getting the command"
                                f"{closest_command_name}."
                            )
                        )
                        return
            if command.help is not None:
                brief = command.help.split("\n")[0]
            else:
                brief = "I can't find any help, sorry."
            embed = discord.Embed(
                title=f"{command.qualified_name} Help",
                color=0x551A8B,
                description=brief,
            )
            embed.add_field(name="Usage", value=command.usage)
            embed.add_field(
                name="Aliases",
                value=", ".join((command.name.lower(), *command.aliases)),
                inline=True,
            )

            if isinstance(command, commands.Group):
                group = command
                subcommands_description = ""
                nesting_characters = ["-", "*"]
                for command in group.walk_commands():
                    nesting_count = len(command.full_parent_name.split(" "))
                    nesting_character = nesting_characters[
                        nesting_count % len(nesting_characters) - 1
                    ]
                    tabs = "\t" * (nesting_count - 1) + nesting_character

                    subcommands_description += (
                        f"{tabs} **{command.usage or command.name.lower()}**\n"
                    )
                embed.add_field(
                    name="Subcommands", value=subcommands_description, inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="Uptime", usage="uptime")
    async def uptime(self, ctx: commands.Context):
        """Says how long the bot has been running.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
        """

        current_time = datetime.datetime.now()
        running_time_delta = current_time - ctx.bot.launch_time
        running_time = humanize.naturaldelta(running_time_delta)

        if running_time_delta.seconds / 60 <= 5:
            message = random.choice(uptime.sleepy)(running_time)
        else:
            message = random.choice(uptime.normal)(running_time)

        if message is not None:
            await ctx.send(message)

    @commands.command(name="Trivia", usage="trivia")
    async def trivia(self, ctx: commands.Context):
        """Sends an answerable trivia question.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
        """
        trivia = None
        async with ctx.typing():
            await ctx.message.add_reaction(emojis.loading)
            trivia = await self.get_trivia(ctx)

        await ctx.message.remove_reaction(emojis.loading, ctx.bot.user)

        if trivia is None:
            logging.warning("get_trivia returned None unexpectedly.")
            await ctx.message.add_reaction(emojis.error)
            await ctx.send("An unexpected error occurred.")
            return

        category = html.unescape(trivia["category"])
        question = html.unescape(trivia["question"])
        question_type = html.unescape(trivia["type"])
        correct_answer = html.unescape(trivia["correct_answer"])
        incorrect_answers = [
            html.unescape(item) for item in trivia["incorrect_answers"]
        ]

        if question_type == "boolean":
            answers = ["True", "False"]
        else:
            answers = [correct_answer, *incorrect_answers]
            random.shuffle(answers)

        blank_answers = [
            f"{index + 1}. {answer}" for index, answer in enumerate(answers)
        ]

        unchecked_answers = [f"{emojis.radio_off} {answer}" for answer in blank_answers]

        embed = discord.Embed(title=category, description=f"{question}")
        embed.add_field(name="\u200B", value="\n".join(unchecked_answers))

        message = await ctx.send(embed=embed)
        number_emojis = emojis.number_emojis[1 : len(answers) + 1]

        too_slow = copy.copy(embed)
        too_slow.clear_fields()
        too_slow.add_field(
            name="\u200B",
            value=(
                "Sorry, you ran out of time. The correct answer was "
                f"{correct_answer}."
            ),
        )

        reaction = await wait_for_reactions(
            ctx,
            message,
            number_emojis,
            timeout=60,
            timeout_message=too_slow,
            remove_reactions=False,
            remove_reactions_on_timeout=True,
        )
        if reaction is None:
            return

        chosen_number = number_emojis.index(reaction.emoji)
        correct_number = answers.index(correct_answer)
        correct_emoji = number_emojis[correct_number]

        blank_answers = copy.copy(blank_answers)

        final_answers = copy.copy(blank_answers)
        for index, answer in enumerate(final_answers):
            if index == correct_number:
                final_answers[index] = f"{emojis.circle_check} {final_answers[index]}"
                continue
            if index == chosen_number:
                final_answers[index] = f"{emojis.circle_x} {final_answers[index]}"
            else:
                final_answers[index] = f"{emojis.radio_off} {final_answers[index]}"
        embed.set_field_at(0, name="\u200B", value="\n".join(final_answers))

        if reaction.emoji == correct_emoji:
            embed.colour = 0x00FF00
        else:
            embed.colour = 0xFF0000

        await message.edit(embed=embed)

    @commands.command(name="Wolfram", usage="wolfram [query]")
    async def wolfram(self, ctx: commands.Context, *, query):
        if self._app_id is None:
            await ctx.send("Quanta is not currently connected to Wolfram Alpha.")
            return
        async with ctx.typing():
            something_went_wrong = (
                "Sorry, something went wrong with connecting to Wolfram Alpha."
            )

            query = urllib.parse.quote(query)
            query_url = (
                "http://api.wolframalpha.com/v2/query"
                f"?appid={self._app_id}"
                f"&input={query}"
                # "&includepodid=Result"
                "&format=plaintext"
            )

            session = await session_helper.get_session()
            try:
                async with session.get(query_url) as response:
                    text = await response.text()
                    try:
                        response_tree = xml.etree.cElementTree.fromstring(text)
                    except xml.etree.ElementTree.ParseError as exception:
                        await ctx.send(something_went_wrong)
                        logging.warning("Wolfram did not send valid xml.")
                        raise exception
                        return

                    result = None
                    for pod in response_tree:
                        print(pod)
                        if pod.id == "result":
                            result = pod
                        # print(pod)
                    # import pprint
                    # print(pprint.pprint(text))
                    # print(response_tree[0])
                    # result_pod = ...
                    print(result)
            except aiohttp.ClientError as exception:
                await ctx.send(something_went_wrong)
                logging.warn("Could not connect to WolframAlpha.")
                raise exception
                return

            # await ctx.send(plaintext_result)

    async def get_trivia(self, ctx=None, loop=None):
        """Gets a trivia question.
        Not providing ctx makes it error to console.

        Keyword Arguments:
            ctx {commands.Context} -- Information about where a command was run.

        Returns:
            Object -- The trivia object.
        """
        loop = loop or self.loop or asyncio.get_running_loop()

        if len(self._trivia) == 0:
            if self._trivia_task is not None:
                # Wait for the previous trivia task to be done
                await self._trivia_task
            else:
                await self.load_trivia(ctx)
        elif len(self._trivia) < self._trivia_count:
            # Let the trivia task run in the background.
            async def _trivia_callback():
                async with self._trivia_lock:
                    self._trivia_task = None

            self._trivia_task = self.loop.create_task(self.load_trivia(ctx))
            self._trivia_task.add_done_callback(
                lambda _: self.loop.create_task(_trivia_callback())
            )
            if self._trivia_task.done():
                self._trivia_task.remove_done_callback()
                await _trivia_callback()

        return self._trivia.pop()

    async def load_trivia(self, ctx=None):
        # await asyncio.sleep(10)
        load_count = self._trivia_count - len(self._trivia)
        # Round up to self._trivia_load_count, and a minimum of self._trivia_minimum
        load_count = max(
            self._trivia_minimum,
            math.ceil(load_count / self._trivia_packet_size) * self._trivia_packet_size,
        )

        url = f"https://opentdb.com/api.php?amount={load_count}"
        trivia_wrong_format = "Sorry, something went wrong with the trivia API."
        trivia_wrong_format_logging = (
            "opentdb did not respond with the expected format."
        )

        session = await session_helper.get_session()
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    if ctx is not None:
                        await ctx.send(trivia_wrong_format)
                    logging.warning(trivia_wrong_format_logging)
                    return

                response_text = await response.text()
                try:
                    trivia_response_json = ujson.loads(response_text)
                except ValueError as exception:
                    if ctx is not None:
                        await ctx.send(trivia_wrong_format)
                    logging.warning("opentdb did not send valid json.")
                    raise exception

                response_json_schema = {
                    "type": "object",
                    "properties": {
                        "status": {"type": "number"},
                        "results": {
                            "type": "array",
                            "minItems": load_count,
                            "maxItems": load_count,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "question": {"type": "string"},
                                    "type": {"type": "string"},
                                    "correct_answer": {"type": "string"},
                                    "incorrect_answers": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                }

                try:
                    jsonschema.validate(trivia_response_json, response_json_schema)
                except jsonschema.exceptions.ValidationError as exception:
                    await ctx.send(self._trivia_wrong_format)
                    logging.warning(self._trivia_wrong_format_logging)
                    raise exception
                    return

                trivia_questions = trivia_response_json["results"]

                self._trivia.extend(trivia_questions)

        except aiohttp.ClientError as exception:
            if ctx is not None:
                await ctx.send(self._trivia_wrong_format)
            logging.warning("Could not connect to opentdb.")
            raise exception
            return


def setup(bot: commands.Bot):
    bot.add_cog(GeneralCommands(bot))
