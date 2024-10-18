from dataclasses import dataclass, field

from discord import Embed
from discord.ext import commands

from utils.dbhandler import DataBaseHandler


@dataclass
class LeaderboardCommand(commands.Cog):
    """Display the top users with the most coins."""
    db_handler: DataBaseHandler = field(default_factory=DataBaseHandler)

    @commands.command(
        help="""
        Use `!leaderboard` to check the top 10 users with the most coins.
        """,
        aliases=["top", "rankings"],
        brief="Check the top 10 users."
    )

    async def leaderboard(self, ctx):
        """Display the top 10 users with the most coins."""
        top_users = self.db_handler.get_top_users(limit=10)
        if not top_users:
            await ctx.send("No one has earned any coins yet.")
            return

        leaderboard_text = "**Top Coin Leaders:**\n"
        position = 1
        for _, username, coins in top_users:
            if position == 1:
                leaderboard_text += f"🥇 **{username}**: {coins} coins\n"
            elif position == 2:
                leaderboard_text += f"🥈 **{username}**: {coins} coins\n"
            elif position == 3:
                leaderboard_text += f"🥉 **{username}**: {coins} coins\n"
            else:
                leaderboard_text += f"{position}. **{username}**: {coins} coins\n"
            position += 1

        embed = Embed(title="Leaderboard", description=leaderboard_text, color=0x00ff00)
        await ctx.send(embed=embed)

# The setup function to load the cog
async def setup(bot):
    await bot.add_cog(LeaderboardCommand())
