import logging
import sys

import discord
from discord.ext import commands


class DiscordLogHandler(logging.Handler):
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

class DiscordStderr:
  def __init__(self, bot: commands.Bot, channel_id: int):
    self.bot = bot
    self.channel_id = channel_id

  def write(self, message: str):
    if message.strip():
      coro = self.send_to_discord(message)
      self.bot.loop.create_task(coro)

  def flush(self):
    pass

  async def send_to_discord(self, message: str):
    channel = self.bot.get_channel(self.channel_id)
    assert isinstance(channel, discord.TextChannel)
    if channel:
      await channel.send(f"[STDERR]```\n{message[-1900:]}\n```")


async def on_ready():
  print(f'Logged in as {bot.user}')

  # discord.py ログのファイル出力
  file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
  file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

  # discord.py ログの Discord チャンネル送信
  discord_handler = DiscordLogHandler(bot, DISCORD_LOG_CHANNEL_ID)
  discord_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

  discord_logger = logging.getLogger('discord')
  discord_logger.setLevel(logging.INFO)
  discord_logger.addHandler(file_handler)
  discord_logger.addHandler(discord_handler)

  # stderr を Discord に送る
  sys.stderr = DiscordStderr(bot, DISCORD_LOG_CHANNEL_ID)

bot.run("YOUR_TOKEN")
