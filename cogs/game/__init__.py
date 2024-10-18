from discord.ext import commands

async def setup(bot: commands.Bot):
    """Load the Tic-Tac-Toe game cog."""
    await bot.load_extension("cogs.game.tic_tac_toe")
    await bot.load_extension("cogs.game.roulette")
    await bot.load_extension("cogs.game.lotto")
    await bot.load_extension("cogs.game.slot_machine")
