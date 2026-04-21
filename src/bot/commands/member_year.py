from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.utils.constants import HUIT_BOT_ROLE_ID

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

JST = tz(td(hours=9), 'JST')

class Selection(discord.ui.View):
  def __init__(self, user: discord.Member):
    super().__init__(timeout=None)
    self.user = user

  async def disable_buttons(self, interaction: discord.Interaction):
    for button in self.children:
      button.disabled = True

    await interaction.response.edit_message(embed=None, view=self)

  @discord.ui.button(label="OK", style=discord.ButtonStyle.success)
  async def ok(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user != self.user:
      return

    await self.disable_buttons(interaction)

  @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
  async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user != self.user:
      return

    await self.disable_buttons(interaction)
    await interaction.channel.send("キャンセルしました")

class CreationView(Selection):
  def __init__(self, user: discord.Member, year: str):
    super().__init__(user)
    self.year = year

  @discord.ui.button(label="OK", style=discord.ButtonStyle.success)
  async def ok(self, interaction: discord.Interaction, button: discord.ui.Button):
    await super().ok(interaction, button)

    await interaction.channel.send("ロール作成を開始します...",)
    await _create(interaction, self.year)


async def _create(interaction: discord.Interaction, year: str):
  guild = interaction.guild
  if guild is None:
    return
  permissions = discord.Permissions(
    view_channel=True,
    manage_roles=True,
    create_expressions=True,
    change_nickname=True,
    send_messages=True,
    send_messages_in_threads=True,
    create_public_threads=True,
    create_private_threads=True,
    embed_links=True,
    attach_files=True,
    add_reactions=True,
    external_emojis=True,
    external_stickers=True,
    read_message_history=True,
    send_tts_messages=True,
    send_voice_messages=True,
    create_polls=True,
    connect=True,
    speak=True,
    stream=True,
    use_voice_activation=True,
    use_application_commands=True,
    request_to_speak=True,
    create_events=True,
    manage_events=True,
  )

  me = guild.get_role(HUIT_BOT_ROLE_ID)
  assert me is not None
  role = await guild.create_role(
    name=f'member-{year}',
    permissions=permissions,
    mentionable=True,
    color=0x3498DB
  )

  await role.edit(position=me.position-1)

  print(f'member-{year} を作成しました')
  await interaction.channel.send(f'member-{year} を作成しました')

  private_categories = {
    "🗒 Text Channels",
    "📣 VOICE CHANNELS",
    "🎈 EVENTS",
    "🔨 Projects",
    "🔧 etc",
    "🏢 企業等",
    "TIMES B1",
    "TIMES B2",
    "TIMES B3",
    "TIMES B4",
    "TIMES AFTER B4",
    "TIMES B5/B6/M/D",
    "TIMES other",
    "情エレ過去問",
    "🗝 Archived",
    "TIMES ARCHIVED",
    "TIMES_ARCHIVED_2"
  }
  private_channels = {
    'cat-gpt',
    'timeline',
    'moderator',
    'これ買いたい'
  }
  permissions = discord.PermissionOverwrite(
    view_channel=True,
    connect=True,
  )

  for category in guild.categories:
    if category.name not in private_categories:
      continue

    await category.set_permissions(role, overwrite=permissions)
    print(f'{category.name} での権限を設定しました')
    await interaction.channel.send(f'{category.name} での権限を設定しました')

  for channel in guild.channels:
    if channel.name not in private_channels:
      continue

    await channel.set_permissions(role, overwrite=permissions)
    print(f'{channel.name} での権限を設定しました')
    await interaction.channel.send(f'{channel.name} での権限を設定しました')

  prev_role = discord.utils.get(guild.roles, name=f'member-{int(year)-1}')
  for channel in guild.channels:
    if channel.permissions_for(prev_role).view_channel \
    and not channel.permissions_for(role).view_channel:
      await channel.set_permissions(role, overwrite=permissions)
      print(f'{channel.name} での権限を設定しました')
      await interaction.channel.send(f'{channel.name} での権限を設定しました')

  await interaction.channel.send('正常終了')

class MemberYear(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
    name="create",
    description='member-{year} ロールを作成し、関連する権限を自動で設定します。' \
      'yearに次年度以外の数値を入れると警告が表示されます。'
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def create(self, interaction: discord.Interaction, year: str):
    this_year = int(dt.now(JST).year)

    if f'member-{year}' in interaction.guild.roles:
      await interaction.response.send_message(
        f'`member-{year}` は既に存在します。'\
        '再作成したい場合は、一度消してからコマンドを実行してください。',
        ephemeral=True
      )
    elif year != str(this_year):
      selection = CreationView(interaction.user, year)
      await interaction.response.send_message(
        f'member-{year} は次年度用ではありません。作成しますか?',
        view=selection,
        ephemeral=True
      )
    else:
      await interaction.response.send_message('続行します...', ephemeral=True)
      await _create(interaction, year)

async def setup(bot: commands.Bot):
  await bot.add_cog(MemberYear(bot))
