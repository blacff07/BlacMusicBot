import asyncio
import os
import aiohttp
from pathlib import Path
from py_yt import VideosSearch, Playlist
import yt_dlp

from BlacMusic import config, logger


async def save_cookies(url):
    if not url:
        logger.warning("⚠️ COOKIES_URL not set in .env")
        return
    
    try:
        cookies_dir = Path("BlacMusic/cookies")
        cookies_dir.mkdir(exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    if not content or b"Netscape" not in content:
                        logger.warning("⚠️ Invalid cookies format from URL")
                        return
                    
                    cookies_file = cookies_dir / "cookies.txt"
                    with open(cookies_file, "wb") as f:
                        f.write(content)
                    
                    file_size = len(content)
                    logger.info(f"✅ Cookies loaded from URL: {file_size} bytes")
                else:
                    logger.warning(f"⚠️ Failed to download cookies: HTTP {response.status}")
    except asyncio.TimeoutError:
        logger.warning("⚠️ Cookies download timeout")
    except Exception as e:
        logger.warning(f"⚠️ Error loading cookies: {e}")


async def search(query: str):
    try:
        _search = VideosSearch(query, limit=1)
        result = await _search.next()
        
        if not result:
            return None
        
        track = result[0]
        return {
            "id": track.get("id"),
            "title": track.get("title"),
            "duration": track.get("duration"),
            "link": f"https://youtu.be/{track.get('id')}",
            "thumbnails": track.get("thumbnails", [{}])[0].get("url", ""),
            "channel": track.get("channel", {}).get("name", "Unknown"),
            "viewCount": track.get("viewCount", {}).get("short", "0"),
        }
    except Exception as e:
        logger.error(f"YouTube search error: {e}")
        return None


async def download(url: str, file_name: str):
    cookies_file = Path("BlacMusic/cookies/cookies.txt")
    
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
    
    if cookies_file.exists():
        ydl_opts["cookiefile"] = str(cookies_file)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False