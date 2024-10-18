from dataclasses import dataclass, field

import discord
from discord.ext import commands

from utils.dbhandler import DataBaseHandler
from discord.ui import Button


@dataclass
class ResetCoinsCommand(commands.Cog):
    """Reset a user's coin balance."""
    db_handler: DataBaseHandler = field(default_factory=DataBaseHandler)

    @commands.command(
        help="""
        Use `!reset_coins` to reset your coin balance.
        """,
        aliases=["resetcoins"],
        brief="Reset your coin balance."
    )
    async def reset_coins(self, ctx):
        """Reset a member's coin balance."""
        member = ctx.author

        class ConfirmResetView(View):
            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
            async def confirm(self, interaction: discord.Interaction, button: Button):
                self.db_handler.reset_coins(user_id=member.id)
                await interaction.response.send_message(f"{member.display_name}'s coins have been reset to 0.", ephemeral=True)
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def cancel(self, interaction: discord.Interaction, button: Button):
                await interaction.response.send_message("Coin reset cancelled.", ephemeral=True)
                self.stop()

        view = ConfirmResetView()
        await ctx.send("Are you sure you want to reset your coins?", view=view)

# The setup function to load the cog
async def setup(bot):
    await bot.add_cog(ResetCoinsCommand())