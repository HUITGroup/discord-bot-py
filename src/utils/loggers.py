import logging
import sys

import discord
from discord.ext import commands


class DiscordHandler(logging.Handler):
  def __init__(self, bot: commands.Bot, channel_id: int):
    super().__init__()
    self.bot = bot
    self.channel_id = channel_id

  def emit(self, record):
    message = self.format(record)
    coro = self.send_to_discord(message)
    self.bot.loop.create_task(coro)

  async def send_to_discord(self, message: str):
    channel = self.bot.get_channel(self.channel_id)
    assert isinstance(channel, discord.TextChannel)
    if channel and message.strip():
      await channel.send(f"[LOG]```\n{message[-1900:]}\n```")
