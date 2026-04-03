"""p"""

from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')

MY_ID = 521879689447473152

class Move(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='move', description='party parrot!')
  async def move(self, interaction: discord.Interaction):

    await interaction.response.send_message()

async def setup(bot: commands.Bot):
  await bot.add_cog(Move(bot))
