"""
˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ - Advanced Telegram Music Bot

Main initialization module. Sets up logging, configuration,
and all core components required for the bot to function.
"""

import asyncio
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import List

from pyrogram.errors import ChannelInvalid

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)

logger = logging.getLogger("BlacMusic")


def _asyncio_exception_handler(loop: asyncio.AbstractEventLoop, context: dict) -> None:
    exc = context.get("exception")
    if isinstance(exc, ChannelInvalid):
        logger.warning("Ignoring CHANNEL_INVALID update (channel probably removed).")
        return
    loop.default_exception_handler(context)


asyncio.get_event_loop().set_exception_handler(_asyncio_exception_handler)

__version__ = "3.0.1"

from config import Config
config = Config()
config.check()

tasks: List = []
boot: float = time.time()

from BlacMusic.core.bot import Bot
app = Bot()

from BlacMusic.core.dir import ensure_dirs
ensure_dirs()

from BlacMusic.core.userbot import Userbot
userbot = Userbot()

from BlacMusic.core.mongo import MongoDB
db = MongoDB()

from BlacMusic.core.lang import Language
lang = Language()

from BlacMusic.core.telegram import Telegram
from BlacMusic.core.youtube import YouTube
tg = Telegram()
yt = YouTube()

from BlacMusic.core.preload import PreloadManager
preload = PreloadManager()

from BlacMusic.helpers import Queue
queue = Queue()



async def stop() -> None:
    logger.info("🛑 Stopping bot...")
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
    await app.exit()
    await userbot.exit()
    await db.close()
    logger.info("✅ Bot stopped successfully.\n")

# Imported last to avoid circular import with _autoplay
from BlacMusic.core.calls import TgCall
tune = TgCall()