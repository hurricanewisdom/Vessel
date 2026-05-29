"""
containerkit.core.message
~~~~~~~~~~~~~~~~~~~~~~~~~
Wrapper around a sent Discord message that provides container-aware
edit / delete / reaction helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

import discord

from ..components.builder import build_components

if TYPE_CHECKING:
    pass


class ContainerMessage:
    """
    Returned by every ``ContainerContext.send*`` call.

    Wraps the raw :class:`discord.Message` and exposes helpers that keep
    the Components V2 flags set correctly on edits.

    Attributes
    ----------
    message : discord.Message
        The underlying Discord message object.
    id : int
        Snowflake ID of the message.
    channel
        Channel the message was sent in.
    """

    def __init__(self, message: discord.Message) -> None:
        self.message = message
        self.id: int = message.id
        self.channel = message.channel
        self.guild = message.guild
        self.author = message.author

    # ------------------------------------------------------------------ #
    #  Edit                                                                #
    # ------------------------------------------------------------------ #

    async def edit(
        self,
        content: str = None,
        *,
        header: str = None,
        footer: str = None,
        sections: list[str] = None,
        thumbnail: str = None,
        image: str = None,
        buttons: list[discord.ui.Button] = None,
        select: discord.ui.Select = None,
        view: discord.ui.View = None,
        color: discord.Color = None,
        spoiler: bool = False,
        components: list = None,
        **kwargs: Any,
    ) -> "ContainerMessage":
        """
        Edit this message in-place.

        Accepts the same keyword arguments as ``ContainerContext.send``.
        Returns ``self`` so you can chain calls.

        Example
        -------
        ::

            msg = await c.send("Loading...")
            await asyncio.sleep(2)
            await msg.edit("Done!", color=discord.Color.green())
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

        await self.message.edit(
            components=built,
            **kwargs,
        )
        return self

    # ------------------------------------------------------------------ #
    #  Delete                                                              #
    # ------------------------------------------------------------------ #

    async def delete(self, *, delay: float = None) -> None:
        """
        Delete this message.

        Parameters
        ----------
        delay : float, optional
            Number of seconds to wait before deleting.
        """
        if delay is not None:
            import asyncio
            await asyncio.sleep(delay)
        try:
            await self.message.delete()
        except discord.NotFound:
            pass

    # ------------------------------------------------------------------ #
    #  Reactions                                                           #
    # ------------------------------------------------------------------ #

    async def add_reaction(self, emoji: Union[str, discord.Emoji]) -> None:
        """Add a reaction to this message."""
        await self.message.add_reaction(emoji)

    async def remove_reaction(
        self,
        emoji: Union[str, discord.Emoji],
        member: discord.Member = None,
    ) -> None:
        """Remove a reaction from this message."""
        await self.message.remove_reaction(emoji, member or self.message.guild.me)

    async def clear_reactions(self) -> None:
        """Remove all reactions from this message."""
        await self.message.clear_reactions()

    # ------------------------------------------------------------------ #
    #  Pin / Unpin                                                         #
    # ------------------------------------------------------------------ #

    async def pin(self, *, reason: str = None) -> None:
        """Pin this message."""
        await self.message.pin(reason=reason)

    async def unpin(self, *, reason: str = None) -> None:
        """Unpin this message."""
        await self.message.unpin(reason=reason)

    # ------------------------------------------------------------------ #
    #  Wait for reaction                                                   #
    # ------------------------------------------------------------------ #

    async def wait_for_reaction(
        self,
        *,
        emojis: list[str] = None,
        user: discord.User = None,
        timeout: float = 60.0,
    ) -> Optional[tuple[discord.Reaction, discord.User]]:
        """
        Wait for a reaction on this message.

        Parameters
        ----------
        emojis : list[str], optional
            Restrict to specific emoji strings. If ``None``, any emoji matches.
        user : discord.User, optional
            Restrict to a specific user. If ``None``, any user matches.
        timeout : float
            Seconds to wait. Returns ``None`` on timeout.

        Returns
        -------
        tuple[discord.Reaction, discord.User] | None
        """
        import asyncio

        def check(reaction: discord.Reaction, u: discord.User) -> bool:
            if reaction.message.id != self.id:
                return False
            if user is not None and u.id != user.id:
                return False
            if emojis is not None and str(reaction.emoji) not in emojis:
                return False
            return True

        try:
            return await self.message._state._get_client().wait_for(
                "reaction_add", check=check, timeout=timeout
            )
        except asyncio.TimeoutError:
            return None

    # ------------------------------------------------------------------ #
    #  Proxy                                                               #
    # ------------------------------------------------------------------ #

    def __getattr__(self, name: str) -> Any:
        return getattr(self.message, name)

    def __repr__(self) -> str:
        return f"<ContainerMessage id={self.id} channel={self.channel!r}>"
