import asyncio
from functools import wraps

from pyrogram import types

from BlacMusic import app, db, lang, logger
from BlacMusic.helpers import buttons


def callback_filter(pattern=None):
    async def decorator(func):
        @wraps(func)
        async def wrapper(client, query: types.CallbackQuery):
            try:
                return await func(client, query)
            except Exception as e:
                await query.answer(f"Error: {str(e)[:100]}", show_alert=False)
                logger.error(f"Error in callback {func.__name__}: {e}", exc_info=True)
        
        if pattern:
            app.on_callback_query(filters=pattern)(wrapper)
        else:
            app.on_callback_query()(wrapper)
        return wrapper
    return decorator


@callback_filter()
@lang.language()
async def _start_callback(_, query: types.CallbackQuery):
    if query.data == "start_back" or query.data == "start":
        _user_link = (
            "<a href='tg://user?id=" + str(query.from_user.id) + "'>"
            + query.from_user.first_name + "</a>"
        )
        _text = query.lang["start_pm"].format(_user_link, app.id, app.name)
        
        await query.edit_message_text(
            text=_text,
            reply_markup=buttons.start_key(query.lang, True),
        )


@callback_filter()
@lang.language()
async def _help_main_callback(_, query: types.CallbackQuery):
    if query.data == "help_main":
        help_text = query.lang["help_menu"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang),
        )


@callback_filter()
@lang.language()
async def _help_playback_callback(_, query: types.CallbackQuery):
    if query.data == "help_playback":
        help_text = query.lang["help_playback"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )


@callback_filter()
@lang.language()
async def _help_controls_callback(_, query: types.CallbackQuery):
    if query.data == "help_controls":
        help_text = query.lang["help_controls"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )


@callback_filter()
@lang.language()
async def _help_admin_callback(_, query: types.CallbackQuery):
    if query.data == "help_admin":
        help_text = query.lang["help_admin"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )


@callback_filter()
@lang.language()
async def _help_blacklist_callback(_, query: types.CallbackQuery):
    if query.data == "help_blacklist":
        help_text = query.lang["help_blacklist"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )


@callback_filter()
@lang.language()
async def _help_filters_callback(_, query: types.CallbackQuery):
    if query.data == "help_filters":
        help_text = query.lang["help_filters"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )


@callback_filter()
@lang.language()
async def _help_tips_callback(_, query: types.CallbackQuery):
    if query.data == "help_tips":
        help_text = query.lang["help_tips"]
        await query.edit_message_text(
            text=help_text,
            reply_markup=buttons.help_markup(query.lang, back=True),
        )


@callback_filter()
@lang.language()
async def _settings_callback(_, query: types.CallbackQuery):
    if query.data.startswith("toggle_playmode"):
        parts = query.data.split()
        if len(parts) < 2:
            await query.answer("Invalid callback data", show_alert=False)
            return
        
        chat_id = int(parts[1])
        admin_only = await db.get_play_mode(chat_id)
        new_mode = not admin_only
        await db.set_play_mode(chat_id, new_mode)
        
        mode_text = "Admin Only" if new_mode else "Everyone"
        await query.answer(f"Play mode changed to: {mode_text}", show_alert=True)
    
    if query.data == "settings":
        chat_id = query.message.chat.id if query.message.chat.type != "private" else query.from_user.id
        admin_only = await db.get_play_mode(chat_id) if query.message.chat.type != "private" else False
        
        settings_text = (
            "⚙️ <b>Group Settings</b>\n\n"
            f"Play Mode: {'Admin Only' if admin_only else 'Everyone'}\n"
        )
        
        await query.edit_message_text(
            text=settings_text,
            reply_markup=buttons.settings_markup(query.lang, admin_only, "en", chat_id),
        )