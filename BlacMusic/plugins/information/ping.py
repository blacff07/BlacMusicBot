# ==============================================================================
# ping.py - Ping/Alive Command
# ==============================================================================
# This plugin shows bot status and performance metrics.
#
# Commands:
# - /ping - Show bot latency and system stats
# - /alive - Same as /ping
#
# Displays:
# - Response latency
# - Uptime
# - CPU usage
# - RAM usage
# - Disk usage
# - Voice call latency
# ==============================================================================

import time
import psutil

from pyrogram import filters, types
from BlacMusic import app, boot, config, db, lang, tune
from BlacMusic.helpers import buttons


def _format_uptime(total_seconds: int) -> str:
    """Format seconds elapsed since boot as 'Xdays, Hh:Mm:Ss' (days omitted if zero)."""
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = (total_seconds // 3600) % 24
    days = total_seconds // 86400

    uptime = f"{hours}h:{minutes}m:{seconds}s"
    if days:
        uptime = f"{days}days, {uptime}"
    return uptime


@app.on_message(filters.command(["alive", "ping"]) & ~app.bl_users)
@lang.language()
async def _ping(_, m: types.Message) -> None:
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    start = time.time()
    sent = await m.reply_text(m.lang["pinging"])

    uptime = _format_uptime(int(time.time() - boot))
    latency = round((time.time() - start) * 1000, 2)

    # Get system stats
    mem = psutil.virtual_memory()
    ram_usage = f"{round(mem.used / (1024 ** 3), 1)}GB / {round(mem.total / (1024 ** 3), 1)}GB"
    cpu_percent = psutil.cpu_percent(interval=0.5)

    # Get active chats count
    active_chats = len(await db.get_chats())

    disk = psutil.disk_usage("/")
    disk_percent = disk.percent
    caption_text = m.lang["ping_pong"].format(
        latency,                        # {0} ping ms
        app.username or app.name,       # {1} username for link
        app.name,                       # {2} display name
        uptime,                         # {3} uptime
        ram_usage,                      # {4} ram
        cpu_percent,                    # {5} cpu%
        disk_percent,                   # {6} disk%
        round(await tune.ping(), 2),    # {7} pytgcalls ms
    )

    # Try to send with media, fallback to text if it fails
    try:
        await sent.edit_media(
            media=types.InputMediaPhoto(
                media=config.PING_IMG,
                caption=caption_text
            ),
            reply_markup=buttons.ping_markup(m.lang["support"]),
        )
    except Exception:
        # Fallback to text if media fails
        await sent.edit_text(
            text=caption_text,
            reply_markup=buttons.ping_markup(m.lang["support"]),
        )