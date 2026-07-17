# ==============================================================================
# _dataclass.py - Data Classes for Media and Tracks
# ==============================================================================
# This file defines data structures used throughout the bot:
# - Media: Represents Telegram audio/video files
# - Track: Represents YouTube tracks
#
# These dataclasses make it easy to pass media information between functions
# while maintaining type safety and clear structure.
# ==============================================================================

from dataclasses import dataclass
from typing import Optional


@dataclass
class Media:
    """Represents a Telegram-hosted audio/video file queued for playback."""
    id: str
    duration: str
    duration_sec: int
    file_path: str
    message_id: int
    title: str
    url: str
    time: int = 0
    user: Optional[str] = None
    is_live: bool = False
    video: bool = False


@dataclass
class Track:
    """Represents a YouTube (or other streamed) track queued for playback."""
    id: str
    channel_name: str
    duration: str
    duration_sec: int
    title: str
    url: str
    file_path: Optional[str] = None
    message_id: int = 0
    time: int = 0
    thumbnail: Optional[str] = None
    user: Optional[str] = None
    view_count: Optional[str] = None
    is_live: bool = False
    video: bool = False
