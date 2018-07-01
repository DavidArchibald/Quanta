import discord
from discord.ext import commands
import discord.utils

import asyncio
import re

import fuzzywuzzy
from fuzzywuzzy import fuzz

import operator

class GetUserConverter(commands.Converter):
    """Fuzzy user converter
    
    Arguments:
        commands {commands.Converter} -- Change the type of a variable.
    
    Returns:
        user {discord.User} -- A discord user if found.
    """

    async def convert(self, ctx: commands.context, identifier: str):
        result_count = 3 # Trim the results to be 3
                         # This will only support up to 10
                         # A possible fix would be "pages"

        if identifier == None or identifier == "":
            return None
        
        if identifier.startswith(r"\<@") and identifier.endswith(">"): # Handle escaped usernames
            identifier = identifier[1:]
        
        try: # Try converting it with the built in UserConverter
            # This will handle exact input in the order:
            # 1. User ID
            # 1. User Mention
            # 2. Username#discriminator
            # 3. Username
            user = await commands.UserConverter().convert(ctx, identifier)
            return user
        except:
            # Ignore any error it gives out.
            # This is only for efficency.
            pass
        
        if identifier.startswith("<@") and identifier.endswith(">"): # if in format <@{user id}> get only the user id.
            identifier = identifier[2:-1]
        
        compare_users = []
        for member in ctx.guild.members:
            user = {
                "compares": [], # What to compare
                "compare_ratio": 0, # The ratio of the closest compare to the input
                "closest_compare": "", # Which of all the compares is closest
                "member": member
            }       
            
            user["compares"] = [str(member.id), member.name]
            if member.nick != None:
                user["compares"].append(member.nick)  

            compare_users.append(user)

        result = []
        for user in compare_users:
            compares = user["compares"]
            for compare in compares:
                compare_ratio = fuzz.ratio(identifier, compare)
                if compare_ratio > user["compare_ratio"]:
                    user["compare_ratio"] = compare_ratio
                    user["closest_compare"] = compare
            result.append(user)        

        result = sorted(result, key=lambda item: item["compare_ratio"], reverse=True) # Sort from closest to farthest ratio
        result = result[:result_count] # Truncate to the top `result_count`
        # Filtering the result to a resonable threshold could also help
        #whom = await ctx.send(
        #             "**Do you mean:**\n"
        #             "{}"
        #             "".format('\n'.join(
        #                        # Results in lines of "n. closest_compare (member_name#member_discriminator)"
        #                        [
        #                            # Format the "n. " part (index + 1)
        #                            str(index + 1) + ". " + \
        #                            # Add the closest compare
        #                            item["closest_compare"] + \
        #                            # str(member) gives "username#discriminator"
        #                            " (" + str(item["member"]) + ")" \
        #                            # Loop through all of the results
        #                            for index, item in enumerate(result)
        #                        ]
        #                    )
        #                )
        #         )
        embed = discord.Embed()
        for i, item in enumerate(result):
            index = str(i + 1)
            embed.add_field(
                name="{index}. {compare}".format(index=index, compare=item["closest_compare"]),
                value=item["member"].name,
                inline=False
            )

        whom = await ctx.send("**Do you mean:**", embed=embed)
        reaction_numbers = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]
        reaction_numbers = reaction_numbers[:result_count]

        for reaction in reaction_numbers:
            await whom.add_reaction(reaction)
        
        

class HelperCommands:    
    @commands.command(aliases=["getmember", "get_member", "get-member"])
    async def getMember(self, ctx: commands.context, user: GetUserConverter):
        """Mainly to test GetUserConverter
        
        Arguments:
            ctx {commands.context} -- Information about where the command was run.
        
        Keyword Arguments:
            user {GetUserConverter} -- Gets the user
        """

        await ctx.send(user.mention)
    
    @commands.command(aliases=["getemoji", "get_emoji", "get-emoji"])
    async def getEmoji(self, ctx: commands.context, *emoji: str):
        """Get an emoji and display it.
        
        Arguments:
            ctx {commands.context} -- Information about where the command was run.
            *emoji {str} -- Get the message
        """
        await ctx.message.delete()
        
        #emoji = ' '.join(emoji)
        #emoji = unicode(emoji, "utf-8") # Emojis are above the normal planes so could normally be counted as multiple characters
        
        #if len(emoji) > 1:
        
        #else:
        await ctx.send(ctx.bot.emojis)
        await ctx.send(discord.utils.get(ctx.bot.get_all_emojis(), name=emoji))

    async def confirmAction(self, ctx: commands.context, message="Are you sure?"):
        confirm=await ctx.send(message)
        await confirm.add_reaction("✅")
        await confirm.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await confirm.delete()
            return False

        await confirm.delete()

        if str(reaction.emoji) == "✅":
            return True
        
        return False

def get_prefix(bot, msesage):
    return "?"
    
def smallest(a: str, b: str):
    ab, ba = a + b, b + a
    if ab == ba:
        return 0
    if ab < ba:
        return -1
    return 1
