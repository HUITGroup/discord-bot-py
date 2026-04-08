"""p"""

import logging
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.db import crud
from src.utils.constants import GUILD_ID

ROOT = Path(__file__).resolve().parents[3]
ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')

MY_ID = 521879689447473152

class Promotion(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='promotion', description='進級用コマンド')
  @app_commands.checks.has_permissions(administrator=True)
  async def promotion(self, interaction: discord.Interaction):
    promotion_dict = {
      'TIMES B1': 'TIMES B2',
      'TIMES B2': 'TIMES B3',
      'TIMES B3': 'TIMES B4',
      'TIMES B4': 'TIMES B5/M1',
      'TIMES B5/M1': 'TIMES B6/M2',
      'TIMES B6/M2': 'TIMES other',
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

  @app_commands.command(name='move', description='test move command')
  @app_commands.checks.has_permissions(administrator=True)
  async def move(self, interaction: discord.Interaction):
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    await interaction.response.send_message('b')

    grade_dict = {
      'b4': 'TIMES B5/M1',
      'm1': 'TIMES B6/M2',
      'm2': 'other',
      'd': 'TIMES D',
    }

    for channel in guild.channels:
      if not isinstance(channel, discord.TextChannel):
        continue
      if channel.category is None:
        continue
      elif channel.category.name != 'TIMES B6/M2':
        continue

      user, err = await crud.get_user_by_channel_id(channel.id)
      if err:
        await interaction.channel.send(f'-1 {channel.name}')
        continue

      if user is None:
        await interaction.channel.send(f'skipped channel {channel.name}')
        continue

      next_ = grade_dict[user.grade]
      category = discord.utils.get(guild.categories, name=next_)
      await channel.edit(category=category)

async def setup(bot: commands.Bot):
  await bot.add_cog(Promotion(bot))
