# ==============================================================================
# _autoplay.py - Autoplay Engine
# ==============================================================================
# Handles:
# 1. Fetching 3 related/mood-based YouTube suggestions from last query
# 2. Sending suggestion buttons when queue is empty
# 3. Silently queueing one autoplay track when autoplay is ON
# 4. Callback handler for suggestion button taps
# ==============================================================================

import asyncio
import random
from dataclasses import replace

from youtubesearchpython import VideosSearch

from BlacMusic import app, db, lang, logger, queue, tune, yt
from BlacMusic.helpers._dataclass import Track
from BlacMusic.helpers._utilities import Utilities

utils = Utilities()

# Mood/genre modifier bank — appended to the last query to find related songs
_MOOD_MODIFIERS = [
    "similar songs",
    "songs like this",
    "related music",
    "same vibe playlist",
    "best mix",
]


async def _search_multi(base_query: str, count: int = 3) -> list[Track]:
    """
    Search YouTube for `count` distinct tracks related to `base_query`.
    Uses different mood modifiers per slot so results vary.
    """
    tracks: list[Track] = []
    seen_ids: set[str] = set()

    modifiers = random.sample(_MOOD_MODIFIERS, min(count, len(_MOOD_MODIFIERS)))
    # Pad if needed
    while len(modifiers) < count:
        modifiers.append(random.choice(_MOOD_MODIFIERS))

    for mod in modifiers:
        query = f"{base_query} {mod}"
        try:
            def _do_search(q=query):
                s = VideosSearch(q, limit=3)
                return s.next()  # sync call

            data = await asyncio.get_event_loop().run_in_executor(None, _do_search)
            data_list = data.get("result", [])
            for data in data_list:
                vid_id = data.get("id")
                if not vid_id or vid_id in seen_ids:
                    continue
                seen_ids.add(vid_id)
                duration = data.get("duration")
                is_live = duration is None or duration == "LIVE"
                track = Track(
                    id=vid_id,
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=duration if not is_live else "LIVE",
                    duration_sec=0 if is_live else utils.to_seconds(duration),
                    message_id=0,
                    title=data.get("title", "Unknown")[:40],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    url=data.get("link", ""),
                    view_count=data.get("viewCount", {}).get("short"),
                    is_live=is_live,
                )
                tracks.append(track)
                break  # one per modifier slot
        except Exception as e:
            logger.debug(f"Autoplay search error for '{query}': {e}")

    return tracks[:count]


async def send_suggestions(chat_id: int, target_chat: int) -> None:
    """
    Send 3 inline suggestion buttons to the group when the queue is empty.
    Each button shows a song title; tapping it queues and plays that song.
    """
    last_query = await db.get_last_query(chat_id)
    if not last_query:
        return

    try:
        suggestions = await _search_multi(last_query, count=3)
    except Exception as e:
        logger.debug(f"Autoplay: failed to fetch suggestions for {chat_id}: {e}")
        return

    if not suggestions:
        return

    from pyrogram import types as ptypes

    # Build one button per suggestion — callback carries the YouTube video ID + title
    buttons = []
    for track in suggestions:
        # Trim title for button label
        label = track.title[:30] + ("…" if len(track.title) > 30 else "")
        # Store vid_id in callback_data; full title stored via vid ID lookup
        buttons.append([ptypes.InlineKeyboardButton(
            text=f"🎵 {label}",
            callback_data=f"autoplay_pick {chat_id} {track.id}",
        )])

    markup = ptypes.InlineKeyboardMarkup(buttons)

    _lang = await lang.get_lang(chat_id)
    text = (
        "<blockquote>🎶 <b>ǫᴜᴇᴜᴇ ᴇᴍᴘᴛɪᴇᴅ</b>\n\n"
        "ᴛᴀᴘ ᴀ ꜱᴏɴɢ ᴛᴏ ᴋᴇᴇᴘ ᴛʜᴇ ᴠɪʙᴇ ɢᴏɪɴɢ ↓</blockquote>"
    )
    try:
        await app.send_message(chat_id=target_chat, text=text, reply_markup=markup)
    except Exception as e:
        logger.debug(f"Autoplay: could not send suggestions in {target_chat}: {e}")


async def trigger_autoplay(chat_id: int, target_chat: int) -> None:
    """
    Silently queue and play one autoplay track.
    Called when autoplay is ON and queue just emptied.
    Also fires send_suggestions so users can see what's coming or pick alternatives.
    """
    last_query = await db.get_last_query(chat_id)
    if not last_query:
        return

    # Show suggestion buttons in parallel (non-blocking)
    asyncio.create_task(send_suggestions(chat_id, target_chat))

    # Pick ONE related track to auto-queue
    try:
        suggestions = await _search_multi(last_query, count=1)
        if not suggestions:
            return
        track = suggestions[0]
    except Exception as e:
        logger.debug(f"Autoplay trigger error for {chat_id}: {e}")
        return

    # Download it
    try:
        track.file_path = await yt.download(track.id, is_live=track.is_live, video=False)
        if not track.file_path:
            return
    except Exception as e:
        logger.debug(f"Autoplay: download failed for {track.id}: {e}")
        return

    # Send a "now autoplaying" message
    _lang = await lang.get_lang(chat_id)
    try:
        msg = await app.send_message(
            chat_id=target_chat,
            text=(
                f"<blockquote>🔁 <b>ᴀᴜᴛᴏᴘʟᴀʏ</b>\n\n"
                f"▶ <a href='{track.url}'>{track.title}</a>\n"
                f"⏱ {track.duration}</blockquote>"
            ),
        )
        track.message_id = msg.id
    except Exception:
        track.message_id = 0
        msg = None

    # Add to queue at position 0 (plays immediately) and start
    queue.force_add(chat_id, track)
    try:
        await tune.play_media(chat_id, msg, track)
    except Exception as e:
        logger.debug(f"Autoplay: play_media failed for {chat_id}: {e}")