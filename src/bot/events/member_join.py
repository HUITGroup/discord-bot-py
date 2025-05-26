import os
from datetime import date, time
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

import db.crud as crud
from utils.constants import (
  ARCHIVED_CATEGORY_ID,
  GUEST_ROLE_ID,
  GUILD_ID,
  INFO_CHANNEL_ID,
  TIMES_MESSAGE_ID,
  WELCOME_CHANNEL_ID,
  YOUR_ID,
)

ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')

JST = tz(td(hours=9), 'JST')

START = time(hour=0, tzinfo=JST)

print(START.tzinfo)
print(START)

class MemberJoin(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.check_deadline.start()
    self.check_near_deadline.start()

    guild = bot.get_guild(GUILD_ID)
    assert guild is not None

    guest_role = guild.get_role(GUEST_ROLE_ID)
    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
    assert guest_role is not None
    assert welcome_channel is not None

    self.guild = guild
    self.guest_role = guest_role
    self.welcome_channel = welcome_channel

  async def _prepare_channel(self, member: discord.Member, raw_limit_day: date) -> None:
    user = await crud.get_user_by_username(member.name)
    if user is None:
      msg = f'{member.mention}さんのフォーム入力情報を確認できませんでした．フォームに入力したニックネームとdiscord上のニックネームが一致しているか確認してください．'
      await member.guild.system_channel.send(msg)
      return

    if user.grade in {'m1', 'm2', 'd'}:
      category_name = 'TIMES M/D'
    elif user.grade == 'other':
      category_name = 'TIMES other'
    else:
      category_name = f'TIMES {user.grade.upper()}'

    if user.channel_id is None:
      channel = await self.guild.create_text_channel(
        f'times_{user.nickname}',
        category=discord.utils.get(self.guild.categories, name=category_name)
      )
      message = self.welcome_channel.get_partial_message(TIMES_MESSAGE_ID)
      await channel.send(
        f'{member.mention}\ntimesを作成しました！\ntimesについての詳細はこちら→{message.jump_url}'
      )
      await crud.register_user(member.name, member.id, channel.id, raw_limit_day)
    else:
      category = discord.utils.get(self.guild.categories, name=category_name)
      channel = self.guild.get_channel(user.channel_id)
      assert channel is not None
      await channel.edit(category=category)

  @app_commands.command(name='link_member_role', description='指定年度のmemberロールと紐付けるコマンドです')
  @app_commands.checks.has_permissions(administrator=True)
  async def link_member_role(self, interaction: discord.Interaction, year: int):
    role = discord.utils.get(self.guild.roles, name=f'member-{year}')
    if role is None:
      await interaction.response.send_message(f'member-{year}ロールが見つかりません．member-{year}ロールが存在することを確認してください')
      return

    member_role_id = role.id
    await crud.update_member_role_id(GUILD_ID, member_role_id, year=year)

    await interaction.response.send_message(f'紐付けが完了しました')

  @app_commands.command(name='rename', description='自分のtimesの名前を変更するコマンドです')
  async def rename(self, interactions: discord.Interaction, name: str):
    channel_id = await crud.get_channel_id_by_user_id(interactions.user.id)
    you = self.guild.get_member(YOUR_ID)
    if you is None:
      you = 'Bot管理者'

    if channel_id is None:
      if isinstance(you, str):
        msg = f'あなたのtimesが見つかりませんでした．お近くの{you}までお知らせください．'
      else:
        msg = f'あなたのtimesが見つかりませんでした．お近くの{you.mention}までお知らせください．'

      await interactions.response.send_message(msg)
      return

    channel = self.guild.get_channel(channel_id)
    assert isinstance(channel, discord.TextChannel)

    await channel.edit(name=f'times_{name}')

    if isinstance(you, str):
      msg = f'変更しました．変わっていない場合はdiscordを再起動するか，お近くの{you}までお知らせください'
    else:
      msg = f'変更しました．変わっていない場合はdiscordを再起動するか，お近くの{you.mention}までお知らせください'
    await interactions.response.send_message(msg)

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    assert self.bot.user is not None
    if member.bot or self.bot.user.id == member.id:
      return

    trial_period_days = 60

    raw_limit_day = (dt.now(JST) + td(days=trial_period_days)).date()
    role_name = raw_limit_day.isoformat().replace('-', '/')

    guild = member.guild

    assert self.guest_role is not None
    await member.add_roles(self.guest_role)

    role = discord.utils.get(guild.roles, name=role_name)
    if role:
      await member.add_roles(role)
    else:
      role = await guild.create_role(name=role_name)
      await member.add_roles(role)

    msg = (
      f"{member.mention} さん、HUITにようこそ！\n" \
      f"体験入部期間は {role_name} までとなります。\n" \
      f"{self.welcome_channel.mention} を読んで、活動に楽しくご参加ください！"
    )

    assert member.guild.system_channel is not None
    await member.guild.system_channel.send(msg)

    await self._prepare_channel(member, raw_limit_day)

  @commands.Cog.listener()
  async def on_member_leave(self, member: discord.Member):
    await crud.delete_user(member.id)

  @commands.Cog.listener()
  async def on_member_update(self, before: discord.Member, after: discord.Member):
    if before.roles == after.roles:
      return

    roles = after.roles
    member_role = discord.utils.find(lambda role: 'member' in role.name, roles)
    guest_role = discord.utils.get(roles, id=GUILD_ID)

    if member_role is None and guest_role is None:
      user_id = after.id
      channel_id = await crud.get_user_by_username(user_id)
      assert channel_id is not None

      channel = self.guild.get_channel(channel_id)
      assert channel is not None

      category = discord.utils.get(self.guild.categories, id=ARCHIVED_CATEGORY_ID)
      assert isinstance(channel, discord.TextChannel)

      await channel.edit(category=category)

  @tasks.loop(time=START)
  async def check_deadline(self):
    print('deadline check has started')

    today = dt.now(JST).date()
    users = await crud.get_users_by_deadline(today)

    if not users:
      return

    role = self.guild.get_role(GUEST_ROLE_ID)
    assert role is not None

    info_channel = self.guild.get_channel(INFO_CHANNEL_ID)
    assert info_channel is not None

    for user in users:
      discord_user = self.guild.get_member(user.user_id)
      if discord_user is None:
        print(f'[Warning]: user with {user.user_id=} is not found')
        continue

      await discord_user.remove_roles(role)

      msg = f"{discord_user.mention} さんの体験入部期間が終了しました。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"

      assert self.guild.system_channel is not None
      await self.guild.system_channel.send(msg)

  @tasks.loop(time=START)
  async def check_near_deadline(self):
    print('deadline check 2 has started')

    deadline = (dt.now(JST) + td(days=7)).date()
    users = await crud.get_users_by_deadline(deadline)
    if not users:
      return

    info_channel = self.guild.get_channel(INFO_CHANNEL_ID)
    assert info_channel is not None

    for user in users:
      discord_user = self.guild.get_member(user.user_id)
      if discord_user is None:
        print(f'[Warning]: user with {user.user_id=} is not found. In check_near_deadline.')
        continue

      msg = f"{discord_user.mention} さんの体験入部期間はあと 7日 で終了します。本入部希望の場合は {info_channel.mention} の手順に沿って部費をお納めください。"

      assert self.guild.system_channel is not None
      await self.guild.system_channel.send(msg)

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
