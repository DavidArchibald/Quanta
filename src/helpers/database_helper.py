#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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
    def __init__(self, db_info_path=None):
        # Go up a directory to the source
        source = os.path.dirname(os.path.dirname(__file__))
        database_info_path = db_info_path or os.path.join(
            source, "secrets/config.yaml"
        )  # Ends up with ./src/secrets/config.yaml
        with open(database_info_path, "r") as database_info_file:
            config = yaml.safe_load(database_info_file)
            database_info = config["database_info"]

        self._database_info = database_info
        self._pool = None
        self.cache = LFUCache(128)

    async def connect(self):
        """Creates a connection pool."""
        self._pool = await asyncpg.create_pool(**self._database_info)
        if self._pool is None:
            logging.warn('The database refused to connect! Falling back to "?" prefix')

    async def get_prefix(self, ctx: commands.context):
        """Gets the channel's prefix for running with

        Arguments:
            ctx {commands.context} -- Information about where the command was run.

        Returns:
            String -- The channel's prefix
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
    async def _get_prefix(self, guild_id, connection=None):
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
    async def set_prefix(self, ctx: commands.context, prefix: str, connection=None):
        """Sets the server prefix.

        Arguments:
            ctx {discord.Context} -- Information about where the command was run.
            prefix {String} -- The prefix for the guild.
        """
        if prefix is None:
            prefix = ""

        if prefix is not str:
            prefix = str(prefix)

        guild_id = str(ctx.message.guild.id)

        async with connection.transaction():
            await connection.execute(
                "UPDATE prefixes SET prefix=$1 WHERE prefixes.serverId=$2",
                prefix,
                guild_id,
            )
            self.cache.set(guild_id, prefix)

    async def close(self):
        """Closes the connection to the database."""
        await self._pool.close()
        self._pool = None
