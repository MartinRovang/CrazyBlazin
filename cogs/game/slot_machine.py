import random
import discord
from discord.ext import commands
from loguru import logger
from utils.dbhandler import DataBaseHandler
import asyncio

db_handler = DataBaseHandler()

class SlotMachineGame(commands.Cog):
    """Slot Machine game with a 3x3 grid where users can bet coins and win based on the outcome."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="""Play the slot machine game and try your luck!

        **Usage:**
        `!slot <bet amount>`

        **Example:**
        `!slot 50` - Bet 50 coins on the slot machine.

        **Jackpot Payouts (3 matching symbols on a payline):**
        7️⃣7️⃣7️⃣ : Bet × **50**
        ⭐⭐⭐ : Bet × **20**
        🔔🔔🔔 : Bet × **10**
        🍇🍇🍇 : Bet × **7**
        🍉🍉🍉 : Bet × **5**
        🍊🍊🍊 : Bet × **4**
        🍋🍋🍋 : Bet × **3**
        🍒🍒🍒 : Bet × **2**
        """,
        aliases=["slots", "pull"],
        brief="Play the slot machine game and win coins."
    )
    async def slot(self, ctx: commands.Context, bet: int | str):
        """Allows a user to play the slot machine with a specified bet amount."""
        user = ctx.author
        logger.debug(f"{user.name} initiated a slot machine game with a bet of {bet} coins.")

        # Validate bet amount
        if isinstance(bet, int):
            if bet <= 0:
                logger.warning(f"{user.name} attempted to bet an invalid amount: {bet}.")
                await ctx.send("The bet amount must be a positive number.")
                return

        # Check if user has enough coins
        user_coins = db_handler.get_coins(user_id=user.id)[0]
        logger.debug(f"{user.name} has {user_coins} coins.")

        if isinstance(bet, str):
            if bet.lower() == "all":
                bet = user_coins
                if bet == 0:
                    logger.warning(f"{user.name} tried to bet all coins but has none.")
                    await ctx.send("You don't have any coins to bet.")
                    return

        if user_coins < bet:
            logger.warning(f"{user.name} does not have enough coins to bet {bet}.")
            await ctx.send(f"{user.mention}, you don't have enough coins to bet {bet}.")
            return

        # Deduct the bet amount from user's coins
        db_handler.add_coins(user_id=user.id, username=user.name, amount=-bet)
        logger.info(f"Deducted {bet} coins from {user.name} for the slot machine bet.")

        # Define slot machine emojis
        emojis = ["🍒", "🍋", "🍊", "🍉", "🍇", "⭐", "🔔", "7️⃣"]
        num_rows = 3
        num_cols = 3  # Number of columns (reels)
        num_spins = 5  # Number of times the reels will spin

        # Send initial message with placeholder emojis
        placeholder = "🔳"
        grid_display = [[placeholder for _ in range(num_cols)] for _ in range(num_rows)]
        grid_message = self.format_grid_message(user, grid_display)
        result_message = await ctx.send(grid_message)

        # Animate the spinning reels
        for _ in range(num_spins):
            # Randomly select emojis for each cell in the grid
            grid_display = [[random.choice(emojis) for _ in range(num_cols)] for _ in range(num_rows)]
            # Update the message
            grid_message = self.format_grid_message(user, grid_display)
            await result_message.edit(content=grid_message)
            # Wait for a short duration before next spin
            await asyncio.sleep(0.3)

        # Final spin to determine the outcome
        final_grid = [[random.choice(emojis) for _ in range(num_cols)] for _ in range(num_rows)]
        final_message_content = self.format_grid_message(user, final_grid, final=True)

        # Determine winnings
        payout, winning_lines = self.calculate_payout(final_grid, bet)
        if payout > 0:
            # Add winnings to user's coins
            db_handler.add_coins(user_id=user.id, username=user.name, amount=payout)
            logger.info(f"Awarded {payout} coins to {user.name} from the slot machine.")
            final_message_content += f"\n\n🎉 You won **{payout}** coins! 🎉\n"
            final_message_content += f"Winning lines: {', '.join(winning_lines)}"
        else:
            final_message_content += "\n\n❌ No winning combinations this time. Better luck next spin!"

        # Update the message with the final result
        await result_message.edit(content=final_message_content)

    def format_grid_message(self, user, grid, final=False):
        """Formats the grid into a message string."""
        title = "🎰 **Slot Machine** 🎰\n\n"
        if not final:
            message = f"{user.mention} is spinning the reels...\n\n"
        else:
            message = f"{user.mention} spun the reels and got:\n\n"

        grid_lines = [' | '.join(row) for row in grid]
        grid_str = '\n'.join(grid_lines)

        return title + message + grid_str

    def calculate_payout(self, grid, bet):
        """Calculates the payout based on the grid and returns the payout amount and winning lines."""
        # Define the paylines (horizontal, vertical, diagonal)
        paylines = {
            "Top Row": [(0, 0), (0, 1), (0, 2)],
            "Middle Row": [(1, 0), (1, 1), (1, 2)],
            "Bottom Row": [(2, 0), (2, 1), (2, 2)],
            "Left Column": [(0, 0), (1, 0), (2, 0)],
            "Middle Column": [(0, 1), (1, 1), (2, 1)],
            "Right Column": [(0, 2), (1, 2), (2, 2)],
            "Diagonal Top-Left to Bottom-Right": [(0, 0), (1, 1), (2, 2)],
            "Diagonal Bottom-Left to Top-Right": [(2, 0), (1, 1), (0, 2)],
        }

        payout = 0
        winning_lines = []

        # Check each payline for matching symbols
        for line_name, positions in paylines.items():
            symbols = [grid[x][y] for x, y in positions]
            if symbols[0] == symbols[1] == symbols[2]:
                # All symbols match
                line_payout = bet * 5  # Adjust the multiplier as desired
                payout += line_payout
                winning_lines.append(line_name)

        return payout, winning_lines

    # Optional: Handle errors globally within the cog
    @slot.error
    async def slot_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid bet amount. Please enter a valid number.")
        else:
            logger.error(f"An error occurred: {error}")
            await ctx.send("An unexpected error occurred. Please try again later.")

# The setup function to load the cog
async def setup(bot):
    await bot.add_cog(SlotMachineGame(bot))
