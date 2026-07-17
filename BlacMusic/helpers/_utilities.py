# ==============================================================================
# _utilities.py - General Utility Functions
# ==============================================================================
# This file contains various helper functions used throughout the bot:
# - Time formatting (ETA, duration)
# - File size formatting (bytes to KB/MB/GB)
# - User extraction from messages (mentions, replies, user IDs)
# - Duration conversion (mm:ss to seconds)
# - Message text extraction
#
# These utilities keep code DRY (Don't Repeat Yourself) across plugins.
# ==============================================================================

import re
from pyrogram import enums, errors, types
from BlacMusic import app, config

GROUP_ONLY_TEXT = (
    "<blockquote>⚠️ <b>ɢʀᴏᴜᴘ ᴏɴʟʏ</b>\n\n"
    "ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛꜱ.\n"
    "ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰɪʀꜱᴛ.</blockquote>"
)


class Utilities:
    def __init__(self):
        pass

    def format_eta(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d} min"
        else:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h}:{m:02d}:{s:02d} h"

    def format_size(self, bytes: int) -> str:
        if bytes >= 1024**3:
            return f"{bytes / 1024 ** 3:.2f} GB"
        elif bytes >= 1024**2:
            return f"{bytes / 1024 ** 2:.2f} MB"
        else:
            return f"{bytes / 1024:.2f} KB"

    def format_duration(self, seconds: int) -> str:
        """Format duration as HH:MM:SS or MM:SS depending on length."""
        if seconds >= 3600:  # 1 hour or more
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:  # Less than 1 hour
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"

    def to_seconds(self, time: str) -> int:
        parts = [int(p) for p in time.strip().split(":")]
        return sum(value * 60**i for i, value in enumerate(reversed(parts)))

    async def group_only_guard(self, m: types.Message) -> bool:
        """
        Reject a command if it's used outside a group chat.

        Shared by every voice-chat playback command (pause, resume, skip,
        shuffle, stop, loop, seek, queue, ...) so the "group only" copy and
        behavior stay identical everywhere instead of being duplicated
        per-file.

        Returns:
            True if the command was blocked (caller should stop processing),
            False if the chat is a group and the command may proceed.
        """
        if m.chat.type == enums.ChatType.PRIVATE:
            await self.safe_text(m, GROUP_ONLY_TEXT)
            return True
        return False

    async def delete_command(self, m: types.Message) -> None:
        """Best-effort auto-delete of the triggering command message."""
        try:
            await m.delete()
        except Exception:
            pass

    async def extract_user(self, msg: types.Message) -> types.User | None:
        if msg.reply_to_message:
            return msg.reply_to_message.from_user

        if msg.entities:
            for e in msg.entities:
                if e.type == enums.MessageEntityType.TEXT_MENTION:
                    return e.user

        if msg.text:
            try:
                if m := re.search(r"@(\w{5,32})", msg.text):
                    return await app.get_users(m.group(0))
                if m := re.search(r"\b\d{6,15}\b", msg.text):
                    return await app.get_users(int(m.group(0)))
            except Exception:
                pass

        return None

    async def play_log(
        self,
        m: types.Message,
        title: str,
        duration: str,
    ) -> None:
        if m.chat.id == app.logger:
            return
        _text = m.lang["play_log"].format(
            app.name,
            m.chat.id,
            m.chat.title,
            m.from_user.id,
            m.from_user.mention,
            m.link,
            title,
            duration,
        )
        await app.send_message(chat_id=app.logger, text=_text)

    async def send_log(self, m: types.Message) -> None:
        """Log new user to logger group when they start the bot in private chat."""
        await app.send_message(
            chat_id=app.logger,
            text=m.lang["log_user"].format(
                m.from_user.id,
                f"@{m.from_user.username}",
                m.from_user.mention,
            ),
        )

    async def send_error(self, error: Exception, context: str = "") -> None:
        """Send runtime errors to logger group as a code block with context."""
        import traceback
        tb = traceback.format_exc()
        if len(tb) > 3000:
            tb = "...truncated..." + "\n" + tb[-3000:]
        text = (
            "<blockquote>⚠️ <b>ʀᴜɴᴛɪᴍᴇ ᴇʀʀᴏʀ</b></blockquote>\n\n"
            f"<b>ᴄᴏɴᴛᴇxᴛ:</b> <code>{context}</code>\n\n"
            f"<pre language='python'>{tb}</pre>"
        )
        try:
            await app.send_message(
                chat_id=app.logger,
                text=text,
            )
        except Exception:
            pass

    async def safe_text(
        self,
        message: types.Message,
        text: str,
        *,
        reply_markup=None,
        quote: bool | None = True,
    ) -> types.Message | None:
        """Send text but gracefully fallback to media-only chats."""
        if not message:
            return None
        try:
            return await message.reply_text(
                text=text,
                reply_markup=reply_markup,
                quote=quote,
            )
        except (errors.ChatSendPlainForbidden, errors.ChatWriteForbidden):
            fallback_photo = getattr(config, "START_IMG", None)
            if not fallback_photo:
                return None
            try:
                return await message.reply_photo(
                    photo=fallback_photo,
                    caption=text,
                    reply_markup=reply_markup,
                    quote=quote,
                )
            except errors.RPCError:
                return None
        except errors.RPCError:
            return None

    async def safe_edit(
        self,
        message: types.Message | None,
        text: str,
        *,
        reply_markup=None,
    ) -> bool:
        """Edit text or caption safely depending on message type."""
        if not message:
            return False
        try:
            if message.text is not None:
                await message.edit_text(text=text, reply_markup=reply_markup)
            else:
                await message.edit_caption(caption=text, reply_markup=reply_markup)
            return True
        except errors.RPCError:
            return False