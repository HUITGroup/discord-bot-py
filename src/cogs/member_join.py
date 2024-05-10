import os
from pathlib import Path
from datetime import timedelta as td, timezone as tz, datetime as dt, time

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from .handler.handler import handler


ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

GUEST_ROLE_ID = int(os.getenv("GUEST_ROLE_ID"))
INFO_CHANNEL_ID = int(os.getenv("INFO_CHANNEL_ID"))
GUILD_ID = int(os.getenv('GUILD_ID'))

JST = tz(td(hours=9), 'JST')

START = time(hour=14, tzinfo=JST)
# now = dt.now(JST) + td(seconds=15)
# print(now.tzinfo)
# START = time(hour=now.hour, minute=now.minute, second=now.second, microsecond=now.microsecond, tzinfo=JST)
print(START.tzinfo)
print(START)


class MemberJoin(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.check_deadline.start()
    self.check_near_deadline.start()

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    if member.bot or self.bot.user.id == member.id:
      return

    trial_period_days = 60

    raw_limit_day = (dt.now(JST) + td(days=trial_period_days)).date()
    role_name = raw_limit_day.isoformat().replace('-', '/')

    guild = member.guild

    guest_role = member.guild.get_role(GUEST_ROLE_ID)
    await member.add_roles(guest_role)

    role = discord.utils.get(guild.roles, name=role_name)
    if role:
      await member.add_roles(role)
    else:
      role = await guild.create_role(name=role_name)
      await member.add_roles(role)

    welcome_channel = guild.get_channel(INFO_CHANNEL_ID)

    msg = (
      f"{member.mention} さん、HUITにようこそ！\n" \
      f"体験入部期間は {role_name} までとなります。\n" \
      f"{welcome_channel.mention} を読んで、活動に楽しくご参加ください！"
    )
    await member.guild.system_channel.send(msg)

    handler.register_user(member.id, raw_limit_day)

  @commands.Cog.listener()
  async def on_member_leave(self, member: discord.Member):
    handler.delete_user(member.id)

  @tasks.loop(time=START)
  async def check_deadline(self):
    print('deadline check has started')

    today = dt.now(JST).date()
    user_ids = handler.get_users_by_deadline(today)

    if not user_ids:
      return

    guild = self.bot.get_guild(GUILD_ID)
    role = guild.get_role(GUEST_ROLE_ID)
    welcome_channel = guild.system_channel
    info_channel = guild.get_channel(INFO_CHANNEL_ID)

    for user_id in user_ids:
      user = guild.get_member(user_id)
      await user.remove_roles(role)

      msg = f"{user.mention} さんの体験入部期間が終了しました。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"

      await welcome_channel.send(msg)

  @tasks.loop(time=START)
  async def check_near_deadline(self):
    deadline = (dt.now(JST) + td(days=7)).date()
    user_ids = handler.get_users_by_deadline(deadline)
    if not user_ids:
      return

    guild = self.bot.get_guild(GUILD_ID)
    welcome_channel = guild.system_channel
    info_channel = guild.get_channel(INFO_CHANNEL_ID)

    for user_id in user_ids:
      user = guild.get_member(user_id)

      msg = f"{user.mention} さんの体験入部期間はあと 7日 で終了します。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"
      await welcome_channel.send(msg)

  @check_deadline.error
  async def check_deadline_error(ctx: commands.Context, error):
    print(error)
    print(ctx)

  @check_near_deadline.error
  async def check_near_deadline_error(ctx: commands.Context, error):
    print(error)
    print(ctx)

async def setup(bot: commands.Bot):
  cog = MemberJoin(bot)
  await bot.add_cog(cog)
