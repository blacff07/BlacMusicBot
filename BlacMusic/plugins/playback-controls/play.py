from pyrogram import filters
from pyrogram import types
from pyrogram.errors import FloodWait, MessageIdInvalid, MessageDeleteForbidden, ChatSendPlainForbidden, ChatWriteForbidden

from BlacMusic import app, tune, config, db, lang, queue, tg, yt
from BlacMusic.helpers import buttons, utils
from BlacMusic.helpers._play import checkUB
import asyncio
import logging
import random

logger = logging.getLogger(__name__)


async def safe_edit(message, text, **kwargs):
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
        return False
    except Exception:
        return False


async def safe_reply(message, text, **kwargs):
    try:
        return await message.reply_text(text, **kwargs)
    except (ChatSendPlainForbidden, ChatWriteForbidden):
        logger.warning(f"Cannot send text in chat {message.chat.id}")
        return None
    except Exception as e:
        logger.error(f"Failed to send reply: {e}")
        return None


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text


async def play(
    client,
    message: types.Message,
    force: bool = False,
    url: str = None,
    cplay: bool = False,
    video: bool = False,
) -> None:
    m = message
    chat_id = m.chat.id
    
    if not m.from_user:
        return

    if m.from_user.id in app.bl_users:
        return

    is_channel = m.chat.type == "channel"

    if is_channel and not cplay:
        return

    if not is_channel and cplay:
        return

    if not is_channel and not await db.is_chat(chat_id):
        return await safe_reply(m, "<blockquote>❌ This group isn't activated yet!</blockquote>")

    user_id = m.from_user.id

    play_mode = await db.get_play_mode(chat_id)
    if play_mode and user_id not in app.sudoers:
        admins = await db.get_admins(chat_id)
        if user_id not in admins:
            return await safe_reply(
                m,
                m.lang["play_mode_admin"].format(m.from_user.mention)
            )

    voice_chat_id = await db.get_call(chat_id)

    if not voice_chat_id:
        return await safe_reply(m, "<blockquote>❌ No active voice chat!</blockquote>")

    query = None
    if url:
        query = url
    elif m.command:
        query = " ".join(m.command[1:])
    elif m.reply_to_message:
        if m.reply_to_message.text or m.reply_to_message.caption:
            query = (m.reply_to_message.text or m.reply_to_message.caption)
    
    if not query:
        return await safe_reply(m, m.lang.get("play_no_query", "No query provided"))

    _EMOJI_POOL = ["🌷","🌹","👀","👁","👣","🫶","🫰","🎩","🦋","🕸",
                   "🐾","💫","💥","❄️","🍾","🥂","🧃","🍭","🎗","🎨",
                   "🚀","🎢","💡","💣","🧨","🔮","🧪","🌡","🎉",
                   "🎊","🪄","💌","🪩","🧮","❤️‍🩹","💝","💗","💞","💔",
                   "🖤","💢","💯","🎶","🎵","🔎","🦠","💥"]
    
    play_emoji = random.choice(_EMOJI_POOL)
    
    try:
        sent = await safe_reply(m, play_emoji)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            sent = await safe_reply(m, play_emoji)
        except Exception:
            return
    except Exception:
        return
    
    if not sent:
        return

    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []
    file = None

    if media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    if not file:
        if url and ("youtube.com" in url or "youtu.be" in url):
            file, tracks = await yt.get_file(url, True)
        else:
            file = await yt.search(query)

            if not file:
                await safe_edit(
                    sent,
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )
                return

        await db.set_last_query(chat_id, query)

    if not file:
        return

    file.video = getattr(file, "video", False) or video
    if file.video:
        for track in tracks:
            track.video = True

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
        position = queue.add(chat_id, file)

        if await db.get_call(chat_id):
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
                        chat_id,
                        added
                    )
                except Exception:
                    pass

            return

    await tune.play(m, file, force)
    await sent.delete()


@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"], prefixes=["/", "!", "."]) & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(client, message: types.Message):
    cmd = message.command[0].lower()
    force = "force" in cmd
    video = "v" in cmd
    cplay = "c" in cmd
    url = None

    if message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()

    await play(client, message, force, url, cplay, video)