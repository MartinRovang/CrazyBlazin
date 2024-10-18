import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from discord.ext import commands, tasks
from loguru import logger

from config import config


@dataclass
class ManageMultiplierTask(commands.Cog):
    """Background task to manage random coin multipliers."""
    bot: commands.Bot

    def __post_init__(self):
        self.manage_multiplier_task.start()

    @tasks.loop(hours=24)
    async def manage_multiplier_task(self):
        """Handle the random coin multiplier activation."""
        global multiplier_active
        channel = self.bot.get_channel(config.CHAT_CHANNEL_ID)

        while not self.bot.is_closed():
            next_day = datetime.now() + timedelta(days=1)
            random_minutes = random.randint(0, config.RANDOM_TIME_WITHIN)
            multiplier_start = datetime.now() + timedelta(minutes=random_minutes)

            time_to_wait = (multiplier_start - datetime.now()).total_seconds()
            await asyncio.sleep(time_to_wait)

            multiplier_active = True
            logger.info(f"{config.EVENT_MULTIPLIER}x coin multiplier has started!")

            if channel:
                await channel.send(
                    f"🚀 **{config.EVENT_MULTIPLIER}x Coin Multiplier is now active!** Earn double CBC for the next {config.BONUS_TIMER_MINUTES} minutes!"
                )

            await asyncio.sleep(config.BONUS_TIMER_MINUTES * 60)
            multiplier_active = False
            logger.info(f"{config.EVENT_MULTIPLIER}x coin multiplier has ended!")

            if channel:
                await channel.send(f"⏳ **The {config.EVENT_MULTIPLIER}x Coin Multiplier has ended.** Stay tuned for the next random bonus!")

            time_to_next_day = (next_day - datetime.now()).total_seconds()
            await asyncio.sleep(time_to_next_day)

    @manage_multiplier_task.before_loop
    async def before_manage_multiplier(self):
        await self.bot.wait_until_ready()

# The setup function to load the cog
async def setup(bot):
    await bot.add_cog(ManageMultiplierTask(bot))
