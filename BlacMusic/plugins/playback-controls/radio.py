# ==============================================================================
# radio.py - Radio / Live Stream Command
# ==============================================================================
# /radio <url or station name> — streams a live radio/internet stream
# /radio — shows usage if no query given
# ==============================================================================

from html import escape

from pyrogram import enums, filters, types
from BlacMusic import app, config, db, lang, tune, queue, yt
import asyncio
import logging

logger = logging.getLogger(__name__)


async def _safe_edit(msg, text):
    """Edit message text safely — silently ignore if message was deleted."""
    try:
        await msg.edit_text(text)
    except Exception:
        pass


def _resolve_stream(url: str) -> str | None:
    """Extract direct stream URL from any URL using yt-dlp (handles m3u8, redirects, playlists)."""
    try:
        import yt_dlp
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "bestvideo+bestaudio/bestvideo/bestaudio/best",
            "noplaylist": True,
            "socket_timeout": 15,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            manifest = info.get("manifest_url")
            if manifest:
                return manifest
            return info.get("url")
    except Exception:
        return None


@app.on_message(filters.command(["radio"]) & ~app.bl_users)
@lang.language()
async def radio_hndlr(_, m: types.Message, force=False, url=None, cplay=False, video=False) -> None:
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
        f"<blockquote>📻 ꜱᴇᴀʀᴄʜɪɴɢ ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍ: <b>{escape(query)}</b>...</blockquote>"
    )

    import time as _time
    from BlacMusic.helpers._dataclass import Track

    # Direct URL — m3u8, icecast, rtmp, http stream
    is_direct = (
        query.startswith("http://")
        or query.startswith("https://")
        or query.startswith("rtmp://")
        or query.startswith("rtsp://")
        or yt.is_network_stream(query)
    )

    if is_direct:
        # Extract actual stream URL via yt-dlp (handles m3u8, redirects, etc.)
        resolved = await asyncio.get_running_loop().run_in_executor(
            None, lambda: _resolve_stream(query)
        )
        stream_url = resolved or query  # fallback to raw URL if extraction fails

        file = Track(
            id=str(int(_time.time())),
            title=escape((query.split("/")[-1][:40]) or "Live Radio"),
            url=query,
            duration="LIVE",
            duration_sec=0,
            thumbnail=config.RADIO_IMG,
            channel_name="Radio",
            view_count=None,
            message_id=sent.id,
            is_live=True,
            video=True,   # auto-detect: stream video if available, else audio
            file_path=stream_url,
        )
    else:
        # Search YouTube for live stream — try video first, fallback to audio
        file = await yt.search(query + " live", sent.id)
        if not file:
            file = await yt.search(query + " radio", sent.id)
        if not file:
            return await _safe_edit(sent, 
                "<blockquote>❌ ɴᴏ ꜱᴛʀᴇᴀᴍ ꜰᴏᴜɴᴅ.\n\n"
                "ᴛʀʏ ᴀ ᴅɪʀᴇᴄᴛ ᴜʀʟ ᴏʀ ᴀ ᴅɪꜰꜰᴇʀᴇɴᴛ ꜱᴇᴀʀᴄʜ ᴛᴇʀᴍ.</blockquote>"
            )
        file.is_live = True
        file.video = True  # prefer video if stream has it

    file.user = m.from_user.mention
    file.message_id = sent.id

    if await db.get_call(chat_id):
        pos = queue.add(chat_id, file)
        return await _safe_edit(sent, 
            f"<blockquote>📻 <b>ǫᴜᴇᴜᴇᴅ #{pos}</b>\n\n"
            f"▶ <a href='{file.url}'>{escape(file.title)}</a>\n"
            f"⏱ LIVE\n"
            f"👤 {m.from_user.mention}</blockquote>"
        )

    queue.force_add(chat_id, file)
    try:
        await tune.play_media(chat_id=chat_id, message=sent, media=file)
    except Exception as e:
        await _safe_edit(sent, 
            f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ꜱᴛʀᴇᴀᴍ.\n\n"
            f"ᴇʀʀᴏʀ: <code>{escape(str(e))}</code>\n\n"
            f"ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪꜱ ᴀᴄᴛɪᴠᴇ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</blockquote>"
        )