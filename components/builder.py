"""
containerkit.components.builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Translates high-level kwargs (header, footer, sections, buttons, etc.)
into a valid Discord Components V2 component tree.
"""

from __future__ import annotations

from typing import Optional

import discord


def build_components(
    *,
    content: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    sections: Optional[list[str]] = None,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None,
    buttons: Optional[list[discord.ui.Button]] = None,
    select: Optional[discord.ui.Select] = None,
    view: Optional[discord.ui.View] = None,
    color: Optional[discord.Color] = None,
    raw_components: Optional[list] = None,
) -> list:
    """
    Build a Components V2 component tree.

    If ``raw_components`` is provided it is returned as-is (full override).
    Otherwise a :class:`discord.ui.Container` is assembled from the kwargs.

    Returns
    -------
    list
        Top-level components list suitable for passing to ``channel.send``.
    """
    if raw_components is not None:
        return raw_components

    container_kwargs: dict = {}
    if color is not None:
        container_kwargs["accent_colour"] = color

    container = discord.ui.Container(**container_kwargs)

    # -- Header ----------------------------------------------------------
    if header:
        container.add_item(discord.ui.TextDisplay(value=f"# {header}"))
        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))

    # -- Thumbnail (right side) ------------------------------------------
    if thumbnail:
        # Thumbnail + text live in a Section component side-by-side
        section = discord.ui.Section(
            accessory=discord.ui.Thumbnail(media=discord.UnfurledMediaItem(url=thumbnail))
        )
        if content:
            section.add_item(discord.ui.TextDisplay(value=content))
        container.add_item(section)
        content = None  # already consumed

    # -- Main body -------------------------------------------------------
    if content:
        container.add_item(discord.ui.TextDisplay(value=content))

    # -- Extra sections --------------------------------------------------
    if sections:
        for section_text in sections:
            container.add_item(
                discord.ui.Separator(spacing=discord.SeparatorSpacing.small)
            )
            container.add_item(discord.ui.TextDisplay(value=section_text))

    # -- Large image -----------------------------------------------------
    if image:
        container.add_item(
            discord.ui.MediaGallery(
                items=[discord.MediaGalleryItem(media=discord.UnfurledMediaItem(url=image))]
            )
        )

    # -- Footer ----------------------------------------------------------
    if footer:
        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))
        container.add_item(discord.ui.TextDisplay(value=f"-# {footer}"))

    # -- Buttons ---------------------------------------------------------
    if buttons:
        row = discord.ui.ActionRow()
        for btn in buttons:
            row.add_item(btn)
        container.add_item(row)

    # -- Select menu -----------------------------------------------------
    if select:
        row = discord.ui.ActionRow()
        row.add_item(select)
        container.add_item(row)

    # -- Arbitrary View children -----------------------------------------
    if view:
        for child in view.children:
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                row = discord.ui.ActionRow()
                row.add_item(child)
                container.add_item(row)

    return [container]
