from dataclasses import dataclass, field

import discord
from discord.ext import commands

from utils.dbhandler import DataBaseHandler


@dataclass
class Balance(commands.Cog):
    """Check user balance."""
    db_handler: DataBaseHandler = field(default_factory=DataBaseHandler)
    
    @commands.command(
        help="""
        Use `!balance` or `!bal` to check your balance. 
        Optionally, you can mention a user (e.g., `!balance @username`) to check their balance instead.
        """,
        aliases=["bal"],
        brief="Check your coin balance."
    )
    async def balance(self, ctx, member: discord.Member = None):
        """Check your coin balance."""
        # If no member is mentioned, use the command author
        if member is None:
            member = ctx.author
        
        # Retrieve the coin balance from the database
        result = self.db_handler.get_coins(user_id=member.id)
        
        # Check if the user has any coins
        if result is None:
            await ctx.send(f"{member.display_name} has no coins yet.")
        else:
            await ctx.send(f"{member.display_name} has {result[0]} CBC.")

async def setup(bot):
    await bot.add_cog(Balance())
