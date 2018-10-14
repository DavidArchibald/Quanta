#!/usr/bin/env python3

import os
import logging

import discord
from discord.ext import commands

import asyncio
import aioredis
import asyncpg
import jsonschema
import yaml

import traceback

from .helper_functions import HelperCommands


helperCommands = HelperCommands()


class Database:
    def __init__(
        self, secrets_path: str = None, loop: asyncio.AbstractEventLoop = None
    ) -> None:
        self._database_info = None
        self._redis_config = None
        self._redis = None
        self._redis_pool = None
        self._pool = None
        self._loop = loop
        self._cache = None

        source = os.path.dirname(os.path.dirname(__file__))
        secrets_path = secrets_path or "secrets/config.yaml"

        if not os.path.isabs(secrets_path):
            secrets_path = os.path.join(source, secrets_path)

        # Opens ./src/secrets/config.yaml or the passed in path.
        with open(secrets_path, "r") as secrets_file:
            try:
                config = yaml.safe_load(secrets_file)
            except yaml.YAMLError:
                pass

        if config is not None:
            database_schema = {
                "type": "object",
                "properties": {
                    "database_info": {
                        "type": "object",
                        "properties": {
                            "database": {"type": "string"},
                            "user": {"type": "string"},
                            "password": {"type": "string"},
                            "host": {"type": "string"},
                        },
                    }
                },
            }

            try:
                jsonschema.validate(config, database_schema)
            except jsonschema.exceptions.ValidationError:
                logging.warning("The database credentials have not been passed.")
                logging.warning(
                    f"The following exception was suppressed:\n{traceback.format_exc()}"
                )
            else:
                self._database_info = config["database_info"]

            if "redis" in config:
                redis_scheme = {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string"},
                        "password": {"type": "string", "optional": "true"},
                    },
                }
                try:
                    jsonschema.validate(config["redis"], redis_scheme)
                except jsonschema.exceptions.ValidationError:
                    self._cache = {}
                else:
                    self._redis_config = config["redis"]

    async def connect(self):
        """Creates a connection pool.
        Connects to Redis if able to. Silently falls back otherwise.
        """
        if self._database_info is None:
            raise RuntimeError("The database credentials weren't given.")
        try:
            if self._loop and not hasattr(self._database_info, "loop"):
                self._database_info.set(loop=self._loop)
            self._pool = await asyncpg.create_pool(**self._database_info)
        except Exception as exception:
            logging.warn('The database refused to connect! Falling back to "?" prefix.')
            print(exception)

        if self._redis_config is not None:
            # The redis_config has already been validated.
            if self._loop and not hasattr(self._redis_config, "loop"):
                self._redis_config["loop"] = self._loop

            if self._redis_config.get("minsize", None) is None:
                self._redis_config["minsize"] = 3

            if self._redis_config.get("maxsize", None) is None:
                minsize = self._redis_config.get("minsize")
                self._redis_config["maxsize"] = min(5, minsize + 5)

            try:
                self._redis_pool = await aioredis.create_redis_pool(
                    **self._redis_config
                )
                self._redis = aioredis.Redis(self._redis_pool)
            except OSError:
                self._redis_pool = None
                self._redis = None
                self._cache = {}
                logging.warn("Could not connect to Redis with the given credentials.")

    async def get_prefix(self, ctx: commands.Context) -> str:
        """Gets the channel's prefix for running with

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Returns:
            str -- The channel's prefix
        """
        # The function may still be run even if there is no connection
        # because it doesn't have the `with_connection` decorator
        if self._pool is None:
            return "?"

        channel = ctx.message.channel
        if isinstance(channel, discord.abc.PrivateChannel):
            snowflake = str(channel.id)
        elif isinstance(channel, discord.abc.GuildChannel):
            snowflake = str(channel.guild.id)

        if self._cache is None:
            with await self._redis_pool as connection:
                prefix = await connection.execute("GET", f"channel-{snowflake}")
        else:
            prefix = self._cache.get(snowflake, None)

        if prefix is None:
            # Calling this directly won't cache it.
            prefix = await self._get_prefix(snowflake)

            if self._cache is None:
                with await self._redis_pool as connection:
                    await connection.execute("SET", f"channel:{snowflake}", prefix)
            else:
                self._cache.set(snowflake, prefix)
        else:
            prefix = prefix.decode("utf-8")

        return prefix

    def acquire(self, timeout=None):
        return asyncpg.pool.PoolAcquireContext(self._pool, timeout)

    def redis_is_connected(self):
        return self._redis_pool is not None

    async def redis_connection(self):
        return await self._redis_pool

    async def _get_prefix(self, snowflake: int) -> str:
        async with self.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT prefix FROM prefixes WHERE snowflake=$1", snowflake
            )

            if row is None:
                async with connection.transaction():
                    # Default prefix is "?"
                    await connection.execute(
                        "INSERT INTO prefixes VALUES ($1, $2)", snowflake, "?"
                    )

                return "?"

            return row["prefix"]

    async def set_prefix(self, ctx: commands.Context, prefix: str):
        """Sets the server prefix.

        Arguments:
            ctx {discord.Context} -- Information about where the command was run.
            prefix {str} -- The prefix for the guild.
        """
        async with self.acquire() as connection:
            if prefix is None:
                prefix = ""

            if not isinstance(prefix, str):
                prefix = str(prefix)

            channel = ctx.message.channel
            if isinstance(channel, discord.abc.PrivateChannel):
                snowflake = str(channel.id)
            elif isinstance(channel, discord.abc.GuildChannel):
                snowflake = str(channel.guild.id)

            async with connection.transaction():
                await connection.execute(
                    "UPDATE prefixes SET prefix=$1 WHERE prefixes.snowflake=$2",
                    prefix,
                    snowflake,
                )
                if self.redis_is_connected():
                    with await self._redis_pool as connection:
                        await connection.execute("SET", f"channel:{snowflake}", prefix)
                else:
                    self._cache.set(snowflake, prefix)

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

        if self.redis_is_connected():
            self._redis_pool.close()

        self._pool = None
        logging.warn('Closed the database! Falling back to "?" prefix mode.')
