from discord.ext import commands


async def setup(bot: commands.Bot):
    """Load all coin-related commands."""
    await bot.load_extension("cogs.coin_commands.balance")
    await bot.load_extension("cogs.coin_commands.reset_coins")
    await bot.load_extension("cogs.coin_commands.leaderboard")
