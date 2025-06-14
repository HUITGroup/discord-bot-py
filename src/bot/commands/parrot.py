"""party parrotコマンド関連"""

from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')

MY_ID = 521879689447473152

class Parrot(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='parrot', description='party parrot!')
  async def parrot(self, interaction: discord.Interaction):
    parrot = discord.File(fp=str(ROOT / 'assets' / 'gif' / '60fpsparrot.gif'))
    await interaction.response.send_message(file=parrot)

  @app_commands.command(name='ultrafastparrot', description='ultrafast parrot!')
  async def ultrafastparrot(self, interaction: discord.Interaction):
    parrot = discord.File(fp=str(ROOT / 'assets' / 'gif' / 'ultrafastparrot.gif'))
    await interaction.response.send_message(file=parrot)

async def setup(bot: commands.Bot):
  await bot.add_cog(Parrot(bot))
