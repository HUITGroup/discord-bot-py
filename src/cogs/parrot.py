from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


ROOT = Path(__file__).resolve().parents[2]

class Parrot(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='parrot', description='party parrot!')
  async def parrot(self, interaction: discord.Interaction):
    parrot = discord.File(fp=str(ROOT / 'assets' / 'gif' / '60fpsparrot.gif'))
    await interaction.response.send_message(parrot)

async def setup(bot: commands.Bot):
  await bot.add_cog(Parrot(bot))
