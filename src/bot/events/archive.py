"""あ"""
import logging

import discord
from discord import app_commands
from discord.ext import commands

from db import crud
from utils.constants import (
  BOT_ROLE_ID,
  GUEST_ROLE_ID,
  GUILD_ID,
  MODERATOR_ROLE_ID,
)

logger = logging.getLogger('huitLogger')

class Archive(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def _create_archive_category(self, category_number: int)\
  -> tuple[discord.CategoryChannel|None, bool]:
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    member_role_id, err = await crud.get_member_role_id(GUILD_ID)
    if err:
      logger.error('member role id取得処理が異常終了しました')
      return None, True
    if member_role_id is None:
      logger.critical('member roleが登録されていません')
      return None, True

    moderator_role = guild.get_role(MODERATOR_ROLE_ID)
    member_role = guild.get_role(member_role_id)
    guest_role = guild.get_role(GUEST_ROLE_ID)
    bot_role = guild.get_role(BOT_ROLE_ID)

    assert moderator_role is not None and member_role is not None and guest_role is not None and bot_role is not None

    overwrites: dict[discord.Role, discord.PermissionOverwrite] = {
      guild.default_role: discord.PermissionOverwrite(view_channel=False),
      moderator_role: discord.PermissionOverwrite(view_channel=True),
      member_role: discord.PermissionOverwrite(view_channel=True),
      guest_role: discord.PermissionOverwrite(view_channel=True),
      bot_role: discord.PermissionOverwrite(view_channel=True),
    }
    discord_category =\
      await guild.create_category(f'TIMES ARCHIVED {category_number}', overwrites=overwrites)
    _, err = await crud.create_archive_category(
      GUILD_ID,
      discord_category.id,
      category_number,
    )

    if err:
      logger.error('archive category idの検索処理が異常終了しました')
      return None, True

    return discord_category, False

  async def _archive_channel(self, channel: discord.TextChannel):
    # archiveカテゴリの検索・作成，archiveの処理
    category, err = await crud.get_latest_archive_category(GUILD_ID)
    if err:
      logger.error('archive category idの検索処理が異常終了しました')
      return

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    if category is None:
      discord_category, err = await self._create_archive_category(1)
      if err:
        logger.error('archive category作成処理が異常終了しました')
        return

    elif (
      discord_category := discord.utils.get(
        guild.categories,
        id=category.archive_category_id)
      ) is None:
      discord_category, err =\
        await self._create_archive_category(category.category_number+1)
      if err:
        logger.error('archive category作成処理が異常終了しました')
        return

    elif len(discord_category.channels) == 50:
      discord_category, err =\
        await self._create_archive_category(category.category_number+1)
      if err:
        logger.error('archive category作成処理が異常終了しました')
        return

    await channel.edit(category=discord_category)

  @commands.Cog.listener()
  async def on_member_update(  # noqa: D102
    self,
    before: discord.Member,
    after: discord.Member
  ) -> None:
    if before.roles == after.roles:
      return

    logger.debug('role update event')

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    roles = after.roles
    member_role = discord.utils.find(lambda role: 'member' in role.name, roles)
    guest_role = discord.utils.get(roles, id=GUEST_ROLE_ID)

    if member_role is not None or guest_role is not None:
      return

    user_id = after.id
    channel_id, err = await crud.get_channel_id_by_user_id(user_id)
    if err:
      logger.error('channel検索処理が異常終了しました')
      return
    if channel_id is None:
      logger.warning(f'{after.name}のchannel idが登録されていません')
      return

    channel = guild.get_channel(channel_id)
    assert isinstance(channel, discord.TextChannel)

    current_category = channel.category
    if current_category is None:
      await self._archive_channel(channel)
    elif current_category.name.startswith('TIMES ARCHIVED'):
      return
    else:
      await self._archive_channel(channel)

  @app_commands.command(
    name='archive_all',
    description='archive all unused times',
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def archive_all(self, interaction: discord.Interaction):
    await interaction.response.send_message('（＾ω＾）')
    users, err = await crud.get_all_users()
    if err:
      print('ee')
      return
    assert users is not None

    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    for user in users:
      if user.channel_id is None:
        logger.warning(f'skipped: no channel id for {user.username} was found')
        continue

      discord_user = guild.get_member(user.user_id)
      if discord_user is None:
        continue

      roles = discord_user.roles
      member_2025 = discord.utils.get(roles, name='member-2025')
      guest = discord.utils.get(roles, name='guest')

      if member_2025 is not None or guest is not None:
        continue

      logger.info(f'archiving channel for {user.username}')

      channel = guild.get_channel(user.channel_id)
      assert isinstance(channel, discord.TextChannel)

      category = channel.category
      if category is None:
        await self._archive_channel(channel)
      elif category.name.startswith('TIMES ARCHIVED'):
        return
      else:
        await self._archive_channel(channel)

  @app_commands.command(name='archive_no_categories', description='a')
  @app_commands.checks.has_permissions(administrator=True)
  async def archive_no_categories(self, interaction: discord.Interaction):
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None
    await interaction.response.send_message('（＾ω＾）')

    for channel in guild.channels:
      if channel.category is not None:
        continue
      if not channel.name.startswith('times_'):
        continue
      if not isinstance(channel, discord.TextChannel):
        continue

      print(channel.name)
      await self._archive_channel(channel)

  @app_commands.command(name='archive', description='指定した名前のチャンネルをarchvieします')
  @app_commands.checks.has_permissions(administrator=True)
  async def archive_no_categories(self, interaction: discord.Interaction, channel_name: str):
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    channel = discord.utils.get(guild.channels, name=channel_name)
    if channel is None:
      await interaction.response.send_message('指定された名前のチャンネルが見つかりませんでした')
      return

    await self._archive_channel(channel)
    await interaction.response.send_message('archiveしました')

  @app_commands.command(name='sync_archive_categories', description='archiveチャンネルを同期するコマンド')
  @app_commands.checks.has_permissions(administrator=True)
  async def sync_archive_categories(self, interaction: discord.Interaction):
    guild = self.bot.get_guild(GUILD_ID)
    assert guild is not None

    for discord_category in guild.categories:
      if not discord_category.name.startswith('TIMES ARCHIVED'):
        continue

      _, _, category_number = discord_category.name.split()
      category, err = await crud.get_archive_category_by_category_number(
        GUILD_ID,
        int(category_number)
      )

      if err:
        logger.error('category検索処理が異常終了しました')
        return

      print(category_number)

      if category is None:
        _, err = await crud.create_archive_category(
          GUILD_ID,
          discord_category.id,
          int(category_number),
        )
        if err:
          logger.error('category登録処理が異常終了しました')
          return
      else:
        _, err = await crud.sync_archive_category(
          GUILD_ID,
          discord_category.id,
          int(category_number)
        )
        if err:
          logger.error('category更新処理が異常終了しました')
          return

    await interaction.response.send_message('同期終了しました')

async def setup(bot: commands.Bot):  # noqa: D103
  cog = Archive(bot)
  await bot.add_cog(cog)
