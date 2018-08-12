#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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

from .handlers import exit_handling
from .helpers import database_helper, logs_helper

cogs = {
    "admin": "src.cogs.admin_cog",
    "developer": "src.cogs.developer_cog",
    "general": "src.cogs.general_cog",
    "helper": "src.helpers.helper_functions",
    "error_handling": "src.handlers.error_handling",
    "event_handling": "src.handlers.event_handling",
    "exit_handling": "src.handlers.exit_handling",
}


class Object(object):
    pass


async def get_prefix_wrapper(bot, message):
    # I have to fake `commands.Context` because `get_context` requires the prefix, which creates an infinite loop.
    ctx = Object()
    ctx.message = message
    prefix = await database.get_prefix(ctx)
    return commands.when_mentioned_or(prefix)(bot, message)


database = database_helper.Database()
bot = commands.Bot(case_insensitive=True, command_prefix=get_prefix_wrapper)


@bot.event
async def on_message(message):
    if not exit_handling.is_terminating():
        await bot.process_commands(message)


if __name__ == "__main__":
    # Because asynchronous things can't be run until the bot loop is set up.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.connect())

    logs_helper.start_logging()

    config_path = os.path.join(os.path.dirname(__file__), "secrets/config.yaml")

    # The help command has to be removed before the cogs are loaded.
    bot.remove_command("help")

    # This basically clones `bot.import_extension` in order to pass in the database object instead.
    for path in cogs.values():
        try:
            lib = importlib.import_module(path)
            if not hasattr(lib, "setup"):
                raise discord.ClientException(
                    "Extension does not have a setup function."
                )
            cog = lib.setup(bot, database)
        except Exception:
            print(f"Could not add {path} due to following exception.")
            raise Exception

        logging.info(f"Added {path} successfully.")

    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    bot_info = config["bot_info"]
    token = bot_info["token"]

    signal.signal(signal.SIGTERM, exit_handling.signal_terminate_handler)
    signal.signal(signal.SIGINT, exit_handling.signal_interupt_handler)

    bot.run(token)
