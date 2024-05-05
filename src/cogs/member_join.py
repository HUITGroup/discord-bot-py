import os
from pathlib import Path
from datetime import date as dt, timedelta as td, timezone as tz

import discord
from discord.ext import commands
from dotenv import load_dotenv


ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

GUEST_ROLE_ID = int(os.getenv("GUEST_ROLE_ID"))

JST = tz(td(hours=9), 'JST')


class MemberJoin(commands):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    if member.bot or self.bot.user.id == member.id:
      return

    trial_period_days = 60

    raw_limit_day = dt.today() + td(days=trial_period_days)
    role_name = raw_limit_day.isoformat().replace('-', '/')

    guild = member.guild

    guest_role = member.guild.get_role(GUEST_ROLE_ID)
    await member.add_roles(guest_role)

    role = discord.utils.get(guild.roles, name=role_name)
    if role:
      await member.add_roles(role)
    else:
      role = discord.Role(name=role_name, guild=guild)
      await member.add_roles(role)




async def setup(bot: commands.Bot):
  await bot.add_cog(MemberJoin(bot))
