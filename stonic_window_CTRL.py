import os
import subprocess
import logging
import sys
import asyncio
import json
from datetime import datetime, timedelta
from fuzzywuzzy import process

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): 
        return func

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache file for storing discovered paths
CACHE_FILE = "jarvis_path_cache.json"
CACHE_EXPIRY_HOURS = 24  # Refresh cache every 24 hours

# App command map
APP_MAPPINGS = {
    "notepad": "notepad",
    "calculator": "calc",
    "chrome": r"C:\Users\Nikhil Pathak\OneDrive\Desktop\Nikhil - Chrome.lnk",
    "command prompt": "cmd",
    "control panel": "control",
    "settings": "start ms-settings:",
    "paint": "mspaint",
    "vs code": r"C:\Users\Nikhil Pathak\OneDrive\Desktop\Visual Studio Code.lnk",
    "youtube" : r"C:\Users\Nikhil Pathak\OneDrive\Desktop\YouTube.lnk",
    "solidworks" : r"C:\Users\Public\Desktop\SOLIDWORKS 2023.lnk",
    "trae" : r"C:\Users\Nikhil Pathak\OneDrive\Desktop\Trae.lnk",
    "classroom" : r"C:\Users\Nikhil Pathak\OneDrive\Desktop\Google Classroom.lnk"
}

# Common search locations (prioritized)
SEARCH_LOCATIONS = [
    os.path.expanduser("~"),  # User home directory
    r"C:\Users\Nikhil Pathak",
    r"C:\Users\Nikhil Pathak\Desktop",
    r"C:\Users\Nikhil Pathak\OneDrive\Desktop",
    r"C:\Users\Nikhil Pathak\Documents",
    r"C:\Users\Nikhil Pathak\Downloads",
    r"D:",
    r"E:",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
]

class SmartPathFinder:
    def __init__(self):
        self.cache = {}
        self.load_cache()
    
    def load_cache(self):
        """Load cached paths from file"""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if cache is still valid
                    cache_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                    if datetime.now() - cache_time < timedelta(hours=CACHE_EXPIRY_HOURS):
                        self.cache = data.get('paths', {})
                        logger.info(f"✅ Loaded {len(self.cache)} cached paths")
                    else:
                        logger.info("🔄 Cache expired, will rebuild")
        except Exception as e:
            logger.warning(f"⚠ Could not load cache: {e}")
    
    def save_cache(self):
        """Save paths to cache file"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'paths': self.cache
            }
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Saved {len(self.cache)} paths to cache")
        except Exception as e:
            logger.warning(f"⚠ Could not save cache: {e}")
    
    async def smart_search(self, query, max_depth=3):
        """Smart search that looks in common locations first"""
        query_lower = query.lower().strip()
        
        # First check cache
        if query_lower in self.cache:
            path = self.cache[query_lower]
            if os.path.exists(path):
                logger.info(f"🎯 Found in cache: {path}")
                return {'name': os.path.basename(path), 'path': path, 'type': 'folder' if os.path.isdir(path) else 'file'}
            else:
                # Remove invalid path from cache
                del self.cache[query_lower]
        
        # Search in prioritized locations
        found_items = []
        
        for location in SEARCH_LOCATIONS:
            if not os.path.exists(location):
                continue
                
            try:
                # Search current directory
                items = self._search_in_directory(location, query_lower, max_depth=max_depth)
                found_items.extend(items)
                
                # If we found exact matches, prioritize them
                exact_matches = [item for item in items if item['name'].lower() == query_lower]
                if exact_matches:
                    best_match = exact_matches[0]
                    # Cache the result
                    self.cache[query_lower] = best_match['path']
                    self.save_cache()
                    return best_match
                    
            except Exception as e:
                logger.warning(f"⚠ Error searching in {location}: {e}")
                continue
        
        # If no exact match, use fuzzy matching on found items
        if found_items:
            names = [item['name'] for item in found_items]
            best_name, score = process.extractOne(query, names)
            
            if score > 70:  # Good enough match
                for item in found_items:
                    if item['name'] == best_name:
                        # Cache the result
                        self.cache[query_lower] = item['path']
                        self.save_cache()
                        logger.info(f"🔍 Fuzzy matched '{query}' to '{best_name}' (score: {score})")
                        return item
        
        return None
    
    def _search_in_directory(self, directory, query, max_depth=3, current_depth=0):
        """Search for items in a specific directory with depth limit"""
        if current_depth >= max_depth:
            return []
        
        found_items = []
        try:
            for item in os.listdir(directory):
                if item.startswith('.'):  # Skip hidden files
                    continue
                    
                item_path = os.path.join(directory, item)
                item_lower = item.lower()
                
                # Check if item name contains query
                if query in item_lower:
                    item_type = 'folder' if os.path.isdir(item_path) else 'file'
                    found_items.append({
                        'name': item,
                        'path': item_path,
                        'type': item_type
                    })
                
                # Recursively search subdirectories (with depth limit)
                if os.path.isdir(item_path) and current_depth < max_depth - 1:
                    try:
                        sub_items = self._search_in_directory(item_path, query, max_depth, current_depth + 1)
                        found_items.extend(sub_items)
                    except (PermissionError, OSError):
                        continue  # Skip inaccessible directories
                        
        except (PermissionError, OSError) as e:
            pass  # Skip inaccessible directories
            
        return found_items

# Initialize smart path finder
path_finder = SmartPathFinder()

# -------------------------
# Global focus utility
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow not available")
        return False

    await asyncio.sleep(1.5)  # Give time for window to appear
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# File/folder actions
async def open_folder(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
        logger.info(f"📂 Opened folder: {path}")
    except Exception as e:
        logger.error(f"❌ Error opening folder: {e}")

async def play_file(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
        logger.info(f"📄 Opened file: {path}")
    except Exception as e:
        logger.error(f"❌ Error opening file: {e}")

async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder created: {path}"
    except Exception as e:
        return f"❌ Error creating folder: {e}"

async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        # Update cache if item was cached
        for key, cached_path in list(path_finder.cache.items()):
            if cached_path == old_path:
                path_finder.cache[key] = new_path
                break
        path_finder.save_cache()
        return f"✅ Renamed to: {new_path}"
    except Exception as e:
        return f"❌ Rename failed: {e}"

async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        
        # Remove from cache if it was cached
        for key, cached_path in list(path_finder.cache.items()):
            if cached_path == path:
                del path_finder.cache[key]
                break
        path_finder.save_cache()
        
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete failed: {e}"

# App control
@function_tool
async def open(app_title: str) -> str:
    app_title = app_title.lower().strip()
    app_command = APP_MAPPINGS.get(app_title, app_title)
    try:
        await asyncio.create_subprocess_shell(f'start "" "{app_command}"', shell=True)
        focused = await focus_window(app_title)
        if focused:
            return f"🚀 App launched and focused: {app_title}"
        else:
            return f"🚀 App launched: {app_title} (couldn't focus window)"
    except Exception as e:
        return f"❌ Failed to launch {app_title}: {e}"

@function_tool
async def close(window_title: str) -> str:
    if not win32gui:
        return "❌ win32gui not available"

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    win32gui.EnumWindows(enumHandler, None)
    return f"🔄 Attempted to close window: {window_title}"

# Enhanced Jarvis command logic
@function_tool
async def folder_file(command: str) -> str:
    """Enhanced folder/file operations with smart path finding"""
    command_lower = command.lower().strip()
    
    # Extract the actual folder/file name from command
    search_terms = ["open", "folder", "file", "find", "search", "in", "drive", "c", "d", "e"]
    
    # Clean command to get the actual item name
    clean_command = command_lower
    for term in search_terms:
        clean_command = clean_command.replace(term, " ").strip()
    
    # Remove extra spaces
    clean_command = " ".join(clean_command.split())
    
    logger.info(f"🔍 Searching for: '{clean_command}'")
    
    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name)
        return await create_folder(path)

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split("to")
        if len(parts) == 2:
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            
            # Search for the item to rename
            item = await path_finder.smart_search(old_name)
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]), new_name)
                return await rename_item(item["path"], new_path)
            else:
                return f"❌ Could not find item to rename: {old_name}"
        return "❌ Invalid rename command format. Use: rename [old_name] to [new_name]"

    if "delete" in command_lower:
        item_name = command_lower.replace("delete", "").strip()
        item = await path_finder.smart_search(item_name)
        if item:
            return await delete_item(item["path"])
        return f"❌ Could not find item to delete: {item_name}"

    # Smart search for the item
    item = await path_finder.smart_search(clean_command)
    
    if item:
        if item["type"] == "folder":
            await open_folder(item["path"])
            return f"✅ Opened folder: {item['name']} at {item['path']}"
        else:
            await play_file(item["path"])
            return f"✅ Opened file: {item['name']} at {item['path']}"
    
    return f"❌ Could not find '{clean_command}' in common locations. Try being more specific or check if the item exists."

# Manual cache refresh function
@function_tool
async def refresh_cache() -> str:
    """Manually refresh the path cache"""
    path_finder.cache.clear()
    path_finder.save_cache()
    return "🔄 Path cache cleared. Next search will rebuild the cache."