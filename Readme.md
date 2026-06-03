<div align="center">

<img src="https://files.catbox.moe/fykkhm.jpg" alt="BlacMusic Banner" width="100%"/>

<br/>

# 🎵 ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼

<div align="center">

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?style=flat-square&logo=telegram)](https://t.me)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green?style=flat-square&logo=python)](https://www.python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-red?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)](https://github.com)

A powerful Telegram music bot with voice chat support, advanced playlist management, and multi-tier access control.

[Features](#-features) • [Installation](#-installation) • [Setup](#-setup) • [Usage](#-usage) • [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

🎶 **Music Playback**
- Play songs from Telegram groups and channels
- Direct YouTube URL support
- Playlist management with queue system
- High-quality audio streaming via py-tgcalls

🔐 **Multi-Tier Access Control**
- Free tier with basic functionality
- Premium tier with extended features
- Elite tier with priority playback
- Owner-only administrative commands

⚙️ **Advanced Features**
- Smart caching system to reduce bandwidth
- Automatic retry on connection failures
- Per-group play mode settings (everyone/admin-only)
- Comprehensive logging and error tracking
- MongoDB database integration

🛠️ **Developer Friendly**
- Plugin-based architecture for easy extensions
- RESTful command structure
- Hot-reload capabilities via `/update`
- Detailed error messages and debugging

---

## 📋 Requirements

- Python 3.8 or higher
- MongoDB (local or cloud instance)
- Git (for version updates)
- Telegram Bot Token (from @BotFather)
- Telegram Account for userbot (assistant account)

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/BlacMusicBot.git
cd BlacMusicBot
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

### 1. Environment Variables

Create `.env` file in root directory:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
ASSISTANT_ID=assistant_user_id
DB_URL=mongodb_connection_string
SOURCE_URL=https://github.com/yourusername/BlacMusicBot.git
SUDO_USERS=user_id_1,user_id_2
START_IMG=https://image_url
HELP_IMG=https://image_url
COOKIES_URL=https://cookie_url
LANGUAGE=en
```

### 2. Database Setup

If using local MongoDB:
```bash
mongod
```

Or use MongoDB Atlas (cloud):
```
mongodb+srv://username:password@cluster.mongodb.net/blacmusic
```

### 3. Get Required Credentials

**API ID & API Hash:**
- Go to https://my.telegram.org
- Create application
- Copy API ID and API Hash

**Bot Token:**
- Message @BotFather on Telegram
- Send `/newbot`
- Choose name and username
- Copy token

**Assistant Account:**
- Telegram account ID (not bot)
- Used for playlist management
- Get from @userinfobot

---

## 📱 Usage

### Starting the Bot

Using the shell script (recommended):
```bash
chmod +x QUICK_SETUP.sh
./QUICK_SETUP.sh
python -m BlacMusic
```

Or manually:
```bash
source venv/bin/activate
python -m BlacMusic
```

### Bot Commands

**Music Commands**
- `/play <song_name>` - Search and play song
- `/play <youtube_url>` - Play from direct YouTube link
- `/playlist <url>` - Add entire playlist to queue
- `/pause` - Pause current playback
- `/resume` - Resume playback
- `/skip` - Skip to next song
- `/queue` - Show current queue

**Admin Commands** (sudo users only)
- `/restart` - Restart bot cleanly
- `/update` - Pull latest changes and restart
- `/logs` - Get bot logs
- `/logger on/off` - Enable/disable logging

**Group Settings**
- `/playmode` - Toggle play mode (everyone/admin-only)
- `/settings` - Show group settings

---

## 🔧 QUICK_SETUP.sh Usage

The shell script automates the entire setup process:

```bash
chmod +x QUICK_SETUP.sh
./QUICK_SETUP.sh
```

**What it does:**
1. Checks for .env file with SOURCE_URL
2. Clones repository (if not already cloned)
3. Removes old virtual environment
4. Creates fresh venv
5. Installs all dependencies
6. Verifies installation
7. Activates venv automatically

**After script completes:**
```bash
python -m BlacMusic
```

---

## 🌐 Hosting Guide

### Option 1: Local Machine (Development)

```bash
./QUICK_SETUP.sh
python -m BlacMusic
```

Keep terminal window open. Bot stays online while running.

### Option 2: VPS/Cloud Server

**Initial Setup:**
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git -y
git clone https://github.com/yourusername/BlacMusicBot.git
cd BlacMusicBot
./QUICK_SETUP.sh
```

**Run with Screen (persistent):**
```bash
screen -S blacmusic
python -m BlacMusic
```

Press `Ctrl+A` then `D` to detach from screen.

**Resume session:**
```bash
screen -r blacmusic
```

**Run with Nohup (persistent):**
```bash
nohup python -m BlacMusic > bot.log 2>&1 &
```

**Check status:**
```bash
tail -f bot.log
```

### Option 3: Docker (Recommended for Scale)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "BlacMusic"]
```

Build and run:
```bash
docker build -t blacmusic .
docker run -d --name blacmusic --env-file .env blacmusic
```

### Option 4: Systemd Service (Production Linux)

Create `/etc/systemd/system/blacmusic.service`:
```ini
[Unit]
Description=BlacMusic Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/BlacMusicBot
ExecStart=/home/ubuntu/BlacMusicBot/venv/bin/python -m BlacMusic
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable blacmusic
sudo systemctl start blacmusic
```

Check status:
```bash
sudo systemctl status blacmusic
sudo journalctl -u blacmusic -f
```

---

## 🔄 Update Process

**Via Telegram (easiest):**
```
Send: /update
Bot automatically pulls latest code and restarts
```

**Manually:**
```bash
git pull origin main
./QUICK_SETUP.sh
python -m BlacMusic
```

---

## 🐛 Troubleshooting

**Bot won't start**
```bash
python3 -c "from BlacMusic import app; print('OK')"
pip install --upgrade -r requirements.txt
```

**Import errors**
```bash
deactivate
rm -rf venv
./QUICK_SETUP.sh
```

**MongoDB connection fails**
- Verify connection string in .env
- Check firewall settings
- Test connection: `mongo "your_connection_string"`

**Song search returns no results**
- Check internet connection
- Verify YouTube availability in region
- Try direct YouTube URL instead

**Bot doesn't respond**
- Check bot token is correct
- Verify bot is added to group/channel
- Check logs: `/logs` command

**venv errors after git clone**
```bash
./QUICK_SETUP.sh
```

---

## 📚 Project Structure

```
BlacMusicBot/
├── BlacMusic/
│   ├── __main__.py          # Entry point
│   ├── core/                # Core modules
│   │   ├── youtube.py       # YouTube search & download
│   │   └── ...
│   ├── plugins/             # Telegram commands
│   │   ├── playback/        # Play, pause, skip
│   │   ├── admin/           # Admin commands
│   │   └── ...
│   ├── helpers/             # Utilities
│   └── config.py            # Configuration
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── QUICK_SETUP.sh          # Setup script
└── README.md               # This file
```

---

## 🔐 Security Notes

- Never commit `.env` file to git
- Use strong MongoDB passwords
- Restrict SUDO_USERS to trusted users only
- Keep API credentials private
- Regularly update dependencies

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 💬 Support

For issues and questions:
- Check troubleshooting section above
- Review existing GitHub issues
- Create new GitHub issue with detailed information
- Contact bot developer via Telegram

---

<div align="center">

**Made with ❤️ for music lovers**

⭐ If you find this project useful, please give it a star!

</div>