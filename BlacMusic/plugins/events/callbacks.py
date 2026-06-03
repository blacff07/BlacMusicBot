import asyncio
from functools import wraps

from pyrogram import types

from BlacMusic import app, db, lang


def callback_filter(pattern=None):
    async def decorator(func):
        @wraps(func)
        async def wrapper(client, query: types.CallbackQuery):
            try:
                return await func(client, query)
            except Exception as e:
                await query.answer(f"Error: {str(e)[:100]}", show_alert=False)
                from BlacMusic import logger
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
    if query.data == "start_back":
        _user_link = (
            "<a href='tg://user?id=" + str(query.from_user.id) + "'>"
            + query.from_user.first_name + "</a>"
        )
        _text = query.lang["start_pm"].format(_user_link, app.id, app.name)
        
        from BlacMusic.helpers import buttons
        await query.edit_message_text(
            text=_text,
            reply_markup=buttons.start_key(query.lang, True),
        )


@callback_filter()
@lang.language()
async def _help_callback(_, query: types.CallbackQuery):
    if query.data == "help_back":
        _user_link = (
            "<a href='tg://user?id=" + str(query.from_user.id) + "'>"
            + query.from_user.first_name + "</a>"
        )
        _text = query.lang["start_pm"].format(_user_link, app.id, app.name)
        
        from BlacMusic.helpers import buttons
        await query.edit_message_text(
            text=_text,
            reply_markup=buttons.start_key(query.lang, True),
        )


@callback_filter()
@lang.language()
async def _settings_callback(_, query: types.CallbackQuery):
    if query.data.startswith("set_"):
        parts = query.data.split("_")
        
        if len(parts) < 3:
            await query.answer("Invalid callback data", show_alert=False)
            return
        
        setting_type = parts[1]
        setting_value = "_".join(parts[2:])
        
        if setting_type == "playmode":
            chat_id = query.message.chat.id
            if setting_value == "everyone":
                await db.set_play_mode(chat_id, False)
                await query.answer("Play mode: Everyone", show_alert=True)
            elif setting_value == "admin":
                await db.set_play_mode(chat_id, True)
                await query.answer("Play mode: Admin only", show_alert=True)
        
        await query.edit_message_text(
            text=query.message.text,
            reply_markup=query.message.reply_markup,
        )