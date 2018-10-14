#!/usr/bin/env python3

import asyncio
import signal
import sys

import functools

from typing import Optional

from discord.ext import commands


class ExitHandler:
    def __init__(self) -> None:
        self.commands_running = 0
        self.lock = asyncio.Lock()
        self.SIGTERM = False

        self.original_sigint = signal.getsignal(signal.SIGINT)
        self.original_sigterm = signal.getsignal(signal.SIGTERM)

    async def on_command(self, ctx: commands.Context):
        async with self.lock:
            self.commands_running += 1

    async def on_command_completion(self, ctx: commands.Context):
        async with self.lock:
            self.commands_running -= 1

            if self.SIGTERM is True and self.commands_running == 0:
                await ctx.bot.logout()
                sys.exit(0)
                return

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        await self.on_command_completion(ctx)

    async def signal_terminate_handler(self, signal, frame):
        signal.signal(signal.SIGTERM, self.original_sigterm)
        if self.SIGTERM is True or self.commands_running == 0:
            sys.exit(0)

        async with self.lock:
            self.SIGTERM = True
        signal.signal(
            signal.SIGTERM,
            functools.partial(asyncio.create_task, self.signal_terminate_handler),
        )

    async def signal_interupt_handler(self, signal, frame):
        signal.signal(signal.SIGINT, self.original_sigint)
        if self.SIGTERM is True or self.commands_running == 0:
            sys.exit(0)

        async with self.lock:
            self.SIGTERM = True
        print("Use CTRL-C again if you're sure you want to skip cleanup handlers.")
        signal.signal(
            signal.SIGINT,
            functools.partial(asyncio.create_task, self.signal_terminate_handler),
        )

    def create_signals(self):
        signal.signal(
            signal.SIGTERM,
            functools.partial(asyncio.create_task, self.signal_terminate_handler),
        )
        signal.signal(
            signal.SIGINT,
            functools.partial(asyncio.create_task, self.signal_interupt_handler),
        )

    def is_terminating(self) -> bool:
        return self.SIGTERM

    async def graceful_terminate(self):
        async with self.lock:
            self.SIGTERM = True
        if self.commands_running == 0:
            sys.exit(0)

    async def cancel_terminate(self):
        async with self.lock:
            self.SIGTERM = False
        self.lock.release()

    def get_commands_running(self) -> int:
        return self.commands_running


def get_exit_handler() -> Optional[ExitHandler]:
    global exit_handler
    return exit_handler


def init(bot) -> ExitHandler:
    global exit_handler
    exit_handler = ExitHandler()
    exit_handler.create_signals()
    bot.add_cog(exit_handler)

    return exit_handler


exit_handler = None
