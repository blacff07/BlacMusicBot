# ==============================================================================
# seek.py - Seek to Timestamp Command
# ==============================================================================
# This plugin allows seeking to a specific timestamp in the current track.
#
# Commands:
# - /seek <seconds> - Seek forward to timestamp
# - /seekback <seconds> - Seek backward to timestamp
#
# Requirements:
# - User must be admin or authorized user
# - Music must be playing (not paused)
# - Track must have a known duration (not live streams)
# - Minimum seek: 10 seconds
# ==============================================================================

from pyrogram import filters, types

from BlacMusic import tune, app, db, lang, queue
from BlacMusic.helpers import can_manage_vc, utils


@app.on_message(filters.command(["seek", "seekback"]) & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _seek(_, m: types.Message) -> None:
    if await utils.group_only_guard(m):
        return

    await utils.delete_command(m)

    if len(m.command) < 2:
        await m.reply_text(m.lang["play_seek_usage"].format(m.command[0]))
        return

    try:
        to_seek = int(m.command[1])
    except ValueError:
        await m.reply_text(m.lang["play_seek_usage"].format(m.command[0]))
        return
    if to_seek < 10:
        await m.reply_text(m.lang["play_seek_min"])
        return

    if not await db.get_call(m.chat.id):
        await m.reply_text(m.lang["not_playing"])
        return

    if not await db.playing(m.chat.id):
        await m.reply_text(m.lang["play_already_paused"])
        return

    media = queue.get_current(m.chat.id)
    if not media:
        # Call is marked active but queue has nothing loaded (edge case, e.g.
        # right after the last track ended and before cleanup finished).
        await m.reply_text(m.lang["not_playing"])
        return
    if not media.duration_sec:
        await m.reply_text(m.lang["play_seek_no_dur"])
        return

    sent = await m.reply_text(m.lang["play_seeking"])

    current_time = getattr(media, 'time', 0)
    if m.command[0] == "seekback":
        stype = m.lang["backward"]
        start_from = max(1, current_time - to_seek)
    else:
        stype = m.lang["forward"]
        start_from = min(current_time + to_seek, media.duration_sec - 5)

    # Use the new seek_stream method
    success = await tune.seek_stream(m.chat.id, int(start_from))

    if success:
        await sent.edit_text(
            m.lang["play_seeked"].format(stype, start_from, m.from_user.mention)
        )
    else:
        await sent.edit_text("❌ Failed to seek!")