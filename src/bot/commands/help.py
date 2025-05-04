"""helpコマンド"""

import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='help', description='show helps')
  @app_commands.checks.has_permissions(administrator=True)
  async def help(self, interaction: discord.Interaction):
    embed = discord.Embed(
      title='help',
      description=(
        '**/create {year}**\n' \
        'member-{year} ロールを作成し、権限を自動で設定します。\n' \
        '\n'
        '**/timeline**\n' \
        'このコマンドを実行したチャンネルを新たにtimelineチャンネルに設定します。\n' \
      ),
      color=0x09cc09,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
  await bot.add_cog(Help(bot))
