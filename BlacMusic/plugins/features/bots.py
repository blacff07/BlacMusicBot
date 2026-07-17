# ==============================================================================
# bots.py - List Bots In Group
# ==============================================================================
# Scans the current group's member list and reports every bot account found,
# along with a running count. Useful for spotting unwanted or duplicate bots.
# ==============================================================================

from html import escape

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ParseMode

from BlacMusic import app


@app.on_message(filters.command("bots") & filters.group)
async def list_bots(client: Client, message: Message) -> None:
    """List all bots in the current group."""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass

    try:
        bot_list = []
        bot_count = 0

        # Send initial message
        status_msg = await message.reply_text("🔍 <b>Scanning for bots...</b>", parse_mode=ParseMode.HTML)

        # Iterate through all members and filter bots
        async for member in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.BOTS):
            bot_count += 1
            # Escape first_name/username since Telegram allows arbitrary text there,
            # which would otherwise be interpreted as HTML markup in the reply.
            bot_name = escape(member.user.first_name or "Unknown")
            bot_username = f"@{escape(member.user.username)}" if member.user.username else "No Username"
            bot_list.append(f"{bot_count}. <a href='tg://user?id={member.user.id}'>{bot_name}</a> - {bot_username}")

        if bot_count == 0:
            await status_msg.edit_text("❌ <b>No bots found in this group.</b>", parse_mode=ParseMode.HTML)
            return

        # Format the response
        response = f"🤖 <b>Bots in {escape(message.chat.title or '')}</b>\n\n"
        response += "<blockquote>" + "\n".join(bot_list) + "</blockquote>"
        response += f"\n\n📊 <b>Total Bots:</b> {bot_count}"

        await status_msg.edit_text(response, disable_web_page_preview=True, parse_mode=ParseMode.HTML)

    except Exception as e:
        await message.reply_text(f"⚠️ <b>Error:</b> {escape(str(e))}", parse_mode=ParseMode.HTML)