"""
# ==============================================================================
# bot.py - Main Bot Client Manager
# ==============================================================================
# This file defines the main Bot class that handles the Telegram bot client.
# Features:
# - Extends Pyrogram Client with custom bot functionality
# - Manages bot authentication and connection
# - Handles bot startup and shutdown procedures
# - Provides owner, logger, and sudo user filters
# - Stores bot information (ID, name, username, mention)
# ==============================================================================
"""

import pyrogram
from typing import Optional

from BlacMusic import config, logger


class Bot(pyrogram.Client):
    """
    Main bot client class extending Pyrogram's Client.

    This class initializes the Telegram bot with proper configuration
    and provides methods for starting and stopping the bot.

    Attributes:
        owner (int): Owner's user ID
        logger (int): Logger group/channel ID
        bl_users (Filter): Filter for blacklisted users
        sudoers (set): Set of sudo user IDs
        sudo_filter (Filter): Filter for sudo users
        id (int): Bot's user ID (set after boot)
        name (str): Bot's first name (set after boot)
        username (str): Bot's username (set after boot)
        mention (str): Bot's mention tag (set after boot)
    """

    def __init__(self):
        """Initialize the bot client with configuration settings."""
        super().__init__(
            name="BlacMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=pyrogram.types.LinkPreviewOptions(
                is_disabled=True),
        )

        self.owner: int = config.OWNER_ID
        self.logger: int = config.LOGGER_ID
        self.bl_users: pyrogram.filters.Filter = pyrogram.filters.user()
        self.sudoers: set = {self.owner}  # Set of sudo user IDs
        self.sudo_filter: pyrogram.filters.Filter = pyrogram.filters.user(
            self.owner)

        # These will be set after boot()
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.username: Optional[str] = None
        self.mention: Optional[str] = None

    async def boot(self) -> None:
        """
        Start the bot and perform initial setup.

        This method:
        - Starts the Pyrogram client
        - Retrieves bot information
        - Verifies access to logger group
        - Checks bot admin status in logger group

        Raises:
            SystemExit: If bot cannot access logger group or is not an admin.
        """
        await super().start()

        # Set bot information
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        # Verify logger group access
        try:
            await self.send_message(self.logger, f"🤖 {config.BOT_NAME} ꜱᴛᴀʀᴛᴇᴅ")
            member = await self.get_chat_member(self.logger, self.id)
        except Exception as ex:
            raise SystemExit(
                f"❌ ʙᴏᴛ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ʟᴏɢɢᴇʀ ɢʀᴏᴜᴘ: {self.logger}\n"
                f"ʀᴇᴀꜱᴏɴ: {ex}\n"
                f"ᴘʟᴇᴀꜱᴇ ᴇɴꜱᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ʟᴏɢɢᴇʀ ɢʀᴏᴜᴘ."
            )

        # Verify admin status
        if member.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit(
                f"❌ ʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛᴏʀ ɪɴ ʟᴏɢɢᴇʀ ɢʀᴏᴜᴘ: {self.logger}\n"
                f"ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴍᴏᴛᴇ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴀᴅᴍɪɴɪꜱᴛʀᴀᴛᴏʀ ᴡɪᴛʜ ɴᴇᴄᴇꜱꜱᴀʀʏ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ."
            )

        # Set bot slash commands in Telegram menu
        await self._set_commands()
        logger.info(f"🤖 Bot started successfully as @{self.username}")

    async def _set_commands(self) -> None:
        """Register bot commands in Telegram slash menu — all commands by scope."""
        from pyrogram.types import (
            BotCommand,
            BotCommandScopeAllGroupChats,
            BotCommandScopeAllPrivateChats,
            BotCommandScopeChat,
        )
        from config import Config
        _cfg = Config()

        # ── Private DM commands ───────────────────────────────────────────────
        private_commands = [
            BotCommand("start",        "ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ & ꜱʜᴏᴡ ɪɴꜰᴏ"),
            BotCommand("help",         "ꜱʜᴏᴡ ʜᴇʟᴘ ᴍᴇɴᴜ"),
            BotCommand("ping",         "ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ & ʟᴀᴛᴇɴᴄʏ"),
            BotCommand("play",         "ᴘʟᴀʏ ᴀᴜᴅɪᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"),
            BotCommand("vplay",        "ᴘʟᴀʏ ᴠɪᴅᴇᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"),
            BotCommand("cplay",        "ᴘʟᴀʏ ɪɴ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ"),
            BotCommand("radio",        "ʟɪᴠᴇ ʀᴀᴅɪᴏ / ꜱᴛʀᴇᴀᴍ"),
            BotCommand("queue",        "ꜱʜᴏᴡ ᴄᴜʀʀᴇɴᴛ ǫᴜᴇᴜᴇ"),
            BotCommand("autoplay",     "ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ ᴍᴏᴅᴇ"),
            BotCommand("stats",        "ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ"),
        ]

        # ── Group commands ────────────────────────────────────────────────────
        group_commands = [
            BotCommand("play",         "ᴘʟᴀʏ ᴀᴜᴅɪᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"),
            BotCommand("vplay",        "ᴘʟᴀʏ ᴠɪᴅᴇᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"),
            BotCommand("cplay",        "ᴘʟᴀʏ ɪɴ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ"),
            BotCommand("playforce",    "ꜰᴏʀᴄᴇ ᴘʟᴀʏ — ꜱᴋɪᴘ ǫᴜᴇᴜᴇ"),
            BotCommand("radio",        "ʟɪᴠᴇ ʀᴀᴅɪᴏ / ꜱᴛʀᴇᴀᴍ"),
            BotCommand("pause",        "ᴘᴀᴜꜱᴇ ᴘʟᴀʏʙᴀᴄᴋ"),
            BotCommand("resume",       "ʀᴇꜱᴜᴍᴇ ᴘʟᴀʏʙᴀᴄᴋ"),
            BotCommand("skip",         "ꜱᴋɪᴘ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ"),
            BotCommand("stop",         "ꜱᴛᴏᴘ & ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ"),
            BotCommand("seek",         "ꜱᴇᴇᴋ ᴛᴏ ᴛɪᴍᴇꜱᴛᴀᴍᴘ"),
            BotCommand("loop",         "ᴛᴏɢɢʟᴇ ʟᴏᴏᴘ ᴍᴏᴅᴇ"),
            BotCommand("shuffle",      "ꜱʜᴜꜰꜰʟᴇ ǫᴜᴇᴜᴇ"),
            BotCommand("queue",        "ꜱʜᴏᴡ ᴄᴜʀʀᴇɴᴛ ǫᴜᴇᴜᴇ"),
            BotCommand("autoplay",     "ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ"),
            BotCommand("auth",         "ᴀᴜᴛʜᴏʀɪꜱᴇ ᴀ ᴜꜱᴇʀ"),
            BotCommand("unauth",       "ʀᴇᴠᴏᴋᴇ ᴜꜱᴇʀ ᴀᴜᴛʜ"),
            BotCommand("channelplay",  "ʟɪɴᴋ / ᴜɴʟɪɴᴋ ᴄʜᴀɴɴᴇʟ"),
            BotCommand("ping",         "ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ & ʟᴀᴛᴇɴᴄʏ"),
            BotCommand("help",         "ꜱʜᴏᴡ ʜᴇʟᴘ ᴍᴇɴᴜ"),
        ]

        # ── Owner-only commands (set for owner's DM specifically) ─────────────
        owner_commands = private_commands + [
            BotCommand("broadcast",    "ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴄʜᴀᴛꜱ"),
            BotCommand("addsudo",      "ᴀᴅᴅ ꜱᴜᴅᴏ ᴜꜱᴇʀ"),
            BotCommand("rmsudo",       "ʀᴇᴍᴏᴠᴇ ꜱᴜᴅᴏ ᴜꜱᴇʀ"),
            BotCommand("gban",         "ɢʟᴏʙᴀʟ ʙᴀɴ ᴀ ᴜꜱᴇʀ"),
            BotCommand("ungban",       "ʟɪꜰᴛ ɢʟᴏʙᴀʟ ʙᴀɴ"),
            BotCommand("maintenance",  "ᴛᴏɢɢʟᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ"),
            BotCommand("restart",      "ʀᴇꜱᴛᴀʀᴛ ʙᴏᴛ"),
            BotCommand("logs",         "ɢᴇᴛ ʟᴏɢ ꜰɪʟᴇ"),
            BotCommand("eval",         "ᴇxᴇᴄᴜᴛᴇ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ"),
            BotCommand("active",       "ꜱʜᴏᴡ ᴀᴄᴛɪᴠᴇ ᴠᴄ ᴄʜᴀᴛꜱ"),
        ]

        try:
            await self.set_bot_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
            await self.set_bot_commands(group_commands,   scope=BotCommandScopeAllGroupChats())
            # Set extended owner commands in owner's DM
            try:
                await self.set_bot_commands(
                    owner_commands,
                    scope=BotCommandScopeChat(chat_id=_cfg.OWNER_ID)
                )
            except Exception:
                pass
            logger.info("✅ Bot slash commands registered.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to set bot commands: {e}")

    async def exit(self) -> None:
        """
        Gracefully stop the bot client.

        This method stops the Pyrogram client and logs the shutdown.
        """
        await super().stop()
        logger.info("🤖 Bot client stopped.")