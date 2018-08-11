
import signal
import sys
from threading import Lock

import discord
from discord.ext import commands


class ExitHandler:
    def __init__(self):
        self.commands_running = 0
        self.lock = Lock()
        self.SIGTERM = False

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
        await self.on_command_completion(ctx)


exit_handler = ExitHandler()


def signal_terminate_handler(signal, frame):
    print("signal_terminate_handler")
    if exit_handler.SIGTERM == True or exit_handler.commands_running == 0:
        sys.exit(0)
    exit_handler.SIGTERM = True


def signal_interupt_handler(signal, frame):
    print("signal_interupt_handler")
    if exit_handler.SIGTERM == True or exit_handler.commands_running == 0:
        sys.exit(0)
    exit_handler.SIGTERM = True
    print("Use CTRL-C again if you're sure you want to skip cleanup handlers.")


def is_terminating():
    return exit_handler.SIGTERM


def terminate():
    exit_handler.SIGTERM = True
    if exit_handler.commands_running == 0:
        sys.exit(0)


def get_commands_running():
    return exit_handler.commands_running


def setup(bot, database):
    signal.signal(signal.SIGTERM, signal_terminate_handler)
    signal.signal(signal.SIGINT, signal_interupt_handler)
    bot.add_cog(exit_handler)
