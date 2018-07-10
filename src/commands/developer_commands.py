import discord
from discord.ext import commands

import sys
import time
import datetime
import os

from ..helpers import helper_functions
helperCommands = helper_functions.HelperCommands()

class DeveloperCommands:
    """Commands just for the developer, mainly for testing."""

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
        await ctx.message.delete()

        confirm = await helperCommands.confirmAction(ctx)
        if not confirm:
            return

        message = await ctx.send("Goodbye...")
        time.sleep(3) # So that the goodbye message will be seen.
        
        await message.delete()
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
    
    @commands.command(hidden=True, aliases=["force", "admin"])
    @commands.has_role("Quanta's Owner")
    async def sudo(self, ctx: commands.Context):
        """Force a command to run without perms.
        
        Arguments:
            ctx {commands.Context} -- Informtion about where the command was run.
        """

        await ctx.message.delete()

        
