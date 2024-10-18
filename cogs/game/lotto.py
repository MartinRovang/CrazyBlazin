import random
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from loguru import logger
from config import config
from dataclasses import dataclass, field
from utils.dbhandler import DataBaseHandler
from datetime import datetime, timedelta, time, timezone

# Initialize database handler
db_handler = DataBaseHandler()

# Keep track of tickets
lotto_tickets = {}
total_lotto_sum = config.LOTTO_BASELINE

# Create a Lotto View with a Button
class LottoView(View):
    def __init__(self, msg):
        super().__init__(timeout=None)  # Ensures the button doesn't disappear
        self.msg = msg

    @discord.ui.button(label="💵Buy Lotto Tickets", style=discord.ButtonStyle.primary)
    async def buy_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show the ticket input modal
        modal = TicketInputModal(view=self)  # Pass the current view instance to the modal
        await interaction.response.send_modal(modal)

class TicketInputModal(discord.ui.Modal, title="Buy Lotto Tickets - 💵150💵 per ticket"):
    ticket_count = discord.ui.TextInput(label="Number of Tickets", placeholder="Enter number of tickets", min_length=1)

    def __init__(self, view):
        super().__init__()
        self.view = view  # Keep a reference to the parent view

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        user_id = user.id
        
        # Get the number of tickets from the modal input
        try:
            number_of_tickets = int(self.ticket_count.value)
            if number_of_tickets <= 0:
                await interaction.response.send_message("Please enter a valid number of tickets.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)
            return

        # Process ticket purchase
        user_coins = db_handler.get_coins(user_id=user_id)[0]
        total_cost = number_of_tickets * config.LOTTO_TICKET_PRICE
        
        if user_coins < total_cost:
            await interaction.response.send_message("You don't have enough coins to buy that many tickets.", ephemeral=True)
            return
        
        # Deduct coins and update the lottery data
        global total_lotto_sum
        total_lotto_sum += total_cost  # Update total pot

        # Add tickets to the user
        if user_id not in lotto_tickets:
            lotto_tickets[user_id] = []

        for _ in range(number_of_tickets):
            ticket_number = random.randint(1, 10000)
            lotto_tickets[user_id].append(ticket_number)

        # Update the existing message with ticket info
        tickets_info = "\n".join(
            [f"{interaction.guild.get_member(uid).name}: {len(tickets)} tickets" for uid, tickets in lotto_tickets.items()]
        )
        
        # Update the original message instead of sending a new one
        await interaction.response.send_message(f"🎟️ {user.name} bought {number_of_tickets} lotto tickets! Total Cost: {total_cost} coins.", ephemeral=True)

        # Update the message with the view
        await self.view.msg.edit(
            content=f"🎲 Current Draw:\n{tickets_info}\nCurrent Pot: 💰 {total_lotto_sum} CBC",
            view=self.view
        )
        logger.info(f"{user.name} bought {number_of_tickets} tickets.")


### Lotto Roll Task
@tasks.loop(time=time(20, 00, tzinfo=timezone(timedelta(hours=2))))
async def roll_lotto(ctx):
    global total_lotto_sum
    if lotto_tickets:
        winning_ticket = random.randint(1, 10000)
        winner = None
        for user_id, tickets in lotto_tickets.items():
            if winning_ticket in tickets:
                winner = user_id
                break

        if winner:
            winner_user = await ctx.fetch_user(winner)
            db_handler.add_coins(user_id=winner, username=winner_user.name, amount=total_lotto_sum)
            message = f"🏆 The winning ticket is {winning_ticket}! Congratulations {winner_user.name}! You've won {total_lotto_sum} coins!"
        else:
            message = f"No winners today. Better luck tomorrow! Winning ticket #: 🎟️ {winning_ticket} total pot: {total_lotto_sum}"

        # Reset tickets for the next day
        lotto_tickets.clear()

        # Send the result to a specific channel (replace CHANNEL_ID with actual channel ID)
        channel = ctx.get_channel(config.CHAT_CHANNEL_ID)
        if channel:
            await channel.send(message)
        else:
            logger.error("Channel not found. Check your CHANNEL_ID.")
        
        logger.info(f"Lotto rolled. Winning ticket: {winning_ticket}")
    else:
        logger.info("No tickets were bought today.")

    # Reset the total lotto sum
    total_lotto_sum = config.LOTTO_BASELINE

@dataclass
class LottoGame(commands.Cog):
    """Lotto game 
    Buy a lotto ticket and win the jackpot!
    """
    bot: commands.Bot = field(default_factory=commands.Bot)

    def __post_init__(self):
        # Start the lotto roll loop when the cog is loaded
        logger.info("Starting Lotto Roll Task...")
        roll_lotto.start(ctx=self.bot)

    @commands.command(
        help="""Buy a lotto ticket and win the jackpot! Use `!lotto` to buy a ticket.""",
        aliases=["lottery", "ticket"],
        brief="Buy a lotto ticket and win the jackpot!"
    )
    async def lotto(self, ctx: commands.Context):
        """Buy a lotto ticket and win the jackpot!"""
        view = LottoView(msg=await ctx.send("🎲 Buy your lotto ticket for today's draw! (Draw starts at 20:00!)"))
        await view.msg.edit(view=view)  # Set the view for the existing message
        logger.info("Lotto command used.")

# The setup function to load the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(LottoGame(bot))
