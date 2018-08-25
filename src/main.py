#!/usr/bin/env python3

"""A Discord.py bot."""

import asyncio

import discord
from discord.ext import commands
import discord.utils

import os
import sys
import signal

import traceback
import logging
import importlib
import yaml

from .helpers import database_helper, logs_helper
from .handlers import exit_handling

from typing import List, Any

exit_handler = None

cogs = {
    "admin": "src.cogs.admin_cog",
    "developer": "src.cogs.developer_cog",
    "general": "src.cogs.general_cog",
    "helper": "src.helpers.helper_functions",
    "error_handling": "src.handlers.error_handling",
    "event_handling": "src.handlers.event_handling",
    "get_user": "src.helpers.fuzzy_user",
}


class fake_ctx(object):
    message: discord.Message = ...


async def get_prefix_wrapper(bot: commands.Bot, message: discord.Message) -> List[str]:
    # I have to fake `commands.Context` because `get_context` requires the prefix, which creates an infinite loop.
    ctx: fake_ctx = fake_ctx()
    ctx.message = message
    prefix = await database.get_prefix(ctx)
    return commands.when_mentioned_or(prefix)(bot, message)


database = database_helper.Database()
bot = commands.Bot(case_insensitive=True, command_prefix=get_prefix_wrapper)


@bot.event
async def on_message(message: discord.Message):
    if exit_handler is not None and not exit_handler.is_terminating():
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

    # The help command has to be removed before the cogs are loaded.
    bot.remove_command("help")

    # This basically clones `bot.import_extension` in order to pass in the database object instead.
    for path in cogs.values():
        try:
            lib: Any = importlib.import_module(
                path
            )  # Has to be put as any to recognize the attribute setup as potentially valid
            if hasattr(lib, "setup"):
                cog = lib.setup(bot, database)
            else:
                raise discord.ClientException(
                    "Extension does not have a setup function."
                )
        except Exception as exception:
            print(f"Could not add {path} due to following exception.")
            print(exception)

        logging.info(f"Added {path} successfully.")

    config_path = os.path.join(os.path.dirname(__file__), "secrets/config.yaml")
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    bot_info = config["bot_info"]
    token = bot_info["token"]

    bot.run(token)
