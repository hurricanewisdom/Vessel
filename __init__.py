"""
containerkit
~~~~~~~~~~~~
A fully-featured Discord.py library for sending Components V2 container
messages as a drop-in replacement for ctx.send / ctx.reply.

Quick start
-----------
::

    from containerkit import ContainerContext, ContainerCog, use_container

    # 1. Manual wrap
    @bot.command()
    async def hello(ctx):
        c = ContainerContext(ctx)
        await c.send(f"Hello, {ctx.author.mention}!")

    # 2. Decorator
    @bot.command()
    @use_container
    async def greet(ctx, member: discord.Member):
        await ctx.send(f"{member.mention} is happy!", header="Greeting")

    # 3. Cog base class (auto-injects for every command)
    class MyCog(ContainerCog):
        @commands.command()
        async def info(self, ctx):
            await ctx.reply("Here's your info!", header="Info")
"""

from .core.context import ContainerContext
from .core.message import ContainerMessage
from .utils.cog import ContainerCog
from .utils.decorators import container_command, use_container
from .utils.modal import ContainerModal
from .utils.paginator import ContainerPaginator

__version__ = "1.0.0"

__all__ = [
    "ContainerContext",
    "ContainerMessage",
    "ContainerCog",
    "ContainerModal",
    "ContainerPaginator",
    "container_command",
    "use_container",
]
