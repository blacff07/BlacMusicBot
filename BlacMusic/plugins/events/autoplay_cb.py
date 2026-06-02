# ==============================================================================
# autoplay_cb.py - Autoplay Suggestion Button Callback Handler
# ==============================================================================
# Handles the inline button taps from the "Queue emptied" suggestion message.
# When user taps a song button:
#   1. Message is deleted
#   2. Song is downloaded and added to queue
#   3. Plays immediately (or queued if something is playing)
# ==============================================================================

import asyncio

from pyrogram import filters, types

from BlacMusic import app, db, lang, logger, queue, yt
# tune imported lazily inside handlers to avoid circular import
from BlacMusic.helpers._dataclass import Track
from BlacMusic.helpers._utilities import Utilities

utils = Utilities()


@app.on_callback_query(filters.regex(r"^autoplay_pick "))
async def autoplay_pick_cb(_, cq: types.CallbackQuery):
    """User tapped a suggestion button — queue the selected track."""
    try:
        # Parse callback data: "autoplay_pick {chat_id} {video_id}"
        parts = cq.data.split(" ", 2)
        if len(parts) != 3:
            return await cq.answer("❌ Invalid callback.", show_alert=False)

        _, chat_id_str, video_id = parts
        chat_id = int(chat_id_str)

        await cq.answer("🎵 ᴀᴅᴅɪɴɢ ᴛᴏ ǫᴜᴇᴜᴇ…", show_alert=False)

        # Delete the suggestion message immediately so it doesn't clutter
        try:
            await cq.message.delete()
        except Exception:
            pass

        user_mention = cq.from_user.mention

        # Fetch track details via YouTube URL (yt.search handles URLs natively)
        try:
            track = await yt.search(f"https://www.youtube.com/watch?v={video_id}", 0)
        except Exception:
            track = None

        if not track:
            try:
                await app.send_message(
                    chat_id=chat_id,
                    text="<blockquote>❌ ᴄᴏᴜʟᴅɴ'ᴛ ꜰᴇᴛᴄʜ ᴛʜᴀᴛ ᴛʀᴀᴄᴋ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ /play.</blockquote>",
                )
            except Exception:
                pass
            return

        track.user = user_mention

        # Check if something is already playing
        is_active = await db.get_call(chat_id)

        if is_active:
            # Queue it — it will play after current track
            pos = queue.add(chat_id, track)
            _lang = await lang.get_lang(chat_id)
            try:
                await app.send_message(
                    chat_id=chat_id,
                    text=(
                        f"<blockquote>✅ <b>ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ #{pos}</b>\n\n"
                        f"▶ <a href='{track.url}'>{track.title}</a>\n"
                        f"⏱ {track.duration}\n"
                        f"👤 {user_mention}</blockquote>"
                    ),
                )
            except Exception:
                pass
        else:
            # Nothing playing — download and play immediately
            try:
                track.file_path = await yt.download(track.id, is_live=track.is_live, video=False)
                if not track.file_path:
                    raise ValueError("Download returned None")
            except Exception as e:
                logger.debug(f"Autoplay pick: download failed: {e}")
                try:
                    await app.send_message(
                        chat_id=chat_id,
                        text="<blockquote>❌ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ /play.</blockquote>",
                    )
                except Exception:
                    pass
                return

            try:
                msg = await app.send_message(
                    chat_id=chat_id,
                    text=(
                        f"<blockquote>🎵 <b>ᴘʟᴀʏɪɴɢ ꜰʀᴏᴍ ꜱᴜɢɢᴇꜱᴛɪᴏɴ</b>\n\n"
                        f"▶ <a href='{track.url}'>{track.title}</a>\n"
                        f"⏱ {track.duration}\n"
                        f"👤 {user_mention}</blockquote>"
                    ),
                )
                track.message_id = msg.id
            except Exception:
                msg = None
                track.message_id = 0

            queue.force_add(chat_id, track)
            try:
                await db.add_call(chat_id)
                from BlacMusic import tune as _tune
                await _tune.play_media(chat_id, msg, track)
            except Exception as e:
                logger.debug(f"Autoplay pick: play_media failed: {e}")

    except Exception as e:
        logger.error(f"autoplay_pick_cb error: {e}", exc_info=True)
        try:
            await cq.answer("❌ ᴇʀʀᴏʀ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ /play.", show_alert=True)
        except Exception:
            pass