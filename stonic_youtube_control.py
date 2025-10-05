import re
import asyncio
from livekit.agents import function_tool
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import os
import logging
import time
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
EDGE_DRIVER_PATH = r"C:\Users\Nikhil Pathak\Downloads\edgedriver_win64\msedgedriver.exe"
YOUTUBE_SHORTCUT = r"C:\Users\Nikhil Pathak\OneDrive\Desktop\YouTube.lnk"
TIMEOUT = 15  # seconds

def get_driver():
    try:
        options = Options()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Reduce console spam

        if not os.path.exists(EDGE_DRIVER_PATH):
            return None, "Edge driver not found. Please check the driver path."

        service = EdgeService(executable_path=EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
        return driver, None
    except Exception as e:
        logger.error(f"Failed to initialize driver: {str(e)}")
        return None, f"Failed to initialize browser: {str(e)}"

async def _perform_youtube_search_and_play(driver, query, play_first=True):
    """
    Navigate to YouTube search and optionally play the first result.
    Returns a tuple (success: bool, message: str)
    """
    try:
        encoded = quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        driver.get(url)

        wait = WebDriverWait(driver, TIMEOUT)
        links = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
        )

        if not links:
            return False, f"❌ No videos found for '{query}'"

        if play_first:
            first = links[0]
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title")))
                try:
                    first.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", first)
                time.sleep(2)
                return True, f"✅ Playing '{query}' on YouTube"
            except TimeoutException:
                try:
                    driver.execute_script("arguments[0].click();", first)
                    time.sleep(2)
                    return True, f"✅ Playing '{query}' on YouTube (clicked via JS)"
                except Exception as e:
                    logger.error(f"Click failed after timeout: {e}")
                    return False, f"❌ Failed to play '{query}': {e}"
        else:
            return True, f"✅ Showing YouTube search results for '{query}'"

    except TimeoutException:
        return False, f"❌ Timeout while loading results for '{query}'"
    except Exception as e:
        logger.error(f"Error in search/play helper: {e}")
        return False, f"❌ Error while searching/playing '{query}': {e}"

@function_tool
async def YouTube_control(command: str) -> str:
    if not command:
        return "Please provide a YouTube command."

    command = command.lower().strip()

    # Patterns
    play_patterns = [
        r"open youtube and play (.+)",
        r"youtube kholo aur (.+) bajao",
        r"youtube kholo aur (.+) chalao",
        r"play (.+) on youtube",
        r"play song (.+) on youtube",
        r"youtube pe (.+) chalao",
        r"youtube par (.+) bajao",
        r"play (.+)$",
    ]

    search_patterns = [
        r"open youtube and search (.+)",
        r"youtube kholo aur (.+) khojo",
        r"youtube kholo aur (.+) dhundo",
        r"search (.+) on youtube",
        r"youtube pe (.+) dhundo",
        r"youtube par (.+) khojo",
        r"search (.+)$",
    ]

    # Play patterns
    for pattern in play_patterns:
        if match := re.search(pattern, command):
            query = match.group(1).strip()
            driver, error = get_driver()
            if error:
                if os.path.exists(YOUTUBE_SHORTCUT):
                    try:
                        subprocess.Popen([YOUTUBE_SHORTCUT], shell=True)
                        return f"❗ Edge driver not available locally, launched YouTube app. Driver error: {error}"
                    except Exception:
                        return f"❌ {error}"
                return f"❌ {error}"

            success, msg = await _perform_youtube_search_and_play(driver, query, play_first=True)
            # DO NOT quit driver → keeps browser open
            return msg

    # Search patterns
    for pattern in search_patterns:
        if match := re.search(pattern, command):
            query = match.group(1).strip()
            driver, error = get_driver()
            if error:
                if os.path.exists(YOUTUBE_SHORTCUT):
                    try:
                        subprocess.Popen([YOUTUBE_SHORTCUT], shell=True)
                        return f"❗ Edge driver not available; opened YouTube app. Driver error: {error}"
                    except Exception:
                        return f"❌ {error}"
                return f"❌ {error}"

            success, msg = await _perform_youtube_search_and_play(driver, query, play_first=False)
            # DO NOT quit driver → keeps browser open
            return msg

    # Just open YouTube
    if re.fullmatch(r"(open youtube|youtube kholo|open youtube app)", command):
        if not os.path.exists(YOUTUBE_SHORTCUT):
            return "❌ YouTube shortcut not found. Please check the path."

        try:
            subprocess.Popen([YOUTUBE_SHORTCUT], shell=True)
            return "✅ YouTube app launched successfully!"
        except Exception as e:
            logger.error(f"Failed to launch YouTube app: {str(e)}")
            return f"❌ Failed to launch YouTube app: {str(e)}"

    return "❓ Invalid YouTube command. Please try again."
