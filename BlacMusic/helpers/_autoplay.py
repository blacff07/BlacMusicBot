# ==============================================================================
# _autoplay.py - Autoplay Engine
# ==============================================================================

import asyncio
import random

from py_yt import VideosSearch

# NOTE: All BlacMusic imports are intentionally lazy (inside functions)
# to avoid circular import since calls.py imports this at module level.

_MOOD_MODIFIERS = [
    "similar songs",
    "songs like this",
    "related music",
    "same vibe playlist",
    "best mix",
    "top hits",
    "new releases",
    "trending",
    "acoustic version",
    "official audio",
    "remix",
    "cover",
    "live session",
    "deep cut",
    "b-side",
]

# Per-chat history to prevent autoplay repeating songs
_played_history: dict[int, set] = {}
_MAX_HISTORY = 30  # Remember last 30 played IDs per chat


def _get_utils():
    from BlacMusic.helpers._utilities import Utilities
    return Utilities()


async def _search_multi(base_query: str, count: int = 3, chat_id: int = 0):
    from BlacMusic import logger
    from BlacMusic.helpers._dataclass import Track

    utils = Utilities()
    tracks = []
    seen_ids: set[str] = set()
    _history = _played_history.get(chat_id, set())

    modifiers = random.sample(_MOOD_MODIFIERS, min(count, len(_MOOD_MODIFIERS)))
    while len(modifiers) < count:
        modifiers.append(random.choice(_MOOD_MODIFIERS))

    for mod in modifiers:
        query = f"{base_query} {mod}"
        try:
            def _do_search(q=query):
                s = VideosSearch(q, limit=3)
                return s.next()

            data = await asyncio.get_running_loop().run_in_executor(None, _do_search)
            data_list = data.get("result", [])
            for item in data_list:
                vid_id = item.get("id")
                if not vid_id or vid_id in seen_ids or vid_id in _history:
                    continue
                seen_ids.add(vid_id)
                duration = item.get("duration")
                is_live = duration is None or duration == "LIVE"
                track = Track(
                    id=vid_id,
                    channel_name=item.get("channel", {}).get("name", ""),
                    duration=duration if not is_live else "LIVE",
                    duration_sec=0 if is_live else utils.to_seconds(duration),
                    message_id=0,
                    title=item.get("title", "Unknown")[:40],
                    thumbnail=item.get("thumbnails", [{}])[-1].get("url", "").split("?")[0],
                    url=item.get("link", ""),
                    view_count=item.get("viewCount", {}).get("short"),
                    is_live=is_live,
                )
                tracks.append(track)
                break
        except Exception as e:
            logger.debug(f"Autoplay search error for '{query}': {e}")

    return tracks[:count]


async def send_suggestions(chat_id: int, target_chat: int, last_msg_id: int = 0) -> None:
    from pyrogram import types as ptypes
    from BlacMusic import app, config, db, logger

    last_query = await db.get_last_query(chat_id)
    if not last_query:
        # Fallback query when no history
        last_query = "popular music"

    try:
        suggestions = await _search_multi(last_query, count=3, chat_id=chat_id)
    except Exception as e:
        logger.debug(f"Autoplay: failed to fetch suggestions for {chat_id}: {e}")
        return

    if not suggestions:
        return

    # Delete old now-playing message if CLEANUP_MSG is enabled
    if config.CLEANUP_MSG and last_msg_id:
        try:
            await app.delete_messages(chat_id=target_chat, message_ids=last_msg_id)
        except Exception:
            pass

    buttons = []
    for track in suggestions:
        label = track.title[:28] + ("…" if len(track.title) > 28 else "")
        buttons.append([ptypes.InlineKeyboardButton(
            text=f"🎵  {label}",
            callback_data=f"autoplay_pick {chat_id} {track.id}",
        )])

    markup = ptypes.InlineKeyboardMarkup(buttons)
    text = (
        "✦ ɪɴꜱᴘɪʀᴇᴅ ʙʏ ʏᴏᴜʀ ʟɪꜱᴛᴇɴɪɴɢ —\n"
        "ʜᴇʀᴇ'ꜱ ᴡʜᴀᴛ ᴡᴇ ᴘɪᴄᴋᴇᴅ ꜰᴏʀ ʏᴏᴜ ✧"
    )
    try:
        await app.send_message(chat_id=target_chat, text=text, reply_markup=markup)
    except Exception as e:
        logger.debug(f"Autoplay: could not send suggestions in {target_chat}: {e}")


async def trigger_autoplay(chat_id: int, target_chat: int) -> None:
    from BlacMusic import app, db, lang, logger, queue, yt

    last_query = await db.get_last_query(chat_id)
    if not last_query:
        return

    # Autoplay ON = play automatically, no suggestion strip needed
    # Vary query with random modifier to get fresh results each time
    _mod = random.choice(_MOOD_MODIFIERS)
    _varied = f"{last_query} {_mod}"

    try:
        suggestions = await _search_multi(_varied, count=1, chat_id=chat_id)
        if not suggestions:
            return
        track = suggestions[0]
        # Record in history to prevent repeat
        if chat_id not in _played_history:
            _played_history[chat_id] = set()
        _played_history[chat_id].add(track.id)
        if len(_played_history[chat_id]) > _MAX_HISTORY:
            _played_history[chat_id] = set(list(_played_history[chat_id])[-15:])
    except Exception as e:
        logger.debug(f"Autoplay trigger error for {chat_id}: {e}")
        return

    try:
        track.file_path = await yt.download(track.id, is_live=track.is_live, video=False)
        if not track.file_path:
            return
    except Exception as e:
        logger.debug(f"Autoplay: download failed for {track.id}: {e}")
        return

    track.user = "ᴀᴜᴛᴏᴘʟᴀʏ"  # Set user field for now-playing card
    try:
        msg = await app.send_message(
            chat_id=target_chat,
            text=(
                "<blockquote>🔁 <b>ᴀᴜᴛᴏᴘʟᴀʏ</b>" + chr(10) + chr(10)
                + "▶ <a href='" + track.url + "'>" + track.title + "</a>" + chr(10)
                + "⏱ " + str(track.duration) + "</blockquote>"
            ),
        )
        track.message_id = msg.id
    except Exception:
        track.message_id = 0
        msg = None

    queue.force_add(chat_id, track)
    try:
        from BlacMusic import tune, db as _db
        await _db.add_call(chat_id)
        await tune.play_media(chat_id, msg, track)
    except Exception as e:
        logger.debug(f"Autoplay: play_media failed for {chat_id}: {e}")