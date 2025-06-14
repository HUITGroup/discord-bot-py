import logging
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

import discord
from discord import app_commands
from discord.ext import commands

import db.crud as crud

JST = tz(td(hours=9), 'JST')
logger = logging.getLogger('huitLogger')

class Timeline(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(
    name='timeline',
    description='このコマンドを実行したチャンネルを新しくtimelineチャンネルとして登録します。むやみに実行しないでください。'
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def timeline(self, interaction: discord.Interaction):  # noqa: D102
    if self.bot.user.id == interaction.user.id:
      return

    if interaction.guild_id is None:
      return

    assert interaction.channel_id is not None

    _, err = await crud.register_timeline_channel(
      interaction.guild_id, interaction.channel_id
    )
    if err:
      return

    await interaction.response.send_message(
      'このチャンネルを新しくtimelineチャンネルとして登録しました'
    )

  def _create_embed(self, message: discord.Message) -> discord.Embed:
    embed = discord.Embed(
      color=0x90ee90,
      description=message.content,
      timestamp=dt.now(JST)
    )

    if message.attachments:
      for attachment in message.attachments:
        if attachment.content_type is None:
          continue
        if attachment.content_type.startswith('image'):
          embed.set_image(url=attachment.url)
          break

    embed.set_author(
      name=message.author.name,
      icon_url=message.author.avatar.url if message.author.avatar else None
    )

    assert isinstance(message.channel, discord.TextChannel)
    footer = message.channel.name

    embed.set_footer(text=footer)

    return embed

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):  # noqa: D102
    channel = message.channel
    if not isinstance(channel, discord.TextChannel):
      return
    if not channel.name.startswith("times_"):
      return

    logger.debug("on_message called")

    timeline_channel_id, err = await crud.get_timeline_channel_id(message.guild.id)
    if err:
      return

    if timeline_channel_id is None:
      logger.warning('timelineチャンネルが登録されていません。timelineチャンネルで`/timeline`コマンドを使用してください。')
      return

    embed = self._create_embed(message)

    timeline_channel = self.bot.get_channel(timeline_channel_id)
    assert isinstance(timeline_channel, discord.TextChannel)

    timeline_message = await timeline_channel.send(
      content=message.jump_url,
      embed=embed,
    )

    _, err = await crud.register_message(timeline_message.id, message.id)
    if err:
      return

    logger.debug('on_message completed')

  @commands.Cog.listener()
  async def on_message_edit(  # noqa: D102
    self,
    before: discord.Message,
    after: discord.Message
  ):
    logger.debug('on_message_edit called')

    timeline_message_id, err = await crud.get_timeline_message_id(before.id)
    if err:
      return
    if not timeline_message_id:
      return

    message_channel = before.channel
    if not message_channel:
      return

    timeline_channel_id, err = await crud.get_timeline_channel_id(after.guild.id)
    if err:
      return

    if timeline_channel_id is None:
      logger.warning('timelineチャンネルが登録されていません。timelineチャンネルで`/timeline`コマンドを使用してください。')
      return

    embed = self._create_embed(after)

    timeline_channel = self.bot.get_channel(timeline_channel_id)
    assert isinstance(timeline_channel, discord.TextChannel)

    timeline_message = await timeline_channel.fetch_message(timeline_message_id)
    await timeline_message.edit(embed=embed)

    print('on_message_edit completed')

  @commands.Cog.listener()
  async def on_message_delete(self, message: discord.Message):  # noqa: D102
    logger.info('on_message_delete called')

    timeline_message_id, err = await crud.get_timeline_message_id(message.id)
    if err:
      return
    if timeline_message_id is None:
      return

    timeline_channel_id, err = await crud.get_timeline_channel_id(message.guild.id)
    if err:
      return

    if timeline_channel_id is None:
      logger.warning('timelineチャンネルが登録されていません。timelineチャンネルで`/timeline`コマンドを使用してください。')
      return

    timeline_channel = self.bot.get_channel(timeline_channel_id)
    assert isinstance(timeline_channel, discord.TextChannel)

    timeline_message = await timeline_channel.fetch_message(timeline_message_id)
    await timeline_message.delete()

    _, err = await crud.delete_timeline(message.id)
    if err:
      return

    logger.info('on_message_delete completed')

async def setup(bot: commands.Bot):  # noqa: D103
  await bot.add_cog(Timeline(bot))
