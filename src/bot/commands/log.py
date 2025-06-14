"""log系コマンド"""

import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.handlers import DiscordHandler


class Log(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='log_level', description='logの出力レベルを変更します')
  @app_commands.checks.has_permissions(administrator=True)
  async def log_level(
    self,
    interaction: discord.Interaction,
    level: Literal['debug', 'info', 'warning', 'error', 'critical'],
  ):
    if level.lower() not in {'debug', 'info', 'warning', 'error', 'critical'}:
      await interaction.response.send_message(
        '対応しているログレベルは\n'\
        '- debug\n'\
        '- info\n'\
        '- warning\n'\
        '- error\n'\
        '- critical\n'\
        'です'
      )
      return

    logger = logging.getLogger('huitLogger')
    for handler in logger.handlers:
      if isinstance(handler, DiscordHandler):
        handler.setLevel(level.upper())

    await interaction.response.send_message(f'ログレベルを `{level}` に変更しました')

async def setup(bot: commands.Bot):
  await bot.add_cog(Log(bot))
