import discord
from discord.ext import commands

import sys
import time
import datetime
import os

from ..helpers.helper_functions import confirm_action

class DeveloperCommands:
    """Commands just for the developer, mainly for testing."""

    def __init__(self, database):
        self.database = database

    @commands.command(hidden=True, aliases=["speak"])
    @commands.has_role("Quanta's Owner")
    async def say(self, ctx: commands.Context, *text: str):
        """Says what you say!
        
        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            *text {str} -- The text for the bot to say.      
        """

        await ctx.message.delete()
        await ctx.send(" ".join(text))

    @commands.command(hidden=True, aliases=["stop", "shutdown", "end"])
    @commands.has_role("Quanta's Owner")
    async def kill(self, ctx: commands.Context):
        """Bye bye Quanta...
        
        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        confirm = await confirm_action(ctx)
        if not confirm:
            return

        message = await ctx.send("Goodbye...")
        await ctx.bot.logout()

    @commands.command(hidden=True, aliases=["guild_info", "guild-info"])
    @commands.has_role("Quanta's Owner")
    async def guildInfo(self, ctx: commands.Context):
        """Retrieve info about this guild.
        
        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        guild = ctx.guild
        embed = discord.Embed()#color="blue")

        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Name",       value=guild.name)
        embed.add_field(name="ID",         value=guild.id)
        embed.add_field(name="Created at", value=guild.created_at.strftime("%x"))
        embed.add_field(name="Owner",      value=guild.owner)
        embed.add_field(name="Members",    value=guild.member_count)
        embed.add_field(name="Channels",   value=len(guild.channels))
        embed.add_field(name="Roles",      value=len(guild.role_hierarchy) - 1) # Remove @everyone
        embed.add_field(name="Emoji",      value=len(guild.emojis))
        embed.add_field(name="Region",     value=guild.region.name)
        embed.add_field(name="Icon URL",   value=guild.icon_url or "This guild has no icon.")

        await ctx.send(embed=embed)
    
    @commands.command(hidden=True, aliases=["force", "dev"])
    @commands.has_role("Quanta's Owner")
    async def sudo(self, ctx: commands.Context, quiet: bool=True, *args):
        """Force a command to run without perms.
        
        Arguments:
            ctx {commands.Context} -- Informtion about where the command was run.
            quiet {bool} -- Whether to run silently or not.

        """
        if quiet == True:
            await ctx.message.delete()
        
    @commands.command(hidden=True, aliases=["run"])  
    async def eval(self, ctx: commands.Context, quiet: bool=False):
        """[summary]
        
        Arguments:
            ctx {commands.Context} -- [description]
            quiet {bool} -- [description] (default: {False})
        """

        pass


    async def __local_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

