import logging

import discord
from discord.ext import commands

from utils.constants import LOG_CHANNEL_ID


class DiscordHandler(logging.Handler):
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot

  def emit(self, record: logging.LogRecord):
    message = self.format(record)
    coro = self.send_to_discord(message)
    self.bot.loop.create_task(coro)

  async def send_to_discord(self, message: str):
    channel = self.bot.get_channel(LOG_CHANNEL_ID)
    assert isinstance(channel, discord.TextChannel)
    if channel and message.strip():
      await channel.send(f"[LOG]```\n{message[-1900:]}\n```")
