#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🎵 BlacMusicBot - Complete Setup Script 🎵      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Create .env with SOURCE_URL before running this script."
    exit 1
fi

export $(cat .env | grep -v '^#' | xargs)
SOURCE_URL="${SOURCE_URL}"

if [ -z "$SOURCE_URL" ]; then
    echo -e "${RED}❌ Error: SOURCE_URL not found in .env!${NC}"
    exit 1
fi

echo -e "${YELLOW}[0/7] 📍 Checking repository...${NC}"

if [ ! -f "requirements.txt" ] || [ ! -d "BlacMusic" ]; then
    echo -e "${YELLOW}   Not in repo directory. Cloning...${NC}"
    REPO_NAME=$(basename "$SOURCE_URL" .git)
    if [ -d "$REPO_NAME" ]; then
        cd "$REPO_NAME"
    else
        git clone "$SOURCE_URL" "$REPO_NAME"
        cd "$REPO_NAME"
    fi
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}   In repo directory. Pulling latest changes...${NC}"
    git pull origin main || git pull origin master
fi

echo -e "${GREEN}   ✅ Repository ready${NC}"

echo -e "${YELLOW}[1/7] 🧹 Cleaning old virtual environment...${NC}"
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate 2>/dev/null || true
fi
rm -rf venv __pycache__ 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}   ✅ Cleaned${NC}"

echo -e "${YELLOW}[2/7] 🐍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}   ✅ Python $PYTHON_VERSION${NC}"

echo -e "${YELLOW}[3/7] 📦 Creating fresh virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}   ✅ venv created${NC}"

echo -e "${YELLOW}[4/7] 🔗 Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}   ✅ venv activated${NC}"

echo -e "${YELLOW}[5/7] 📥 Installing dependencies...${NC}"
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet -r requirements.txt
echo -e "${GREEN}   ✅ All dependencies installed${NC}"

echo -e "${YELLOW}[6/7] ✔️  Verifying installation...${NC}"
if python3 -c "from py_yt import VideosSearch; import yt_dlp; from pyrogram import Client" 2>/dev/null; then
    echo -e "${GREEN}   ✅ All modules loaded successfully${NC}"
else
    echo -e "${YELLOW}   ⚠️  Warning: Could not verify some modules${NC}"
fi

echo -e "${YELLOW}[7/7] 🔍 Final verification...${NC}"
if [ -d "BlacMusic" ] && [ -f "BlacMusic/__main__.py" ]; then
    echo -e "${GREEN}   ✅ Bot structure verified${NC}"
else
    echo -e "${YELLOW}   ⚠️  Warning: Could not verify bot structure${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        ✅ SETUP COMPLETE - READY TO RUN! ✅        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Virtual environment is already ACTIVATED.${NC}"
echo ""
echo -e "${BLUE}To start the bot, simply run:${NC}"
echo -e "${YELLOW}python -m BlacMusic${NC}"
echo ""