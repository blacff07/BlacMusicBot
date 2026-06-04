<img src="https://files.catbox.moe/fykkhm.jpg" alt="BlacMusic Banner" width="100%"/>

# ˹ʙʟᴀᴄ ᴍᴜꜱɪᴄ˼ 🎵

<div align="center">

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?style=flat-square&logo=telegram)](https://t.me)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green?style=flat-square&logo=python)](https://www.python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-red?style=flat-square)](LICENSE)

A powerful Telegram voice chat music bot with playlist support, group controls, and advanced playback features.

[Quick Start](#-quick-start) • [Setup](#-setup) • [Commands](#-commands) • [Cookies](#-cookies) • [Hosting](#-hosting)

</div>

---

## ✨ What This Bot Does

🎵 **Play Music** - Search and play songs from YouTube in voice chats
👥 **Group Control** - Admins can restrict who can play music
🔐 **User Permissions** - Authorize specific users without making them admins
📻 **Radio & Playlists** - Stream radio stations and entire YouTube playlists
⏪ **Full Playback Control** - Pause, resume, skip, seek, loop, shuffle

---

## 📋 Requirements

- **Python** 3.8 or higher
- **MongoDB** (local or cloud)
- **Telegram Bot Token** (from @BotFather)
- **Telegram Account** (for assistant userbot)

---

## 🚀 Quick Start

### Step 1: Clone & Setup

```bash
git clone https://github.com/yourusername/BlacMusicBot.git
cd BlacMusicBot
chmod +x QUICK_SETUP.sh
./QUICK_SETUP.sh
```

### Step 2: Create .env File

Create a file named `.env` in the root directory:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
ASSISTANT_ID=assistant_user_id
DB_URL=mongodb_connection_string
SOURCE_URL=https://github.com/yourusername/BlacMusicBot.git
COOKIES_URL=https://your-cookies-url.com/cookies.txt
SUDO_USERS=your_user_id
SUPPORT_CHANNEL=https://t.me/yourchannel
SUPPORT_CHAT=https://t.me/yourchat
LANGUAGE=en
```

### Step 3: Start Bot

```bash
python -m BlacMusic
```

Bot is now online! 🎉

---

## ⚙️ Setup Details

### Get API Credentials

1. **API ID & Hash:**
   - Go to https://my.telegram.org
   - Create an app
   - Copy `api_id` and `api_hash`

2. **Bot Token:**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions and copy token

3. **Assistant ID:**
   - Message @userinfobot on Telegram
   - Copy your User ID

### Database Setup

**Local MongoDB:**
```bash
mongod
```

**Cloud MongoDB (Atlas):**
- Create account at https://www.mongodb.com/cloud/atlas
- Create cluster
- Get connection string: `mongodb+srv://user:password@cluster.mongodb.net/blacmusic`

### Cookies for YouTube (Optional but Recommended)

YouTube blocks downloads from servers. Cookies bypass this.

**Get Cookies:**

#### Windows/Mac/Linux

1. Open **Chrome** or **Firefox**
2. Go to https://www.youtube.com
3. **Log in** to your account
4. Press **F12** (Developer Tools)
5. Go to **Storage/Application** tab
6. Click **Cookies** → **https://www.youtube.com**
7. Copy all cookie data
8. Save as `cookies.txt`

#### Android

**Using Firefox:**
1. Install Firefox
2. Go to youtube.com and log in
3. Install extension: **"Cookies.txt"**
4. Export cookies to file

**Using Kiwi Browser:**
1. Install Kiwi Browser (plays extensions)
2. Install **"Cookie Editor"** extension
3. Go to youtube.com and log in
4. Click extension → Export

**Place Cookies:**
```bash
mkdir -p BlacMusic/cookies
cp cookies.txt BlacMusic/cookies/cookies.txt
```

---

## 📱 Commands

### Playback (Anyone)

```
/play song_name           - Search and play song
/play youtube_url         - Play direct YouTube link
/playlist url             - Add entire playlist
/pause                    - Pause music
/resume                   - Resume music
/skip                     - Next song
/stop                     - Stop playing
/queue                    - Show queue
/now                      - Current song
/seek 120                 - Jump to 2 minutes
/loop [off/one/all]       - Loop mode
/shuffle                  - Randomize queue
```

### Admin Commands

```
/playmode                 - Toggle everyone/admin-only mode
/settings                 - View group settings
/auth @user               - Allow user to control music
/unauth @user             - Remove user permission
/authlist                 - Show authorized users
```

### Owner Commands (Sudo)

```
/addsudo @user            - Add bot admin
/delsudo @user            - Remove bot admin
/sudolist                 - Show all bot admins
/restart                  - Restart bot
/update                   - Pull latest & restart
/gban user_id             - Global ban user
/ungban user_id           - Unban user
/logs                     - Get bot logs
```

### Info Commands

```
/start                    - Welcome message
/help                     - All commands
/ping                     - Check bot response
/stats                    - Bot statistics
```

---

## 🍪 YouTube Cookies

Cookies expire after ~1 year. When you get "Sign in to confirm you're not a bot" error:

1. Export fresh cookies (repeat above steps)
2. Replace `BlacMusic/cookies/cookies.txt`
3. Run `/update` command in Telegram

---

## 🌐 Hosting

### Local Machine

```bash
./QUICK_SETUP.sh
python -m BlacMusic
```

Keep terminal open. Bot stays online while running.

### VPS/Cloud Server (Ubuntu)

**Initial Setup:**
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git -y
git clone https://github.com/yourusername/BlacMusicBot.git
cd BlacMusicBot
./QUICK_SETUP.sh
```

**Run with Screen (Keep Online):**
```bash
screen -S blacmusic
python -m BlacMusic
```

Press `Ctrl+A` then `D` to detach. Resume with: `screen -r blacmusic`

**Run with Nohup (Keep Online):**
```bash
nohup python -m BlacMusic > bot.log 2>&1 &
tail -f bot.log
```

### Docker

```bash
docker build -t blacmusic .
docker run -d --name blacmusic --env-file .env blacmusic
```

### Production (Systemd Service)

Create `/etc/systemd/system/blacmusic.service`:

```ini
[Unit]
Description=BlacMusic Bot
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

Enable & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable blacmusic
sudo systemctl start blacmusic
```

Check status:
```bash
sudo systemctl status blacmusic
```

---

## 🔄 Update Bot

**Via Telegram:**
```
/update
```

Bot automatically pulls latest code and restarts.

**Manually:**
```bash
git pull origin main
./QUICK_SETUP.sh
python -m BlacMusic
```

---

## 🐛 Troubleshooting

### "Sign in to confirm you're not a bot"

Solution: Add cookies.txt
```bash
# 1. Export cookies (see Cookies section)
# 2. Place in BlacMusic/cookies/cookies.txt
# 3. Run /update in Telegram
```

### Bot won't start

```bash
python3 -c "from BlacMusic import app; print('OK')"
pip install --upgrade -r requirements.txt
./QUICK_SETUP.sh
```

### MongoDB connection fails

- Check connection string in .env
- Verify network access in MongoDB Atlas
- Test: `mongosh "mongodb+srv://..."`

### Import errors

```bash
deactivate
rm -rf venv
./QUICK_SETUP.sh
```

### Check logs

```bash
tail -f log.txt
```

Look for error messages with timestamps.

---

## 📁 Project Structure

```
BlacMusicBot/
├── BlacMusic/
│   ├── __main__.py           - Entry point
│   ├── core/                 - YouTube, database
│   ├── plugins/              - Commands
│   ├── helpers/              - Utilities
│   ├── cookies/              - cookies.txt goes here
│   └── locales/              - Language files
├── requirements.txt          - Dependencies
├── .env                      - Configuration
├── QUICK_SETUP.sh           - Setup script
└── README.md                - This file
```

---

## 🔐 Security

### Do's ✅
- Use dedicated YouTube account (not personal)
- Keep `.env` file private
- Add to `.gitignore`:
  ```
  .env
  BlacMusic/cookies/
  cookies.txt
  log.txt
  ```
- Use strong passwords
- Enable 2FA on accounts

### Don'ts ❌
- Don't commit cookies to GitHub
- Don't share .env publicly
- Don't use personal YouTube account
- Don't upload to public servers unencrypted

---

## 📚 Useful Links

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **My Telegram ID:** https://t.me/userinfobot
- **Get API Credentials:** https://my.telegram.org

---

## 💬 Support

For issues:
1. Check logs: `tail -f log.txt`
2. Read troubleshooting section above
3. Create GitHub issue with error message

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

<div align="center">

**Made with ❤️ for music lovers**

⭐ Star this repo if you find it useful!

</div>