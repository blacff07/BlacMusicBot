# ==============================================================================
# dir.py - Directory Management
# ==============================================================================
# This file ensures that required directories exist for the bot to store:
# - cache: Temporary cache files
# - downloads: Downloaded audio/video files from Telegram or YouTube
# These directories are created automatically on startup if they don't exist.
# ==============================================================================

from pathlib import Path

from BlacMusic import logger


def ensure_dirs() -> None:
    """
    Create necessary directories if they don't exist.

    Creates:
    - cache/: For temporary cache files
    - downloads/: For downloaded media files
    """
    # List of required directories
    for folder in ("cache", "downloads"):
        # Create directory (and parents if needed)
        Path(folder).mkdir(parents=True, exist_ok=True)
    logger.info("📁 Cache directories updated.")