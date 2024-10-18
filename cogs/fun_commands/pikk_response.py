from dataclasses import dataclass

from discord.ext import commands


@dataclass
class PikkResponse(commands.Cog):
    """Respond to 'Pikk' command."""

    @commands.command(
        help="""
        Use `!pikk` to trigger Tormod's special command.
        """,
        aliases=["special", "pikkresponse"],
        brief="Tormod's special command."
    )
    async def pikk(self, ctx):
        """Tormod's special command."""
        member = ctx.author
        await ctx.send(f"Hello beautiful, {member.display_name}! 😘 Tormod has a big pikk and has entered the chat.")

async def setup(bot):
    await bot.add_cog(PikkResponse())
