# ==============================================================================
# __main__.py - Main Entry Point for ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼
# ==============================================================================

import asyncio
import importlib
import sys
import logging

from pyrogram import idle

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


async def main():
    try:
        await db.connect()
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
        app.sudo_filter.update(sudoers)
        app.bl_users.update(await db.get_blacklisted())
        logger.info(f"👑 Loaded {len(app.sudoers)} sudo users.")
        logger.info("\n🎵 ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ started successfully! Ready to play.\n")

        # Edit restart message if bot was restarted via /restart
        import json as _json, os as _os
        _ctx_file = ".restart_ctx"
        if _os.path.exists(_ctx_file):
            try:
                with open(_ctx_file) as _f:
                    _ctx = _json.load(_f)
                await app.edit_message_text(
                    chat_id=_ctx["chat_id"],
                    message_id=_ctx["message_id"],
                    text="<blockquote>✅ <b>ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.</b> ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ! 🎵</blockquote>",
                )
                _os.remove(_ctx_file)
            except Exception as _e:
                logger.debug(f"Could not edit restart message: {_e}")
                try:
                    _os.remove(_ctx_file)
                except Exception:
                    pass

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