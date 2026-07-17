# ==============================================================================
# loop.py - Loop Mode Command
# ==============================================================================
# This plugin handles loop mode management.
#
# Commands:
# - /loop - Cycle through loop modes (disable -> single -> queue -> disable)
# - /loop disable - Disable loop
# - /loop single - Loop current track
# - /loop queue - Loop entire queue
#
# Requirements:
# - User must be admin or authorized user
# ==============================================================================

from pyrogram import filters, types

from BlacMusic import app, db, lang
from BlacMusic.helpers import can_manage_vc, utils


@app.on_message(filters.command(["loop"]) & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _loop(_, m: types.Message) -> None:
    if await utils.group_only_guard(m):
        return

    await utils.delete_command(m)

    current_loop = await db.get_loop(m.chat.id)

    # Check if user specified a mode
    if len(m.command) > 1:
        mode_arg = m.command[1].lower()
        if mode_arg in ["0", "disable"]:
            new_loop = 0
            text = "<blockquote>➡️ Loop mode disabled</blockquote>"
        elif mode_arg in ["single", "1", "one"]:
            new_loop = 1
            text = "<blockquote>🔂 Loop mode set to Single Track</blockquote>"
        elif mode_arg in ["queue", "all", "10"]:
            new_loop = 10
            text = "<blockquote>🔁 Loop mode set to Queue</blockquote>"
        else:
            await m.reply_text(
                "<blockquote><b>Usage:</b>\n"
                "• /loop - Cycle through modes\n"
                "• /loop disable - Disable loop\n"
                "• /loop single - Loop current track\n"
                "• /loop queue - Loop entire queue</blockquote>"
            )
            return
    else:
        # Cycle through modes
        if current_loop == 0:
            new_loop = 1
            text = "<blockquote>🔂 Loop mode set to Single Track</blockquote>"
        elif current_loop == 1:
            new_loop = 10
            text = "<blockquote>🔁 Loop mode set to Queue</blockquote>"
        else:
            new_loop = 0
            text = "<blockquote>➡️ Loop mode disabled</blockquote>"

    await db.set_loop(m.chat.id, new_loop)
    await m.reply_text(text)