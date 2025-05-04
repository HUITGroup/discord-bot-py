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

from src.db import crud

JST = tz(td(hours=9), 'JST')

ABS = Path(__file__).resolve().parents[4]
load_dotenv(ABS / '.env')

GUEST_ROLE_ID = int(os.getenv('GUEST_ROLE_ID'))
GUILD_ID = int(os.getenv('GUILD_ID'))
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
  'd1': 1368682518257205329,
  'd2': 1368682565350981692,
  'd3': 1368682621613117490,
}

class CheckRole(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='check_guest_role', description='test')
  async def check_guest_role(self, interaction: discord.Interaction):
    guild = self.bot.get_guild(GUILD_ID)
    role = guild.get_role(GUEST_ROLE_ID)

    user = guild.get_member(MY_ID)
    print(role)

    await interaction.response.send_message('done')

  @app_commands.command(name='grant_guest_role', description='misaizuにguestロールを付与するコマンド')
  async def grant_guest_role(self, interaction: discord.Interaction):
    guild = self.bot.get_guild(GUILD_ID)
    role = guild.get_role(GUEST_ROLE_ID)

    user = guild.get_member(MY_ID)
    print(user)
    await user.add_roles(role)

    await interaction.response.send_message('granted')

  @app_commands.command(name='revoke_guest_role', description='期限切れのguestロールを一斉剥奪するコマンド')
  async def revoke_guest_role(self, interaction: discord.Interaction):
    print('deadline check has started')

    user_ids = [MY_ID]

    guild = self.bot.get_guild(GUILD_ID)
    role = guild.get_role(GUEST_ROLE_ID)
    welcome_channel = guild.get_channel(1228918335933124628)
    info_channel = guild.get_channel(1228918335933124628)

    for user_id in user_ids:
      user = guild.get_member(user_id)
      await user.remove_roles(role)

      msg = f"{user.mention} さんの体験入部期間が終了しました。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"

      await welcome_channel.send(msg)

  @app_commands.command(name='sync_user_data', description='サーバーにいる全員のuser dataを同期するコマンド(試験運用)')
  async def sync_user_data(self, interaction: discord.Interaction):
    if interaction.user.nick != 'misaizu':
      interaction.response.send_message('misaizuにしか実行できない設定にしてあります')

    df = pd.read_csv(ABS / 'map.csv')
    df = df.where(pd.notnull(df), None)
    await crud.csv_to_sql(df)

    await interaction.response.send_message('running...')

  @app_commands.command(name='grant_grade_roles', description='a')
  async def grant_grade_roles(self, interaction: discord.Interaction):
    users = await crud.get_all_users()
    guild = self.bot.get_guild(GUILD_ID)

    for user in users:
      # if user.nickname != 'takemura':
      if user.grade == 'other' or user.grade is None:
        continue

      role = guild.get_role(roles[user.grade])
      discord_user = guild.get_member(user.user_id)

      if discord_user is not None:
        await discord_user.add_roles(role)

    await interaction.response.send_message('done.')

  @app_commands.command(name='revoke_outdated_guests', description='guestロール一括剥奪')
  async def revoke_outdated_guests(self, interaction: discord.Interaction):
    today = dt.now(JST).date()
    users = await crud.get_users_by_deadline(today)

    guild = self.bot.get_guild(GUILD_ID)
    guest_role = guild.get_role(GUEST_ROLE_ID)

    await interaction.response.send_message('running...')
    for user in users:
      if user.deadline is None:
        continue

      print(type(user.username))
      discord_user = guild.get_member(user.user_id)
      if discord_user:
        print('aaaaaa')
        try:
          await discord_user.remove_roles(guest_role)
        except Exception as e:
          print(e)


async def setup(bot: commands.Bot):
  await bot.add_cog(CheckRole(bot))
