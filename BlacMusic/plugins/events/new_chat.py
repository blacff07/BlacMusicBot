# ==============================================================================
# new_chat.py - New/Left Chat Member Notifications
# ==============================================================================
# Notifies the logger group whenever the bot is added to or removed from a
# group, including who added/removed it and basic chat metadata.
# ==============================================================================

from html import escape

from pyrogram import filters, types

from BlacMusic import app, config, logger


@app.on_message(filters.new_chat_members & filters.group)
async def new_chat_member(_, message: types.Message) -> None:
    for member in message.new_chat_members:
        if member.id == app.id:
            chat = message.chat
            chat_username = f"@{chat.username}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"
            members_count = await app.get_chat_members_count(chat.id)
            added_by = message.from_user
            added_by_name = added_by.mention if added_by else "ᴜɴᴋɴᴏᴡɴ"

            text = (
                f"<blockquote>🟢 <b>˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ</b></blockquote>\n\n"
                f"<blockquote>\n"
                f"🔖 <b>ᴄʜᴀᴛ ɴᴀᴍᴇ:</b> {escape(chat.title or '')}\n"
                f"🆔 <b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat.id}</code>\n"
                f"👤 <b>ᴄʜᴀᴛ ᴜꜱᴇʀɴᴀᴍᴇ:</b> {chat_username}\n"
                f"🔗 <b>ᴄʜᴀᴛ ʟɪɴᴋ:</b> {f'https://t.me/{chat.username}' if chat.username else 'ᴘʀɪᴠᴀᴛᴇ'}\n"
                f"👥 <b>ᴍᴇᴍʙᴇʀꜱ:</b> {members_count}\n"
                f"🤵 <b>ᴀᴅᴅᴇᴅ ʙʏ:</b> {added_by_name}\n"
                f"</blockquote>"
            )
            try:
                await app.send_photo(chat_id=config.LOGGER_ID, photo=config.START_IMG, caption=text)
            except Exception as e:
                logger.warning(f"Failed to send new chat notification: {e}")
            break


@app.on_message(filters.left_chat_member & filters.group)
async def left_chat_member(_, message: types.Message) -> None:
    if message.left_chat_member.id == app.id:
        chat = message.chat
        chat_username = f"@{chat.username}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"
        removed_by = message.from_user
        removed_by_name = removed_by.mention if removed_by else "ᴜɴᴋɴᴏᴡɴ"

        text = (
            f"<blockquote>🔴 <b>˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀ ɢʀᴏᴜᴘ</b></blockquote>\n\n"
            f"<blockquote>\n"
            f"🔖 <b>ᴄʜᴀᴛ ɴᴀᴍᴇ:</b> {escape(chat.title or '')}\n"
            f"🆔 <b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat.id}</code>\n"
            f"👤 <b>ᴄʜᴀᴛ ᴜꜱᴇʀɴᴀᴍᴇ:</b> {chat_username}\n"
            f"🚫 <b>ʀᴇᴍᴏᴠᴇᴅ ʙʏ:</b> {removed_by_name}\n"
            f"</blockquote>"
        )
        try:
            await app.send_photo(chat_id=config.LOGGER_ID, photo=config.START_IMG, caption=text)
        except Exception as e:
            logger.warning(f"Failed to send left chat notification: {e}")