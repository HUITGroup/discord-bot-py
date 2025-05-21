from discord.ext import commands

class GrantMemberRole(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
