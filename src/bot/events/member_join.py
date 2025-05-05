import os
from datetime import datetime as dt
from datetime import time
from datetime import timedelta as td
from datetime import timezone as tz
from pathlib import Path

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import src.db.crud as crud

ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')

GUEST_ROLE_ID = int(os.getenv("GUEST_ROLE_ID"))
INFO_CHANNEL_ID = int(os.getenv("INFO_CHANNEL_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
TIMES_MESSAGE_ID = int(os.getenv("TIMES_MESSAGE_ID"))
GUILD_ID = int(os.getenv('GUILD_ID'))

JST = tz(td(hours=9), 'JST')

START = time(hour=0, tzinfo=JST)

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
    # trial_period_minutes = 1

    raw_limit_day = (dt.now(JST) + td(days=trial_period_days)).date()
    # raw_limit_day = (dt.now(JST) + td(minutes=trial_period_minutes)).date()
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

    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)

    # register

    msg = (
      f"{member.mention} さん、HUITにようこそ！\n" \
      f"体験入部期間は {role_name} までとなります。\n" \
      f"{welcome_channel.mention} を読んで、活動に楽しくご参加ください！"
    )
    await member.guild.system_channel.send(msg)

    user = await crud.get_user_by_username(member.name)

    if user.grade in {'m1', 'm2', 'd'}:
      category_name = 'TIMES M/D'
    elif user.grade == 'other':
      category_name = 'TIMES other'
    else:
      category_name = f'TIMES {user.grade.upper()}'

    if user is None:
      ...
    elif user.channel_id is None:

      channel = await guild.create_text_channel(
        f'times_{user.nickname}',
        category=discord.utils.get(guild.categories, name=category_name)
      )
      message = welcome_channel.get_partial_message(TIMES_MESSAGE_ID)
      await channel.send(
        f'{member.mention}\ntimesを作成しました！\ntimesについての詳細はこちら→{message.jump_url}'
      )
      await crud.register_user(member.name, member.id, channel.id, raw_limit_day)
    else:
      category = discord.utils.get(guild.categories, name=category_name)
      channel = guild.get_channel(user.channel_id)
      await channel.edit(category=category)

  @commands.Cog.listener()
  async def on_member_leave(self, member: discord.Member):
    await crud.delete_user(member.id)

  @tasks.loop(time=START)
  # @tasks.loop(seconds=20)
  async def check_deadline(self):
    print('deadline check has started')

    today = dt.now(JST).date()
    users = await crud.get_users_by_deadline(today)

    if not users:
      return

    guild = self.bot.get_guild(GUILD_ID)
    role = guild.get_role(GUEST_ROLE_ID)
    # welcome_channel = guild.get_channel(1228918335933124628)
    info_channel = guild.get_channel(INFO_CHANNEL_ID)

    for user in users:
      discord_user = guild.get_member(user.user_id)
      await discord_user.remove_roles(role)

      msg = f"{discord_user.mention} さんの体験入部期間が終了しました。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"

      await guild.system_channel.send(msg)

  @tasks.loop(time=START)
  async def check_near_deadline(self):
    print('deadline check 2 has started')

    deadline = (dt.now(JST) + td(days=7)).date()
    users = await crud.get_users_by_deadline(deadline)
    if not users:
      return

    guild = self.bot.get_guild(GUILD_ID)
    info_channel = guild.get_channel(INFO_CHANNEL_ID)

    for user in users:
      discord_user = guild.get_member(user.user_id)

      msg = f"{discord_user.mention} さんの体験入部期間はあと 7日 で終了します。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"
      await guild.system_channel.send(msg)

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
