import fuzzywuzzy
from fuzzywuzzy import fuzz

import discord
from discord.ext import commands

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
