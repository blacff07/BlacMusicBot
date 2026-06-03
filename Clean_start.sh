#!/bin/bash
# ==============================================================================
# clean_start.sh - Clean Virtual Environment & Fresh Install
# ==============================================================================
# This script fixes venv path corruption that occurs after git clone.
# Run this whenever you pull latest changes or clone the repo fresh.
#
# Usage: ./clean_start.sh
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧹 BlacMusicBot - Clean Installation Script${NC}"
echo "================================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Deactivate existing venv
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Deactivating current virtual environment...${NC}"
    deactivate
fi

# Remove old venv
if [ -d "venv" ]; then
    echo -e "${YELLOW}🗑️  Removing old virtual environment...${NC}"
    rm -rf venv
fi

# Remove pycache
if [ -d "__pycache__" ]; then
    echo -e "${YELLOW}Cleaning Python cache...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
fi

# Create fresh venv
echo -e "${YELLOW}📦 Creating fresh virtual environment...${NC}"
python3 -m venv venv

# Activate venv
echo -e "${YELLOW}🔗 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip, setuptools, wheel
echo -e "${YELLOW}⬆️  Upgrading pip, setuptools, wheel...${NC}"
pip install --upgrade pip setuptools wheel

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found!${NC}"
    echo "Please make sure requirements.txt is in the current directory."
    deactivate
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}📥 Installing dependencies from requirements.txt...${NC}"
pip install -r requirements.txt

# Show summary
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Your virtual environment is ready. To run BlacMusic:"
echo ""
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo -e "${YELLOW}python -m BlacMusic${NC}"
echo ""
echo "To use this in future, just run:"
echo -e "${YELLOW}./clean_start.sh${NC}"
echo ""