# ==============================================================================
# play.py - Main Play Command Handler
# ==============================================================================
# This is the core plugin that handles all play-related commands:
# - /play <query> - Play audio from YouTube search or URL
# - /vplay <query> - Play video in the voice chat (when enabled)
# - /playforce - Force play (skip queue and play immediately)
# - /vplayforce - Force video playback (skip queue)
# - /cplay - Play in connected channel
# - /cvplay - Play video in connected channel (when enabled)
# 
# Supports:
# - YouTube search queries
# - YouTube URLs (videos and playlists)
# - Telegram audio files (via reply)
# - Queue management
# - Channel play mode
# ==============================================================================

import asyncio
import logging
import random

from pyrogram import filters
from pyrogram import types
from pyrogram.errors import FloodWait, MessageIdInvalid, MessageDeleteForbidden, ChatSendPlainForbidden, ChatWriteForbidden

from BlacMusic import app, tune, config, db, lang, queue, tg, yt
from BlacMusic.helpers import buttons, utils
from BlacMusic.helpers._play import checkUB

logger = logging.getLogger(__name__)

# Reaction emoji pool - one is picked at random after a successful /play
_EMOJI_POOL = [
    "🌷", "🌹", "👀", "👁", "👣", "🫶", "🫰", "🎩", "🦋", "🕸",
    "🐾", "💫", "💥", "❄️", "🍾", "🥂", "🧃", "🍭", "🎗", "🎨",
    "🚀", "🎢", "💡", "💣", "🧨", "🔮", "🧪", "🌡", "🎉",
    "🎊", "🪄", "💌", "🪩", "🧮", "❤️‍🩹", "💝", "💗", "💞", "💔",
    "🖤", "💢", "💯", "🎶", "🎵", "🔎", "🦠", "💥"
]


async def safe_edit(message, text, **kwargs):
    """
    Safely edit a message with proper error handling for common Telegram API errors.
    
    Args:
        message: The message object to edit
        text: New text content
        **kwargs: Additional arguments for edit_text
        
    Returns:
        True if successful, False otherwise
    """
    try:
        await message.edit_text(text, **kwargs)
        return True
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await message.edit_text(text, **kwargs)
            return True
        except (MessageIdInvalid, MessageDeleteForbidden, Exception):
            return False
    except (MessageIdInvalid, MessageDeleteForbidden):
        # Message was deleted or became invalid - this is expected
        return False
    except Exception:
        # Other errors - log but don't crash
        return False


async def safe_reply(message, text, **kwargs):
    """
    Safely send a reply message with proper error handling for media-only chats.
    
    Args:
        message: The message object to reply to
        text: Text content to send
        **kwargs: Additional arguments for reply_text
        
    Returns:
        The sent message object if successful, None otherwise
    """
    try:
        return await message.reply_text(text, **kwargs)
    except (ChatSendPlainForbidden, ChatWriteForbidden):
        logger.warning(f"Cannot send text in chat {message.chat.id} (chat write forbidden)")
        return None
    except Exception as e:
        logger.error(f"Failed to send reply: {e}")
        return None


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    """
    Add multiple tracks to queue and format them as a message.
    
    Args:
        chat_id: The chat ID where queue is managed
        tracks: List of Track objects to add
        
    Returns:
        Formatted string listing all added tracks
    """
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)  # Add track to queue (returns 0-based index)
        text += f"<b>{pos}.</b> {track.title}\n"  # Show actual queue position
    text = text[:1948] + "</blockquote>"  # Limit message length
    return text

@app.on_message(
    filters.command(
        [
            "play",
            "playforce",
            "cplay",
            "cplayforce",
            "vplay",
            "vplayforce",
            "cvplay",
            "cvplayforce",
        ]
    )
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    url: str = None,
    cplay: bool = False,
    video: bool = False,
) -> None:
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    # DM guard — command-specific responses
    from pyrogram import enums as _enums
    if m.chat.type == _enums.ChatType.PRIVATE:
        cmd = m.command[0].lower()
        if cmd.startswith("c"):
            return await m.reply_text(
                "<blockquote>📢 <b>/cplay — ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ</b>\n\n"
                "ꜱᴛʀᴇᴀᴍꜱ ᴍᴜꜱɪᴄ ɪɴᴛᴏ ʏᴏᴜʀ <b>ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ'ꜱ</b> ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.\n\n"
                "<b>ꜱᴇᴛᴜᴘ:</b>\n"
                "1. ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ\n"
                "2. ᴜꜱᴇ <code>/channelplay linked</code> ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ\n"
                "3. ᴛʜᴇɴ ᴜꜱᴇ <code>/cplay songname</code>\n\n"
                "ᴄᴜʀʀᴇɴᴛ ᴄʜᴀɴɴᴇʟ: ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘ ᴛᴏ ᴄʜᴇᴄᴋ.</blockquote>"
            )
        elif cmd.startswith("v"):
            enabled = config.VIDEO_PLAY
            return await m.reply_text(
                "<blockquote>📺 <b>/vplay — ᴠɪᴅᴇᴏ ᴘʟᴀʏ</b>\n\n"
                f"ꜱᴛᴀᴛᴜꜱ: {'✅ ᴇɴᴀʙʟᴇᴅ' if enabled else '❌ ᴅɪꜱᴀʙʟᴇᴅ'}\n\n"
                "ꜱᴛʀᴇᴀᴍꜱ ᴠɪᴅᴇᴏ ᴅɪʀᴇᴄᴛʟʏ ɪɴᴛᴏ ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.\n"
                + ("ᴜꜱᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴡɪᴛʜ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ." if enabled else
                   "ᴇɴᴀʙʟᴇ ᴠɪᴅᴇᴏ: ꜱᴇᴛ <code>VIDEO_PLAY=True</code> ɪɴ .ᴇɴᴠ") + "</blockquote>"
            )
        else:
            return await m.reply_text(
                "<blockquote>🎵 <b>/play — ᴍᴜꜱɪᴄ ᴘʟᴀʏ</b>\n\n"
                "ꜱᴇᴀʀᴄʜᴇꜱ ʏᴏᴜᴛᴜʙᴇ ᴀɴᴅ ꜱᴛʀᴇᴀᴍꜱ ᴀᴜᴅɪᴏ ɪɴᴛᴏ ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.\n\n"
                "<b>ᴜꜱᴀɢᴇ:</b>\n"
                "• <code>/play songname</code>\n"
                "• <code>/play youtube.com/watch?v=...</code>\n\n"
                "ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰɪʀꜱᴛ.</blockquote>"
            )

    # Detect mode from command name
    _cmd = m.command[0].lower()
    cplay = _cmd.startswith("c")
    video = _cmd.startswith("v") or _cmd.startswith("cv")
    force = "force" in _cmd or (len(m.command) > 1 and "-f" in m.command[1:])

    # Handle channel play mode
    chat_id = m.chat.id
    message_chat_id = m.chat.id  # Store original group chat ID for thumbnail
    if cplay:
        channel_id = await db.get_cmode(m.chat.id)
        if channel_id is None:
            return await safe_reply(m,
                "<blockquote>❌ Channel play is not enabled.\n\n"
                "To enable for linked channel:\n"
                "`/channelplay linked`\n\n"
                "To enable for any channel:\n"
                "`/channelplay [channel_id]`</blockquote>"
            )
        try:
            chat = await app.get_chat(channel_id)
            chat_id = channel_id
        except Exception:
            await db.set_cmode(m.chat.id, None)
            return await safe_reply(m,
                "<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴄʜᴀɴɴᴇʟ.\n\n"
                "ᴍᴀᴋᴇ ꜱᴜʀᴇ ɪ'ᴍ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ ɪꜱ ꜱᴇᴛ ᴄᴏʀʀᴇᴄᴛʟʏ.</blockquote>"
            )
        
        # Auto-join assistant to channel if not already a member
        client = await db.get_client(channel_id)
        try:
            # Check if assistant is in the channel
            await app.get_chat_member(channel_id, client.id)
        except Exception:
            # Assistant not in channel, try to join
            try:
                # For channels, we need an invite link
                if chat.username:
                    invite_link = chat.username
                else:
                    # Try to get/create invite link
                    try:
                        invite_link = chat.invite_link
                        if not invite_link:
                            invite_link = await app.export_chat_invite_link(channel_id)
                    except Exception:
                        return await safe_reply(m,
                            f"<blockquote>❌ ᴀꜱꜱɪꜱᴛᴀɴᴛ ɴᴏᴛ ɪɴ ᴄʜᴀɴɴᴇʟ!\n\n"
                            f"ᴘʟᴇᴀꜱᴇ ᴀᴅᴅ @{client.username if client.username else client.mention} "
                            f"ᴛᴏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ.</blockquote>"
                        )
                
                # Show joining message
                join_msg = await safe_reply(m,
                    f"<blockquote>🔄 ᴊᴏɪɴɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ᴄʜᴀɴɴᴇʟ...</blockquote>"
                )
                
                # Try to join the channel
                await client.join_chat(invite_link)
                await asyncio.sleep(1)  # Give it time to fully join
                
                # Delete joining message
                try:
                    await join_msg.delete()
                except Exception:
                    pass
                    
            except Exception as e:
                error_str = str(e)
                return await safe_reply(m,
                    f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ᴄʜᴀɴɴᴇʟ!\n\n"
                    f"ᴘʟᴇᴀꜱᴇ ᴍᴀɴᴜᴀʟʟʏ ᴀᴅᴅ @{client.username if client.username else client.mention} "
                    f"ᴛᴏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ.\n\n"
                    f"Error: {error_str}</blockquote>"
                )

    # Select emoji randomly at runtime from pool
    import random as _rnd
    _EMOJI_POOL = [
        "🌷","🌹","👀","👁","👣","🫶","🫰","🎩","🦋","🕸",
        "🐾","💫","💥","❄️","🍾","🥂","🧃","🍭","🎗","🎨",
        "🚀","🎢","💡","💣","🧨","🔮","🧪","🌡","🎉",
        "🎊","🪄","💌","🪩","🧮","❤️‍🩹","💝","💗","💞","💔",
        "🖤","💢","💯","🎶","🎵","🔎","🦠","💥"
    ]
    play_emoji = _rnd.choice(_EMOJI_POOL)
    
    _search_msg = play_emoji
    try:
        sent = await safe_reply(m, _search_msg)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            sent = await safe_reply(m, _search_msg)
        except FloodWait as e2:
            # If still flood wait, wait longer and give up gracefully
            await asyncio.sleep(e2.value)
            return  # Abort silently
        except Exception:
            return  # Abort silently
    except Exception:
        return  # If we can't even send initial message, abort
    
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []
    file = None  # Initialize file variable

    # Check media first (Telegram files) before URL extraction
    if media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    elif url:
        if "playlist" in url:
            await safe_edit(sent, m.lang["playlist_fetch"])
            try:
                tracks = await yt.playlist(
                    config.PLAYLIST_LIMIT, mention, url
                )
            except Exception as e:
                await safe_edit(
                    sent,
                    f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ᴘʟᴀʏʟɪꜱᴛ.\n\n"
                    f"ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪꜱᴛꜱ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴇxᴘᴇʀɪᴇɴᴄɪɴɢ ɪꜱꜱᴜᴇꜱ. "
                    f"ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴘʟᴀʏɪɴɢ ɪɴᴅɪᴠɪᴅᴜᴀʟ ꜱᴏɴɢꜱ ɪɴꜱᴛᴇᴀᴅ.</blockquote>"
                )
                return

            if not tracks:
                await safe_edit(sent, m.lang["playlist_error"])
                return

            file = tracks[0]
            tracks.remove(file)
            file.message_id = sent.id
        else:
            file = await yt.search(url, sent.id)

        if not file:
            await safe_edit(
                sent,
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )
            return

    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        file = await yt.search(query, sent.id)
        if not file:
            await safe_edit(
                sent,
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )
            return
        # Store query for autoplay mood seeding
        await db.set_last_query(chat_id, query)

    if not file:
        return

    file.video = getattr(file, "video", False) or video
    if file.video:
        for track in tracks:
            track.video = True

    # Skip duration check for live streams
    if not file.is_live and file.duration_sec > config.DURATION_LIMIT:
        await safe_edit(
            sent,
            m.lang["play_duration_limit"].format(config.DURATION_LIMIT // 60)
        )
        return

    if await db.is_logger():
        await utils.play_log(m, file.title, file.duration)

    file.user = mention
    if force:
        queue.force_add(chat_id, file)
    else:
        position = queue.add(chat_id, file)  # Returns 0-based index

        if await db.get_call(chat_id):
            # When call is active, position 0 is currently playing
            # So actual waiting position is: position (e.g., 1st waiting = index 1)
            # Display as 1-based for users: index 1 → "1st in queue"
            await safe_edit(
                sent,
                m.lang["play_queued"].format(
                    position,
                    file.url,
                    file.title,
                    file.duration,
                    m.from_user.mention,
                ),
                reply_markup=buttons.play_queued(
                    chat_id, file.id, m.lang["play_now"]
                ),
            )
            # Auto-cleanup queued message after 25 seconds
            if sent:
                async def _auto_del(msg=sent):
                    await asyncio.sleep(25)
                    try:
                        await msg.delete()
                    except Exception:
                        pass
                asyncio.create_task(_auto_del())
            if tracks:
                added = playlist_to_queue(chat_id, tracks)
                try:
                    await app.send_message(
                        chat_id=m.chat.id,
                        text=m.lang["playlist_queued"].format(len(tracks)) + added,
                    )
                except Exception:
                    # Can't send message, continue anyway
                    pass
            
            # ✨ NEW: Start preloading queued tracks in background
            try:
                from BlacMusic import preload
                asyncio.create_task(preload.start_preload(chat_id, count=2))
            except Exception:
                # Non-critical, continue without preload
                pass
            
            return

    if not file.file_path:
        file.file_path = await yt.download(
            file.id,
            is_live=file.is_live,
            video=getattr(file, "video", False),
        )
        if not file.file_path:
            await safe_edit(
                sent,
                "<blockquote>❌ Failed to download media.\n\n"
                "Possible reasons:\n"
                "• YouTube detected bot activity (update cookies)\n"
                "• Video is region-blocked or private\n"
                "• Age-restricted content (requires cookies)</blockquote>"
            )

    try:
        # Pass message_chat_id only if it's different from chat_id (channel play mode)
        await tune.play_media(
            chat_id=chat_id, 
            message=sent, 
            media=file, 
            message_chat_id=message_chat_id if chat_id != message_chat_id else None
        )
        # React with random emoji on successful play
        try:
            _react_emoji = _rnd.choice(_EMOJI_POOL)
            await app.send_reaction(
                chat_id=m.chat.id,
                message_id=m.id,
                emoji=_react_emoji,
                big=True,
            )
        except Exception:
            pass
    except Exception as e:
        error_msg = str(e)
        if "bot" in error_msg.lower() or "sign in" in error_msg.lower():
            await safe_edit(
                sent,
                "<blockquote>❌ YouTube bot detection triggered.\n\n"
                "Solution:\n"
                "• Update YouTube cookies in `BlacMusic/cookies/` folder\n"
                "• Wait a few minutes before trying again\n"
                "• Try /radio for uninterrupted music\n\n"
                f"Support: {config.SUPPORT_CHAT}</blockquote>"
            )
        else:
            await safe_edit(
                sent,
                f"<blockquote>❌ Playback error:\n{error_msg}\n\n"
                f"Support: {config.SUPPORT_CHAT}</blockquote>"
            )
        return
    if not tracks:
        return
    added = playlist_to_queue(chat_id, tracks)
    try:
        await app.send_message(
            chat_id=m.chat.id,
            text=m.lang["playlist_queued"].format(len(tracks)) + added,
        )
    except Exception:
        # Can't send message, but playback is working
        pass