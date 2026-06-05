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
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.warned = False

        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

        self.search_cache = {}
        self.cache_time = {}
        self._download_semaphore = asyncio.Semaphore(5)
        self._max_video_height = getattr(config, "VIDEO_MAX_HEIGHT", 1080)

    def _locate_download_file(self, video_id: str, video: bool = False) -> Optional[str]:
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
            try:
                for file in os.listdir("BlacMusic/cookies"):
                    if file.endswith(".txt"):
                        self.cookies.append(file)
            except FileNotFoundError:
                pass
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return f"BlacMusic/cookies/{random.choice(self.cookies)}"

    async def save_cookies(self, urls: list) -> None:
        if not urls:
            return
            
        logger.info("Saving cookies from COOKIES_URL (.env)...")
        saved_count = 0
        
        for url in urls:
            try:
                path = f"BlacMusic/cookies/cookie{random.randint(10000, 99999)}.txt"
                link = url.replace("me/", "me/raw/")
                async with aiohttp.ClientSession() as session:
                    async with session.get(link, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if resp.status != 200:
                            logger.error(f"Cookie download failed: HTTP {resp.status}")
                            continue
                        content = await resp.read()
                        if not content or len(content) < 50:
                            logger.error("Cookie file empty or invalid")
                            continue
                        if b"Netscape" not in content:
                            logger.error("Invalid cookies format")
                            continue
                        with open(path, "wb") as fw:
                            fw.write(content)
                        if os.path.exists(path) and os.path.getsize(path) > 0:
                            saved_count += 1
                            cookie_filename = os.path.basename(path)
                            if cookie_filename not in self.cookies:
                                self.cookies.append(cookie_filename)
                            logger.info(f"Loaded: {cookie_filename}")
            except asyncio.TimeoutError:
                logger.error("Cookie download timeout")
            except Exception as e:
                logger.error(f"Cookie download error: {e}")
        
        self.checked = True
        if saved_count > 0:
            logger.info(f"Cookies from URL loaded: {saved_count} file(s)")
        else:
            logger.warning("Failed to load cookies from URL, will try local cookies.txt")
            self.checked = False

    def is_network_stream(self, url: str) -> bool:
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

    async def search(self, query: str):
        try:
            _search = VideosSearch(query, limit=1)
            result = await _search.next()
            
            if not result:
                return None
            
            track = result[0]
            return Track(
                id=track.get("id"),
                title=track.get("title"),
                duration=track.get("duration"),
                link=f"https://youtu.be/{track.get('id')}",
                url=f"https://youtu.be/{track.get('id')}",
                source="youtube",
                thumb=track.get("thumbnails", [{}])[0].get("url", ""),
                channel=track.get("channel", {}).get("name", "Unknown"),
            )
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return None

    async def get_file(self, url: str, playlist: bool = False):
        try:
            if not self.valid(url):
                return None, []
            
            if playlist and "playlist" in url.lower():
                pl = Playlist(url)
                videos = []
                async for video in pl.get_videos():
                    videos.append(video)
                
                if videos:
                    track = await self.search(videos[0].get("title", ""))
                    return track, videos[:10]
            
            if "youtube.com" in url or "youtu.be" in url:
                video_id = url.split("v=")[-1].split("&")[0]
                result = await self.search(video_id)
                return result, []
            
            return None, []
        except Exception as e:
            logger.error(f"Get file error: {e}")
            return None, []

    async def download(self, url: str, file_name: str) -> bool:
        async with self._download_semaphore:
            try:
                cookies_file = self.get_cookies()
                
                ydl_opts = {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "opus",
                            "preferredquality": "192",
                        }
                    ],
                    "outtmpl": file_name,
                    "quiet": False,
                    "no_warnings": False,
                }
                
                if cookies_file and os.path.exists(cookies_file):
                    ydl_opts["cookiefile"] = cookies_file
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return True
            except Exception as e:
                logger.error(f"Download error: {e}")
                return False