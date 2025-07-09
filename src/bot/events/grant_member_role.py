import logging
import re

import discord
from discord.ext import commands

from db import crud
from utils.constants import GUEST_ROLE_ID, GUILD_ID

logger = logging.getLogger('huitLogger')

class GrantMemberRole(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  async def grant_member_role(self, username: str) -> tuple[bool, bool]:
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    member_role_id, err = await crud.get_member_role_id(GUILD_ID)
    if err:
      logger.error('member role idの検索処理が異常終了しました')
      return False, True

    assert member_role_id is not None
    member_role = guild.get_role(member_role_id)
    assert member_role is not None

    guest_role = guild.get_role(GUEST_ROLE_ID)
    assert guest_role is not None

    user, err = await crud.get_user_by_username(username)
    if err:
      logger.error('ユーザーの検索処理が異常終了しました')
      return False, True
    if user is None:
      return False, False

    discord_user = guild.get_member(user.user_id)
    assert discord_user is not None

    deadline_role = discord.utils.find(
      lambda role: bool(re.fullmatch(r'\d{4}/\d{2}/\d{2}', role.name)),
      discord_user.roles
    )

    await discord_user.add_roles(member_role)
    await discord_user.remove_roles(guest_role)
    if deadline_role is None:
      logger.info(
        f'Skipped deadline role revocation: no deadline roles found for {username}'
      )
    else:
      await discord_user.remove_roles(deadline_role)

    _, err = await crud.reset_deadline(username)
    if err:
      logger.error('体験入部期間の期日のリセット処理が異常終了しました')

    return True, False

  async def manage_channel(self, username: str) -> bool:
    user, err = await crud.get_user_by_username(username)
    if err:
      logger.error('ユーザーの検索処理が異常終了しました')
      return True
    if user is None:
      return True

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    if user.channel_id is None:
      ...
    else:
      channel = guild.get_channel(user.channel_id)
      assert isinstance(channel, discord.TextChannel)

      if user.grade in {'m1', 'm2', 'd'}:
        category_name = 'TIMES M/D'
      elif user.grade == 'other':
        category_name = 'TIMES other'
      else:
        category_name = f'TIMES {user.grade.upper()}'

      category = discord.utils.get(guild.categories, name=category_name)
      assert category is not None
      await channel.edit(category=category)

    return False

async def setup(bot: commands.Bot):  # noqa: D103
  cog = GrantMemberRole(bot)
  await bot.add_cog(cog)
