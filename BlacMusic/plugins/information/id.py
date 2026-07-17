# ==============================================================================
# id.py - User ID & Chat ID Fetcher
# ==============================================================================
# /id — shows your own user ID (+ group chat ID if used in group)
# /id @username — shows that user's ID
# /id (reply) — shows replied-to user's ID
# ==============================================================================

# ==============================================================================
# id.py - User ID & Chat ID Fetcher
# ==============================================================================
# /id — shows your own user ID (+ group chat ID if used in group)
# /id @username — shows that user's ID
# /id (reply) — shows replied-to user's ID
# ==============================================================================

from html import escape

from pyrogram import enums, filters, types
from BlacMusic import app


@app.on_message(filters.command(["id"]) & ~app.bl_users)
async def id_cmd(_, m: types.Message) -> None:
    try:
        await m.delete()
    except Exception:
        pass

    lines = []

    # ── Determine target user ─────────────────────────────────────────────────
    target = None

    if m.reply_to_message and m.reply_to_message.from_user:
        target = m.reply_to_message.from_user

    elif len(m.command) > 1:
        query = m.command[1].lstrip("@")
        try:
            user = await app.get_users(query)
            target = user
        except Exception:
            await m.reply_text(
                "<blockquote>❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.\n\n"
                "ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴇ ᴜꜱᴇʀɴᴀᴍᴇ ɪꜱ ᴄᴏʀʀᴇᴄᴛ ᴏʀ ᴛʜᴇ ᴜꜱᴇʀ ʜᴀꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.</blockquote>"
            )
            return
    else:
        target = m.from_user

    # ── Build user info block ─────────────────────────────────────────────────
    if target:
        name = (target.first_name or "") + (" " + target.last_name if target.last_name else "")
        mention = f"<a href='tg://user?id={target.id}'>{escape(name.strip())}</a>"
        uname = f"@{escape(target.username)}" if target.username else "ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ"
        bot_tag = " 🤖" if target.is_bot else ""

        lines.append(
            "<blockquote>"
            "👤 <b>ᴜꜱᴇʀ ɪɴꜰᴏ</b>\n\n"
            f"➤ <b>ɴᴀᴍᴇ :</b> {mention}{bot_tag}\n"
            f"➤ <b>ᴜꜱᴇʀɴᴀᴍᴇ :</b> {uname}\n"
            f"➤ <b>ᴜꜱᴇʀ ɪᴅ :</b> <code>{target.id}</code>"
            "</blockquote>"
        )

    # ── Build chat info block (groups only) ───────────────────────────────────
    if m.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
        chat = m.chat
        chat_username = f"@{escape(chat.username)}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ"
        lines.append(
            "<blockquote>"
            "💬 <b>ɢʀᴏᴜᴘ ɪɴꜰᴏ</b>\n\n"
            f"➤ <b>ɴᴀᴍᴇ :</b> {escape(chat.title or '')}\n"
            f"➤ <b>ᴜꜱᴇʀɴᴀᴍᴇ :</b> {chat_username}\n"
            f"➤ <b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{chat.id}</code>"
            "</blockquote>"
        )

    if not lines:
        return

    await m.reply_text(
        "\n".join(lines),
        quote=True,
    )