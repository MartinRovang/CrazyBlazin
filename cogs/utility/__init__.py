from discord.ext import commands


async def setup(bot: commands.Bot):
    """Load both utility-related tasks."""
    await bot.load_extension("cogs.utility.uptime")
