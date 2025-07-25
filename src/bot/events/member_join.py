import logging
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
from db.models import UserData
from utils.constants import (
  GRADE_ROLE_ID,
  GUEST_ROLE_ID,
  GUILD_ID,
  INFO_CHANNEL_ID,
  TIMES_MESSAGE_ID,
  WELCOME_CHANNEL_ID,
  YOUR_ID,
)

ABS = Path(__file__).resolve().parents[3]
load_dotenv(ABS / '.env')
logger = logging.getLogger('huitLogger')

JST = tz(td(hours=9), 'JST')

START = time(hour=9, tzinfo=JST)

logger.info(f'入部期間チェックは毎日 {START} に行われます。')

class MemberJoin(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.check_deadline.start()
    self.check_near_deadline.start()

  async def grant_grade_role(self, user_id: int, grade: str):
    if grade == 'other':
      return

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    discord_user = guild.get_member(user_id)
    assert discord_user is not None

    for grade_, role_id in GRADE_ROLE_ID.items():
      role = guild.get_role(role_id)
      if role is None:
        logger.warning(f'{grade_} のロールが存在しません。'\
          'constants.pyに登録されているrole_idと整合しているかを確認してください')
        continue

      await discord_user.remove_roles(role)

    role = guild.get_role(GRADE_ROLE_ID[grade])
    if role is None:
      logger.warning(f'{grade} のロールが存在しません。'\
        f'constants.pyに登録されているrole_idと整合しているかを確認してください')
      return

    await discord_user.add_roles(role)

  async def _check_times_exists(self, username: str, nickname: str) -> bool:
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    times_channel = discord.utils.get(guild.channels, name=f'times_{nickname}')

    if times_channel is None:
      return False
    else:
      discord_user = discord.utils.get(guild.members, name=username)
      assert discord_user is not None

      msg = f'{discord_user.mention} フォームで入力いただいた「ニックネーム（半角英数字）」が既に使われています。フォームを編集し、違うニックネームへの変更をお願いします。\nhttps://forms.gle/7xzSLV9xvpciJoJYA'
      await guild.system_channel.send(msg)

      return True

  async def check_already_in_server(self, username: str):
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    discord_user = discord.utils.get(guild.members, name=username)

    if discord_user:
      await self.on_member_join(discord_user)

  async def _prepare_channel(
    self,
    member: discord.Member,
    user: UserData,
    raw_limit_day: date
  ) -> None:
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
    assert isinstance(welcome_channel, discord.TextChannel)

    if user.grade in {'m1', 'm2', 'd'}:
      category_name = 'TIMES M/D'
    elif user.grade == 'other':
      category_name = 'TIMES other'
    else:
      category_name = f'TIMES {user.grade.upper()}'

    if user.channel_id is None:
      channel = await guild.create_text_channel(
        f'times_{user.nickname}',
        category=discord.utils.get(guild.categories, name=category_name)
      )
      message = welcome_channel.get_partial_message(TIMES_MESSAGE_ID)
      await channel.send(
        f'{member.mention}\ntimesを作成しました！\ntimesについての詳細はこちら→{message.jump_url}'
      )
      _, err = await crud.register_user(
        member.name,
        member.id,
        channel.id,
        raw_limit_day
      )
      if err:
        logger.error('ユーザーの本登録処理が異常終了しました')
    else:
      category = discord.utils.get(guild.categories, name=category_name)
      channel = guild.get_channel(user.channel_id)
      assert isinstance(channel, discord.TextChannel)
      await channel.edit(category=category)

  @app_commands.command(
    name='link_member_role',
    description='指定年度のmemberロールと紐付けるコマンドです'
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def link_member_role(self, interaction: discord.Interaction, year: int):
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    role = discord.utils.get(guild.roles, name=f'member-{year}')
    if role is None:
      await interaction.response.send_message(
        f'member-{year}ロールが見つかりません。member-{year}ロールが存在することを確認してください'
      )
      return

    member_role_id = role.id
    _, err =\
      await crud.update_member_role_id(GUILD_ID, member_role_id, year=year)
    if err:
      return

    await interaction.response.send_message('紐付けが完了しました')

  @app_commands.command(
    name='rename',
    description='自分のtimesの名前を変更するコマンドです'
  )
  async def rename(self, interactions: discord.Interaction, name: str):
    channel_id, err =\
      await crud.get_channel_id_by_user_id(interactions.user.id)
    if err:
      return

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    you = guild.get_member(YOUR_ID)
    if you is None:
      you = 'Bot管理者'

    if channel_id is None:
      if isinstance(you, str):
        msg = 'あなたのtimesが見つかりませんでした。'\
          f'お近くの{you}までお知らせください。'
      else:
        msg = 'あなたのtimesが見つかりませんでした。'\
          f'お近くの{you.mention}までお知らせください。'

      await interactions.response.send_message(msg)
      return

    channel = guild.get_channel(channel_id)
    assert isinstance(channel, discord.TextChannel)

    await channel.edit(name=f'times_{name}')

    if isinstance(you, str):
      msg = '変更しました。変わっていない場合はdiscordを再起動するか、お近くの'\
        f'{you}までお知らせください'
    else:
      msg = '変更しました。変わっていない場合はdiscordを再起動するか、'\
        f'お近くの{you.mention}までお知らせください'
    await interactions.response.send_message(msg)

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):  # noqa: D102
    assert self.bot.user is not None
    if member.bot or self.bot.user.id == member.id:
      return

    user, err = await crud.get_user_by_username(member.name)
    if err:
      return

    if user is None:
      msg = f'{member.mention}さんのフォーム入力情報を確認できませんでした。'\
        'フォームに入力した「Discord の ID」が実際のものと一致しているか'\
        '確認してください。\nフォームに誤りがあった場合はフォームを編集し、'\
        '正しいものに修正してください。\n'\
        'https://forms.gle/7xzSLV9xvpciJoJYA\nわからない点があれば'\
        '`@moderator` までご連絡ください。'
      await member.guild.system_channel.send(msg)
      return

    res = await self._check_times_exists(user.username, user.nickname)
    if res:
      return

    trial_period_days = 60

    raw_limit_day = (dt.now(JST) + td(days=trial_period_days)).date()
    role_name = raw_limit_day.isoformat().replace('-', '/')

    guild = member.guild

    guest_role = guild.get_role(GUEST_ROLE_ID)
    assert guest_role is not None
    await member.add_roles(guest_role)

    role = discord.utils.get(guild.roles, name=role_name)
    if role:
      await member.add_roles(role)
    else:
      role = await guild.create_role(name=role_name)
      await member.add_roles(role)

    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
    assert welcome_channel is not None

    msg = (
      f"{member.mention} さん、HUITにようこそ！\n" \
      f"体験入部期間は {role_name} までとなります。\n" \
      f"{welcome_channel.mention} を読んで、活動に楽しくご参加ください！"
    )

    assert member.guild.system_channel is not None
    await member.guild.system_channel.send(msg)

    await self._prepare_channel(member, user, raw_limit_day)
    await self.grant_grade_role(member.id, user.grade)

  @commands.Cog.listener()
  async def on_member_leave(self, member: discord.Member):  # noqa: D102
    _, err = await crud.delete_user(member.id)
    if err:
      logger.error('ユーザーの削除処理が異常終了しました')

  @commands.Cog.listener()
  async def on_member_update(  # noqa: D102
    self,
    before: discord.Member,
    after: discord.Member
  ):
    if before.name != after.name:
      logging.debug('username update event')

      _, err = await crud.update_username(before.name, after.name)
      if err:
        logging.error('username更新処理が異常終了しました')
        return

  @tasks.loop(time=START)
  async def check_deadline(
    self,
    _date: date|None = None,
  ):
    logger.info('体験入部期間の期日の確認処理を開始しました')

    if _date is None:
      today = dt.now(JST).date()
    else:
      today = _date

    users, err = await crud.get_users_by_deadline(today-td(days=1))
    if err:
      logger.error('check_deadlineが異常終了しました')

    logger.info(f'{today=} として処理を開始します')

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    if not users:
      logger.info('対象ユーザーが見つかりませんでした。処理を終了します。')
      return

    role = guild.get_role(GUEST_ROLE_ID)
    assert role is not None

    info_channel = guild.get_channel(INFO_CHANNEL_ID)
    assert info_channel is not None

    for user in users:
      discord_user = guild.get_member(user.user_id)
      if discord_user is None:
        logger.info(
          f'{user.user_id=} のユーザーが見つかりませんでした。'\
            'すでに退会したユーザーの可能性があります。'
        )
        continue

      await discord_user.remove_roles(role)

      msg = f"{discord_user.mention} さんの体験入部期間が終了しました。"\
        f"本入部希望の場合は {info_channel.mention} の手順に沿って"\
        "部費をお納めください。"

      assert guild.system_channel is not None
      await guild.system_channel.send(msg)

  @tasks.loop(time=START)
  async def check_near_deadline(
    self,
    _date: date|None = None
  ):
    logger.info('体験入部期間の期日(1週間前警告)の確認処理を開始しました')

    if _date is None:
      deadline = (dt.now(JST) + td(days=7)).date()
    else:
      deadline = _date + td(days=7)

    users, err = await crud.get_users_by_deadline(deadline)
    if err:
      logger.error('check_near_deadlineが異常終了しました')
    if not users:
      return

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    info_channel = guild.get_channel(INFO_CHANNEL_ID)
    assert info_channel is not None

    for user in users:
      discord_user = guild.get_member(user.user_id)
      if discord_user is None:
        logger.info(
          f'{user.user_id=} のユーザーが見つかりませんでした。'\
            'すでに退会したユーザーの可能性があります。'
        )
        continue

      msg = f"{discord_user.mention} さんの体験入部期間は"\
        "あと 7日 で終了します。"\
        f"本入部希望の場合は {info_channel.mention} の手順に沿って"\
        "部費をお納めください。"

      assert guild.system_channel is not None
      await guild.system_channel.send(msg)

  @app_commands.command(
    name='check_deadlines',
    description='手動期限チェックコマンド'
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def check_deadlines(
    self,
    interactions: discord.Interaction,
    year: int,
    month: int,
    day: int,
  ):
    try:
      deadline = date(year, month, day)
    except ValueError as e:
      logger.exception(e)
      await interactions.response.send_message('無効な日付です')
      return

    await interactions.response.send_message('（＾ω＾）')
    await self.check_deadline(deadline)
    await self.check_near_deadline(deadline)

async def setup(bot: commands.Bot):  # noqa: D103
  cog = MemberJoin(bot)
  await bot.add_cog(cog)
