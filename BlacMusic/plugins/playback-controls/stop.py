# ==============================================================================
# stop.py - Stop Playback Command
# ==============================================================================
# This plugin handles stopping voice chat playback and clearing the queue.
#
# Commands:
# - /stop - Stop playback and clear queue
# - /end - Same as /stop
#
# Requirements:
# - User must be admin or authorized user
# - Music must be playing
# ==============================================================================

import asyncio
import logging
from pyrogram import filters, types
from pyrogram.errors import ChatSendPlainForbidden, ChatWriteForbidden

from BlacMusic import tune, app, db, lang
from BlacMusic.helpers import can_manage_vc, utils

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["end", "stop"]) & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _stop(_, m: types.Message) -> None:
    if await utils.group_only_guard(m):
        return

    await utils.delete_command(m)

    if len(m.command) > 1:
        return
    if not await db.get_call(m.chat.id):
        try:
            await m.reply_text(m.lang["not_playing"])
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            logger.warning("Cannot send text in this chat, skipping reply.")
        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
        return

    await tune.stop(m.chat.id)
    try:
        sent_msg = await m.reply_text(m.lang["play_stopped"].format(m.from_user.mention))
    except (ChatSendPlainForbidden, ChatWriteForbidden):
        logger.warning("Cannot send text in this chat, stream stopped silently.")
        return
    except Exception as e:
        logger.error(f"Failed to send stop confirmation: {e}")
        return

    # Auto-delete after 5 seconds
    await asyncio.sleep(5)
    try:
        await sent_msg.delete()
    except Exception:
        pass