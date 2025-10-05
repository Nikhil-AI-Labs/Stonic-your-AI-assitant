import json
import os
import re
import logging
from livekit.agents import function_tool

STATE_FILE = os.path.abspath(r"C:\Users\Nikhil Pathak\OneDrive\Desktop\Stonic 2.0\sleep_state.json")  # Absolute path for safety

logger = logging.getLogger(__name__)

# Get the sleep state from file
@function_tool
async def get_sleep_state() -> bool:
    """Get the current sleep state of Stonic"""
    if not os.path.exists(STATE_FILE):
        logger.info("STATE_FILE not found, creating new file and assuming awake.")
        # Create the file if it doesn't exist
        try:
            with open(STATE_FILE, "w") as f:
                json.dump({"sleeping": False}, f)
        except Exception as e:
            logger.error(f"Error creating sleep state file: {e}")
        return False
    
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            sleeping = data.get("sleeping", False)
            logger.info(f"Read sleep state: {sleeping} from {STATE_FILE}")
            return sleeping
    except Exception as e:
        logger.error(f"Error reading sleep state file: {e}")
        return False

# Set sleep state to True or False
@function_tool
async def set_sleep_state(sleeping: bool):
    """Set the sleep state of Stonic"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"sleeping": sleeping}, f, indent=2)
        logger.info(f"Sleep state successfully set to: {sleeping} in {STATE_FILE}")
        
        # Verify the write was successful
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            actual_state = data.get("sleeping", False)
            logger.info(f"Verified sleep state in file: {actual_state}")
            
    except Exception as e:
        logger.error(f"Error writing sleep state file: {e}")

# Process sleep/wake commands - REMOVED from tools list
async def process_sleep_intent(command: str) -> str:
    """Process sleep/wake commands - internal function, not a tool"""
    command = command.lower()
    if re.search(r"\b(so jao|sone chalo|go to sleep|sleep now|stonic so jao|stonic go to sleep|sleep mode|sleep stonic|chup ho jao)\b", command):
        await set_sleep_state(True)
        return ""  # No response when going to sleep
    elif re.search(r"\b(uth jao|jaago|wake up|stonic uth jao|wake up stonic)\b", command):
        await set_sleep_state(False)
        return "Stonic is now awake."
    return ""

# Tool to provide sleep/awake status
@function_tool
async def is_jarvis_sleeping(query: str) -> str:
    """Check if Stonic is currently sleeping"""
    sleeping = await get_sleep_state()
    return "Yes, Stonic is sleeping." if sleeping else "No, Stonic is awake."