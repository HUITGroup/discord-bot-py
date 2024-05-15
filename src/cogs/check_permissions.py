import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

GUILD_ID = int(os.getenv('GUILD_ID'))

class CheckPermissions(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='check_permissions')
  @app_commands.checks.has_permissions(administrator=True)
  async def check_permissions(self, interaction: discord.Interaction, role_name: str):
    await interaction.response.send_message("start")
    guild = self.bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name=role_name)

    for channel in guild.channels:
      if not channel.permissions_for(role).view_channel:
        await interaction.channel.send(channel.name)



async def setup(bot: commands.Bot):
  await bot.add_cog(CheckPermissions(bot))
