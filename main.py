import asyncio

import discord
from discord.ext import commands
from loguru import logger

from config import config
from utils.signal_handler import \
    setup_signal_handlers  # Import the signal handler

# Initialize bot with intents
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


async def load_all_cogs():
    """Load all cogs from different categories."""
    cogs = [
        "cogs.help",
        "cogs.coin_tasks",
        "cogs.coin_commands",
        "cogs.fun_commands",
        "cogs.utility",
        "cogs.game",
    ]

    # Dynamically load each cog
    for cog in cogs:
        await load_cog(cog)


async def main():
    """Main entry point to start the bot and load cogs."""
    logger.info("Starting the bot and adding cogs...")
    # Load all cogs
    await load_all_cogs()

    # Start the bot
    try:
        await bot.start(config.TOKEN)
    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")


async def load_cog(cog_name: str):
    """Helper function to load a cog and handle errors."""
    try:
        await bot.load_extension(cog_name)
        logger.info(f"Successfully loaded '{cog_name}' cog.")
    except Exception as e:
        logger.error(f"Failed to load '{cog_name}' cog: {e}")


# On ready event
@bot.event
async def on_ready():
    logger.info("Bot started successfully.")
    # Message the channel saying the bot is online
    channel = bot.get_channel(config.CHAT_CHANNEL_ID)
    await channel.send("🚀 **CrazyBlazin Bot is now online**")


# On exit event cleanup and save data
@bot.event
async def on_exit():
    logger.info("Bot is exiting...")
    # Message the channel saying the bot is offline
    channel = bot.get_channel(config.CHAT_CHANNEL_ID)
    await channel.send("🧨🖥️🔥 **CrazyBlazin Bot is now offline** 🧨🖥️🔥")
    # Close the bot
    await bot.close()


if __name__ == "__main__":
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers(bot, on_exit)

    # Start the bot
    asyncio.run(main())
