import re

import discord
from discord.ext import commands

from db import crud
from utils.constants import GUEST_ROLE_ID, GUILD_ID


class GrantMemberRole(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  async def grant_member_role(self, username: str) -> bool:
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    member_role_id = await crud.get_member_role_id(GUILD_ID)
    assert member_role_id is not None
    member_role = guild.get_role(member_role_id)
    assert member_role is not None

    guest_role = guild.get_role(GUEST_ROLE_ID)
    assert guest_role is not None

    deadline_role = discord.utils.find(lambda role: bool(re.fullmatch(r'\d{4}/\d{2}/\d{2}', role.name)), guild.roles)
    assert deadline_role is not None

    user = await crud.get_user_by_username(username)
    if user is None:
      return False

    discord_user = guild.get_member(user.user_id)
    assert discord_user is not None

    await discord_user.add_roles(member_role)
    await discord_user.remove_roles(guest_role, deadline_role)

    await crud.reset_deadline(username)

    return True

  async def manage_channel(self, username: str) -> bool:
    user = await crud.get_user_by_username(username)
    if user is None:
      return False

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

    return True

async def setup(bot: commands.Bot):
  cog = GrantMemberRole(bot)
  await bot.add_cog(cog)
