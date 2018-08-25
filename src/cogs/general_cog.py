#!/usr/bin/env python3

import discord
from discord.ext import commands

import asyncio
import aiohttp

import binascii
import base64
import json

import datetime
import humanize

import inspect

import re
import textwrap

import random

import html
import copy

from ..constants import emojis, latency, uptime
from ..helpers import helper_functions, session_helper
from ..helpers.helper_functions import wait_for_reactions
from ..helpers.database_helper import Database


class GeneralCommands:
    """Commands for everyone."""

    icon = "<:quantaperson:473983023797370880>"

    def __init__(self, database: Database) -> None:
        self.database: Database = database

    @commands.command(usage="ping")
    async def ping(self, ctx, round_to=4):
        """Returns the bot latency.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.

        Keyword Arguments:
            round_to {int} -- How many digits to round the bot latency to. (default: {4})
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

    @commands.command(aliases=["commands"], usage="help (command)")
    async def help(self, ctx, command=None):
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
                    if cog_command.hidden == True:
                        continue
                    description += f"**{command_usage}**\n"
                if description:
                    header = title_case_name
                    if icon is not None:
                        header = f"{icon} {title_case_name}"
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

    @commands.command(usage="uptime")
    async def uptime(self, ctx: commands.Context):
        current_time = datetime.datetime.now()
        running_time_delta = current_time - ctx.bot.launch_time
        running_time = humanize.naturaldelta(running_time_delta)

        if running_time_delta.seconds / 60 <= 5:
            message = random.choice(uptime.sleepy)(running_time)
        else:
            message = random.choice(uptime.normal)(running_time)

        if message is not None:
            await ctx.send(message)

    @commands.command(usage="trivia")
    async def trivia(self, ctx: commands.Context):
        something_went_wrong = f"Sorry, something went wrong with the trivia API."
        url = "https://opentdb.com/api.php?amount=1"

        session = await session_helper.get_session()
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send(something_went_wrong)
                    return

                try:
                    trivia = json.loads(await response.text())["results"][0]

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
                except (json.decoder.JSONDecodeError, KeyError, IndexError, ValueError):
                    await ctx.send(something_went_wrong)
                    return

                formatted_answers = [
                    f"{index + 1}. {answer}" for index, answer in enumerate(answers)
                ]

                unchecked_answers = [
                    f"{emojis.radio_off} {answer}" for answer in formatted_answers
                ]

                embed = discord.Embed(title=category, description=f"{question}")
                embed.add_field(name="\u200B", value="\n".join(unchecked_answers))

                message = await ctx.send(embed=embed)
                number_emojis = emojis.number_emojis[1 : len(answers) + 1]

                too_slow = copy.copy(embed)
                too_slow.clear_fields()
                too_slow.add_field(
                    name="\u200B",
                    value=f"Sorry, you ran out of time. The correct answer was {correct_answer}.",
                )

                reaction = await wait_for_reactions(
                    ctx,
                    message,
                    number_emojis,
                    timeout=1,
                    timeout_message=too_slow,
                    remove_reactions=False,
                    remove_reactions_on_timeout=True,
                )
                if reaction is None:
                    return

                chosen_number = number_emojis.index(reaction.emoji)
                correct_number = answers.index(correct_answer)
                correct_emoji = number_emojis[correct_number]

                chosen_answers = copy.copy(formatted_answers)

                if reaction.emoji == correct_emoji:
                    chosen_answers[
                        chosen_number
                    ] = f"{emojis.circle_x} {formatted_answers[chosen_number]}"
                    embed.colour = 0x00ff00
                    embed.set_field_at(
                        0, name="\u200B", value="\n".join(formatted_answers)
                    )
                else:
                    formatted_answers[
                        correct_number
                    ] = f"{emojis.circle_check} {formatted_answers[correct_number]}"

                    embed.colour = 0xff0000
                    embed.set_field_at(
                        0, name="\u200B", value="\n".join(formatted_answers)
                    )

                await message.edit(embed=embed)

        except aiohttp.ClientError:
            await ctx.send(something_went_wrong)
            return


def setup(bot: commands.Bot, database):
    bot.add_cog(GeneralCommands(database))
