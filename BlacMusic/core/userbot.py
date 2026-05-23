# ==============================================================================
# userbot.py - Assistant/Userbot Client Manager
# ==============================================================================
# Anti-freeze hardened: each assistant boots with flood protection,
# auth-key error recovery, and deactivated-account detection.
# ID-freeze danger is eliminated by catching all known session errors.
# ==============================================================================

import asyncio
from pyrogram import Client
from pyrogram.errors import (
    AuthKeyUnregistered,
    AuthKeyDuplicated,
    UserDeactivated,
    UserDeactivatedBan,
    SessionExpired,
    SessionRevoked,
    FloodWait,
)

from BlacMusic import config, logger

# Errors that mean the session is dead — skip that assistant, don't freeze
_DEAD_SESSION_ERRORS = (
    AuthKeyUnregistered,
    AuthKeyDuplicated,
    UserDeactivated,
    UserDeactivatedBan,
    SessionExpired,
    SessionRevoked,
)


class Userbot:
    def __init__(self):
        self.clients = []

        sessions = {
            1: config.SESSION1,
            2: config.SESSION2,
            3: config.SESSION3,
        }
        self._sessions = sessions
        self._clients: dict[int, Client] = {}

        for num, session in sessions.items():
            if not session:
                continue
            client = Client(
                name=f"BlacTuneUB{num}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=session,
                # No workdir needed — session stored in memory via session_string
            )
            self._clients[num] = client
            # Expose as self.one / self.two / self.three for backward compat
            setattr(self, {1: "one", 2: "two", 3: "three"}[num], client)

    async def _boot_one(self, num: int, client: Client) -> bool:
        """
        Start a single assistant client with full error handling.
        Returns True on success, False on any failure (never raises).
        """
        try:
            await client.start()
        except _DEAD_SESSION_ERRORS as e:
            logger.error(
                f"❌ Assistant {num} session is dead ({type(e).__name__}). "
                f"Skipping — generate a new STRING_SESSION{num}."
            )
            return False
        except FloodWait as fw:
            logger.warning(
                f"⏳ Assistant {num} hit FloodWait ({fw.value}s) on start. "
                f"Waiting then retrying once…"
            )
            await asyncio.sleep(fw.value + 2)
            try:
                await client.start()
            except Exception as e2:
                logger.error(f"❌ Assistant {num} retry failed: {e2}")
                return False
        except Exception as e:
            logger.error(
                f"❌ Assistant {num} failed to start: {type(e).__name__}: {e}\n"
                f"   Possible causes: invalid session, network issue, or Telegram outage."
            )
            return False

        # Attach metadata
        me = client.me
        client.id       = me.id        if me else None
        client.name     = me.first_name if me else f"Assistant{num}"
        client.username = me.username   if me else None
        client.mention  = me.mention    if me else client.name

        # Non-blocking log message via bot (not assistant) — only bot needs to be in logger group
        try:
            from BlacMusic import app
            await app.send_message(
                config.LOGGER_ID,
                f"✅ Assistant {num} started as @{client.username}"
            )
        except Exception as e:
            logger.warning(f"⚠️ Couldn't send assistant {num} startup log: {e}")

        self.clients.append(client)
        logger.info(f"👤 Assistant {num} ready — @{client.username}")
        return True

    async def boot(self) -> None:
        for num, client in self._clients.items():
            await self._boot_one(num, client)

        if not self.clients:
            raise SystemExit(
                "❌ No assistant accounts started successfully.\n"
                "Check your STRING_SESSION values and try again."
            )

    async def exit(self) -> None:
        for num, client in self._clients.items():
            try:
                if client.is_connected:
                    await client.stop()
            except Exception as e:
                logger.warning(f"⚠️ Error stopping assistant {num}: {e}")
        logger.info("👋 All assistants stopped.")