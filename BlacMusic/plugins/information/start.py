import asyncio
import random
import json
from pathlib import Path
from pyrogram import enums, errors, filters, types

from BlacMusic import app, config, db, lang, logger
from BlacMusic.helpers import buttons, utils

_EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

VALID_REACTIONS = ["👀", "💔", "⚡", "❤️", "🎉"]


async def handle_restart_message():
    """Edit restart message after bot boots up"""
    restart_ctx_file = Path(".restart_ctx")
    
    if restart_ctx_file.exists():
        try:
            with open(restart_ctx_file, "r") as f:
                ctx = json.load(f)
            
            chat_id = ctx.get("chat_id")
            message_id = ctx.get("message_id")
            
            if chat_id and message_id:
                await app.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="✅ <b>Bot Restarted Successfully!</b>\n\n🚀 Ready to play music."
                )
            
            restart_ctx_file.unlink()
        except Exception as e:
            logger.warning(f"Error handling restart message: {e}")
            try:
                restart_ctx_file.unlink()
            except:
                pass


@app.on_message(filters.command(["help"]) & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats - shows help menu with image."""
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
    """Handle /start command - welcome message for users."""
    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception:
            pass

    if not message.from_user:
        return

    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE

    if private:
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
            if private and _effect:
                try:
                    await app.send_photo(
                        chat_id=message.chat.id,
                        photo=config.START_IMG,
                        caption=_text,
                        reply_markup=key,
                        reply_to_message_id=message.id,
                        message_effect_id=_effect,
                    )
                except TypeError:
                    await message.reply_photo(
                        photo=config.START_IMG,
                        caption=_text,
                        reply_markup=key,
                        quote=not private,
                    )
            else:
                await message.reply_photo(
                    photo=config.START_IMG,
                    caption=_text,
                    reply_markup=key,
                    quote=not private,
                )
        except Exception:
            try:
                if private and _effect:
                    await app.send_message(
                        chat_id=message.chat.id,
                        text=_text,
                        reply_markup=key,
                        reply_to_message_id=message.id,
                        message_effect_id=_effect,
                    )
                else:
                    await message.reply_text(
                        text=_text,
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
        try:
            if private and _effect:
                await app.send_message(
                    chat_id=message.chat.id,
                    text=_text,
                    reply_markup=key,
                    reply_to_message_id=message.id,
                    message_effect_id=_effect,
                )
            else:
                await message.reply_text(
                    text=_text,
                    reply_markup=key,
                    quote=not private,
                )
        except TypeError:
            await message.reply_text(
                text=_text,
                reply_markup=key,
                quote=not private,
            )
        except Exception as e:
            logger.warning(f"Error sending start message: {e}")
            await message.reply_text(
                text=_text,
                reply_markup=key,
                quote=not private,
            )

    if private:
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
            return
        await utils.send_log(message)
        return await db.add_user(message.from_user.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    """Handle /playmode or /settings command - show group settings."""
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
    """Handle new member events - detect when bot is added to groups."""
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await db.add_chat(message.chat.id)