import asyncio
import signal

from loguru import logger


def setup_signal_handlers(bot, on_exit):
    """Set up signal handlers for graceful bot shutdown."""

    def handle_exit_signal(signal, frame):
        """Handle the signal to perform the bot's exit routine."""
        logger.info("Received exit signal. Cleaning up...")
        asyncio.run_coroutine_threadsafe(on_exit(), bot.loop)

    # Catch the Ctrl+C (SIGINT) interrupt
    signal.signal(signal.SIGINT, handle_exit_signal)
    # Optional: Catch other signals like SIGTERM for external shutdown requests
    signal.signal(signal.SIGTERM, handle_exit_signal)
