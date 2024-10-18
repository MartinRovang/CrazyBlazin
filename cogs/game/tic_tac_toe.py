import discord
from discord.ext import commands
from discord.ui import Button, View
from loguru import logger
from utils.dbhandler import DataBaseHandler

db_handler = DataBaseHandler()

# Define the button class for Tic-Tac-Toe
class TicTacToeButton(Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=x)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if interaction.user != view.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        if self.label != "\u200b":
            await interaction.response.send_message("This position is already taken!", ephemeral=True)
            return

        # Update the button with the current player's symbol (X or O)
        self.label = view.current_player_symbol
        self.style = (
            discord.ButtonStyle.success if view.current_player_symbol == "X" else discord.ButtonStyle.danger
        )
        self.disabled = True

        # Update the game state
        view.board[self.x][self.y] = view.current_player_symbol

        # Check for a winner or tie
        if view.check_winner():
            view.disable_all_buttons()
            await interaction.response.edit_message(
                content=f"Game over! {interaction.user.mention} won!", view=view
            )
            view.award_winner(interaction.user)
        elif view.is_tie():
            view.disable_all_buttons()
            await interaction.response.edit_message(content="It's a tie!", view=view)
            view.refund_bets()
        else:
            # Switch turns
            view.switch_turns()
            await interaction.response.edit_message(
                content=f"It's {view.current_player.mention}'s turn!", view=view
            )


# Define the view class for Tic-Tac-Toe
class TicTacToeView(View):
    def __init__(self, player_x: discord.User, player_o: discord.User, bet_amount: int):
        super().__init__(timeout=None)  # Disable timeout
        self.current_player = player_x
        self.player_x = player_x
        self.player_o = player_o
        self.current_player_symbol = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.bet_amount = bet_amount

        # Deduct coins from both players
        db_handler.add_coins(user_id=self.player_x.id, username=self.player_x.name, amount=-self.bet_amount)
        db_handler.add_coins(user_id=self.player_o.id, username=self.player_o.name, amount=-self.bet_amount)

        # Add buttons to the view (3x3 grid)
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def switch_turns(self):
        """Switch the turn between the two players."""
        if self.current_player == self.player_x:
            self.current_player = self.player_o
            self.current_player_symbol = "O"
        else:
            self.current_player = self.player_x
            self.current_player_symbol = "X"

    def check_winner(self) -> bool:
        """Check if there is a winner."""
        # Rows, columns, and diagonals
        lines = (
            self.board,  # rows
            [list(col) for col in zip(*self.board)],  # columns
            [  # diagonals
                [self.board[i][i] for i in range(3)],
                [self.board[i][2 - i] for i in range(3)],
            ],
        )
        for line_group in lines:
            for triplet in line_group:
                if triplet[0] == triplet[1] == triplet[2] != "":
                    return True
        return False

    def is_tie(self) -> bool:
        """Check if the game is a tie."""
        return all(cell != "" for row in self.board for cell in row)

    def disable_all_buttons(self):
        """Disable all buttons after the game ends."""
        for child in self.children:
            child.disabled = True
        self.stop()

    def award_winner(self, winner: discord.User):
        """Award the total bet amount to the winner."""
        total_bet = self.bet_amount * 2
        db_handler.add_coins(user_id=winner.id, username=winner.name, amount=total_bet)
        logger.info(f"Awarded {total_bet} coins to {winner.name}")

    def refund_bets(self):
        """Refund the bet amount to both players in case of a tie."""
        db_handler.add_coins(
            user_id=self.player_x.id, username=self.player_x.name, amount=self.bet_amount
        )
        db_handler.add_coins(
            user_id=self.player_o.id, username=self.player_o.name, amount=self.bet_amount
        )
        logger.info(
            f"Refunded {self.bet_amount} coins to {self.player_x.name} and {self.player_o.name}"
        )


class AcceptDeclineView(View):
    def __init__(self, challenger: discord.Member, opponent: discord.Member, bet: int):
        super().__init__(timeout=60)  # Timeout after 60 seconds if no response
        self.challenger = challenger
        self.opponent = opponent
        self.bet = bet
        self.message = None  # Will be set after sending the message
        logger.debug(
            f"View initialized: Challenger={self.challenger.name}, Opponent={self.opponent.name}, Bet={self.bet}"
        )

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: Button):
        """Start the game if the opponent accepts."""
        logger.debug(f"Accept button pressed by {interaction.user.name}")
        if interaction.user != self.opponent:
            logger.debug(
                f"Accept button press rejected - {interaction.user.name} is not the opponent"
            )
            await interaction.response.send_message(
                "Only the challenged player can accept.", ephemeral=True
            )
            return

        logger.info(f"{self.opponent.name} accepted the challenge.")
        self.stop()  # Stop the accept/decline view

        # Start the game with the bet
        view = TicTacToeView(self.challenger, self.opponent, self.bet)
        await interaction.response.edit_message(
            content=f"Tic-Tac-Toe: {self.challenger.mention} vs {self.opponent.mention}\n{self.challenger.mention}'s turn (X)\nBet: {self.bet} coins each",
            view=view,
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: Button):
        """Cancel the game if the opponent declines."""
        logger.debug(f"Decline button pressed by {interaction.user.name}")
        if interaction.user != self.opponent:
            logger.debug(
                f"Decline button press rejected - {interaction.user.name} is not the opponent"
            )
            await interaction.response.send_message(
                "Only the challenged player can decline.", ephemeral=True
            )
            return

        logger.info(f"{self.opponent.name} declined the challenge.")
        self.stop()  # Stop the accept/decline view

        await interaction.response.edit_message(
            content=f"{self.opponent.mention} declined the Tic-Tac-Toe challenge.", view=None
        )

    async def on_timeout(self):
        """Handle the view timing out."""
        logger.info("AcceptDeclineView has timed out.")
        # Disable the buttons
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(content="The challenge has timed out.", view=None)


class TicTacToeGame(commands.Cog):
    """Tic-Tac-Toe game with betting between two players."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="""Challenge a user to a Tic-Tac-Toe game with a bet.""",
        aliases=["ttt", "tic"],
        brief="Challenge a user to Tic-Tac-Toe with a bet.",
    )
    async def tictactoe(
        self, ctx: commands.Context, opponent: discord.Member, bet: int
    ):
        """Start a Tic-Tac-Toe game between the author and the opponent with a bet."""
        logger.debug(
            f"Received Tic-Tac-Toe command from {ctx.author.name} to challenge {opponent.name} with a bet of {bet}"
        )

        if opponent.bot:
            logger.warning(f"{ctx.author.name} tried to challenge a bot.")
            await ctx.send("You can't play against a bot!")
            return

        if ctx.author == opponent:
            logger.warning(f"{ctx.author.name} tried to challenge themselves.")
            await ctx.send("You cannot challenge yourself!")
            return

        # Validate bet amount
        if bet <= 0:
            logger.warning(f"Invalid bet amount: {bet}")
            await ctx.send("The bet amount must be a positive number.")
            return

        # Check if both players have enough coins
        author_coins = db_handler.get_coins(user_id=ctx.author.id)[0]
        opponent_coins = db_handler.get_coins(user_id=opponent.id)[0]

        logger.debug(
            f"{ctx.author.name} has {author_coins} coins, {opponent.name} has {opponent_coins} coins"
        )

        if author_coins < bet:
            logger.warning(
                f"{ctx.author.name} does not have enough coins to bet {bet}."
            )
            await ctx.send(
                f"{ctx.author.mention}, you don't have enough coins to bet {bet}."
            )
            return
        if opponent_coins < bet:
            logger.warning(
                f"{opponent.name} does not have enough coins to bet {bet}."
            )
            await ctx.send(
                f"{opponent.mention} doesn't have enough coins to bet {bet}."
            )
            return

        logger.info(
            f"Sending Tic-Tac-Toe challenge to {opponent.name} with bet of {bet}"
        )
        # Send challenge request to opponent with Accept/Decline buttons
        view = AcceptDeclineView(ctx.author, opponent, bet)
        message = await ctx.send(
            f"{opponent.mention}, {ctx.author.mention} has challenged you to a Tic-Tac-Toe game with a bet of {bet} coins! Do you accept?",
            view=view,
        )
        view.message = message  # Store the message reference in the view for timeout handling


# The setup function to load the cog
async def setup(bot):
    await bot.add_cog(TicTacToeGame(bot))
