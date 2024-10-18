from discord.ext import commands


async def setup(bot: commands.Bot):
    """Load both fun_commands-related tasks."""
    await bot.load_extension("cogs.fun_commands.pikk_response")
