"""
containerkit.utils.cog
~~~~~~~~~~~~~~~~~~~~~~~
A base Cog class that automatically injects ContainerContext into every
command, so you never have to wrap ctx manually.
"""

from __future__ import annotations

import inspect
from typing import Any

import discord
from discord.ext import commands

from ..core.context import ContainerContext


class ContainerCog(commands.Cog):
    """
    Base :class:`discord.ext.commands.Cog` subclass that transparently
    replaces ``ctx`` with a :class:`ContainerContext` in every command.

    Just inherit from this instead of ``commands.Cog``::

        class MyCog(ContainerCog):
            @commands.command()
            async def hello(self, ctx, member: discord.Member):
                # ctx is already a ContainerContext here
                await ctx.send(f"Hello, {member.mention}!")
                await ctx.reply("Nice to meet you!", header="Greeting")

    Applies recursively to all subcommands (including groups).
    """

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        # Replace ctx.send / ctx.reply on the real ctx so that code paths
        # that pass ctx around and call ctx.send still get containers.
        wrapped = ContainerContext(ctx)
        ctx.send = wrapped.send          # type: ignore[method-assign]
        ctx.reply = wrapped.reply        # type: ignore[method-assign]
        ctx.confirm = wrapped.confirm    # type: ignore[method-assign]
        ctx.send_paginated = wrapped.send_paginated  # type: ignore[method-assign]
        ctx.send_modal = wrapped.send_modal          # type: ignore[method-assign]
        ctx.typing = wrapped.typing      # type: ignore[method-assign]

    async def cog_after_invoke(self, ctx: commands.Context) -> None:
        pass
