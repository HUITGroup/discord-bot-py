from datetime import datetime as dt, timedelta as td, timezone as tz

import discord
from discord import app_commands
from discord.ext import commands

from .handler.handler import handler


JST = tz(td(hours=9), 'JST')


# handler = Handler()

class Timeline(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name='timeline', description='このコマンドを実行したチャンネルを新しくtimelineチャンネルとして登録します。むやみに実行しないでください。')
  @app_commands.checks.has_permissions(administrator=True)
  async def timeline(self, interaction: discord.Interaction):
    if self.bot.user.id == interaction.user.id:
      return

    handler.register_timeline_channel(interaction.guild_id, interaction.channel_id)
    await interaction.response.send_message('このチャンネルを新しくtimelineチャンネルとして登録しました')

  @app_commands.command(name='check_id')
  @app_commands.checks.has_permissions(administrator=True)
  async def check_id(self, interaction: discord.Interaction):
    await interaction.response.send_message('⊂二二二（　＾ω＾）二⊃')
    print(interaction.user.id)
    print(self.bot.user.id)
    ...

  def _create_embed(self, message: discord.Message) -> discord.Embed:
    embed = discord.Embed(
      color=0x90ee90,
      description=message.content,
      timestamp=dt.now(JST)
    )

    if message.attachments:
      for attachment in message.attachments:
        if attachment.content_type.startswith('image'):
          embed.set_image(url=attachment.url)
          break

    embed.set_author(
      name=message.author.name,
      icon_url=message.author.avatar.url if message.author.avatar else None
    )

    footer = message.channel.name

    embed.set_footer(text=footer)

    return embed

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    print("create event")

    if message.author.id == self.bot.user.id:
      return

    if message.content == "/timeline":
      return

    channel = message.channel
    assert channel is not None

    if not channel.name.startswith("times_"):
      return

    timeline_channel_id = handler.get_timeline_channel_id(message.guild.id)

    if timeline_channel_id is None:
      return

    embed = self._create_embed(message)

    timeline_channel = self.bot.get_channel(timeline_channel_id)
    timeline_message = await timeline_channel.send(content=message.jump_url, embed=embed)

    handler.register_message(timeline_message.id, message.id)

    print('create event completed')

  @commands.Cog.listener()
  async def on_message_edit(self, before: discord.Message, after: discord.Message):
    print('update event')

    timeline_message_id = handler.get_timeline_message_id(before.id)
    if not timeline_message_id:
      return

    message_channel = before.channel
    if not message_channel:
      return

    timeline_channel_id = handler.get_timeline_channel_id(after.guild.id)

    embed = self._create_embed(after)

    timeline_channel = self.bot.get_channel(timeline_channel_id)
    timeline_message = await timeline_channel.fetch_message(timeline_message_id)
    await timeline_message.edit(embed=embed)

    print('update event completed')

  @commands.Cog.listener()
  async def on_message_delete(self, message: discord.Message):
    print('delete event')

    timeline_message_id = handler.get_timeline_message_id(message.id)
    if not timeline_message_id:
      return

    timeline_channel_id = handler.get_timeline_channel_id(message.guild.id)
    if not timeline_channel_id:
      return

    timeline_channel = self.bot.get_channel(timeline_channel_id)
    timeline_message = await timeline_channel.fetch_message(timeline_message_id)
    await timeline_message.delete()

    handler.del_timeline(message.id)

    print('delete event completed')

async def setup(bot: commands.Bot):
  await bot.add_cog(Timeline(bot))
