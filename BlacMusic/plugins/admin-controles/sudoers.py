# ==============================================================================
# sudoers.py - Sudo User Management (Owner Only)
# ==============================================================================
# This plugin allows the bot owner to add/remove sudo users.
# Sudo users have elevated permissions and can use admin commands.
#
# Commands:
# - /addsudo <user> - Grant sudo permissions
# - /delsudo <user> - Revoke sudo permissions
# - /rmsudo <user> - Same as /delsudo
#
# Only the bot owner (defined in config) can manage sudo users.
# ==============================================================================

from pyrogram import filters, types

from BlacMusic import app, config, db, lang
from BlacMusic.helpers import utils


async def _rebuild_sudo_filter() -> None:
    """
    Rebuild the sudo filter from scratch based on the current app.sudoers set.

    This replaces the previous reset-then-rebuild pattern (update([]) followed
    by update(app.sudoers)), which briefly left the filter in an inconsistent
    state between the two calls if a message arrived in between. Building a
    fresh filter object and swapping it in as a single assignment avoids that
    race entirely.
    """
    app.sudo_filter = filters.user(app.sudoers)


@app.on_message(filters.command(["addsudo", "delsudo", "rmsudo"]) & app.sudo_filter)
@lang.language()
async def _sudo(_, m: types.Message) -> None:
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    user = await utils.extract_user(m)
    if not user:
        await m.reply_text(m.lang["user_not_found"])
        return

    if m.command[0] == "addsudo":
        if user.id in app.sudoers:
            await m.reply_text(m.lang["sudo_already"].format(user.mention))
            return

        app.sudoers.add(user.id)
        await _rebuild_sudo_filter()
        await db.add_sudo(user.id)
        await m.reply_text(m.lang["sudo_added"].format(user.mention))
    else:
        if user.id not in app.sudoers:
            await m.reply_text(m.lang["sudo_not"].format(user.mention))
            return

        app.sudoers.discard(user.id)
        await _rebuild_sudo_filter()
        await db.del_sudo(user.id)
        await m.reply_text(m.lang["sudo_removed"].format(user.mention))


@app.on_message(filters.command(["listsudo", "sudolist"]) & app.sudo_filter)
@lang.language()
async def _listsudo(_, m: types.Message) -> None:
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    sent = await m.reply_text(m.lang["sudo_fetching"])

    # Always fetch fresh owner info with ID
    try:
        owner_user = await app.get_users(app.owner)
        o_mention = f"{owner_user.mention} ({app.owner})"
    except Exception:
        # Owner account inaccessible/deleted - fall back to the configured
        # username (if set) so the ID is still actionable, rather than a
        # bare, unlinkable number.
        if config.OWNER_USERNAME:
            o_mention = f"@{config.OWNER_USERNAME} ({app.owner})"
        else:
            o_mention = f"({app.owner})"

    txt = m.lang["sudo_owner"].format(o_mention)
    sudoers = await db.get_sudoers()

    if sudoers:
        sudo_list = ""
        for user_id in sudoers:
            try:
                user = await app.get_users(user_id)
                sudo_list += f"\n- {user.mention} ({user_id})"
            except Exception:
                # Deleted account or inaccessible user
                sudo_list += f"\n- Deleted Account ({user_id})"
                continue

        if sudo_list:
            txt += f"<blockquote><u><b>ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ:</b></u>{sudo_list}\n\n</blockquote>"

    await sent.edit_text(txt)