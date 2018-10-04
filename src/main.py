#!/usr/bin/env python3

"""A Discord.py bot."""

import asyncio

import discord
from discord.ext import commands
import discord.utils

import os

import re
import yaml

from typing import List

from .helpers import database_helper, logs_helper
from .handlers import exit_handling

from .globals import variables

exit_handler = None

cogs = {
    "admin": "src.cogs.admin_cog",
    "developer": "src.cogs.developer_cog",
    "code": "src.cogs.code_cog",
    "general": "src.cogs.general_cog",
    "helper": "src.helpers.helper_functions",
    "error_handling": "src.handlers.error_handling",
    "event_handling": "src.handlers.event_handling",
    "get_user": "src.helpers.fuzzy_user",
}


class fake_ctx(object):
    message: discord.Message = ...


async def get_prefix_wrapper(bot: commands.Bot, message: discord.Message) -> List[str]:
    # I have to fake `commands.Context` because `get_context` requires the prefix,
    # which creates an infinite loop.
    ctx: fake_ctx = fake_ctx()
    ctx.message = message
    prefix = await database.get_prefix(ctx)
    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(case_insensitive=True, command_prefix=get_prefix_wrapper)
database = database_helper.Database()


@bot.event
async def on_message(message: discord.Message):
    if (
        variables.is_ready is True
        and exit_handler is not None
        and not exit_handler.is_terminating()
    ):
        prefixes = await get_prefix_wrapper(bot, message)
        to_rot_command = re.compile("(.?(rotate|rot)(?! ))")
        if message.content.startswith(tuple(prefixes)):
            # Add a space between rot or rotate and it's degree.
            message.content = re.sub(
                to_rot_command, lambda match: match.group(0) + " ", message.content
            )
        await bot.process_commands(message)


# Quanta won't respond to other bots.
@bot.check
async def not_bot(message: discord.Message) -> bool:
    return not message.author.bot


if __name__ == "__main__":
    exit_handler = exit_handling.init(bot)

    # Because asynchronous things can't be run until the bot loop is set up.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.connect())

    logs_helper.start_logging()

    variables.bot = bot
    variables.database = database
    variables.exit_handler = exit_handler

    # The help command has to be removed before the cogs are loaded.
    bot.remove_command("help")

    for path in cogs.values():
        bot.load_extension(path)

    config_path = os.path.join(os.path.dirname(__file__), "secrets/config.yaml")
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    bot_info = config["bot_info"]
    token = bot_info["token"]

    bot.run(token)
