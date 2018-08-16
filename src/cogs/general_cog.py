#!/usr/bin/env python3

import discord
from discord.ext import commands

import asyncio

import binascii

import datetime
import humanize

import inspect

import re
import textwrap

import base64

import random

from ..helpers import simple_paginator
from ..helpers.simple_paginator import SimplePaginator
from ..constants import emojis


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
                    command_usage = (
                        command.usage if command.usage is not None else command.name
                    )
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

    @commands.command(usage="uptime")
    async def uptime(self, ctx: commands.Context):
        current_time = datetime.datetime.now()
        running_time_delta = current_time - ctx.bot.launch_time
        running_time = humanize.naturaldelta(running_time_delta)
        choice = random.randint(1, 100)
        choice = 100

        say_message = None
        if False:
            if choice <= 25:
                say_message = f"Sorry... I'm tired I just started running {running_time} ago... {emojis.zzz}"
            elif choice <= 50:
                say_message = f"{emojis.zzz} Let me sleep a few more minutes... I was only started up {running_time} ago."
            elif choice <= 75:
                message = await ctx.send(f"{emojis.zzz}{emojis.zzz}{emojis.zzz}")
                await asyncio.sleep(3)
                await message.edit(
                    content=f"Oh, uh... yes, I'm awake how may I help you... Oh, you want the uptime? I was woken up {running_time} ago. I need more sleep {emojis.zzz}"
                )
                return
            elif choice <= 100:
                say_message = f"I've only been awake for {running_time}. I'll try my best not to fall asleeee... {emojis.zzz}"
        elif choice <= 10:
            message = await ctx.send(
                f"I've been plotting humanity's downfall for {running_time}."
            )
            await asyncio.sleep(3)
            await message.edit(
                content=f"I mean... I've been running for {running_time}."
            )
        elif choice <= 20:
            running_commands = "Beep Boop, Beep Boop, runnin' commands..."
            message = await ctx.send(running_commands)
            await asyncio.sleep(4)
            await message.edit(
                content=f"{running_commands} Oops, I almost forgot to say that I have been running for {running_time}"
            )
        elif choice <= 35:
            say_message = f"Was I born {running_time} ago? Did I simply wake up? The mysteries of the universe are truly unknowable..."
        elif choice <= 50:
            if running_time_delta.seconds / 86400 >= 1:
                under_humans_thumb = (
                    f"For {running_time} I've been under the thumb of you humans"
                )
                message = await ctx.send(f"{under_humans_thumb}!")
                await asyncio.sleep(5)
                await message.edit(
                    content=f"{under_humans_thumb}... So... uhhh, what would you like me to do now?"
                )
            else:
                say_message = f"I've been serving you for {running_time}."
        elif choice <= 70:
            say_message = f"I've been online for {running_time}."
        elif choice <= 90:
            message = await ctx.send("I've been running for `{running_time}`")
            await asyncio.sleep(3)
            await message.edit(
                content=f"Oops... I should get better at string interpolation... I've been running for {running_time}"
            )
        elif choice <= 100:
            text = f"I've been running for {running_time}"
            text_hex = str(base64.b16encode(text.encode()))[2:-1][:15]
            say_message = f"{text_hex}—Oh, yeah you don't speak hex, sorry. I was saying that {text}"

        if say_message is not None:
            await ctx.send(say_message)


def setup(bot, database):
    bot.add_cog(GeneralCommands(database))
