<div align="center">

<br/>

```
 ▄▄   ▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄     
█  █ █  █       █       █       █       █   █    
█  █▄█  █    ▄▄▄█  ▄▄▄▄▄█  ▄▄▄▄▄█    ▄▄▄█   █    
█       █   █▄▄▄█ █▄▄▄▄▄█ █▄▄▄▄▄█   █▄▄▄█   █    
█       █    ▄▄▄█▄▄▄▄▄  █▄▄▄▄▄  █    ▄▄▄█   █▄▄▄ 
 █     ██   █▄▄▄ ▄▄▄▄▄█ █▄▄▄▄▄█ █   █▄▄▄█       █
  █▄▄▄█ █▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█
```

**A fully-featured Discord.py library for sending Components V2 containers**  
*Drop-in replacement for `ctx.send` — zero refactoring required*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.5%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Components V2](https://img.shields.io/badge/Components-V2-f59e0b?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/developers/docs/components/overview)

<br/>

```py
c = ContainerContext(ctx)
await c.send(f"{member.mention} is happy! 🎉", header="Greeting", color=discord.Color.gold())
```

<br/>

</div>

---

## ✦ What is Vessel?

Discord's **Components V2** introduced a new way to send structured messages using *containers* — but discord.py's raw API for building them is verbose and repetitive.

**Vessel** wraps all of that into a single class that behaves exactly like `ctx` — same attributes, same patterns, same f-string support — but every `.send()` becomes a beautifully structured container instead of a plain message.

---

## ✦ Feature Overview

| Feature | Description |
|:--------|:------------|
| 🔁 **Drop-in replacement** | `ContainerContext` proxies every `ctx` attribute transparently |
| 📦 **Auto container building** | Headers, footers, sections, colors, thumbnails — all via kwargs |
| 📄 **Paginator** | Multi-page containers with Prev / Next / First / Last / Stop buttons |
| ✅ **Confirmation dialog** | `await ctx.confirm("Are you sure?")` → returns `True / False / None` |
| 📝 **Modal prompts** | Button-triggered modal forms, awaitable with returned values |
| ✏️ **In-place editing** | `msg.edit(...)` with the same kwargs as `send` |
| ⏰ **Auto-delete** | `delete_after=5.0` on any send |
| 💬 **Reactions** | Add, remove, wait for reactions on container messages |
| 📌 **Pin / Unpin** | `msg.pin()` and `msg.unpin()` |
| 🎛️ **Buttons & Selects** | Attach interactive components with one kwarg |
| 🧩 **Raw override** | `components=[...]` for full manual control |
| 🔌 **3 integration styles** | Manual wrap, decorator, or base Cog class |

---

## ✦ Installation

> **Requirements:** Python 3.10+, discord.py 2.5+

**1. Clone the repo**

```bash
git clone https://github.com/hurricanewisdom/Vessel.git
```

**2. Copy the `Vessel/` folder into your bot project**

```
your-bot/
├── Vessel/
├── cogs/
├── main.py
└── ...
```

**3. Import and use**

```python
from Vessel import ContainerContext, ContainerCog, use_container
```

That's it. No pip install required — it's a local library.

---

## ✦ Quick Start

### The simplest usage

```python
from Vessel import ContainerContext

@bot.command()
async def hello(ctx, member: discord.Member):
    c = ContainerContext(ctx)
    await c.send(f"{member.mention} says hello! 👋")
```

### With styling

```python
await c.send(
    f"Welcome to the server, {member.mention}!",
    header="New Member",
    footer="Read the rules in #rules",
    thumbnail=member.display_avatar.url,
    color=discord.Color.green(),
)
```

### Using the decorator (auto-wraps ctx)

```python
from Vessel import use_container

@bot.command()
@use_container
async def greet(ctx, member: discord.Member):
    await ctx.send(f"{member.mention} is happy! 🎉", header="Greeting")
#   ^^^ ctx is already a ContainerContext here
```

### Using the Cog base class (zero decorators)

```python
from Vessel import ContainerCog

class MyCog(ContainerCog):        # ← just change this line
    @commands.command()
    async def info(self, ctx):
        await ctx.reply("Here's your info", header="Info")
        #    ^^^ ctx is automatically a ContainerContext
```

---

## ✦ API Reference

### `ContainerContext`

The core class. Wraps a `commands.Context` and replaces its messaging methods.

```python
c = ContainerContext(ctx)
```

All standard `ctx` attributes (`ctx.author`, `ctx.guild`, `ctx.bot`, etc.) are fully accessible via proxy.

---

#### `await c.send(...)`

Send a container message.

```python
msg = await c.send(
    content,            # str  — main body text, f-strings/mentions/markdown all work
    *,
    header,             # str  — heading at the top
    footer,             # str  — small text at the bottom
    sections,           # list[str] — extra text blocks separated by dividers
    thumbnail,          # str  — image URL (top-right corner)
    image,              # str  — large image URL inside the container
    buttons,            # list[discord.ui.Button]
    select,             # discord.ui.Select
    view,               # discord.ui.View — children appended automatically
    color,              # discord.Color  — accent color on the left border
    spoiler,            # bool — wrap content in ||spoiler||
    components,         # list — raw override, bypasses all auto-building
    reference,          # discord.Message — message to reply to
    mention_author,     # bool
    delete_after,       # float — seconds before auto-delete
    ephemeral,          # bool — slash command only
)
```

Returns a [`ContainerMessage`](#containermessage).

---

#### `await c.reply(...)`

Shortcut for `send(..., reference=ctx.message)`. Accepts all the same kwargs.

```python
await c.reply("Got it!", header="Response", color=discord.Color.teal())
```

---

#### `await c.send_paginated(pages, ...)`

Send a multi-page container with navigation buttons.

```python
pages = [
    "**Page 1** — Introduction content here.",
    "**Page 2** — More details here.",
    "**Page 3** — Final notes here.",
]

await c.send_paginated(
    pages,
    header="Help Menu",
    footer="Use the buttons to navigate",
    color=discord.Color.blurple(),
    thumbnail="https://example.com/icon.png",
    timeout=120.0,          # seconds before buttons disable
    show_page_counter=True, # appends "Page N / M" to footer
)
```

Navigation includes **⏮ First**, **◀ Prev**, **▶ Next**, **⏭ Last**, and **⏹ Stop**.
Only the invoking user can control the paginator. Buttons auto-disable on timeout or stop.

---

#### `await c.confirm(...)`

Send a container with Confirm / Cancel buttons and wait for the invoking user.

```python
result = await c.confirm(
    "Are you sure you want to delete this?",
    header="⚠️ Confirmation",
    confirm_label="Yes, delete",   # default: "Confirm"
    cancel_label="No, cancel",     # default: "Cancel"
    color=discord.Color.red(),
    timeout=30.0,
)

if result is True:
    # confirmed
elif result is False:
    # cancelled
else:
    # timed out (None)
```

---

#### `await c.send_modal(title, fields=...)`

Sends a container with an "Open Form" button. When clicked, a Discord modal appears. Awaits submission and returns the values.

```python
values = await c.send_modal(
    "Feedback Form",
    fields=[
        {
            "label": "Your name",
            "placeholder": "e.g. Dylan",
            "max_length": 50,
        },
        {
            "label": "Your message",
            "placeholder": "Tell us what you think...",
            "style": discord.TextStyle.paragraph,
            "max_length": 1000,
        },
    ],
    timeout=300.0,
)

if values:
    name, message = values
    await c.send(f"Thanks {name}! You said: {message}")
```

**Field options:**

| Key | Type | Default | Description |
|:----|:-----|:--------|:------------|
| `label` | `str` | *required* | Field label shown in the modal |
| `placeholder` | `str` | `None` | Gray hint text |
| `required` | `bool` | `True` | Whether the field must be filled |
| `style` | `discord.TextStyle` | `short` | `short` or `paragraph` |
| `min_length` | `int` | `None` | Minimum character count |
| `max_length` | `int` | `1000` | Maximum character count |
| `default` | `str` | `None` | Pre-filled value |

Returns `list[str]` in field order, or `None` if timed out.

---

#### `c.typing()`

Trigger the typing indicator. Use as an async context manager.

```python
async with c.typing():
    await asyncio.sleep(2)
    await c.send("Done processing!")
```

---

### `ContainerMessage`

Returned by every `send*` method. Wraps `discord.Message` with container-aware helpers.

---

#### `await msg.edit(...)`

Edit the container in-place. Accepts the same kwargs as `send`.

```python
msg = await c.send("⏳ Loading...")
await asyncio.sleep(2)
await msg.edit("✅ Done!", color=discord.Color.green())
```

---

#### `await msg.delete(delay=None)`

Delete the message, optionally after a delay.

```python
await msg.delete()          # immediately
await msg.delete(delay=5.0)
```

---

#### `await msg.add_reaction(emoji)` / `remove_reaction(...)` / `clear_reactions()`

```python
await msg.add_reaction("👍")
await msg.remove_reaction("👍", member)
await msg.clear_reactions()
```

---

#### `await msg.wait_for_reaction(emojis=None, user=None, timeout=60.0)`

Wait for a specific reaction on this message.

```python
result = await msg.wait_for_reaction(
    emojis=["✅", "❌"],
    user=ctx.author,
    timeout=30.0,
)
if result:
    reaction, user = result
```

Returns `(discord.Reaction, discord.User)` or `None` on timeout.

---

#### `await msg.pin()` / `msg.unpin()`

```python
await msg.pin(reason="Important announcement")
await msg.unpin()
```

---

### `ContainerCog`

Base cog class that auto-injects `ContainerContext` into every command.

```python
from Vessel import ContainerCog
from discord.ext import commands

class MyCog(ContainerCog):
    @commands.command()
    async def hello(self, ctx):
        # ctx is ContainerContext — no wrapping needed
        await ctx.send("Hello!", header="Greeting")

    @commands.command()
    async def help(self, ctx):
        await ctx.send_paginated(["Page 1", "Page 2"], header="Help")

    @commands.command()
    async def confirm_action(self, ctx):
        if await ctx.confirm("Really do this?"):
            await ctx.send("Action executed.")
```

Every method on `ContainerContext` is available directly on `ctx`.

---

### `@use_container`

Decorator that wraps `ctx` into a `ContainerContext` automatically.

```python
from Vessel import use_container

@bot.command()
@use_container
async def command(ctx, ...):
    await ctx.send(...)    # ContainerContext
```

Works for both standalone commands and cog commands.

---

### `@container_command(**kwargs)`

Combines `@commands.command()` and `@use_container` into one decorator.

```python
from Vessel import container_command

@container_command(name="ping", aliases=["p"])
async def ping(ctx):
    await ctx.send("Pong!")

bot.add_command(ping)
```

---

## ✦ Full Examples

<details>
<summary><strong>📄 Paginated help menu</strong></summary>

```python
class HelpCog(ContainerCog):
    @commands.command()
    async def help(self, ctx):
        pages = [
            "**General**\n`!ping` — Latency check\n`!help` — This menu",
            "**Moderation**\n`!ban @user` — Ban a member\n`!kick @user` — Kick a member",
            "**Fun**\n`!greet @user` — Send a greeting\n`!form` — Submit feedback",
        ]
        await ctx.send_paginated(
            pages,
            header="📖 Help Menu",
            footer="Page navigation below",
            color=discord.Color.blurple(),
            timeout=90.0,
        )
```

</details>

<details>
<summary><strong>Ban command with confirmation gate</strong></summary>

```python
class ModCog(ContainerCog):
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        confirmed = await ctx.confirm(
            f"Ban **{member}** for: *{reason}*?",
            header="⚠️ Ban Confirmation",
            confirm_label="Yes, ban them",
            cancel_label="Cancel",
            color=discord.Color.red(),
            timeout=20.0,
        )
        if confirmed:
            await member.ban(reason=reason)
            await ctx.send(
                f"**{member}** was banned.\n**Reason:** {reason}",
                header="🔨 Member Banned",
                color=discord.Color.dark_red(),
                footer=f"Actioned by {ctx.author}",
            )
        elif confirmed is False:
            await ctx.send("Ban cancelled.", color=discord.Color.greyple())
        else:
            await ctx.send("Timed out — no action taken.", color=discord.Color.greyple())
```

</details>

<details>
<summary><strong>Feedback form with modal</strong></summary>

```python
class FeedbackCog(ContainerCog):
    @commands.command()
    async def feedback(self, ctx):
        values = await ctx.send_modal(
            "Feedback Form",
            fields=[
                {"label": "Your name", "placeholder": "e.g. Alex", "max_length": 50},
                {
                    "label": "Feedback",
                    "placeholder": "What would you like us to know?",
                    "style": discord.TextStyle.paragraph,
                    "max_length": 800,
                },
                {"label": "Rating (1–10)", "max_length": 2},
            ],
        )
        if values:
            name, feedback, rating = values
            channel = bot.get_channel(FEEDBACK_CHANNEL_ID)
            await channel.send(  # plain message to log channel
                f"New feedback from {ctx.author.mention}"
            )
            await ctx.send(
                f"Thanks, **{name}**! We've received your {rating}/10 rating.",
                header="✅ Feedback Submitted",
                color=discord.Color.green(),
            )
```

</details>

<details>
<summary><strong>Rich member profile card</strong></summary>

```python
@bot.command()
@use_container
async def profile(ctx, member: discord.Member = None):
    target = member or ctx.author
    roles = ", ".join(r.mention for r in target.roles[1:]) or "None"

    await ctx.send(
        f"**Display Name:** {target.display_name}\n"
        f"**ID:** `{target.id}`\n"
        f"**Joined Discord:** {discord.utils.format_dt(target.created_at, 'D')}\n"
        f"**Joined Server:** {discord.utils.format_dt(target.joined_at, 'D')}",
        header=f"👤 {target.name}",
        sections=[f"**Roles:** {roles}"],
        thumbnail=target.display_avatar.url,
        footer=f"Requested by {ctx.author.display_name}",
        color=target.color if target.color.value else discord.Color.blurple(),
    )
```

</details>

<details>
<summary><strong>Self-editing loading message</strong></summary>

```python
@bot.command()
@use_container
async def process(ctx):
    msg = await ctx.send("⏳ Step 1 of 3 — Initializing...", header="Processing")
    await asyncio.sleep(2)

    await msg.edit("⏳ Step 2 of 3 — Running checks...", header="Processing",
                   color=discord.Color.yellow())
    await asyncio.sleep(2)

    await msg.edit("✅ All steps complete!", header="Done",
                   color=discord.Color.green())
```

</details>

---

## ✦ How Components V2 Works

Vessel handles all of this for you:

```
ContainerContext.send(content, header=..., footer=..., buttons=...)
        │
        ▼
components/builder.py → builds discord.ui.Container tree
        │
        ├── discord.ui.TextDisplay(f"# {header}")
        ├── discord.ui.Separator()
        ├── discord.ui.Section(accessory=Thumbnail) ← if thumbnail
        │       └── discord.ui.TextDisplay(content)
        ├── discord.ui.TextDisplay(content) ← if no thumbnail
        ├── discord.ui.Separator()
        ├── discord.ui.TextDisplay(f"-# {footer}")
        └── discord.ui.ActionRow()
                └── buttons / select
        │
        ▼
channel.send(components=[container], flags=MessageFlags(is_components_v2=True))
```

The `is_components_v2=True` flag is **required** by Discord — Vessel sets it automatically on every send and edit.

---

## ✦ Requirements

| Package | Version |
|:--------|:--------|
| Python  |  3.10+  |
| discord.py | 2.5+ |

Install discord.py if you haven't:

```bash
pip install discord.py
```

---

## ✦ Project Structure

```
Vessel/
├── __init__.py                ← top-level exports
├── core/
│   ├── __init__.py
│   ├── context.py             ← ContainerContext
│   └── message.py             ← ContainerMessage
├── components/
│   ├── __init__.py
│   └── builder.py             ← component tree builder
├── utils/
│   ├── __init__.py
│   ├── cog.py                 ← ContainerCog base class
│   ├── decorators.py          ← @use_container, @container_command
│   ├── modal.py               ← ContainerModal
│   └── paginator.py           ← ContainerPaginator
└── examples.py                ← full working demo of every feature
```

---

## ✦ License

do whatever you want with it.

---

<div align="center">

<br/>

*Built for Discord.py 2.5+ · Components V2*

</div>
