import os
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from pathlib import Path

import discord
import pandas as pd
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from db import crud
from utils.constants import GUEST_ROLE_ID, GUILD_ID

JST = tz(td(hours=9), 'JST')

ABS = Path(__file__).resolve().parents[4]
load_dotenv(ABS / '.env')

MY_ID = 521879689447473152

roles = {
  'b1': 1368681784702926938,
  'b2': 1368681991527989359,
  'b3': 1368682142686773320,
  'b4': 1368682222713966613,
  'b5': 1368682298731663400,
  'b6': 1368682359292956732,
  'm1': 1368682420311687218,
  'm2': 1368682473869021235,
  'd': 1368682518257205329,
}

class CheckRole(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='sync_user_data', description='サーバーにいる全員のuser dataを同期するコマンド(試験運用)')
  @app_commands.checks.has_permissions(administrator=True)
  async def sync_user_data(self, interaction: discord.Interaction):
    if interaction.user.nick != 'misaizu':
      await interaction.response.send_message('misaizuにしか実行できない設定にしてあります')

    df = pd.read_csv(ABS / 'map.csv')
    df = df.where(pd.notnull(df), None)
    await crud.csv_to_sql(df)

    await interaction.response.send_message('running...')

  @app_commands.command(name='test', description='test')
  @app_commands.checks.has_permissions(administrator=True)
  async def test(self, interaction: discord.Interaction):
    await interaction.response.send_message('（＾ω＾）')

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    channel = guild.get_channel(1225392486743146526)
    print(channel.name)

async def setup(bot: commands.Bot):
  await bot.add_cog(CheckRole(bot))
