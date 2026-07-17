# ==============================================================================
# skip.py - Skip Track Command
# ==============================================================================
# This plugin handles skipping to the next track in the queue.
#
# Commands:
# - /skip - Skip current track and play next
# - /next - Same as /skip
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


@app.on_message(filters.command(["skip", "next"]) & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _skip(_, m: types.Message) -> None:
    if await utils.group_only_guard(m):
        return

    await utils.delete_command(m)

    if not await db.get_call(m.chat.id):
        try:
            await m.reply_text(m.lang["not_playing"])
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            pass
        return

    await tune.play_next(m.chat.id)
    try:
        sent_msg = await m.reply_text(m.lang["play_skipped"].format(m.from_user.mention))
    except (ChatSendPlainForbidden, ChatWriteForbidden):
        logger.warning("Cannot send plain text in media-only chat")
        return

    # Auto-delete after 5 seconds
    await asyncio.sleep(5)
    try:
        await sent_msg.delete()
    except Exception:
        pass