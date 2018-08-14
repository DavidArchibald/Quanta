#!/usr/bin/env python3

import signal
import sys
from threading import Lock

import discord
from discord.ext import commands

exit_handler = None


class ExitHandler:
    def __init__(self):
        self.commands_running = 0
        self.lock = Lock()
        self.SIGTERM = False

        self.original_sigint = signal.getsignal(signal.SIGINT)
        self.original_sigterm = signal.getsignal(signal.SIGTERM)

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

    def signal_terminate_handler(self, signal, frame):
        signal.signal(signal.SIGTERM, self.original_sigterm)
        if self.SIGTERM == True or self.commands_running == 0:
            sys.exit(0)

        self.lock.acquire()
        self.SIGTERM = True
        self.lock.release()
        signal.signal(signal.SIGTERM, self.signal_terminate_handler)

    def signal_interupt_handler(self, signal, frame):
        signal.signal(signal.SIGINT, self.original_sigint)
        if self.SIGTERM == True or self.commands_running == 0:
            sys.exit(0)

        self.lock.acquire()
        self.SIGTERM = True
        self.lock.release()
        print("Use CTRL-C again if you're sure you want to skip cleanup handlers.")
        signal.signal(signal.SIGINT, self.signal_terminate_handler)

    def create_signals(self):
        signal.signal(signal.SIGTERM, self.signal_terminate_handler)
        signal.signal(signal.SIGINT, self.signal_interupt_handler)

    def is_terminating(self):
        return self.SIGTERM

    def terminate(self):
        self.lock.acquire()
        self.SIGTERM = True
        self.lock.release()
        if self.commands_running == 0:
            sys.exit(0)

    def cancel_terminate(self):
        self.lock.acquire()
        self.SIGTERM = False
        self.lock.release()

    def get_commands_running(self):
        return self.commands_running


def get_exit_handler():
    global exit_handler
    return exit_handler


def init(bot):
    global exit_handler
    exit_handler = ExitHandler()
    exit_handler.create_signals()
    bot.add_cog(exit_handler)

    return exit_handler
