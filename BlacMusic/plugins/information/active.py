# ==============================================================================
# active.py - Active Voice Chats Command (Sudo Only)
# ==============================================================================
# This plugin shows statistics about active voice chats where the bot is playing.
#
# Commands:
# - /ac - Show count of active voice chats
# - /activevc - Show detailed list of active chats with currently playing track
#
# Only sudo users can use these commands.
# ==============================================================================

import os
import uuid

from pyrogram import filters, types
from BlacMusic import app, db, lang, queue


@app.on_message(filters.command(["ac", "activevc"]) & app.sudo_filter)
@lang.language()
async def _activevc(_, m: types.Message) -> None:
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    if not db.active_calls:
        await m.reply_text(m.lang["vc_empty"])
        return

    if m.command[0] == "ac":
        await m.reply_text(m.lang["vc_count"].format(len(db.active_calls)))
        return

    sent = await m.reply_text(m.lang["vc_fetching"])
    text = ""

    for i, chat in enumerate(db.active_calls):
        playing = queue.get_current(chat)
        if playing:
            text += f"\n{i+1}. <code>{chat}</code>\n    ➜ {playing.title[:25]}"

    if len(text) < 4000:
        await sent.edit_text(m.lang["vc_list"] + text)
        return

    # Unique filename avoids clobbering another concurrent /activevc call
    tmp_path = f"activevc_{uuid.uuid4().hex}.txt"
    with open(tmp_path, "w") as f:
        f.write(text)

    try:
        await sent.edit_media(
            media=types.InputMediaDocument(
                media=tmp_path,
                caption=m.lang["vc_list"],
            )
        )
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass