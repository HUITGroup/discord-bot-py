"""p"""

import logging
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.utils.constants import GUILD_ID

ROOT = Path(__file__).resolve().parents[3]
ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')

MY_ID = 521879689447473152

class Promotion(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='promotion', description='進級用コマンド')
  async def promotion(self, interaction: discord.Interaction):
    promotion_dict = {
      'TIMES B1': 'TIMES B2',
      'TIMES B2': 'TIMES B3',
      'TIMES B3': 'TIMES B4',
      'TIMES B4': 'TIMES M/D',
      'TIMES B5': 'TIMES B6',
    }

    await interaction.response.send_message('test')
    logger = logging.getLogger('huitLogger')

    for channel in self.bot.get_all_channels():
      if not channel.category:
        continue
      if not isinstance(channel, discord.TextChannel):
        continue

      if channel.category.name in promotion_dict:
        next_ = promotion_dict[channel.category.name]

        guild = self.bot.get_guild(GUILD_ID)
        assert guild

        next_category = discord.utils.get(guild.categories, name=next_)
        assert next_category

        await channel.edit(category=next_category)

        logger.info(f'Moved {channel.name}')

async def setup(bot: commands.Bot):
  await bot.add_cog(Promotion(bot))
