import discord
from discord.ext import commands

import asyncio
import asyncpg

import os
import time

import yaml
import json

import functools
import inspect

from .cache import LFUCache # "Least Recently Used (LRU) cache"
                            # Caches a (key, value) pair by how much it has been used recently.

from .helper_functions import HelperCommands
helperCommands = HelperCommands()

def with_connection():
    def wrapper(method):
        @functools.wraps(method)
        async def get_connection(self, *args, **kwargs):
            if self._pool is None:
                raise NameError("The function {} wasn't run because the database isn't connected to.".format(method.__name__))
            
            async with self._pool.acquire() as connection:
                if not hasattr(kwargs, "connection"): # in case something wants to overide it(testing?)
                    kwargs["connection"] = connection

                return await method(self, *args, **kwargs)
    
        return get_connection

    return wrapper

class Database:
    def __init__(self, db_info_path=None):
        source = os.path.dirname(os.path.dirname(__file__)) # go up a directory to the source
        database_info_path = db_info_path or os.path.join(source, "secrets\\config.yaml") # ends up with ./src/secrets/config.yaml
        with open(database_info_path, "r") as database_info_file:
            config = yaml.safe_load(database_info_file)
            database_info = config["database_info"]
        
        self._database_info = database_info
        self._pool = None
        self.cache = LFUCache(128)
    
    async def connect(self):
        """Creates a connection pool."""
        self._pool = await asyncpg.create_pool(**self._database_info)

    async def get_prefix(self, ctx: commands.context):
        """Get's the channel's prefix for running with 
        
        Arguments:
            ctx {commands.context} -- Information about where the command was run.
        
        Returns:
            String -- The channel's prefix
        """
        channel = ctx if isinstance(ctx, discord.abc.GuildChannel) else ctx.message.channel # because some code is forced to pass in a channel
        guild_id = str(channel.guild.id)

        prefix = self.cache.get(guild_id)
        if prefix == -1:
            prefix = await self._get_prefix(guild_id) # calling this directly won't cache it.
            
            self.cache.set(guild_id, prefix)

        return prefix

    @with_connection()
    async def _get_prefix(self, guild_id, connection=None):
        row = await connection.fetchrow("SELECT prefix FROM prefixes WHERE serverId=$1", guild_id)

        if row is None:
            async with connection.transaction():
                await connection.execute("INSERT INTO prefixes VALUES ($1, $2)", guild_id, "?") # default prefix

            return "?"
        
        return row["prefix"]


    @with_connection()
    async def set_prefix(self, ctx: commands.context, prefix: str, connection=None):
        """Sets the server prefix.
        
        Arguments:
            ctx {discord.Context} -- Information about where the command was run.
            prefix {String} -- The prefix for the guild.
        """

        guild_id = str(ctx.message.guild.id)

        async with connection.transaction():
            await connection.execute("UPDATE prefixes SET prefix=$1 WHERE prefixes.serverId=$2", prefix, guild_id)
            print(self.cache.get(guild_id))
            self.cache.set(guild_id, prefix)
            print(self.cache.get(guild_id))
        
    async def close(self):
        """Closes the connection to the database."""
        await self._pool.close()
