# ==============================================================================
# autoplay.py - Autoplay Toggle Command
# ==============================================================================
# This plugin lets group admins / authorized users turn autoplay on or off
# for their chat. When enabled, BlacMusic automatically queues a related
# track once the queue runs empty (see BlacMusic.helpers._autoplay and the
# stream-end handling in BlacMusic.core.calls).
#
# Commands:
# - /autoplay - Show current status
# - /autoplay on - Enable autoplay for this chat
# - /autoplay off - Disable autoplay for this chat
#
# Requirements:
# - User must be admin, authorized, or sudo (same as other VC controls)
# ==============================================================================

from pyrogram import filters, types

from BlacMusic import app, db, lang
from BlacMusic.helpers import can_manage_vc, utils


@app.on_message(filters.command(["autoplay"]) & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _autoplay(_, m: types.Message) -> None:
    if await utils.group_only_guard(m):
        return

    await utils.delete_command(m)

    current = await db.get_autoplay(m.chat.id)

    if len(m.command) > 1:
        mode_arg = m.command[1].strip().lower()
        if mode_arg in ("on", "enable", "1"):
            new_state = True
        elif mode_arg in ("off", "disable", "0"):
            new_state = False
        else:
            await m.reply_text(
                "<blockquote><b>Usage:</b>\n"
                "• /autoplay - Show current status\n"
                "• /autoplay on - Enable autoplay\n"
                "• /autoplay off - Disable autoplay</blockquote>"
            )
            return

        if new_state == current:
            state_word = "enabled" if current else "disabled"
            await m.reply_text(
                f"<blockquote>⚠️ Autoplay is already {state_word} for this chat.</blockquote>"
            )
            return

        await db.set_autoplay(m.chat.id, new_state)
        if new_state:
            await m.reply_text(
                "<blockquote>🔁 <b>ᴀᴜᴛᴏᴘʟᴀʏ ᴇɴᴀʙʟᴇᴅ</b>\n\n"
                "ɪ'ʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ǫᴜᴇᴜᴇ ᴀ ʀᴇʟᴀᴛᴇᴅ ᴛʀᴀᴄᴋ ᴡʜᴇɴᴇᴠᴇʀ ᴛʜᴇ ǫᴜᴇᴜᴇ ʀᴜɴꜱ ᴇᴍᴘᴛʏ.</blockquote>"
            )
        else:
            await m.reply_text(
                "<blockquote>➡️ <b>ᴀᴜᴛᴏᴘʟᴀʏ ᴅɪꜱᴀʙʟᴇᴅ</b> ꜰᴏʀ ᴛʜɪꜱ ᴄʜᴀᴛ.</blockquote>"
            )
    else:
        state_word = "🔁 enabled" if current else "➡️ disabled"
        await m.reply_text(
            f"<blockquote><b>Autoplay is currently {state_word} for this chat.</b>\n\n"
            "Use <code>/autoplay on</code> or <code>/autoplay off</code> to change it.</blockquote>"
        )
