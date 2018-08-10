
import signal
import sys
from threading import Lock

lock = Lock()

import discord
from discord.ext import commands


commands_running = 0
SIGTERM = False


class ExitHandler:
    async def on_command(self, ctx: commands.Context):
        global commands_running

        lock.acquire()
        commands_running += 1
        lock.release()

    async def on_command_completion(self, ctx: commands.Context):
        global commands_running
        global SIGTERM

        lock.acquire()
        commands_running -= 1
        lock.release()

        if SIGTERM == True and commands_running == 0:
            await ctx.bot.logout()
            sys.exit(0)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        global commands_running
        global SIGTERM

        lock.acquire()
        commands_running -= 1
        lock.release()

        if SIGTERM == True and commands_running == 0:
            await ctx.bot.logout()
            sys.exit(0)

    @commands.command(usage="terminate")
    async def terminate(self, ctx: commands.Context):
        global SIGTERM
        SIGTERM = True
        print("Terminating when it can.")


def handle_SIGTERM():
    def signal_terminate_handler():
        global SIGTERM
        if SIGTERM == True:
            sys.exit(0)
        SIGTERM = True

    def signal_interupt_handler():
        global SIGTERM
        if SIGTERM == True:
            sys.exit(0)
        SIGTERM = True
        print("Use CTRL-C again if you're sure you want to skip cleanup handlers.")

    signal.signal(signal.SIGTERM, signal_terminate_handler)
    signal.signal(signal.SIGINT, signal_interupt_handler)


def is_terminating():
    return SIGTERM


def setup(bot, database):
    exit_handler = ExitHandler()
    handle_SIGTERM()
    bot.add_cog(exit_handler)
