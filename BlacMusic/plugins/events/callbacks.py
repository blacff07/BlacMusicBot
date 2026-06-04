import re
import asyncio
from functools import wraps

from pyrogram import filters, types
from pyrogram.errors import FloodWait, QueryIdInvalid

from BlacMusic import tune, app, config, db, lang, logger, queue, tg, yt
from BlacMusic.helpers import admin_check, buttons, can_manage_vc


def safe_callback(func):
    @wraps(func)
    async def wrapper(client, query: types.CallbackQuery):
        try:
            return await func(client, query)
        except QueryIdInvalid:
            return
        except Exception as e:
            logger.error(f"Error in callback {func.__name__}: {e}", exc_info=True)
            try:
                await query.answer("An error occurred. Please try again.", show_alert=True)
            except Exception:
                pass
    return wrapper


@app.on_callback_query(filters.regex("^start$") & ~app.bl_users)
@lang.language()
@safe_callback
async def _start_callback(_, query: types.CallbackQuery):
    await query.answer()
    
    _text = query.lang["start_pm"].format(query.from_user.first_name, app.name)
    key = buttons.start_key(query.lang, True)
    
    try:
        await query.edit_message_caption(
            caption=_text,
            reply_markup=key,
        )
    except Exception:
        try:
            await query.edit_message_text(
                text=_text,
                reply_markup=key,
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex("^help$") & ~app.bl_users)
@lang.language()
@safe_callback
async def _help_main(_, query: types.CallbackQuery):
    await query.answer()
    
    try:
        await query.edit_message_caption(
            caption=query.lang["help_menu"],
            reply_markup=buttons.help_markup(query.lang),
        )
    except Exception:
        try:
            await query.edit_message_text(
                text=query.lang["help_menu"],
                reply_markup=buttons.help_markup(query.lang),
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex("^help_") & ~app.bl_users)
@lang.language()
@safe_callback
async def _help_categories(_, query: types.CallbackQuery):
    await query.answer()
    
    category = query.data.replace("help_", "")
    
    help_key = f"help_{category}"
    text = query.lang.get(help_key, "Coming soon...")
    
    try:
        await query.edit_message_caption(
            caption=text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )
    except Exception:
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=buttons.help_markup(query.lang, back=True),
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
@safe_callback
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)


@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@safe_callback
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    chat_id = int(args[1])
    control = args[2] if len(args) > 2 else None

    if not control:
        await query.answer()
        return

    if control == "close":
        await query.answer()
        return await query.message.delete()

    if control == "stop":
        await query.answer()
        if not await can_manage_vc(chat_id, query.from_user.id, query.message):
            return
        return await tune.stop_playing(chat_id)

    if control == "pause":
        await query.answer()
        if not await can_manage_vc(chat_id, query.from_user.id, query.message):
            return
        return await tune.pause(chat_id)

    if control == "resume":
        await query.answer()
        if not await can_manage_vc(chat_id, query.from_user.id, query.message):
            return
        return await tune.resume(chat_id)

    if control == "skip":
        await query.answer()
        if not await can_manage_vc(chat_id, query.from_user.id, query.message):
            return
        return await tune.skip(chat_id)

    if control == "replay":
        await query.answer()
        if not await can_manage_vc(chat_id, query.from_user.id, query.message):
            return
        return await tune.replay(chat_id)

    if control in ["seek_back_10", "seek_back_30", "seek_forward_10", "seek_forward_30"]:
        await query.answer()
        if not await can_manage_vc(chat_id, query.from_user.id, query.message):
            return

        if control == "seek_back_10":
            return await tune.seek(chat_id, -10)
        elif control == "seek_back_30":
            return await tune.seek(chat_id, -30)
        elif control == "seek_forward_10":
            return await tune.seek(chat_id, 10)
        elif control == "seek_forward_30":
            return await tune.seek(chat_id, 30)

    await query.answer()


@app.on_callback_query(filters.regex("^settings$") & ~app.bl_users)
@lang.language()
@safe_callback
async def _settings(_, query: types.CallbackQuery):
    await query.answer()

    if query.message.chat.type == "private":
        return

    admin_only = await db.get_play_mode(query.message.chat.id)

    try:
        await query.edit_message_caption(
            caption=query.lang["start_settings"].format(query.message.chat.title),
            reply_markup=buttons.settings_markup(query.lang, admin_only, "en", query.message.chat.id),
        )
    except Exception:
        try:
            await query.edit_message_text(
                text=query.lang["start_settings"].format(query.message.chat.title),
                reply_markup=buttons.settings_markup(query.lang, admin_only, "en", query.message.chat.id),
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex("^playmode") & ~app.bl_users)
@lang.language()
@safe_callback
async def _playmode(_, query: types.CallbackQuery):
    await query.answer()

    if query.message.chat.type == "private":
        return

    if not await admin_check(query):
        await query.answer("You're not an admin.", show_alert=True)
        return

    chat_id = query.message.chat.id
    admin_only = await db.get_play_mode(chat_id)
    await db.set_play_mode(chat_id, not admin_only)

    new_mode = "Admin Only" if not admin_only else "Everyone"
    await query.answer(f"Play mode: {new_mode}", show_alert=True)

    admin_only = not admin_only
    try:
        await query.edit_message_caption(
            caption=query.lang["start_settings"].format(query.message.chat.title),
            reply_markup=buttons.settings_markup(query.lang, admin_only, "en", chat_id),
        )
    except Exception:
        try:
            await query.edit_message_text(
                text=query.lang["start_settings"].format(query.message.chat.title),
                reply_markup=buttons.settings_markup(query.lang, admin_only, "en", chat_id),
            )
        except Exception:
            pass