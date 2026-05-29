"""
containerkit.core.context
~~~~~~~~~~~~~~~~~~~~~~~~~
The main ContainerContext class — a drop-in ctx replacement that sends
Components V2 containers instead of plain messages or embeds.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional, Union

import discord
from discord.ext import commands

from ..components.builder import build_components
from ..core.message import ContainerMessage
from ..utils.modal import ContainerModal
from ..utils.paginator import ContainerPaginator

if TYPE_CHECKING:
    pass


class ContainerContext:
    """
    A fully-featured drop-in replacement for ``commands.Context`` that sends
    Discord Components V2 containers instead of plain messages or embeds.

    All normal ``ctx`` attributes are transparently proxied, so existing code
    (``ctx.author``, ``ctx.guild``, ``ctx.bot``, etc.) continues to work
    unchanged.

    Parameters
    ----------
    ctx : commands.Context
        The original context to wrap.

    Examples
    --------
    Basic usage (just like ctx.send)::

        c = ContainerContext(ctx)
        await c.send(f"{member.mention} is happy!")

    With styling::

        await c.send(
            f"Welcome, {member.mention}!",
            header="New Member",
            footer="Read the rules in #rules",
            color=discord.Color.green(),
            thumbnail=member.display_avatar.url,
        )

    Paginated::

        pages = ["Page one content", "Page two content", "Page three content"]
        await c.send_paginated(pages, header="Help Menu")

    Modal prompt::

        values = await c.send_modal("Feedback", fields=[
            {"label": "Your feedback", "placeholder": "Type here..."}
        ])
        await c.send(f"Thanks! You said: {values[0]}")
    """

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def __init__(self, ctx: commands.Context) -> None:
        self._ctx = ctx

        # Expose common attributes directly for autocomplete convenience
        self.author: discord.Member | discord.User = ctx.author
        self.guild: Optional[discord.Guild] = ctx.guild
        self.channel = ctx.channel
        self.message: discord.Message = ctx.message
        self.bot: commands.Bot = ctx.bot
        self.command = ctx.command
        self.prefix: Optional[str] = ctx.prefix
        self.invoked_with: Optional[str] = ctx.invoked_with
        self.args: list = ctx.args
        self.kwargs: dict = ctx.kwargs
        self.voice_client = ctx.voice_client
        self.cog = ctx.cog

    # ------------------------------------------------------------------ #
    #  Core send                                                           #
    # ------------------------------------------------------------------ #

    async def send(
        self,
        content: str = None,
        *,
        # Structural
        header: str = None,
        footer: str = None,
        sections: list[str] = None,
        # Media
        thumbnail: str = None,
        image: str = None,
        # Interactivity
        buttons: list[discord.ui.Button] = None,
        select: discord.ui.Select = None,
        view: discord.ui.View = None,
        # Visual
        color: discord.Color = None,
        spoiler: bool = False,
        # Raw override
        components: list = None,
        # Message delivery
        reference: Union[discord.Message, discord.MessageReference] = None,
        mention_author: bool = False,
        delete_after: float = None,
        ephemeral: bool = False,
        **kwargs: Any,
    ) -> ContainerMessage:
        """
        Send a container message.

        Parameters
        ----------
        content : str
            Main body text. Supports f-strings, mentions, and markdown.
        header : str
            Heading shown at the top of the container.
        footer : str
            Small subtext shown at the bottom of the container.
        sections : list[str]
            Additional text sections separated by dividers.
        thumbnail : str
            URL for a thumbnail image (top-right corner).
        image : str
            URL for a large media image inside the container.
        buttons : list[discord.ui.Button]
            Buttons to attach in an ActionRow below the text.
        select : discord.ui.Select
            A select menu to attach below the text.
        view : discord.ui.View
            A full View; its children are appended as-is.
        color : discord.Color
            Accent color on the container's left border.
        spoiler : bool
            Wrap the content text in a spoiler tag.
        components : list
            Raw component list — bypasses all auto-building.
        reference : discord.Message | discord.MessageReference
            Message to reply to.
        mention_author : bool
            Whether to ping the author on reply.
        delete_after : float
            Seconds after which to auto-delete the message.
        ephemeral : bool
            Send as ephemeral (slash command contexts only).
        **kwargs
            Passed through to the underlying ``channel.send``.

        Returns
        -------
        ContainerMessage
            Thin wrapper around the sent message with ``.edit()`` / ``.delete()``
            / ``.add_reaction()`` helpers.
        """
        if content is not None and spoiler:
            content = f"||{content}||"

        built = build_components(
            content=content,
            header=header,
            footer=footer,
            sections=sections,
            thumbnail=thumbnail,
            image=image,
            buttons=buttons,
            select=select,
            view=view,
            color=color,
            raw_components=components,
        )

        send_kwargs: dict[str, Any] = {
            "components": built,
            "flags": discord.MessageFlags(is_components_v2=True),
        }

        if reference is not None:
            send_kwargs["reference"] = reference
            send_kwargs["mention_author"] = mention_author

        # Slash-command ephemeral
        if ephemeral:
            interaction: Optional[discord.Interaction] = getattr(
                self._ctx, "interaction", None
            )
            if interaction is not None:
                send_kwargs["ephemeral"] = True

        msg = await self._ctx.send(**send_kwargs)
        container_msg = ContainerMessage(msg)

        if delete_after is not None:
            asyncio.ensure_future(container_msg.delete(delay=delete_after))

        return container_msg

    # ------------------------------------------------------------------ #
    #  Reply shortcut                                                      #
    # ------------------------------------------------------------------ #

    async def reply(
        self,
        content: str = None,
        *,
        mention_author: bool = False,
        **kwargs: Any,
    ) -> ContainerMessage:
        """
        Reply to the invoking message as a container.

        Identical to ``send(..., reference=ctx.message)``.
        """
        return await self.send(
            content,
            reference=self._ctx.message,
            mention_author=mention_author,
            **kwargs,
        )

    # ------------------------------------------------------------------ #
    #  Paginator                                                           #
    # ------------------------------------------------------------------ #

    async def send_paginated(
        self,
        pages: list[str],
        *,
        header: str = None,
        footer: str = None,
        color: discord.Color = None,
        thumbnail: str = None,
        timeout: float = 120.0,
        show_page_counter: bool = True,
        ephemeral: bool = False,
    ) -> ContainerMessage:
        """
        Send a paginated container message with Prev / Next navigation buttons.

        Parameters
        ----------
        pages : list[str]
            List of text strings, one per page.
        header : str
            Heading displayed above every page (static).
        footer : str
            Additional footer text appended below the page counter.
        color : discord.Color
            Accent color for every page.
        thumbnail : str
            Thumbnail URL shown on every page.
        timeout : float
            Seconds before the buttons are disabled. Default 120.
        show_page_counter : bool
            Whether to append "Page N / M" to the footer.
        ephemeral : bool
            Ephemeral (slash only).

        Returns
        -------
        ContainerMessage
        """
        paginator = ContainerPaginator(
            ctx=self,
            pages=pages,
            header=header,
            footer=footer,
            color=color,
            thumbnail=thumbnail,
            timeout=timeout,
            show_page_counter=show_page_counter,
        )
        return await paginator.start(ephemeral=ephemeral)

    # ------------------------------------------------------------------ #
    #  Confirmation prompt                                                 #
    # ------------------------------------------------------------------ #

    async def confirm(
        self,
        content: str = "Are you sure?",
        *,
        header: str = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        color: discord.Color = None,
        timeout: float = 30.0,
    ) -> Optional[bool]:
        """
        Send a confirmation container and wait for the invoking user to respond.

        Returns
        -------
        bool | None
            ``True`` if confirmed, ``False`` if cancelled, ``None`` if timed out.
        """
        result: list[Optional[bool]] = [None]
        event = asyncio.Event()

        confirm_btn = discord.ui.Button(
            label=confirm_label,
            style=discord.ButtonStyle.success,
            custom_id="ck_confirm",
        )
        cancel_btn = discord.ui.Button(
            label=cancel_label,
            style=discord.ButtonStyle.danger,
            custom_id="ck_cancel",
        )

        async def _confirm_cb(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.defer()
                return
            result[0] = True
            event.set()
            await interaction.response.defer()

        async def _cancel_cb(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.defer()
                return
            result[0] = False
            event.set()
            await interaction.response.defer()

        confirm_btn.callback = _confirm_cb
        cancel_btn.callback = _cancel_cb

        msg = await self.send(
            content,
            header=header,
            color=color,
            buttons=[confirm_btn, cancel_btn],
        )

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass

        # Disable buttons after response or timeout
        confirm_btn.disabled = True
        cancel_btn.disabled = True
        try:
            await msg.edit(
                content,
                header=header,
                color=color,
                buttons=[confirm_btn, cancel_btn],
            )
        except discord.HTTPException:
            pass

        return result[0]

    # ------------------------------------------------------------------ #
    #  Modal helper                                                        #
    # ------------------------------------------------------------------ #

    async def send_modal(
        self,
        title: str,
        *,
        fields: list[dict],
        timeout: float = 300.0,
    ) -> Optional[list[str]]:
        """
        Send a modal prompt via button interaction and wait for the response.

        Sends a container with a button; when the invoking user clicks it,
        a Discord modal pops up. Returns the submitted values.

        Parameters
        ----------
        title : str
            Title shown at the top of the modal window.
        fields : list[dict]
            Each dict describes a ``TextInput`` field::

                {
                    "label": "Your name",           # required
                    "placeholder": "e.g. Alex",     # optional
                    "required": True,               # optional, default True
                    "style": discord.TextStyle.short,  # optional
                    "min_length": 1,               # optional
                    "max_length": 1000,            # optional
                }

        timeout : float
            Seconds to wait for the user to submit. Default 300.

        Returns
        -------
        list[str] | None
            The submitted values in field order, or ``None`` if timed out.
        """
        modal_helper = ContainerModal(
            ctx=self,
            title=title,
            fields=fields,
            timeout=timeout,
        )
        return await modal_helper.prompt()

    # ------------------------------------------------------------------ #
    #  Typing context manager                                              #
    # ------------------------------------------------------------------ #

    def typing(self):
        """Trigger the typing indicator. Use as ``async with c.typing()``."""
        return self._ctx.typing()

    # ------------------------------------------------------------------ #
    #  Transparent proxy to the underlying ctx                            #
    # ------------------------------------------------------------------ #

    def __getattr__(self, name: str) -> Any:
        return getattr(self._ctx, name)

    def __repr__(self) -> str:
        return (
            f"<ContainerContext author={self.author!r} "
            f"channel={self.channel!r} guild={self.guild!r}>"
        )
