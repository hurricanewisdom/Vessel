"""
containerkit.utils.paginator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Paginated container messages with Prev / Next navigation.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

import discord

if TYPE_CHECKING:
    from ..core.context import ContainerContext
    from ..core.message import ContainerMessage


class ContainerPaginator:
    """
    Drives a multi-page container message.

    Users interact via Prev / Next buttons. Pages time out and buttons
    are disabled automatically after ``timeout`` seconds of inactivity.

    Parameters
    ----------
    ctx : ContainerContext
        The invoking context.
    pages : list[str]
        Text content for each page.
    header : str, optional
        Static heading shown on every page.
    footer : str, optional
        Extra footer text appended after the page counter.
    color : discord.Color, optional
        Container accent color.
    thumbnail : str, optional
        Thumbnail URL shown on every page.
    timeout : float
        Seconds of inactivity before buttons are disabled.
    show_page_counter : bool
        Whether to append "Page N / M" to the footer.
    """

    def __init__(
        self,
        ctx: "ContainerContext",
        pages: list[str],
        *,
        header: Optional[str] = None,
        footer: Optional[str] = None,
        color: Optional[discord.Color] = None,
        thumbnail: Optional[str] = None,
        timeout: float = 120.0,
        show_page_counter: bool = True,
    ) -> None:
        self._ctx = ctx
        self.pages = pages
        self.header = header
        self.footer = footer
        self.color = color
        self.thumbnail = thumbnail
        self.timeout = timeout
        self.show_page_counter = show_page_counter

        self._current: int = 0
        self._msg: Optional["ContainerMessage"] = None
        self._task: Optional[asyncio.Task] = None
        self._last_interaction: float = asyncio.get_event_loop().time()

    # ------------------------------------------------------------------ #

    def _make_buttons(self) -> list[discord.ui.Button]:
        first = discord.ui.Button(
            emoji="⏮️",
            style=discord.ButtonStyle.secondary,
            custom_id="ck_page_first",
            disabled=self._current == 0,
        )
        prev = discord.ui.Button(
            label="Prev",
            emoji="◀️",
            style=discord.ButtonStyle.primary,
            custom_id="ck_page_prev",
            disabled=self._current == 0,
        )
        next_ = discord.ui.Button(
            label="Next",
            emoji="▶️",
            style=discord.ButtonStyle.primary,
            custom_id="ck_page_next",
            disabled=self._current >= len(self.pages) - 1,
        )
        last = discord.ui.Button(
            emoji="⏭️",
            style=discord.ButtonStyle.secondary,
            custom_id="ck_page_last",
            disabled=self._current >= len(self.pages) - 1,
        )
        stop_btn = discord.ui.Button(
            emoji="⏹️",
            style=discord.ButtonStyle.danger,
            custom_id="ck_page_stop",
        )

        for btn in (first, prev, next_, last, stop_btn):
            btn.callback = self._make_callback(btn.custom_id)

        return [first, prev, next_, last, stop_btn]

    def _make_callback(self, custom_id: str):
        async def _cb(interaction: discord.Interaction):
            if interaction.user.id != self._ctx.author.id:
                await interaction.response.send_message(
                    "You can't control this menu.", ephemeral=True
                )
                return

            self._last_interaction = asyncio.get_event_loop().time()

            if custom_id == "ck_page_first":
                self._current = 0
            elif custom_id == "ck_page_prev":
                self._current = max(0, self._current - 1)
            elif custom_id == "ck_page_next":
                self._current = min(len(self.pages) - 1, self._current + 1)
            elif custom_id == "ck_page_last":
                self._current = len(self.pages) - 1
            elif custom_id == "ck_page_stop":
                await self._disable_buttons()
                await interaction.response.defer()
                return

            await self._update_page(interaction)

        return _cb

    def _build_footer(self) -> Optional[str]:
        parts = []
        if self.show_page_counter:
            parts.append(f"Page {self._current + 1} / {len(self.pages)}")
        if self.footer:
            parts.append(self.footer)
        return " • ".join(parts) if parts else None

    async def _update_page(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await self._msg.edit(
            self.pages[self._current],
            header=self.header,
            footer=self._build_footer(),
            color=self.color,
            thumbnail=self.thumbnail,
            buttons=self._make_buttons(),
        )

    async def _disable_buttons(self) -> None:
        if self._msg is None:
            return
        disabled = []
        for btn in self._make_buttons():
            btn.disabled = True
            disabled.append(btn)
        try:
            await self._msg.edit(
                self.pages[self._current],
                header=self.header,
                footer=self._build_footer(),
                color=self.color,
                thumbnail=self.thumbnail,
                buttons=disabled,
            )
        except discord.HTTPException:
            pass

    async def _timeout_loop(self) -> None:
        loop = asyncio.get_event_loop()
        while True:
            await asyncio.sleep(5)
            elapsed = loop.time() - self._last_interaction
            if elapsed >= self.timeout:
                await self._disable_buttons()
                return

    # ------------------------------------------------------------------ #

    async def start(self, *, ephemeral: bool = False) -> "ContainerMessage":
        """Send the first page and start listening for interactions."""
        self._msg = await self._ctx.send(
            self.pages[self._current],
            header=self.header,
            footer=self._build_footer(),
            color=self.color,
            thumbnail=self.thumbnail,
            buttons=self._make_buttons(),
            ephemeral=ephemeral,
        )
        self._task = asyncio.ensure_future(self._timeout_loop())
        return self._msg
