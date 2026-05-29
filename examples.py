"""
examples.py
~~~~~~~~~~~
Full demonstration of every Vessel feature.
Drop your bot token in and run to test.
"""

import asyncio
import discord
from discord.ext import commands

# ─── Import everything from Vessel ──────────────────────────────────────
from Vessel import (
    ContainerContext,
    ContainerCog,
    use_container,
    container_command,
)

# ─── Bot setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 1 — Manual wrap: ContainerContext(ctx)
# ══════════════════════════════════════════════════════════════════════════════

@bot.command()
async def hello(ctx, member: discord.Member = None):
    """Basic send — just like ctx.send with an f-string."""
    target = member or ctx.author
    c = ContainerContext(ctx)
    await c.send(f"{target.mention} says hello! 👋")


@bot.command()
async def profile(ctx, member: discord.Member = None):
    """Header, footer, thumbnail, sections."""
    target = member or ctx.author
    c = ContainerContext(ctx)

    await c.send(
        f"**Name:** {target.display_name}\n"
        f"**ID:** `{target.id}`\n"
        f"**Joined:** {discord.utils.format_dt(target.joined_at, 'R')}",
        header=f"Profile — {target.display_name}",
        footer=f"Requested by {ctx.author.display_name}",
        thumbnail=target.display_avatar.url,
        color=target.color if target.color.value else discord.Color.blurple(),
    )


@bot.command()
async def multisection(ctx):
    """Multiple sections separated by dividers."""
    c = ContainerContext(ctx)
    await c.send(
        "This is the **main** body text.",
        header="Multi-Section Demo",
        sections=[
            "📌 **Section 2** — Some extra info here.",
            "📌 **Section 3** — Even more content below.",
        ],
        footer="Sections are separated by dividers automatically.",
        color=discord.Color.teal(),
    )


@bot.command()
async def spoilertest(ctx):
    """Spoiler-wrapped content."""
    c = ContainerContext(ctx)
    await c.send("This is a secret message!", spoiler=True, header="Spoiler")


@bot.command()
async def imagegallery(ctx):
    """Large image inside container."""
    c = ContainerContext(ctx)
    await c.send(
        "Here's a sample image:",
        header="Image Demo",
        image="https://picsum.photos/800/400",
        footer="Image via picsum.photos",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 2 — @use_container decorator
# ══════════════════════════════════════════════════════════════════════════════

@bot.command()
@use_container
async def greet(ctx, member: discord.Member):
    """ctx is already a ContainerContext here."""
    await ctx.send(
        f"{member.mention} is happy! 🎉",
        header="Greeting",
        color=discord.Color.gold(),
    )


@bot.command()
@use_container
async def editdemo(ctx):
    """Demonstrate ContainerMessage.edit() and delete()."""
    msg = await ctx.send("⏳ Loading...", header="Edit Demo")
    await asyncio.sleep(2)
    await msg.edit("✅ Done loading!", header="Edit Demo", color=discord.Color.green())
    await asyncio.sleep(3)
    await msg.delete()


@bot.command()
@use_container
async def reactiondemo(ctx):
    """Add reactions to a container message."""
    msg = await ctx.send("React to this message!", header="Reaction Demo")
    await msg.add_reaction("👍")
    await msg.add_reaction("❤️")

    result = await msg.wait_for_reaction(
        emojis=["👍", "❤️"],
        user=ctx.author,
        timeout=15.0,
    )
    if result:
        reaction, user = result
        await ctx.send(f"{user.mention} reacted with {reaction.emoji}!")
    else:
        await ctx.send("No reaction received in time.", header="Timed Out")


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 3 — @container_command shorthand
# ══════════════════════════════════════════════════════════════════════════════

@container_command(name="ping")
async def ping(ctx):
    """Shorthand decorator combining @command + @use_container."""
    latency = round(ctx.bot.latency * 1000)
    await ctx.send(
        f"🏓 Pong! Latency: **{latency}ms**",
        header="Ping",
        color=discord.Color.green() if latency < 100 else discord.Color.orange(),
    )

bot.add_command(ping)


# ══════════════════════════════════════════════════════════════════════════════
#  METHOD 4 — ContainerCog base class (auto-injects for every command)
# ══════════════════════════════════════════════════════════════════════════════

class FeatureCog(ContainerCog):
    """
    All commands in this cog automatically receive a ContainerContext.
    No wrapper or decorator needed.
    """

    # -- Paginator ---------------------------------------------------------

    @commands.command()
    async def help(self, ctx):
        """Paginated help menu."""
        pages = [
            "**General Commands**\n`!hello` — Say hello\n`!ping` — Check latency\n`!profile [@user]` — View a profile",
            "**Fun Commands**\n`!greet @user` — Greet someone\n`!spoilertest` — Spoiler demo\n`!imagegallery` — Image in container",
            "**Interactive**\n`!confirm` — Confirmation prompt\n`!form` — Modal form\n`!paghelp` — This paginated menu",
        ]
        await ctx.send_paginated(
            pages,
            header="📖 Help Menu",
            footer="Use the buttons to navigate",
            color=discord.Color.blurple(),
            timeout=60.0,
        )

    @commands.command()
    async def longlist(self, ctx):
        """Ten-page paginator example."""
        pages = [f"**Entry {i}**\nThis is page {i} of 10." for i in range(1, 11)]
        await ctx.send_paginated(
            pages,
            header="Long List",
            color=discord.Color.purple(),
        )

    # -- Confirmation ------------------------------------------------------

    @commands.command()
    async def confirm(self, ctx):
        """Confirmation prompt example."""
        result = await ctx.confirm(
            "Are you sure you want to do this?",
            header="⚠️ Confirmation Required",
            color=discord.Color.yellow(),
            timeout=20.0,
        )
        if result is True:
            await ctx.send("✅ Confirmed! Action executed.", color=discord.Color.green())
        elif result is False:
            await ctx.send("❌ Cancelled.", color=discord.Color.red())
        else:
            await ctx.send("⏰ Timed out — no response.", color=discord.Color.greyple())

    @commands.command()
    async def ban(self, ctx, member: discord.Member):
        """Ban with confirmation gate."""
        confirmed = await ctx.confirm(
            f"Ban **{member}** from this server?",
            header="⚠️ Ban Confirmation",
            confirm_label="Yes, ban",
            cancel_label="No, cancel",
            color=discord.Color.red(),
        )
        if confirmed:
            await ctx.send(
                f"{member.mention} has been banned.",
                header="🔨 Banned",
                color=discord.Color.dark_red(),
            )
            # await member.ban(reason=f"Banned by {ctx.author}")
        else:
            await ctx.send("Ban cancelled.", color=discord.Color.greyple())

    # -- Modal -------------------------------------------------------------

    @commands.command()
    async def form(self, ctx):
        """Collect multi-field input via a modal."""
        values = await ctx.send_modal(
            "Feedback Form",
            fields=[
                {
                    "label": "Your name",
                    "placeholder": "e.g. Alex",
                    "max_length": 50,
                },
                {
                    "label": "Your feedback",
                    "placeholder": "Tell us what you think...",
                    "style": discord.TextStyle.paragraph,
                    "max_length": 500,
                },
                {
                    "label": "Rating (1–10)",
                    "placeholder": "e.g. 8",
                    "max_length": 2,
                },
            ],
        )

        if values is None:
            await ctx.send("Form expired — no response received.", color=discord.Color.greyple())
            return

        name, feedback, rating = values
        await ctx.send(
            f"**From:** {name}\n**Rating:** {rating}/10\n\n{feedback}",
            header="📬 Feedback Received",
            footer=f"Submitted by {ctx.author.display_name}",
            color=discord.Color.green(),
            sections=[f"✅ Thank you, {name}! We've recorded your response."],
        )

    @commands.command()
    async def suggest(self, ctx):
        """Single-field suggestion box."""
        values = await ctx.send_modal(
            "Submit a Suggestion",
            fields=[
                {
                    "label": "Your suggestion",
                    "placeholder": "What would you like to see?",
                    "style": discord.TextStyle.paragraph,
                    "max_length": 1000,
                }
            ],
        )
        if values:
            await ctx.send(
                values[0],
                header="💡 New Suggestion",
                footer=f"From {ctx.author.display_name}",
                color=discord.Color.yellow(),
            )

    # -- Buttons -----------------------------------------------------------

    @commands.command()
    async def buttons(self, ctx):
        """Interactive buttons with callbacks."""
        results: list[str] = []
        event = asyncio.Event()

        async def _make_cb(label: str):
            async def _cb(interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.defer()
                    return
                results.append(label)
                event.set()
                await interaction.response.defer()
            return _cb

        btn_a = discord.ui.Button(label="Option A", style=discord.ButtonStyle.primary)
        btn_b = discord.ui.Button(label="Option B", style=discord.ButtonStyle.secondary)
        btn_c = discord.ui.Button(label="Option C", style=discord.ButtonStyle.success)

        btn_a.callback = await _make_cb("A")
        btn_b.callback = await _make_cb("B")
        btn_c.callback = await _make_cb("C")

        msg = await ctx.send(
            "Pick an option below:",
            header="Button Demo",
            buttons=[btn_a, btn_b, btn_c],
            color=discord.Color.blurple(),
        )

        try:
            await asyncio.wait_for(event.wait(), timeout=30.0)
            await msg.edit(
                f"You chose **Option {results[0]}**!",
                header="Choice Recorded",
                color=discord.Color.green(),
            )
        except asyncio.TimeoutError:
            await msg.edit("No choice made.", header="Timed Out", color=discord.Color.greyple())

    # -- Select menu -------------------------------------------------------

    @commands.command()
    async def selectdemo(self, ctx):
        """Select menu inside a container."""
        result: list[str] = []
        event = asyncio.Event()

        select = discord.ui.Select(
            placeholder="Choose a color...",
            options=[
                discord.SelectOption(label="Red", value="red", emoji="🔴"),
                discord.SelectOption(label="Green", value="green", emoji="🟢"),
                discord.SelectOption(label="Blue", value="blue", emoji="🔵"),
            ],
        )

        async def _select_cb(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.defer()
                return
            result.extend(select.values)
            event.set()
            await interaction.response.defer()

        select.callback = _select_cb

        msg = await ctx.send(
            "Pick a color from the menu:",
            header="Select Demo",
            select=select,
            color=discord.Color.blurple(),
        )

        try:
            await asyncio.wait_for(event.wait(), timeout=30.0)
            color_map = {
                "red": discord.Color.red(),
                "green": discord.Color.green(),
                "blue": discord.Color.blue(),
            }
            chosen = result[0]
            await msg.edit(
                f"You chose **{chosen.title()}**!",
                header="Color Chosen",
                color=color_map.get(chosen, discord.Color.default()),
            )
        except asyncio.TimeoutError:
            await msg.edit("No selection made.", color=discord.Color.greyple())

    # -- Reply shortcut ----------------------------------------------------

    @commands.command()
    async def echoreply(self, ctx, *, text: str):
        """Reply to the invoking message as a container."""
        await ctx.reply(
            f"> {text}",
            header="Echo",
            color=discord.Color.teal(),
        )

    # -- delete_after ------------------------------------------------------

    @commands.command()
    async def tempnotice(self, ctx):
        """Self-deleting container message."""
        await ctx.send(
            "⚠️ This message will self-destruct in 5 seconds.",
            header="Temporary Notice",
            color=discord.Color.orange(),
            delete_after=5.0,
        )

    # -- Raw components override -------------------------------------------

    @commands.command()
    async def rawdemo(self, ctx):
        """Full raw component override for maximum control."""
        container = discord.ui.Container()
        container.add_item(discord.ui.TextDisplay(value="# Raw Override"))
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(value="Built entirely by hand."))

        c = ContainerContext(ctx)
        await c.send(components=[container])


async def setup_cogs():
    await bot.add_cog(FeatureCog())


@bot.event
async def on_ready():
    await setup_cogs()
    print(f"Logged in as {bot.user} — Vessel ready!")


bot.run("YOUR_TOKEN_HERE")
