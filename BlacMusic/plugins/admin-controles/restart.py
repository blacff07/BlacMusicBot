# ==============================================================================
# restart.py - Bot Restart & Logging Commands (Sudo Only)
# ==============================================================================
# This plugin provides administrative commands for bot maintenance.
#
# Commands:
# - /logs - Get log file
# - /logger on/off - Enable/disable database logging
# - /restart - Restart the bot
# - /update - Update bot from git and restart
#
# All commands require sudo user permissions.
# ==============================================================================

import json
import os
import subprocess
import sys
import shutil
import asyncio
from html import escape

from pyrogram import filters, types

from BlacMusic import app, db, lang, stop


def _save_restart_ctx(chat_id: int, message_id: int) -> None:
    """Persist the restart-confirmation message location so __main__.py can
    edit it to 'restarted successfully' once the new process boots."""
    try:
        with open(".restart_ctx", "w") as f:
            json.dump({"chat_id": chat_id, "message_id": message_id}, f)
    except Exception:
        pass


@app.on_message(filters.command(["logs"]) & app.sudo_filter)
@lang.language()
async def _logs(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    sent = await m.reply_text(m.lang["log_fetch"])
    if not os.path.exists("log.txt"):
        return await sent.edit_text(m.lang["log_not_found"])
    
    # Read log file and extract logs from last bot start
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the last occurrence of bot start marker (first log line of startup sequence)
        start_marker = "📁 Cache directories updated."
        last_start_index = content.rfind(start_marker)
        
        if last_start_index != -1:
            # Get logs from the last bot start
            recent_logs = content[last_start_index:]
            
            # Write to temporary file
            temp_log_path = "temp_recent_logs.txt"
            with open(temp_log_path, "w", encoding="utf-8") as f:
                f.write(recent_logs)
            
            await sent.edit_media(
                media=types.InputMediaDocument(
                    media=temp_log_path,
                    caption=m.lang["log_sent"].format(app.name) + " (Last session)",
                )
            )
            
            # Clean up temp file
            try:
                os.remove(temp_log_path)
            except Exception:
                pass
        else:
            # If no start marker found, send the full log file
            await sent.edit_media(
                media=types.InputMediaDocument(
                    media="log.txt",
                    caption=m.lang["log_sent"].format(app.name),
                )
            )
    except Exception as e:
        await sent.edit_text(f"Error reading logs: {escape(str(e))}")


@app.on_message(filters.command(["logger"]) & app.sudo_filter)
@lang.language()
async def _logger(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    if len(m.command) < 2:
        return await m.reply_text(m.lang["logger_usage"].format(m.command[0]))
    if m.command[1] not in ("on", "off"):
        return await m.reply_text(m.lang["logger_usage"].format(m.command[0]))

    if m.command[1] == "on":
        await db.set_logger(True)
        await m.reply_text(m.lang["logger_on"])
    else:
        await db.set_logger(False)
        await m.reply_text(m.lang["logger_off"])


@app.on_message(filters.command(["restart"]) & app.sudo_filter)
@lang.language()
async def _restart(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    sent = await m.reply_text(m.lang["restarting"])

    # Save restart context so we can edit message after boot
    _save_restart_ctx(sent.chat.id, sent.id)

    # Keep downloads to allow instant reuse after restart.
    shutil.rmtree("cache", ignore_errors=True)

    asyncio.create_task(stop())
    await asyncio.sleep(2)

    os.execl(sys.executable, sys.executable, "-m", "BlacMusic")


@app.on_message(filters.command(["update"]) & app.sudo_filter)
@lang.language()
async def _update(_, m: types.Message):
    """
    Update bot from git repository and restart.
    """
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    sent = await m.reply_text(
        "<blockquote><b>🔄 Updating...</b></blockquote>\n\n"
        "<blockquote>Pulling latest changes from repository...</blockquote>"
    )
    
    try:
        # Pull latest changes
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.returncode != 0:
            return await sent.edit_text(
                f"<blockquote><b>❌ Update Failed</b></blockquote>\n\n"
                f"<blockquote>Git error: {escape(result.stderr)}</blockquote>"
            )
        
        output = result.stdout
        
        # Check if there are any changes
        if "Already up to date" in output or "Already up-to-date" in output:
            return await sent.edit_text(
                "<blockquote><b>✅ Already Updated</b></blockquote>\n\n"
                "<blockquote>Bot is already running the latest version.</blockquote>"
            )
        
        # Install/update requirements
        await sent.edit_text(
            "<blockquote><b>📦 Installing Dependencies...</b></blockquote>\n\n"
            "<blockquote>Updating Python packages...</blockquote>"
        )
        
        pip_result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
            capture_output=True,
            text=True
        )
        
        # Clear cache and restart
        await sent.edit_text(
            "<blockquote><b>🔄 Restarting...</b></blockquote>\n\n"
            "<blockquote>Bot will be back online shortly...</blockquote>"
        )
        
        # Keep downloads to allow instant reuse after update.
        shutil.rmtree("cache", ignore_errors=True)

        # Save restart context so we can edit message after boot
        _save_restart_ctx(sent.chat.id, sent.id)

        asyncio.create_task(stop())
        await asyncio.sleep(2)

        os.execl(sys.executable, sys.executable, "-m", "BlacMusic")

    except FileNotFoundError:
        await sent.edit_text(
            "<blockquote><b>❌ Git Not Found</b></blockquote>\n\n"
            "<blockquote>Git is not installed on this system. Use /restart instead.</blockquote>"
        )
    except Exception as e:
        await sent.edit_text(
            f"<blockquote><b>❌ Update Error</b></blockquote>\n\n"
            f"<blockquote>{escape(str(e))}</blockquote>"
        )