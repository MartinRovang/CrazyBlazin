from dataclasses import dataclass, field

from discord.ext import commands, tasks

from config import config
from utils.dbhandler import DataBaseHandler


@dataclass
class GiveCoinsTask(commands.Cog):
    """Task to give coins to users in voice channels."""
    bot: commands.Bot
    db_handler: DataBaseHandler = field(default_factory=DataBaseHandler)

    def __post_init__(self):
        self.give_coins.start()

    @tasks.loop(seconds=config.PAY_INTERVAL)
    async def give_coins(self):
        """Give coins to users in active voice channels."""
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if not member.bot:  # Skip bots
                        coins_to_give = config.PAY_AMOUNT
                        self.db_handler.add_coins(user_id=member.id, username=member.display_name, amount=coins_to_give)

    @give_coins.before_loop
    async def before_give_coins(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(GiveCoinsTask(bot))
