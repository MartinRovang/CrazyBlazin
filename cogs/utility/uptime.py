import time
from dataclasses import dataclass

from discord.ext import commands


@dataclass
class Uptime(commands.Cog):
    """Check how long the bot has been running."""
    bot: commands.Bot

    def __post_init__(self):
        self.start_time = time.time()

    @commands.command(
        help="""
        Use `!uptime` to see how long the bot has been running.
        """,
        aliases=["botuptime", "up"],
        brief="Shows the bot's uptime."
    )
    async def uptime(self, ctx):
        """Shows the bot's uptime."""
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: {hours}h {minutes}m {seconds}s")

async def setup(bot):
    await bot.add_cog(Uptime(bot))
