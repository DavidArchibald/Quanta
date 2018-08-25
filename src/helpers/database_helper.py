#!/usr/bin/env python3

import discord
from discord.ext import commands

import asyncio
import asyncpg

import os
import time

import json
import yaml

import logging

import functools
import inspect

# "Least Recently Used (LRU) cache"
# Caches a (key, value) pair by how much it has been used recently.
from .cache import LFUCache

from .helper_functions import HelperCommands

from typing import Optional

helperCommands = HelperCommands()


def with_connection():
    def wrapper(method):
        @functools.wraps(method)
        async def get_connection(self, *args, **kwargs):
            if hasattr(kwargs, "connection"):
                return await method(self, *args, **kwargs)

            if self._pool is None:
                raise RuntimeError(
                    "The function {method.__name__} wasn't run because the database isn't connected to."
                )
            async with self._pool.acquire() as connection:
                kwargs["connection"] = connection

                return await method(self, *args, **kwargs)

        return get_connection

    return wrapper


class Database:
    def __init__(
        self, db_info_path: str = None, loop: asyncio.AbstractEventLoop = None
    ) -> None:
        source = os.path.dirname(os.path.dirname(__file__))
        database_info_path = db_info_path or os.path.join(source, "secrets/config.yaml")

        # Opens ./src/secrets/config.yaml or the
        with open(database_info_path, "r") as database_info_file:
            config = yaml.safe_load(database_info_file)
            database_info = config["database_info"]

        self._database_info = database_info
        self._pool = None
        self.cache = LFUCache(128)
        self.loop = loop

    async def connect(self):
        """Creates a connection pool."""
        try:
            if self.loop and not hasattr(self._database_info, "loop"):
                self._database_info.set(loop=self.loop)
            self._pool = await asyncpg.create_pool(**self._database_info)
        except Exception as exception:
            logging.warn('The database refused to connect! Falling back to "?" prefix.')
            print(exception)

    async def get_prefix(self, ctx: commands.Context) -> str:
        """Gets the channel's prefix for running with

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Returns:
            str -- The channel's prefix
        """
        # The function may still be run even if there is no connection because it doesn't have the `with_connection` decorator
        if self._pool is None:
            return "?"
        channel = ctx.message.channel
        guild_id = str(channel.guild.id)

        prefix = self.cache.get(guild_id)
        if prefix == -1:
            # Calling this directly won't cache it.
            prefix = await self._get_prefix(guild_id)

            self.cache.set(guild_id, prefix)

        return prefix

    @with_connection()
    async def _get_prefix(
        self, guild_id: int, connection: Optional[asyncpg.Connection] = None
    ) -> str:
        if connection is None:
            return "?"

        row = await connection.fetchrow(
            "SELECT prefix FROM prefixes WHERE serverId=$1", guild_id
        )

        if row is None:
            async with connection.transaction():
                # Default prefix is "?"
                await connection.execute(
                    "INSERT INTO prefixes VALUES ($1, $2)", guild_id, "?"
                )

            return "?"

        return row["prefix"]

    @with_connection()
    async def set_prefix(
        self,
        ctx: commands.Context,
        prefix: str,
        connection: Optional[asyncpg.Connection] = None,
    ):
        """Sets the server prefix.

        Arguments:
            ctx {discord.Context} -- Information about where the command was run.
            prefix {str} -- The prefix for the guild.
        """
        if connection is None:
            raise RuntimeError("The prefix cannot be set without a connection.")

        if prefix is None:
            prefix = ""

        if not isinstance(prefix, str):
            prefix = str(prefix)

        guild_id = str(ctx.message.guild.id)

        async with connection.transaction():
            await connection.execute(
                "UPDATE prefixes SET prefix=$1 WHERE prefixes.serverId=$2",
                prefix,
                guild_id,
            )
            self.cache.set(guild_id, prefix)

    def is_connected(self) -> bool:
        """Returns if the database is connected or not.

        Returns:
            bool -- If the database is connected.
        """

        return self._pool is not None

    async def close(self, timeout: int = 10):
        """Closes the connection to the database."""
        if self._pool is None:
            raise RuntimeWarning("The connection has already been closed.")

        if timeout not in (0, -1, None):
            await asyncio.wait_for(self._pool.close(), timeout)

        await self._pool.terminate()

        self._pool = None
        logging.warn('Closed the database! Falling back to "?" prefix mode.')
