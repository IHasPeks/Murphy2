"""
Build script to create a standalone executable for MurphyAI Twitch Bot
This script uses PyInstaller to package the bot with all dependencies
"""

import subprocess
import sys
import os
import shutil
import json

def check_config():
    """Check if config.py has been properly configured"""
    try:
        import config

        # Check if credentials are still placeholder values
        if config.TWITCH_TOKEN == "oauth:your_twitch_oauth_token_here":
            print("\n⚠️  WARNING: Please update your credentials in config.py!")
            print("Edit config.py and replace the placeholder values with your actual credentials:")
            print("  - BOT_NICK: Your bot's Twitch username")
            print("  - TWITCH_TOKEN: Your OAuth token from https://twitchapps.com/tmi/")
            print("  - TWITCH_CLIENT_ID: Your Client ID from https://dev.twitch.tv/console/apps")
            print("  - TWITCH_INITIAL_CHANNELS: Channels the bot should join")
            print("  - OPENAI_API_KEY: Your OpenAI API key from https://platform.openai.com/api-keys")

            response = input("\nDo you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)

    except Exception as e:
        print(f"Error checking config: {e}")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    print("Installing PyInstaller and dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_spec_file():
    """Create PyInstaller spec file for proper packaging"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['bot.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('dynamic_commands.json', '.'),
        ('commands.md', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'twitchio',
        'twitchio.ext',
        'twitchio.ext.commands',
        'openai',
        'apscheduler',
        'googletrans',
        'psutil',
        'watchdog',
        'async_timeout',
        'aiohttp',
        'pkg_resources.py2_warn',
        'pkg_resources.markers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MurphyAI_Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='bot_icon.ico' if os.path.exists('bot_icon.ico') else None,
)
'''

    with open('MurphyAI.spec', 'w') as f:
        f.write(spec_content)

    print("Created PyInstaller spec file: MurphyAI.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")

    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("state", exist_ok=True)
    os.makedirs("state/ai_cache", exist_ok=True)
    os.makedirs("state/command_backups", exist_ok=True)

    # Ensure dynamic_commands.json exists
    if not os.path.exists("dynamic_commands.json"):
        with open("dynamic_commands.json", "w") as f:
            json.dump({}, f)

    # Run PyInstaller
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "--clean", "MurphyAI.spec"])

    print("\n✅ Build complete!")

def create_batch_file():
    """Create a batch file for easy launching on Windows"""
    batch_content = '''@echo off
title MurphyAI Twitch Bot
echo Starting MurphyAI Twitch Bot...
echo.
cd /d "%~dp0"
MurphyAI_Bot.exe
echo.
echo Bot has stopped. Press any key to exit...
pause > nul
'''

    output_dir = "dist"
    if os.path.exists(output_dir):
        with open(os.path.join(output_dir, "Start_MurphyAI_Bot.bat"), "w") as f:
            f.write(batch_content)
        print("Created batch file: Start_MurphyAI_Bot.bat")

def create_readme():
    """Create a user-friendly README for the packaged bot"""
    readme_content = '''# MurphyAI Twitch Bot - User Guide

## Quick Start

1. **First Time Setup**
   - Make sure you have configured your credentials in config.py before building
   - The bot needs your Twitch and OpenAI credentials to work

2. **Starting the Bot**
   - Double-click `Start_MurphyAI_Bot.bat` to start the bot
   - Or run `MurphyAI_Bot.exe` directly

3. **Bot Commands**
   - Type `?help` in chat to see available commands
   - Mod commands use `\\` prefix
   - AI commands: `?ai <your message>`

4. **Folders Created**
   - `logs/` - Contains bot logs
   - `state/` - Stores bot data and settings

5. **Troubleshooting**
   - If the bot crashes, check the logs folder
   - Make sure your internet connection is stable
   - Verify your credentials are correct

6. **Stopping the Bot**
   - Close the console window
   - Or press Ctrl+C in the console

## Need Help?
Check the logs folder for error messages if something goes wrong.
'''

    output_dir = "dist"
    if os.path.exists(output_dir):
        with open(os.path.join(output_dir, "README_USER.txt"), "w") as f:
            f.write(readme_content)
        print("Created user README: README_USER.txt")

def package_distribution():
    """Create a distribution package with all necessary files"""
    print("\nPackaging distribution...")

    dist_dir = "dist"
    if os.path.exists(dist_dir):
        # Create necessary directories in dist
        for folder in ["logs", "state", "state/ai_cache", "state/command_backups"]:
            os.makedirs(os.path.join(dist_dir, folder), exist_ok=True)

        # Copy dynamic_commands.json if it exists
        if os.path.exists("dynamic_commands.json"):
            shutil.copy("dynamic_commands.json", dist_dir)

        # Create a zip file
        shutil.make_archive("MurphyAI_Bot_Package", "zip", dist_dir)
        print("\n📦 Created distribution package: MurphyAI_Bot_Package.zip")

def main():
    print("=== MurphyAI Bot Packaging Script ===\n")

    # Check Python version
    if sys.version_info < (3, 8):
        print("⚠️  Warning: Python 3.8 or higher is recommended")

    try:
        # Check config
        check_config()

        # Install dependencies
        install_dependencies()

        # Create spec file
        create_spec_file()

        # Build executable
        build_executable()

        # Create batch file for easy launching
        create_batch_file()

        # Create user-friendly README
        create_readme()

        # Package everything
        package_distribution()

        print("\n✅ Packaging complete!")
        print("\n📁 Output files:")
        print("  - dist/MurphyAI_Bot.exe - The main executable")
        print("  - dist/Start_MurphyAI_Bot.bat - Easy launcher")
        print("  - MurphyAI_Bot_Package.zip - Complete package to distribute")
        print("\n📝 Instructions:")
        print("  1. Edit config.py with your actual credentials")
        print("  2. Run this script again to rebuild with your credentials")
        print("  3. Give the .zip file to the end user")
        print("  4. They just need to extract and run Start_MurphyAI_Bot.bat")

    except Exception as e:
        print(f"\n❌ Error during packaging: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
