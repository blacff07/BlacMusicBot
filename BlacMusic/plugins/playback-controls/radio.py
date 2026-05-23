# ==============================================================================
# radio.py - Radio / Live Stream Command
# ==============================================================================
# /radio <url or station name> — streams a live radio/internet stream
# /radio — shows usage if no query given
# ==============================================================================

from pyrogram import enums, filters, types
from BlacMusic import app, config, db, lang, tune, queue, yt
from BlacMusic.helpers._play import checkUB
import asyncio
import logging

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["radio"]) & ~app.bl_users)
@lang.language()
@checkUB
async def radio_hndlr(_, m: types.Message) -> None:
    try:
        await m.delete()
    except Exception:
        pass

    # DM guard
    if m.chat.type == enums.ChatType.PRIVATE:
        return await m.reply_text(
            "<blockquote>📻 <b>/radio — ʟɪᴠᴇ ʀᴀᴅɪᴏ ꜱᴛʀᴇᴀᴍ</b>\n\n"
            "ꜱᴛʀᴇᴀᴍꜱ ᴀɴʏ ʟɪᴠᴇ ɪɴᴛᴇʀɴᴇᴛ ʀᴀᴅɪᴏ ᴜʀʟ ɪɴᴛᴏ ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.\n\n"
            "<b>ᴜꜱᴀɢᴇ:</b>\n"
            "• <code>/radio https://stream.url/live</code>\n"
            "• <code>/radio lofi hip hop</code> — ꜱᴇᴀʀᴄʜᴇꜱ ʏᴏᴜᴛᴜʙᴇ ʟɪᴠᴇ\n\n"
            "ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰɪʀꜱᴛ.</blockquote>"
        )

    chat_id = m.chat.id

    # No query — show usage
    if len(m.command) < 2:
        return await m.reply_text(
            "<blockquote>📻 <b>ʀᴀᴅɪᴏ / ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍ</b>\n\n"
            "<b>ᴜꜱᴀɢᴇ:</b>\n"
            "• <code>/radio https://stream.url/live</code>\n"
            "• <code>/radio lofi hip hop</code> — ꜱᴇᴀʀᴄʜᴇꜱ ʏᴏᴜᴛᴜʙᴇ ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍ\n\n"
            "<b>ᴘᴏᴘᴜʟᴀʀ ꜱᴛᴀᴛɪᴏɴꜱ:</b>\n"
            "• <code>/radio lofi hip hop radio</code>\n"
            "• <code>/radio chillhop music</code>\n"
            "• <code>/radio jazz radio live</code></blockquote>"
        )

    query = " ".join(m.command[1:])
    sent = await m.reply_text(
        f"<blockquote>📻 ꜱᴇᴀʀᴄʜɪɴɢ ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍ: <b>{query}</b>...</blockquote>"
    )

    # If it's a direct URL, treat as live stream
    if query.startswith("http://") or query.startswith("https://"):
        from BlacMusic.helpers._dataclass import Track
        import time
        file = Track(
            id=str(int(time.time())),
            title=query,
            url=query,
            duration="LIVE",
            duration_sec=0,
            thumbnail=config.RADIO_IMG,
            channel_name="Radio",
            view_count=None,
            message_id=sent.id,
            is_live=True,
            file_path=query,
        )
    else:
        # Search YouTube for live stream
        file = await yt.search(query + " live stream", sent.id)
        if not file:
            return await sent.edit_text(
                "<blockquote>❌ ɴᴏ ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍ ꜰᴏᴜɴᴅ.\n\n"
                "ᴛʀʏ ᴀ ᴅɪʀᴇᴄᴛ ꜱᴛʀᴇᴀᴍ ᴜʀʟ ᴏʀ ᴀ ᴅɪꜰꜰᴇʀᴇɴᴛ ꜱᴇᴀʀᴄʜ ᴛᴇʀᴍ.</blockquote>"
            )
        file.is_live = True

    file.user = m.from_user.mention
    file.message_id = sent.id

    if await db.get_call(chat_id):
        pos = queue.add(chat_id, file)
        return await sent.edit_text(
            f"<blockquote>📻 <b>ǫᴜᴇᴜᴇᴅ #{pos}</b>\n\n"
            f"▶ <a href='{file.url}'>{file.title}</a>\n"
            f"⏱ LIVE\n"
            f"👤 {m.from_user.mention}</blockquote>"
        )

    queue.force_add(chat_id, file)
    try:
        await tune.play_media(chat_id=chat_id, message=sent, media=file)
    except Exception as e:
        await sent.edit_text(
            f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ꜱᴛʀᴇᴀᴍ.\n\n"
            f"ᴇʀʀᴏʀ: <code>{e}</code>\n\n"
            f"ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪꜱ ᴀᴄᴛɪᴠᴇ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</blockquote>"
        )