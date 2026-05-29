"""
Vessel.utils.modal
~~~~~~~~~~~~~~~~~~~~~~~~~
Send a modal prompt via a button, collect the response, and return values.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

import discord

if TYPE_CHECKING:
    from ..core.context import ContainerContext


class _InnerModal(discord.ui.Modal):
    def __init__(self, title: str, fields: list[dict], future: asyncio.Future) -> None:
        super().__init__(title=title)
        self._future = future
        self._inputs: list[discord.ui.TextInput] = []

        for field in fields:
            ti = discord.ui.TextInput(
                label=field["label"],
                placeholder=field.get("placeholder"),
                required=field.get("required", True),
                style=field.get("style", discord.TextStyle.short),
                min_length=field.get("min_length"),
                max_length=field.get("max_length", 1000),
                default=field.get("default"),
            )
            self._inputs.append(ti)
            self.add_item(ti)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        if not self._future.done():
            self._future.set_result([ti.value for ti in self._inputs])


class ContainerModal:
    """
    Sends a container with an "Open Form" button; clicking it spawns a modal.

    Parameters
    ----------
    ctx : ContainerContext
    title : str
        Modal window title.
    fields : list[dict]
        Field descriptors (see ``ContainerContext.send_modal`` docstring).
    timeout : float
        Seconds to wait for submission.
    """

    def __init__(
        self,
        ctx: "ContainerContext",
        title: str,
        fields: list[dict],
        timeout: float = 300.0,
    ) -> None:
        self._ctx = ctx
        self.title = title
        self.fields = fields
        self.timeout = timeout

    async def prompt(self) -> Optional[list[str]]:
        """
        Send the trigger button and wait for the user to submit the modal.

        Returns
        -------
        list[str] | None
            Submitted values in field order, or ``None`` on timeout.
        """
        loop = asyncio.get_event_loop()
        future: asyncio.Future[list[str]] = loop.create_future()

        open_btn = discord.ui.Button(
            label=f"Open: {self.title}",
            style=discord.ButtonStyle.primary,
            emoji="📝",
            custom_id="ck_modal_open",
        )

        async def _btn_cb(interaction: discord.Interaction) -> None:
            if interaction.user.id != self._ctx.author.id:
                await interaction.response.send_message(
                    "This form isn't for you.", ephemeral=True
                )
                return
            modal = _InnerModal(self.title, self.fields, future)
            await interaction.response.send_modal(modal)

        open_btn.callback = _btn_cb

        msg = await self._ctx.send(
            f"Click the button below to open **{self.title}**.",
            buttons=[open_btn],
        )

        try:
            result = await asyncio.wait_for(
                asyncio.shield(future), timeout=self.timeout
            )
        except asyncio.TimeoutError:
            result = None

        # Disable the button afterward
        open_btn.disabled = True
        try:
            label = "Form submitted ✓" if result is not None else "Form expired"
            await msg.edit(label, buttons=[open_btn])
        except discord.HTTPException:
            pass

        return result
