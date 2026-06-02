# ==============================================================================
# youtube.py - YouTube Download & Search Handler
# ==============================================================================
# This file handles all YouTube-related operations:
# - Searching for videos/audio using yt-dlp (fixes youtubesearchpython issues)
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
                            # Add the new cookie file to the list immediately
                            cookie_filename = os.path.basename(path)
                            if cookie_filename not in self.cookies:
                                self.cookies.append(cookie_filename)
                            logger.info(f"✅ Saved: {cookie_filename} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"❌ Cookie download error from {url}: {e}")
        
        # Force refresh of cookie list after download
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
        Search for a YouTube video by query string using yt-dlp.
        
        FIXED: Uses yt-dlp's built-in search instead of youtubesearchpython
        to avoid the 'proxies' parameter error in newer aiohttp versions.
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

        def _search_yt(search_query: str) -> dict | None:
            """Synchronous YouTube search using yt-dlp."""
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "default_search": "ytsearch1",  # Search YouTube and get 1 result
                    "extract_flat": True,  # Don't download, just extract metadata
                    "socket_timeout": 15,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search_query, download=False)
                    
                    if info and "entries" in info and len(info["entries"]) > 0:
                        video = info["entries"][0]
                        return {
                            "id": video.get("id"),
                            "title": video.get("title"),
                            "url": video.get("url"),
                            "duration": video.get("duration"),
                            "thumbnail": video.get("thumbnail"),
                            "channel": video.get("uploader"),
                            "view_count": video.get("view_count"),
                        }
            except Exception as e:
                logger.warning(f"⚠️ yt-dlp search error for '{search_query}': {e}")
                return None
            
            return None

        try:
            # Run search in thread pool to avoid blocking
            result = await asyncio.to_thread(_search_yt, query)
            
            if not result:
                logger.warning(f"⚠️ No results found for '{query}'")
                return None

            # Parse duration
            duration = result.get("duration")
            is_live = duration is None or duration == 0

            track = Track(
                id=result.get("id"),
                channel_name=result.get("channel"),
                duration=utils.sec_to_str(duration) if duration else "LIVE",
                duration_sec=duration if duration else 0,
                message_id=m_id,
                title=result.get("title", "Unknown")[:25],
                thumbnail=result.get("thumbnail", ""),
                url=result.get("url", ""),
                view_count=str(result.get("view_count", 0)) if result.get("view_count") else "0",
                is_live=is_live,
            )

            # Cache the result
            self.search_cache[cache_key] = (track, current_time)
            # Limit cache size to 100 entries
            if len(self.search_cache) > 100:
                oldest_key = min(self.search_cache.keys(),
                                 key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]

            logger.info(f"✅ Found: {track.title} by {track.channel_name}")
            return replace(track)
            
        except Exception as e:
            logger.warning(f"⚠️ Search failed for '{query}': {e}")
            return None

    async def playlist(self, limit: int, user: str, url: str) -> list[Track]:
        """Fetch playlist videos using yt-dlp."""
        def _fetch_playlist(playlist_url: str, video_limit: int) -> list[dict]:
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": True,
                    "playlistend": video_limit,
                    "socket_timeout": 15,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(playlist_url, download=False)
                    
                    if info and "entries" in info:
                        return info["entries"]
            except Exception as e:
                logger.error(f"Playlist fetch error: {e}")
            
            return []

        try:
            videos = await asyncio.to_thread(_fetch_playlist, url, limit)
            tracks = []

            for video in videos:
                try:
                    if not video or "id" not in video:
                        continue
                    
                    duration = video.get("duration")
                    is_live = duration is None or duration == 0

                    track = Track(
                        id=video.get("id"),
                        channel_name=video.get("uploader"),
                        duration=utils.sec_to_str(duration) if duration else "LIVE",
                        duration_sec=duration if duration else 0,
                        title=video.get("title", "Unknown")[:25],
                        thumbnail=video.get("thumbnail", ""),
                        url=video.get("url", ""),
                        view_count=str(video.get("view_count", 0)) if video.get("view_count") else "0",
                        user=user,
                        is_live=is_live,
                    )
                    tracks.append(track)
                except Exception as ex:
                    logger.warning(f"Skipping video in playlist: {ex}")
                    continue

            return tracks
        except Exception as e:
            logger.error(f"Playlist processing error: {e}")
            return []

    async def download(
        self,
        url: str,
        is_live: bool = False,
        video: bool = False,
    ) -> Optional[str]:
        """
        Download a video/audio file from YouTube or stream URL.
        
        Args:
            url: YouTube URL or direct stream URL
            is_live: True if it's a live stream
            video: True to download video, False for audio only
            
        Returns:
            Path to the downloaded file, or None if failed
        """
        video_id = None
        if url.startswith("http"):
            # Extract video ID from YouTube URL
            match = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)", url)
            if match:
                video_id = match.group(1)
        
        if not video_id:
            video_id = url  # Assume it's already a video ID

        if self.is_network_stream(url):
            # Handle m3u8 or direct streams
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
                        logger.error(
                            "❌ Stream not available: May be offline or region-blocked."
                        )
                    else:
                        logger.error("❌ Stream extraction failed: %s", ex)
                        return None
                except Exception as ex:
                    logger.error(
                        "Unexpected error during live stream extraction: %s", ex)
                    return None

            try:
                stream_url = await asyncio.wait_for(asyncio.to_thread(_extract_url), timeout=35)
            except asyncio.TimeoutError:
                logger.error("Live stream URL extraction timed out for %s", video_id)
                return None

            return stream_url

        # Download audio/video file
        filename_pattern = f"downloads/{video_id}"
        
        # Check if any completed file for this video_id already exists
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

            # VPS caches are often dominated by mp4 due to prior /vplay usage.
            # Reuse those files for /play (audio-only mode) to avoid redundant redownloads.
            container_fallbacks = [
                f for f in existing_files
                if Path(f).suffix.lower() in {".mp4", ".mkv", ".mov"}
            ]
            if container_fallbacks:
                return container_fallbacks[0]
        
        # Ensure downloads directory exists with write permissions
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            try:
                downloads_dir.mkdir(parents=True, exist_ok=True)
                logger.info("📁 Created downloads directory")
            except Exception as e:
                logger.error(f"❌ Cannot create downloads directory: {e}")
                return None

        # **PERFORMANCE FIX**: Use semaphore to limit concurrent downloads
        # Prevents bandwidth saturation when 15-20 groups download simultaneously
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
                "http_chunk_size": 524288,  # 512KB chunks
                "socket_timeout": 30,
                "retries": 2,
                "fragment_retries": 2,
                "extractor_retries": 5,
                "sleep_interval_requests": 1,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }

            if video:
                # Video mode: download best video/audio combo up to configured height
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
                # Audio mode: favor m4a/opus for best compatibility
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
                    # Extract info to get actual extension downloaded
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
                        logger.error(
                            "❌ Video not available: May be region-blocked or private.")
                    elif "age" in error_msg.lower():
                        logger.error(
                            "❌ Age-restricted video: Cookies required.")
                    else:
                        logger.error("❌ YouTube extraction failed: %s", ex)
                    return None
                except yt_dlp.utils.DownloadError as ex:
                    error_msg = str(ex)
                    recovered = self._locate_download_file(video_id, video=video)
                    if "unable to rename file" in error_msg.lower() and recovered:
                        logger.warning(
                            f"⚠️ Renaming failed for {video_id}, using recovered file {Path(recovered).name}"
                        )
                        return recovered
                    if "416" in error_msg or "Requested range not satisfiable" in error_msg:
                        logger.warning(f"⚠️ Range error for {video_id}, skipping")
                    else:
                        if "ffmpeg exited with code 255" not in str(ex):
                            logger.warning(f"⚠️ Download error for {video_id}: {ex}")
                        if recovered:
                            logger.warning(
                                f"⚠️ Using recovered file for {video_id} despite download error"
                            )
                            return recovered
                    return None
                except Exception as ex:
                    logger.warning(f"⚠️ Unexpected download error for {video_id}: {ex}")
                    return None
                finally:
                    # CRITICAL: Explicitly close yt-dlp to release file handles
                    if ydl_instance:
                        try:
                            ydl_instance.close()
                        except Exception:
                            pass

            # Single attempt with the initially selected cookie.
            return await asyncio.to_thread(_download, ydl_opts_cookie)