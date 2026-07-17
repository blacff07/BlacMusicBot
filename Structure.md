# BlacMusicBot — Project Structure

## 📁 Root
```
BlacMusicBot/
├── BlacMusic/          # Main application package
├── config.py           # Configuration loader (reads .env)
├── requirements.txt    # Python dependencies
├── sample.env          # Environment variable template
├── Dockerfile          # Docker / Railway build
├── railway.toml        # Railway deployment config
├── Procfile            # Heroku-style process definition
├── README.md
├── SECURITY.md
└── .gitignore
```

## 📦 BlacMusic/
```
BlacMusic/
├── __init__.py         # Package init, logging, component wiring
├── __main__.py         # Entry point (python -m BlacMusic)
├── core/               # Core components
│   ├── bot.py          # Pyrogram bot client
│   ├── userbot.py      # Assistant session manager (anti-freeze)
│   ├── calls.py        # PyTgCalls voice chat handler
│   ├── mongo.py        # MongoDB database layer
│   ├── lang.py         # Localization system
│   ├── telegram.py     # Telegram helper utilities
│   ├── youtube.py      # yt-dlp / search wrapper
│   ├── preload.py      # Background track pre-downloader
│   └── dir.py          # Directory setup
├── helpers/
│   ├── _inline.py      # Inline keyboard builder
│   ├── _thumbnails.py  # Now Playing thumbnail generator
│   ├── _utilities.py   # General utilities
│   ├── _play.py        # Play flow helpers
│   ├── _queue.py       # Queue management
│   ├── _admins.py      # Admin cache helpers
│   ├── _dataclass.py   # Track dataclass
│   ├── _preload.py     # Preload helpers
│   ├── _exec.py        # Exec helpers
│   ├── Inter-Light.ttf
│   └── Raleway-Bold.ttf
├── locales/
│   └── en.json         # English strings
├── plugins/
│   ├── information/    # /start, /ping, /stats, /active
│   ├── playback-controls/ # /play, /vplay, /pause, /resume, /skip, /stop, /seek, /loop, /shuffle, /queue
│   ├── admin-controles/   # /restart, /broadcast, /sudo, /gban, /maintenance, /autoleave
│   ├── settings/       # /auth, /blacklist, /channelplay
│   ├── events/         # callbacks, inline query, new_chat, misc
│   └── features/       # admin mention, group data, etc.
└── cookies/            # YouTube cookie files (optional)
```