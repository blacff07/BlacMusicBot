# ==============================================================================
# youtube.py - YouTube Download & Search Handler
# ==============================================================================
# This file handles all YouTube-related operations:
# - Searching for videos/audio using py-yt-search (proper library)
# - Downloading YouTube content using yt-dlp
# - Managing YouTube cookies for age-restricted content
# - Caching search results for better performance
# - Validating YouTube URLs
# ==============================================================================

import os
import re
import glob
import time
import yt_dlp
import random
import asyncio
import aiohttp
from dataclasses import replace
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
from py_yt import Playlist, VideosSearch
from BlacMusic import config, logger
from BlacMusic.helpers import Track, utils


class YouTube:
    def __init__(self):
        """Initialize YouTube handler with configuration and caching."""
        self.base = "https://www.youtube.com/watch?v="  # Base YouTube URL
        self.cookies = []  # List of available cookie files
        self.checked = False  # Whether cookies directory has been checked
        self.warned = False  # Whether missing cookies warning has been shown

        # Regular expression to match YouTube URLs (videos, shorts, live, playlists)
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

        # Cache search results to reduce API calls (10 minute TTL)
        self.search_cache = {}  # {"query_video": (result, timestamp)}
        self.cache_time = {}  # Deprecated, using tuple in search_cache instead

        # **PERFORMANCE FIX**: Limit concurrent downloads to prevent bandwidth saturation
        # With 15-20 groups, unlimited concurrent downloads cause 320+ connections
        self._download_semaphore = asyncio.Semaphore(5)  # Max 5 simultaneous downloads
        self._max_video_height = getattr(config, "VIDEO_MAX_HEIGHT", 1080)

    def _locate_download_file(self, video_id: str, video: bool = False) -> Optional[str]:
        """Locate any completed download file for a video id."""
        pattern = f"downloads/{video_id}*"
        candidates = sorted([
            path for path in glob.glob(pattern)
            if not path.endswith((".part", ".ytdl", ".info.json", ".temp"))
        ])

        video_exts = {".mp4", ".mkv", ".webm", ".mov"}
        audio_exts = {".m4a", ".webm", ".opus", ".mp3", ".ogg", ".wav", ".flac"}

        if video:
            for path in candidates:
                if os.path.isdir(path):
                    continue
                if Path(path).suffix.lower() in video_exts:
                    return path
        else:
            for path in candidates:
                if os.path.isdir(path):
                    continue
                if Path(path).suffix.lower() in audio_exts:
                    return path

        for path in candidates:
            if os.path.isdir(path):
                continue
            return path
        return None

    def get_cookies(self):
        if not self.checked:
            if os.path.exists("BlacMusic/cookies"):
                for file in os.listdir("BlacMusic/cookies"):
                    if file.endswith(".txt"):
                        self.cookies.append(file)
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return f"BlacMusic/cookies/{random.choice(self.cookies)}"

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("🍪 Saving cookies from urls...")
        saved_count = 0
        for url in urls:
            try:
                path = f"BlacMusic/cookies/cookie{random.randint(10000, 99999)}.txt"
                link = url.replace("me/", "me/raw/")
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as resp:
                        if resp.status != 200:
                            logger.error(f"❌ Cookie download failed: HTTP {resp.status} from {url}")
                            continue
                        content = await resp.read()
                        if not content or len(content) < 50:
                            logger.error(f"❌ Cookie file empty or invalid from {url}")
                            continue
                        with open(path, "wb") as fw:
                            fw.write(content)
                        if os.path.exists(path) and os.path.getsize(path) > 0:
                            saved_count += 1
                            cookie_filename = os.path.basename(path)
                            if cookie_filename not in self.cookies:
                                self.cookies.append(cookie_filename)
                            logger.info(f"✅ Saved: {cookie_filename} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"❌ Cookie download error from {url}: {e}")
        
        self.checked = True
        
        if saved_count > 0:
            logger.info(f"✅ Cookies saved. ({saved_count} file(s))")
        else:
            logger.error("❌ No cookies saved! Check COOKIE_URL in .env. YouTube downloads will fail!")

    def is_network_stream(self, url: str) -> bool:
        """Return True for direct network streams (m3u8, icecast, etc.)."""
        url = url.lower()
        return (
            url.endswith('.m3u8') or
            url.endswith('.m3u') or
            '/stream' in url or
            url.startswith('rtmp://') or
            url.startswith('rtsp://') or
            url.startswith('rtp://') or
            url.startswith('udp://') or
            '.m3u8?' in url or
            'icecast' in url or
            'shoutcast' in url
        )

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def url(self, message_1: types.Message) -> Union[str, None]:
        messages = [message_1]
        link = None
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            text = message.text or message.caption or ""

            if message.entities:
                for entity in message.entities:
                    if entity.type == enums.MessageEntityType.URL:
                        link = text[entity.offset: entity.offset +
                                    entity.length]
                        break

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == enums.MessageEntityType.TEXT_LINK:
                        link = entity.url
                        break

        if link:
            return link.split("&si")[0].split("?si")[0]
        return None

    async def search(self, query: str, m_id: int) -> Track | None:
        """
        Search for a YouTube video by query string using py-yt-search.
        FIXED: Uses proper py-yt-search library instead of youtubesearchpython.
        """
        # Check cache first (10-minute TTL)
        cache_key = query
        current_time = asyncio.get_running_loop().time()

        if cache_key in self.search_cache:
            cached_result, cache_timestamp = self.search_cache[cache_key]
            if current_time - cache_timestamp < 600:  # 10 minutes
                # Return a fresh copy so downstream mutations don't leak back into cache
                fresh = replace(cached_result)
                fresh.message_id = m_id
                fresh.file_path = None
                fresh.user = None
                fresh.time = 0
                fresh.video = False
                return fresh

        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
        except Exception as e:
            logger.warning(f"⚠️ YouTube search failed for '{query}': {e}")
            return None

        if results and results.get("result"):
            data = results["result"][0]
            duration = data.get("duration")
            is_live = duration is None or duration == "LIVE"

            track = Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=duration if not is_live else "LIVE",
                duration_sec=0 if is_live else utils.to_seconds(duration),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get(
                    "thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                is_live=is_live,
            )

            # Cache the result
            self.search_cache[cache_key] = (track, current_time)
            # Limit cache size to 100 entries
            if len(self.search_cache) > 100:
                oldest_key = min(self.search_cache.keys(),
                                 key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]

            return replace(track)
        return None

    async def playlist(self, limit: int, user: str, url: str) -> list[Track]:
        """Fetch playlist videos using py-yt-search."""
        try:
            plist = await Playlist.get(url)
            tracks = []

            if not plist or "videos" not in plist or not plist["videos"]:
                return []

            for video in plist["videos"][:limit]:
                try:
                    duration = video.get("duration")
                    is_live = duration is None or duration == "LIVE"

                    track = Track(
                        id=video.get("id"),
                        channel_name=video.get("channel", {}).get("name"),
                        duration=duration if not is_live else "LIVE",
                        duration_sec=0 if is_live else utils.to_seconds(duration),
                        title=video.get("title")[:25],
                        thumbnail=video.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                        url=video.get("link"),
                        view_count=video.get("viewCount", {}).get("short"),
                        user=user,
                        is_live=is_live,
                    )
                    tracks.append(track)
                except Exception as ex:
                    logger.warning(f"Skipping video in playlist: {ex}")
                    continue

            return tracks
        except Exception as e:
            logger.error(f"Playlist fetch error: {e}")
            return []

    async def download(
        self,
        url: str,
        is_live: bool = False,
        video: bool = False,
    ) -> Optional[str]:
        """Download a video/audio file from YouTube or stream URL."""
        video_id = None
        if url.startswith("http"):
            match = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)", url)
            if match:
                video_id = match.group(1)
        
        if not video_id:
            video_id = url

        if self.is_network_stream(url):
            def _extract_url():
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "format": "best",
                    "socket_timeout": 30,
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            return info.get("url") or url
                except yt_dlp.utils.ExtractorError as ex:
                    if "not available" in str(ex).lower():
                        logger.error("❌ Stream not available: May be offline or region-blocked.")
                    else:
                        logger.error("❌ Stream extraction failed: %s", ex)
                        return None
                except Exception as ex:
                    logger.error("Unexpected error during live stream extraction: %s", ex)
                    return None

            try:
                stream_url = await asyncio.wait_for(asyncio.to_thread(_extract_url), timeout=35)
            except asyncio.TimeoutError:
                logger.error("Live stream URL extraction timed out for %s", video_id)
                return None

            return stream_url

        filename_pattern = f"downloads/{video_id}"
        
        existing_files = [
            f for f in glob.glob(f"{filename_pattern}.*")
            if not f.endswith('.part')
        ]
        if video:
            video_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}
            ]
            if video_candidates:
                return video_candidates[0]
        else:
            audio_candidates = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".m4a", ".webm", ".opus", ".mp3", ".ogg", ".wav", ".flac"}
            ]
            if audio_candidates:
                return audio_candidates[0]

            container_fallbacks = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".mov"}
            ]
            if container_fallbacks:
                return container_fallbacks[0]
        
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            try:
                downloads_dir.mkdir(parents=True, exist_ok=True)
                logger.info("📁 Created downloads directory")
            except Exception as e:
                logger.error(f"❌ Cannot create downloads directory: {e}")
                return None

        async with self._download_semaphore:
            cookie = self.get_cookies()
            base_opts = {
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "quiet": True,
                "noplaylist": True,
                "geo_bypass": True,
                "no_warnings": True,
                "overwrites": False,
                "nocheckcertificate": True,
                "continuedl": True,
                "noprogress": True,
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 524288,
                "socket_timeout": 30,
                "retries": 2,
                "fragment_retries": 2,
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            if video:
                height_filter = ""
                if self._max_video_height and self._max_video_height > 0:
                    height_filter = f"[height<={self._max_video_height}]"
                format_chain = (
                    f"bestvideo[ext=mp4]{height_filter}+bestaudio[ext=m4a]/"
                    f"bestvideo{height_filter}+bestaudio/"
                    "bestvideo+bestaudio/best"
                )
                ydl_opts = {
                    **base_opts,
                    "format": format_chain,
                    "merge_output_format": "mp4",
                    "postprocessors": [
                        {
                            "key": "FFmpegVideoConvertor",
                            "preferedformat": "mp4",
                        }
                    ],
                }
            else:
                ydl_opts = {
                    **base_opts,
                    "format": "bestaudio[ext=m4a]/bestaudio[acodec=opus]/bestaudio/best",
                    "postprocessors": [],
                }

            ydl_opts_cookie = {
                **ydl_opts,
                "cookiefile": cookie,
            }

            def _download(ydl_runtime_opts):
                ydl_instance = None
                try:
                    ydl_instance = yt_dlp.YoutubeDL(ydl_runtime_opts)
                    info = ydl_instance.extract_info(url, download=True)
                    if not info:
                        logger.error(f"❌ Failed to extract info for {video_id}")
                        return None
                    
                    time.sleep(0.5)
                    located = self._locate_download_file(video_id, video=video)
                    if located:
                        return located
                    logger.error(f"❌ Download completed but file not found for: {video_id}")
                    return None
                except yt_dlp.utils.ExtractorError as ex:
                    error_msg = str(ex)
                    if "not available" in error_msg.lower():
                        logger.error("❌ Video not available: May be region-blocked or private.")
                    elif "age" in error_msg.lower():
                        logger.error("❌ Age-restricted video: Cookies required.")
                    else:
                        logger.error("❌ YouTube extraction failed: %s", ex)
                    return None
                except yt_dlp.utils.DownloadError as ex:
                    error_msg = str(ex)
                    recovered = self._locate_download_file(video_id, video=video)
                    if "unable to rename file" in error_msg.lower() and recovered:
                        logger.warning(f"⚠️ Using recovered file for {video_id}")
                        return recovered
                    if "416" in error_msg or "Requested range not satisfiable" in error_msg:
                        logger.warning(f"⚠️ Range error for {video_id}, skipping")
                    else:
                        if "ffmpeg exited with code 255" not in str(ex):
                            logger.warning(f"⚠️ Download error for {video_id}: {ex}")
                        if recovered:
                            logger.warning(f"⚠️ Using recovered file for {video_id} despite error")
                            return recovered
                    return None
                except Exception as ex:
                    logger.warning(f"⚠️ Unexpected download error for {video_id}: {ex}")
                    return None
                finally:
                    if ydl_instance:
                        try:
                            ydl_instance.close()
                        except Exception:
                            pass

            return await asyncio.to_thread(_download, ydl_opts_cookie)