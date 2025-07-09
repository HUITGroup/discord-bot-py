import logging
import os
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from pathlib import Path
from typing import cast

import discord
import pandas as pd
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from bot.events.grant_member_role import GrantMemberRole
from db import crud
from utils.constants import (
  GUEST_ROLE_ID,
  GUILD_ID,
  INFO_CHANNEL_ID,
)

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

logger = logging.getLogger('huitLogger')

class CheckRole(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='sync_user_data', description='サーバーにいる全員のuser dataを同期するコマンド(試験運用)')
  @app_commands.checks.has_permissions(administrator=True)
  async def sync_user_data(self, interaction: discord.Interaction):
    if interaction.user.nick != 'misaizu':
      await interaction.response.send_message('misaizuにしか実行できない設定にしてあります')
      return

    df = pd.read_csv(ABS / 'map.csv')
    df = df.where(pd.notnull(df), None)
    await crud.csv_to_sql(df)

    await interaction.response.send_message('running...')

  @app_commands.command(name='sync_user_data2', description='サーバーにいる全員のuser dataを同期するコマンド(試験運用)2')
  @app_commands.checks.has_permissions(administrator=True)
  async def sync_user_data(self, interaction: discord.Interaction):
    if interaction.user.nick != 'misaizu':
      await interaction.response.send_message('misaizuにしか実行できない設定にしてあります')
      return

    df = pd.read_csv(ABS / 'map.csv')
    df = df.where(pd.notnull(df), None)
    await crud.csv_to_sql_each_row(df)

    await interaction.response.send_message('running...')

  @app_commands.command(name='test', description='test')
  @app_commands.checks.has_permissions(administrator=True)
  async def test(self, interaction: discord.Interaction):
    await interaction.response.send_message('（＾ω＾）')

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    channel = guild.get_channel(1225392486743146526)
    print(channel.name)

  @app_commands.command(name='archive_no_roles', description='archive')
  @app_commands.checks.has_permissions(administrator=True)
  async def archive_no_roles(self, interaction: discord.Interaction):
    if interaction.user.nick != 'misaizu':
      await interaction.response.send_message('null')
      return

    private_categories = {
      "TIMES B1",
      "TIMES B2",
      "TIMES B3",
      "TIMES B4",
      "TIMES AFTER B4",
      "TIMES B5",
      "TIMES B6",
      "TIMES M/D",
      "TIMES other",
    }

    await interaction.response.send_message('（＾ω＾）')

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    archive_category = discord.utils.get(guild.categories, id=ARCHIVED_CATEGORY_ID)
    assert archive_category is not None

    edited: list[str] = []
    for category in guild.categories:
      if category.name not in private_categories:
        continue

      for channel in category.channels:
        if not isinstance(channel, discord.TextChannel):
          continue

        user, err = await crud.get_user_by_channel_id(channel.id)
        if err:
          return
        if user is None:
        #   # edited.append(channel.name)
        #   # print(channel.id)
        #   await interaction.channel.send(f'WARNING: no user assigned to {channel.name}')
          continue

        #   await channel.edit(category=archive_category)
        #   continue

        discord_user = guild.get_member(user.user_id)
        if discord_user is None:
          continue

        roles = discord_user.roles
        if all(discord.utils.get(roles, name=name) is None for name in ['guest', 'member-2024', 'member-2025']):
          # role_names = [role.name for role in roles]
          # role_names.pop(0)
          # await interaction.channel.send(f'{user.username} {user.nickname}')

          # edited.append(channel.name)
          # continue

          await channel.edit(category=archive_category)
          await channel.send(f'{channel.name} を archiveしました')

    print(*edited, sep='\n')

  @app_commands.command(name='grant_member_role', description='grant')
  @app_commands.checks.has_permissions(administrator=True)
  async def grant_member_role(self, interaction: discord.Interaction, username: str):
    await interaction.response.send_message('（＾ω＾）')

    cog = self.bot.get_cog('GrantMemberRole')
    assert cog is not None
    cog = cast(GrantMemberRole, cog)
    await cog.grant_member_role(username)

  @app_commands.command(name='grant_grade_role', description='tst')
  @app_commands.checks.has_permissions(administrator=True)
  async def grant_grade_role(self, interaction: discord.Interaction):
    await interaction.response.send_message('（＾ω＾）')

    users, err = await crud.get_all_users()
    if err:
      return

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    for user in users:
      discord_user = guild.get_member(user.user_id)
      if discord_user is None:
        logger.warning(f'skipped for {user.username=}')
        continue

      if user.grade == 'other':
        continue
      role = guild.get_role(roles[user.grade])
      assert role is not None

      await discord_user.add_roles(role)

  @app_commands.command(name='warn', description='warn')
  @app_commands.checks.has_permissions(administrator=True)
  async def warn(self, interaction: discord.Interaction, username: str):
    user, err = await crud.get_user_by_username(username)
    if err:
      logger.exception(err)
      await interaction.response.send_message('(´・ω・`) ')
      return

    if user is None:
      await interaction.response.send_message('指定ユーザーが見つかりませんでした')
      return

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    discord_user = guild.get_member(user.user_id)
    assert discord_user is not None

    role = guild.get_role(GUEST_ROLE_ID)
    assert role is not None
    info_channel = guild.get_channel(INFO_CHANNEL_ID)

    await discord_user.remove_roles(role)

    msg = f"{discord_user.mention} さんの体験入部期間が終了しました。"\
      f"本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"

    assert guild.system_channel is not None
    await guild.system_channel.send(msg)

    await interaction.response.send_message('（＾ω＾）')


async def setup(bot: commands.Bot):
  await bot.add_cog(CheckRole(bot))
