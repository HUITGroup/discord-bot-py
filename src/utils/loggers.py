import asyncio
import logging

import discord
from discord.ext import commands

from utils.constants import GUILD_ID, LEVELNAME_TO_COLOR, LOG_CHANNEL_ID

logger = logging.getLogger('textLogger')

class DiscordHandler(logging.Handler):
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot
    self.loop: asyncio.AbstractEventLoop|None = None

  def emit(self, record: logging.LogRecord):
    try:
      self.loop = asyncio.get_running_loop()
    except RuntimeError:
      logger.warning('Skipped: no running event loop')
      return

    message = self.format(record)
    coro = self.send_to_discord(message, record.levelname)
    asyncio.run_coroutine_threadsafe(coro, self.loop)

  async def send_to_discord(self, message: str, level: str):
    guild = self.bot.get_guild(GUILD_ID)
    if guild is None:
      logger.warning('Skipped: either bot has no yet started or GUILD_ID is wrong')
      return

    channel = guild.get_channel(LOG_CHANNEL_ID)
    assert isinstance(channel, discord.TextChannel)
    print(channel)
    if channel and message.strip():
      embed = discord.Embed(
        title=level,
        description=f"```\n{message[-1900:]}\n```",
        color=LEVELNAME_TO_COLOR[level],
      )
      await channel.send(embed=embed)
      # await channel.send(f"```\n{message[-1900:]}\n```")
