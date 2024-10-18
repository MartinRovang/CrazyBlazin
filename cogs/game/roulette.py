import random
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import asyncio

# Roulette colors and numbers
ROULETTE_NUMBERS = {
    0: 'green', 
    1: 'red', 2: 'black', 3: 'red', 4: 'black', 5: 'red', 6: 'black', 7: 'red', 8: 'black', 9: 'red', 10: 'black', 
    11: 'black', 12: 'red', 13: 'black', 14: 'red', 15: 'black', 16: 'red', 17: 'black', 18: 'red', 19: 'red', 
    20: 'black', 21: 'red', 22: 'black', 23: 'red', 24: 'black', 25: 'red', 26: 'black', 27: 'red', 28: 'black', 
    29: 'black', 30: 'red', 31: 'black', 32: 'red', 33: 'black', 34: 'red', 35: 'black', 36: 'red'
}

# Emoji representations for colors
COLOR_EMOJIS = {
    'red': '🔴',
    'black': '⚫',
    'green': '🟢',
}

class BetTypeView(View):
    def __init__(self, ctx, bet_amount):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.bet_amount = bet_amount
        self.bet_type = None
        self.bet_value = None

        self.number_button = Button(label="Bet on Number", style=discord.ButtonStyle.primary)
        self.color_button = Button(label="Bet on Color", style=discord.ButtonStyle.secondary)

        self.number_button.callback = self.bet_on_number
        self.color_button.callback = self.bet_on_color

        self.add_item(self.number_button)
        self.add_item(self.color_button)

    async def bet_on_number(self, interaction: discord.Interaction):
        # Send a modal to input the number
        await interaction.response.send_modal(BetNumberModal(self))

    async def bet_on_color(self, interaction: discord.Interaction):
        # Send a message with color buttons
        await interaction.response.send_message("Choose a color:", view=ColorSelectView(self), ephemeral=True)

class BetNumberModal(Modal):
    def __init__(self, parent_view):
        super().__init__(title="Bet on Number")
        self.parent_view = parent_view

        self.number_input = TextInput(
            label="Enter a number between 0 and 36",
            placeholder="Number",
            required=True,
            min_length=1,
            max_length=2,
        )
        self.add_item(self.number_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Validate the number
        try:
            number = int(self.number_input.value)
            if 0 <= number <= 36:
                self.parent_view.bet_type = 'number'
                self.parent_view.bet_value = number
                await interaction.response.send_message(
                    f"You placed a bet on number {number}. Click 'Spin the Wheel' to proceed.",
                    view=SpinWheelView(self.parent_view),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Invalid number. Please enter a number between 0 and 36.",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message(
                "Invalid input. Please enter a valid number.",
                ephemeral=True
            )

class ColorSelectView(View):
    def __init__(self, parent_view):
        super().__init__(timeout=60)
        self.parent_view = parent_view

        self.red_button = Button(label="Red", style=discord.ButtonStyle.danger)
        self.black_button = Button(label="Black", style=discord.ButtonStyle.secondary)
        self.green_button = Button(label="Green", style=discord.ButtonStyle.success)

        self.red_button.callback = self.select_red
        self.black_button.callback = self.select_black
        self.green_button.callback = self.select_green

        self.add_item(self.red_button)
        self.add_item(self.black_button)
        self.add_item(self.green_button)

    async def select_red(self, interaction: discord.Interaction):
        self.parent_view.bet_type = 'color'
        self.parent_view.bet_value = 'red'
        await interaction.response.send_message(
            f"You placed a bet on Red. Click 'Spin the Wheel' to proceed.",
            view=SpinWheelView(self.parent_view),
            ephemeral=True
        )

    async def select_black(self, interaction: discord.Interaction):
        self.parent_view.bet_type = 'color'
        self.parent_view.bet_value = 'black'
        await interaction.response.send_message(
            f"You placed a bet on Black. Click 'Spin the Wheel' to proceed.",
            view=SpinWheelView(self.parent_view),
            ephemeral=True
        )

    async def select_green(self, interaction: discord.Interaction):
        self.parent_view.bet_type = 'color'
        self.parent_view.bet_value = 'green'
        await interaction.response.send_message(
            f"You placed a bet on Green. Click 'Spin the Wheel' to proceed.",
            view=SpinWheelView(self.parent_view),
            ephemeral=True
        )

class SpinWheelView(View):
    def __init__(self, parent_view):
        super().__init__(timeout=60)
        self.parent_view = parent_view
        self.spin_button = Button(label="Spin the Wheel", style=discord.ButtonStyle.primary)
        self.spin_button.callback = self.spin_wheel
        self.add_item(self.spin_button)

    async def spin_wheel(self, interaction: discord.Interaction):
        # Acknowledge the interaction and defer
        await interaction.response.defer(ephemeral=False)
        message = await interaction.followup.send("The wheel is spinning...")

        spin_sequence = random.choices(list(ROULETTE_NUMBERS.keys()), k=10)
        for number in spin_sequence:
            color = ROULETTE_NUMBERS[number]
            emoji = COLOR_EMOJIS[color]
            await message.edit(content=f"The wheel is spinning... {emoji} {number}")
            await asyncio.sleep(0.5)  # Adjust the sleep time for effect

        # Final result
        spin_result = random.choice(list(ROULETTE_NUMBERS.keys()))
        result_color = ROULETTE_NUMBERS[spin_result]
        result_emoji = COLOR_EMOJIS[result_color]

        # Determine win or loss
        if self.parent_view.bet_type == 'number':
            if spin_result == self.parent_view.bet_value:
                result_message = f"The wheel landed on {result_emoji} **{spin_result}**! You win with an exact number match!"
                win = True
            else:
                result_message = f"The wheel landed on {result_emoji} **{spin_result}**! You lost this round!"
                win = False
        elif self.parent_view.bet_type == 'color':
            if result_color == self.parent_view.bet_value:
                result_message = f"The wheel landed on {result_emoji} **{spin_result}**! You win with a color match!"
                win = True
            else:
                result_message = f"The wheel landed on {result_emoji} **{spin_result}**! You lost this round!"
                win = False
        else:
            result_message = "An error occurred."
            win = False

        await message.edit(content=result_message)
        self.stop()

class RouletteGame(commands.Cog):
    """Roulette game with a visual representation of the wheel using buttons."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="""
        Start a roulette game and place your bet! Use `!roulette <bet amount>` to start a game.
    
        Example usage:
        `!roulette 100` - Place a bet of 100 coins and spin the wheel!
        """,
        aliases=["rlt", "spin"],
        brief="Play a roulette game and place bets."
    )
    async def roulette(self, ctx: commands.Context, bet: int):
        """Start a roulette game. Place your bet and spin the wheel."""
        if bet <= 0:
            await ctx.send("Bet must be a positive amount!")
            return

        # Add a debug message to check if the command is triggered
        await ctx.send(f"Roulette game started with bet {bet}!")

        view = BetTypeView(ctx, bet)
        await ctx.send(f"{ctx.author.mention}, place your bet by selecting a bet type!", view=view)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(RouletteGame(bot))
