from discord.ext import commands


async def setup(bot: commands.Bot):
    """Load both coin-related tasks."""
    await bot.load_extension("cogs.coin_tasks.give_coins_task")
    await bot.load_extension("cogs.coin_tasks.manage_multiplier_task")
