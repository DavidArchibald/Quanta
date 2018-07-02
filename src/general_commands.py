import discord
from discord.ext import commands

class GeneralCommands:
    """Commands for everyone."""

    @commands.command()
    async def ping(self, ctx: commands.Context, round_to=4):
        """Returns the bot latency.
        
        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
        
        Keyword Arguments:
            exact {int} -- How many digits to round the bot latency to. (default: {4})
        """

        # Check digits is a string then casefold
        if isinstance(round_to, str) and (round_to.casefold() == "true" or round_to.casefold() == "exact"):
            pingTime = ctx.bot.latency
        elif isinstance(round_to, str) and round_to.isdigit():
            pingTime = round(ctx.bot.latency, int(round_to))
        else:
            pingTime = round(ctx.bot.latency, 4) #fallback

        await ctx.send("Pong! | {0} seconds".format(pingTime))
        await ctx.message.delete()
