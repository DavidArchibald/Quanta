"""A Discord.py bot."""

import discord
from discord.ext import commands
import discord.utils

import traceback
import logging

#import src
from .helpers import database
from .helpers import helper_functions

from .commands import general_commands, developer_commands, admin_commands
from .bot_handling import error_handling, bot_event_handling

client = discord.Client()
bot = commands.Bot(case_insensitive=True, command_prefix=database.get_prefix)

if __name__ == "__main__":
    tokenFile = open("token.txt", "r")
    token = tokenFile.read()
    tokenFile.close()

    helperCommands = helper_functions.HelperCommands()
    developerCommands = developer_commands.DeveloperCommands()
    generalCommands = general_commands.GeneralCommands()
    adminCommands = admin_commands.AdminCommands()
    commandErrorHandler = error_handling.CommandErrorHandler()
    botEventHandler = bot_event_handling.BotEventHandler(bot)

    bot.add_cog(helperCommands)
    bot.add_cog(developerCommands)
    bot.add_cog(generalCommands)
    bot.add_cog(adminCommands)
    bot.add_cog(commandErrorHandler)
    bot.add_cog(botEventHandler)

    bot.run(token)
    #client.run(token)
