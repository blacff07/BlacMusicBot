#!/bin/bash
# ==============================================================================
# QUICK_SETUP.sh - One Command Complete Setup with Auto Git Clone
# ==============================================================================
# This script handles everything:
# 1. Reads SOURCE_URL from .env file
# 2. Clones the repo if not already cloned
# 3. Sets up clean virtual environment
# 4. Installs all dependencies
# 5. Verifies installation
# 6. Activates venv
#
# Usage: ./QUICK_SETUP.sh
# ==============================================================================

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

# Function to read .env file
read_env_file() {
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
}

# Step 0: Check for .env and clone repo if needed
echo -e "${YELLOW}[0/7] 📍 Checking repository...${NC}"

# Look for .env in current directory or parent
if [ -f ".env" ]; then
    ENV_FILE=".env"
elif [ -f "../.env" ]; then
    ENV_FILE="../.env"
else
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env with SOURCE_URL or run this script from the repo directory."
    exit 1
fi

# Read SOURCE_URL from .env
read_env_file
SOURCE_URL="${SOURCE_URL}"

if [ -z "$SOURCE_URL" ]; then
    echo -e "${RED}❌ Error: SOURCE_URL not found in .env!${NC}"
    echo "Add this to your .env file:"
    echo "  SOURCE_URL=https://github.com/yourusername/BlacMusicBot.git"
    exit 1
fi

# Check if we're in the repo directory
if [ ! -f "requirements.txt" ] && [ ! -f "BlacMusic/__main__.py" ]; then
    echo -e "${YELLOW}   Not in repo directory. Cloning from SOURCE_URL...${NC}"
    
    # Extract repo name from URL
    REPO_NAME=$(basename "$SOURCE_URL" .git)
    
    # Check if repo already exists
    if [ -d "$REPO_NAME" ]; then
        echo -e "${YELLOW}   Directory $REPO_NAME already exists. Using it...${NC}"
        cd "$REPO_NAME"
    else
        echo -e "${YELLOW}   Cloning from $SOURCE_URL...${NC}"
        git clone "$SOURCE_URL" "$REPO_NAME"
        cd "$REPO_NAME"
    fi
    
    # Reload .env from new location
    read_env_file
    echo -e "${GREEN}   ✅ Repository ready${NC}"
else
    echo -e "${GREEN}   ✅ Already in repository${NC}"
fi

# Verify requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found!${NC}"
    exit 1
fi

# Step 1: Clean old environment
echo -e "${YELLOW}[1/7] 🧹 Cleaning old virtual environment...${NC}"
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate 2>/dev/null || true
fi
rm -rf venv __pycache__ 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}   ✅ Cleaned${NC}"

# Step 2: Verify Python
echo -e "${YELLOW}[2/7] 🐍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}   ✅ Python $PYTHON_VERSION${NC}"

# Step 3: Create fresh venv
echo -e "${YELLOW}[3/7] 📦 Creating fresh virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}   ✅ venv created${NC}"

# Step 4: Activate venv
echo -e "${YELLOW}[4/7] 🔗 Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}   ✅ venv activated${NC}"

# Step 5: Upgrade pip & install dependencies
echo -e "${YELLOW}[5/7] 📥 Installing dependencies...${NC}"
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet -r requirements.txt
echo -e "${GREEN}   ✅ All dependencies installed${NC}"

# Step 6: Verify installation
echo -e "${YELLOW}[6/7] ✔️  Verifying installation...${NC}"
if python3 -c "from py_yt import VideosSearch; import yt_dlp; from pyrogram import Client" 2>/dev/null; then
    echo -e "${GREEN}   ✅ All modules loaded successfully${NC}"
else
    echo -e "${YELLOW}   ⚠️  Warning: Could not verify some modules${NC}"
fi

# Step 7: Final check
echo -e "${YELLOW}[7/7] 🔍 Final verification...${NC}"
if [ -d "BlacMusic" ] && [ -f "BlacMusic/__main__.py" ]; then
    echo -e "${GREEN}   ✅ Bot structure verified${NC}"
else
    echo -e "${YELLOW}   ⚠️  Warning: Could not verify bot structure${NC}"
fi

# Final message
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
echo -e "${BLUE}If venv deactivates, reactivate with:${NC}"
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo ""