import logging

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger('huitLogger')

class TestLog(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='test_log', description='test')
  @app_commands.checks.has_permissions(administrator=True)
  async def test_log(self, interaction: discord.Interaction):
    logger.info('This is the info log.')
    logger.warning('This is the warning log.')
    logger.error('This is the error log.')
    logger.fatal('This is the fatal log.')
    logger.critical('This is the critical log.')

    await interaction.response.send_message('（＾ω＾）')

async def setup(bot: commands.Bot):
  await bot.add_cog(TestLog(bot))
