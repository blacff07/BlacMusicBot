# ==============================================================================
# autoplay.py - Autoplay Plugin
# ==============================================================================
# /autoplay on  → enables autoplay for this group
# /autoplay off → disables autoplay for this group
#
# When the queue empties with autoplay ON:
#   1. Bot fetches 3 related YouTube tracks based on last user query
#   2. Sends inline suggestion buttons (track titles) to the group
#   3. If user clicks one → song is queued and played
#   4. If bot can determine related tracks → auto-queues one silently
#
# User requests always take priority — autoplay tracks are marked so the
# system knows to resume autoplay when the user-requested queue drains again.
# ==============================================================================

from pyrogram import filters, types
from BlacMusic import app, db, lang
from BlacMusic.helpers._admins import is_admin


@app.on_message(
    filters.command(["autoplay"]) & ~app.bl_users
)
@lang.language()
async def autoplay_cmd(_, m: types.Message):
    try:
        await m.delete()
    except Exception:
        pass

    from pyrogram import enums as _enums
    if m.chat.type == _enums.ChatType.PRIVATE:
        return await m.reply_text(
            "<blockquote>⚠️ <b>ɢʀᴏᴜᴘ ᴏɴʟʏ</b>\n\n"
            "ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛꜱ.\n"
            "ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰɪʀꜱᴛ.</blockquote>"
        )

    if not m.from_user:
        return

    # Require admin or auth
    if not await is_admin(m.chat.id, m.from_user.id):
        if not await db.is_auth(m.chat.id, m.from_user.id):
            if m.from_user.id not in app.sudoers:
                return await m.reply_text(
                    "<blockquote>❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴀᴜᴛᴏᴘʟᴀʏ ꜱᴇᴛᴛɪɴɢ.</blockquote>"
                )

    if len(m.command) < 2 or m.command[1].lower() not in ("on", "off"):
        current = await db.get_autoplay(m.chat.id)
        status = "🟢 ᴏɴ" if current else "🔴 ᴏꜰꜰ"
        return await m.reply_text(
            f"<blockquote><b>˹ ᴀᴜᴛᴏᴘʟᴀʏ ˼</b>\n\n"
            f"ꜱᴛᴀᴛᴜꜱ: {status}\n\n"
            f"ᴜꜱᴀɢᴇ:\n"
            f"• <code>/autoplay on</code>  — ᴇɴᴀʙʟᴇ\n"
            f"• <code>/autoplay off</code> — ᴅɪꜱᴀʙʟᴇ</blockquote>"
        )

    enable = m.command[1].lower() == "on"
    await db.set_autoplay(m.chat.id, enable)

    if enable:
        await m.reply_text(
            "<blockquote>✅ <b>ᴀᴜᴛᴏᴘʟᴀʏ ᴇɴᴀʙʟᴇᴅ</b>\n\n"
            "ᴡʜᴇɴ ᴛʜᴇ ǫᴜᴇᴜᴇ ᴇɴᴅꜱ, ɪ'ʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴘʟᴀʏ ᴀ ʀᴇʟᴀᴛᴇᴅ ꜱᴏɴɢ\n"
            "ʙᴀꜱᴇᴅ ᴏɴ ᴛʜᴇ ᴍᴏᴏᴅ ᴏꜰ ᴛʜᴇ ʟᴀꜱᴛ ᴛʀᴀᴄᴋ ᴘʟᴀʏᴇᴅ.</blockquote>"
        )
    else:
        await m.reply_text(
            "<blockquote>🔴 <b>ᴀᴜᴛᴏᴘʟᴀʏ ᴅɪꜱᴀʙʟᴇᴅ</b>\n\n"
            "ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ꜱᴛᴏᴘ ᴡʜᴇɴ ᴛʜᴇ ǫᴜᴇᴜᴇ ɪꜱ ᴇᴍᴘᴛʏ.</blockquote>"
        )