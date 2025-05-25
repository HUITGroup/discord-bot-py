from discord.ext import commands

from db import crud
from utils.constants import GUEST_ROLE_ID, GUILD_ID


class GrantMemberRole(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    self.guild = guild

  async def grant_member_role(self, username: str) -> bool:
    member_role_id = await crud.get_member_role_id(GUILD_ID)
    assert member_role_id is not None
    member_role = self.guild.get_role(member_role_id)
    assert member_role is not None

    guest_role = self.guild.get_role(GUEST_ROLE_ID)
    assert guest_role is not None

    user = await crud.get_user_by_username(username)
    if user is None:
      return False

    discord_user = self.guild.get_member(user.user_id)
    assert discord_user is not None

    await discord_user.add_roles(member_role)
    await discord_user.remove_roles(guest_role)

    await crud.reset_deadline(username)

    return True
