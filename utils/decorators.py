"""
Vessel.utils.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Convenience decorators for wrapping ctx automatically.
"""

from __future__ import annotations

import functools
from typing import Callable

from discord.ext import commands

from ..core.context import ContainerContext


def use_container(func: Callable) -> Callable:
    """
    Command decorator that auto-wraps ``ctx`` into a :class:`ContainerContext`.

    Works for both standalone commands and cog commands (with a ``self``
    parameter).

    Example
    -------
    ::

        @bot.command()
        @use_container
        async def greet(ctx, member: discord.Member):
            await ctx.send(f"Hello, {member.mention}!")  # ctx is ContainerContext

        # In a Cog:
        class MyCog(commands.Cog):
            @commands.command()
            @use_container
            async def info(self, ctx):
                await ctx.reply("Here's your info!", header="Info")
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Detect cog (first arg is self) vs bare command (first arg is ctx)
        if args and isinstance(args[0], commands.Cog):
            # args = (self, ctx, ...)
            self_obj = args[0]
            ctx = args[1]
            rest = args[2:]
            return await func(self_obj, ContainerContext(ctx), *rest, **kwargs)
        else:
            # args = (ctx, ...)
            ctx = args[0]
            rest = args[1:]
            return await func(ContainerContext(ctx), *rest, **kwargs)

    return wrapper


def container_command(**kwargs):
    """
    Shorthand for ``@commands.command() + @use_container``.

    Example
    -------
    ::

        @container_command(name="ping")
        async def ping(ctx):
            await ctx.send("Pong!")
    """
    def decorator(func: Callable) -> Callable:
        return commands.command(**kwargs)(use_container(func))
    return decorator
