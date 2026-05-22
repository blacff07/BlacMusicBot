# ==============================================================================
# config.py - Bot Configuration Manager
# ==============================================================================
# All settings load from environment variables (.env file).
# Required variables are validated on startup.
# Optional variables have sensible defaults.
# Watermark/branding is fully configurable via env.
# ==============================================================================

from os import getenv
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:

    def __init__(self):

        # ── TELEGRAM CREDENTIALS ──────────────────────────────────────────────
        self.API_ID: int = int(getenv("API_ID", "0"))
        self.API_HASH: str = getenv("API_HASH", "")
        self.BOT_TOKEN: str = getenv("BOT_TOKEN", "")
        self.LOGGER_ID: int = int(getenv("LOGGER_ID", "0"))
        self.OWNER_ID: int = int(getenv("OWNER_ID", "0"))

        # ── DATABASE ──────────────────────────────────────────────────────────
        self.MONGO_URL: str = getenv("MONGO_DB_URI", "")

        # ── ASSISTANT SESSIONS (up to 3) ──────────────────────────────────────
        self.SESSION1: str = getenv("STRING_SESSION", "")
        self.SESSION2: str = getenv("STRING_SESSION2", "")
        self.SESSION3: str = getenv("STRING_SESSION3", "")

        # ── BRANDING (fully configurable, safe defaults) ──────────────────────
        self.BOT_NAME: str    = getenv("BOT_NAME",    "˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼")
        self.BOT_ABOUT: str   = getenv("BOT_ABOUT",   "ꜱᴛᴜᴅɪᴏ-ǫᴜᴀʟɪᴛʏ ᴍᴜꜱɪᴄ ꜱᴛʀᴇᴀᴍɪɴɢ ꜰᴏʀ ᴛᴇʟᴇɢʀᴀᴍ")
        self.SOURCE_URL: str  = getenv("SOURCE_URL",  "https://github.com/blacmusic/BlacMusicBot")

        # ── SUPPORT LINKS ─────────────────────────────────────────────────────
        self.SUPPORT_CHANNEL: str = getenv("SUPPORT_CHANNEL", "https://t.me/blacmusic")
        self.SUPPORT_CHAT: str    = getenv("SUPPORT_CHAT",    "https://t.me/blacmusicchat")

        # ── IMAGES (all overridable) ──────────────────────────────────────────
        self.DEFAULT_THUMB: str = getenv("DEFAULT_THUMB", "https://files.catbox.moe/kgrs8f.png")
        self.PING_IMG: str      = getenv("PING_IMG",      "https://files.catbox.moe/djilyq.png")
        self.START_IMG: str     = getenv("START_IMG",     "https://files.catbox.moe/7jihmf.png")
        self.RADIO_IMG: str     = getenv("RADIO_IMG",     "https://files.catbox.moe/t03fzk.png")

        # ── LIMITS ────────────────────────────────────────────────────────────
        self.DURATION_LIMIT: int  = int(getenv("DURATION_LIMIT",  "300")) * 60
        self.QUEUE_LIMIT: int     = int(getenv("QUEUE_LIMIT",     "30"))
        self.PLAYLIST_LIMIT: int  = int(getenv("PLAYLIST_LIMIT",  "20"))

        # ── FEATURE FLAGS ─────────────────────────────────────────────────────
        self.AUTO_END: bool        = self._bool(getenv("AUTO_END",    "False"))
        self.AUTO_LEAVE: bool      = self._bool(getenv("AUTO_LEAVE",  "False"))
        self.THUMB_GEN: bool       = self._bool(getenv("THUMB_GEN",   "True"))
        self.VIDEO_PLAY: bool      = self._bool(getenv("VIDEO_PLAY",  "False"))
        self.VIDEO_MAX_HEIGHT: int = self._clamp_height()

        # ── YOUTUBE COOKIES ───────────────────────────────────────────────────
        self.COOKIES_URL: List[str] = self._parse_cookies()

        # ── MODERATION ────────────────────────────────────────────────────────
        self.EXCLUDED_CHATS: List[int]    = self._parse_excluded_chats()
        self.EXCLUDED_USERNAMES: List[str] = getenv("EXCLUDED_USERNAMES", "").split()

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _bool(v: str) -> bool:
        return v.lower() in ("true", "1", "yes", "y", "on")

    def _clamp_height(self) -> int:
        try:
            h = int(getenv("VIDEO_MAX_HEIGHT", "1080"))
        except (TypeError, ValueError):
            return 1080
        if h <= 0:
            return 0
        return max(480, min(h, 2160))

    def _parse_excluded_chats(self) -> List[int]:
        raw = getenv("EXCLUDED_CHATS", "")
        ids = []
        for part in raw.split(","):
            part = part.strip()
            if part.lstrip("-").isdigit():
                ids.append(int(part))
        return ids

    def _parse_cookies(self) -> List[str]:
        raw = getenv("COOKIE_URL", "")
        if not raw:
            return []
        valid = ["batbin.me", "pastebin.com", "paste.ee", "rentry.co"]
        return [u.strip() for u in raw.split() if u.strip() and any(s in u for s in valid)]

    def check(self) -> None:
        required = {
            "API_ID":         self.API_ID,
            "API_HASH":       self.API_HASH,
            "BOT_TOKEN":      self.BOT_TOKEN,
            "MONGO_DB_URI":   self.MONGO_URL,
            "LOGGER_ID":      self.LOGGER_ID,
            "OWNER_ID":       self.OWNER_ID,
            "STRING_SESSION": self.SESSION1,
        }
        missing = [k for k, v in required.items() if not v or (isinstance(v, int) and v == 0)]
        if missing:
            raise SystemExit(
                f"❌ Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file."
            )