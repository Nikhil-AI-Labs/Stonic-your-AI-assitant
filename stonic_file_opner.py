import os
import subprocess
import sys
import logging
import asyncio
from fuzzywuzzy import process
from livekit.agents import function_tool

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Fix for Unicode in some Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 👁 Focus the opened window if possible
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow module not found.")
        return False

    await asyncio.sleep(1.5)
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            logger.info(f"🪟 Window focused: {window.title}")
            return True

    logger.warning("⚠ No matching window found for focus.")
    return False

# 🔍 Index all files and folders under specified directories
async def index_items(base_dirs):
    index = []
    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for name in files + dirs:
                index.append({
                    "name": name,
                    "path": os.path.join(root, name),
                    "type": "folder" if name in dirs else "file"
                })
    logger.info(f"✅ Indexed {len(index)} items from {base_dirs}")
    return index

# 🎯 Search best match using fuzzy logic
async def search_item(query, index):
    choices = [item["name"] for item in index]
    if not choices:
        logger.warning("⚠ No files or folders to search.")
        return None

    best_match, score = process.extractOne(query, choices)
    logger.info(f"🔍 Matched '{query}' to '{best_match}' (Score: {score})")

    if score > 70:
        for item in index:
            if item["name"] == best_match:
                return item
    return None

# 🚀 Open the file or folder
async def open_item(item):
    try:
        logger.info(f"📂 Opening: {item['path']}")
        if os.name == 'nt':
            os.startfile(item["path"])
        else:
            subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', item["path"]])

        await focus_window(item["name"])  # Optional: bring to front
        return f"✅ '{item['name']}' open हो गया।"
    except Exception as e:
        logger.error(f"❌ Error opening: {e}")
        return f"❌ '{item['name']}' open नहीं हो सका। {e}"

# 🧠 Overall handler
async def handle_command(command, index):
    item = await search_item(command, index)
    if item:
        return await open_item(item)
    else:
        logger.warning("❌ No matching item found.")
        return "❌ कोई matching file या folder नहीं मिला।"

# 📢 Tool exposed to LiveKit
@function_tool
async def Play_file(name: str) -> str:
    base_dirs = ["C:/"]  # 🔧 Change this as needed
    index = await index_items(base_dirs)
    command = name.strip()
    return await handle_command(command, index)
