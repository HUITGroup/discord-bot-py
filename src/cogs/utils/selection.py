import discord


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
