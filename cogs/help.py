import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    """Custom help command to display available commands, descriptions, examples, and aliases."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Displays a list of available commands for each cog."""
        embed = discord.Embed(title="Help", description="List of available commands", color=discord.Color.blue())
        
        # Loop through each loaded cog
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            if commands_list:
                cog_commands = ""
                
                # Loop through each command in the cog
                for command in commands_list:
                    help_text = command.help or "No description available"
                    example_text = getattr(command, 'example', 'No example available')
                    aliases_text = ", ".join(command.aliases) if command.aliases else "No aliases available"
                    
                    # Format as a table row with help, aliases, and example
                    cog_commands += f"**!{command.name}**\n"
                    cog_commands += f"  **Description:** {help_text}\n"
                    cog_commands += f"  **Aliases:** {aliases_text}\n"
                    cog_commands += f"  **Example:** {example_text}\n\n"
                
                if cog_commands:
                    embed.add_field(name=cog_name, value=cog_commands, inline=False)

        # If there are no commands, notify the user
        if len(embed.fields) == 0:
            embed.description = "No commands available."

        await ctx.send(embed=embed)

# The setup function to load the cog
async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
