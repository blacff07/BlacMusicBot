import asyncio
import random
# ==============================================================================
# start.py - Start Command and Basic Bot Interactions
# ==============================================================================
# This plugin handles:
# - /start command (welcome message for new users)
# - /help command (show help menu)
# - /playmode or /settings command (group settings)
# - New member detection (when bot joins a group)
# ==============================================================================

from pyrogram import enums, errors, filters, types

from BlacMusic import app, config, db, lang
from BlacMusic.helpers import buttons, utils

# Telegram message effect IDs — visible to Premium users only, silently ignored otherwise
_EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

# Valid reaction emojis (Telegram reaction tray)
VALID_REACTIONS = ["👀", "💔", "⚡", "❤️", "🎉"]


@app.on_message(filters.command(["help"]) & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats - shows help menu with image."""
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    if config.START_IMG:
        try:
            await m.reply_photo(
                photo=config.HELP_IMG or config.START_IMG,
                caption=m.lang["help_menu"],
                reply_markup=buttons.help_markup(m.lang),
                quote=True,
            )
            return
        except Exception:
            pass
    await m.reply_text(
        text=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """
    Handle /start command - welcome message for users.

    - In private chat: Shows welcome message with inline buttons
    - In group chat: Shows short welcome message
    - Adds new users to database
    - Sends log to logger group for new users
    """
    # Auto-delete command message in group chats
    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception:
            pass

    # Skip if message from channel or anonymous admin
    if not message.from_user:
        return

    # Check if user is blacklisted
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    # If /start help, show help menu
    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    # Determine if chat is private or group
    private = message.chat.type == enums.ChatType.PRIVATE

    # Choose appropriate welcome message
    if private:
        # Hyperlink sender's name to their Telegram profile
        _user_link = (
            "<a href='tg://user?id=" + str(message.from_user.id) + "'>"
            + message.from_user.first_name + "</a>"
        )
        _text = message.lang["start_pm"].format(
            _user_link,
            app.id,
            app.name,
        )
    else:
        import time as _t
        from BlacMusic import boot as _boot
        def _fmt_uptime(s):
            s = int(s)
            parts = []
            if s >= 86400: parts.append(f"{s//86400}ᴅ")
            if s >= 3600:  parts.append(f"{(s%86400)//3600}ʜ")
            parts.append(f"{(s%3600)//60}ᴍ:{s%60}s")
            return ":".join(parts) if parts else "0s"
        _text = message.lang["start_gp"].format(
            app.username or "",
            app.name,
            _fmt_uptime(_t.time() - _boot),
        )

    key = buttons.start_key(message.lang, private)
    _effect = random.choice(_EFFECT_IDS) if private else None
    if config.START_IMG:
        try:
            _kw = {"message_effect_id": _effect} if _effect else {}
            await message.reply_photo(
                photo=config.START_IMG,
                caption=_text,
                reply_markup=key,
                quote=not private,
                **_kw,
            )
        except Exception:
            try:
                await message.reply_photo(
                    photo=config.START_IMG,
                    caption=_text,
                    reply_markup=key,
                    quote=not private,
                )
            except Exception:
                await message.reply_text(
                    text=_text,
                    reply_markup=key,
                    quote=not private,
                )
    else:
        await message.reply_text(
            text=_text,
            reply_markup=key,
            quote=not private,
        )

    # For private chats — send random reaction, log, and add user to database
    if private:
        # Send a valid reaction from the list
        try:
            reaction_emoji = random.choice(VALID_REACTIONS)
            await app.send_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                emoji=reaction_emoji,
                big=True,
            )
        except Exception:
            pass

        if await db.is_user(message.from_user.id):
            return  # User already exists, no need to add
        # Log new user to logger group
        await utils.send_log(message)
        # Add user to database
        return await db.add_user(message.from_user.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    """
    Handle /playmode or /settings command - show group settings.

    Displays:
    - Play mode (everyone or admin only)
    - Current language
    - Options to change settings
    """
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass

    admin_only = await db.get_play_mode(message.chat.id)
    _language = "en"
    await utils.safe_text(
        message,
        message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    """
    Handle new member events - detect when bot is added to groups.

    - Leaves non-supergroup chats
    - Adds new groups to database
    """
    # Only work in supergroups (not basic groups)
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    # Check each new member
    for member in message.new_chat_members:
        if member.id == app.id:  # Bot itself was added
            if await db.is_chat(message.chat.id):
                return  # Chat already in database
            # Add chat to database (log is sent from new_chat.py with photo)
            await db.add_chat(message.chat.id)