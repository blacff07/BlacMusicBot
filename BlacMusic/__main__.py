import asyncio
import importlib
import sys
import logging

from pyrogram import filters, idle

if sys.platform != "win32":
    try:
        import resource
        _soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        _target = min(65536, _hard)
        if _soft < _target:
            resource.setrlimit(resource.RLIMIT_NOFILE, (_target, _hard))
    except Exception:
        pass

from BlacMusic import app, config, db, logger, stop, tune, userbot, yt
from BlacMusic.plugins import all_modules

# Number of attempts and delay (seconds) used when connecting to MongoDB at
# startup. A single transient network hiccup against the DB shouldn't be
# enough to kill the whole process before it even gets going.
DB_CONNECT_MAX_ATTEMPTS = 5
DB_CONNECT_RETRY_DELAY = 5


async def _connect_db_with_retry() -> None:
    """Connect to MongoDB, retrying a few times with a fixed backoff delay
    before giving up. Raises the last encountered exception if all attempts
    fail."""
    last_exc: Exception | None = None
    for attempt in range(1, DB_CONNECT_MAX_ATTEMPTS + 1):
        try:
            await db.connect()
            return
        except Exception as e:
            last_exc = e
            logger.warning(
                f"MongoDB connection attempt {attempt}/{DB_CONNECT_MAX_ATTEMPTS} "
                f"failed: {e}"
            )
            if attempt < DB_CONNECT_MAX_ATTEMPTS:
                await asyncio.sleep(DB_CONNECT_RETRY_DELAY)
    logger.error("Exhausted all MongoDB connection attempts.")
    raise last_exc


async def main():
    try:
        await _connect_db_with_retry()
        await app.boot()
        await userbot.boot()
        await tune.boot()

        for module in all_modules:
            try:
                importlib.import_module(f"BlacMusic.plugins.{module}")
            except Exception as e:
                logger.error(f"Failed to load plugin {module}: {e}", exc_info=True)
                try:
                    from BlacMusic.helpers._utilities import Utilities
                    await Utilities().send_error(e, f"Plugin load: {module}")
                except Exception:
                    pass
        logger.info(f"🔌 Loaded {len(all_modules)} plugin modules.")

        if config.COOKIES_URL:
            try:
                await yt.save_cookies(config.COOKIES_URL)
            except Exception as e:
                logger.error(f"Failed to download cookies: {e}")

        sudoers = await db.get_sudoers()
        app.sudoers.update(sudoers)
        # Rebuild the filter from the full sudoers set rather than mutating
        # the existing filter in place, so behaviour stays consistent with
        # the rebuild helper used by the /addsudo, /delsudo, /rmsudo plugin.
        app.sudo_filter = filters.user(app.sudoers)
        app.bl_users = filters.user(await db.get_blacklisted())
        logger.info(f"👑 Loaded {len(app.sudoers)} sudo users.")
        logger.info("\n🎵 ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ started successfully! Ready to play.\n")

        import json as _json
        import os as _os
        _ctx_file = ".restart_ctx"
        if _os.path.exists(_ctx_file):
            # Read the restart context and remove the marker file up front.
            # Removing it before the (possibly slow/failing) network call
            # means a second bot instance starting concurrently, or a crash
            # during edit_message_text, can never see and act on the same
            # stale context file twice.
            _ctx = None
            try:
                with open(_ctx_file) as _f:
                    _ctx = _json.load(_f)
            except Exception as _e:
                logger.debug(f"Could not read restart context file: {_e}")
            finally:
                try:
                    _os.remove(_ctx_file)
                except Exception:
                    pass

            if _ctx:
                try:
                    await app.edit_message_text(
                        chat_id=_ctx["chat_id"],
                        message_id=_ctx["message_id"],
                        text="<blockquote>✅ <b>ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.</b> ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ! 🎵</blockquote>",
                    )
                except Exception as _e:
                    logger.debug(f"Could not edit restart message: {_e}")

        await idle()

    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
    finally:
        await stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except SystemExit as e:
        logger.error(f"Bot exited: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logging.shutdown()