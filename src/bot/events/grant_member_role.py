from discord.ext import commands

from db import crud

class GrantMemberRole(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  def grand_member_role(self, username: str) -> None:
    member_role_id = crud.get_member_role_id()
