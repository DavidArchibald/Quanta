
import signal
import sys
from threading import Lock

import discord
from discord.ext import commands


class ExitHandler:
    def __init__(self):
        self.commands_running = 0
        self.SIGTERM = False
        self.lock = Lock()

        signal.signal(signal.SIGTERM, self.signal_terminate_handler)
        signal.signal(signal.SIGINT, self.signal_interupt_handler)

    async def on_command(self, ctx: commands.Context):
        self.lock.acquire()
        self.commands_running += 1
        self.lock.release()

    async def on_command_completion(self, ctx: commands.Context):
        self.lock.acquire()
        self.commands_running -= 1

        if self.SIGTERM == True and self.commands_running == 0:
            self.lock.release()
            await ctx.bot.logout()
            sys.exit(0)
            return

        self.lock.release()

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        self.on_command_completion(ctx)

    def signal_terminate_handler(self):
        if self.SIGTERM == True:
            sys.exit(0)
        self.SIGTERM = True

    def signal_interupt_handler(self):
        if self.SIGTERM == True:
            sys.exit(0)
        self.SIGTERM = True
        print("Use CTRL-C again if you're sure you want to skip cleanup handlers.")


exit_handler = ExitHandler()


def is_terminating():
    return exit_handler.SIGTERM


def terminate():
    exit_handler.SIGTERM = True
    return exit_handler.commands_running


def setup(bot, database):
    bot.add_cog(exit_handler)