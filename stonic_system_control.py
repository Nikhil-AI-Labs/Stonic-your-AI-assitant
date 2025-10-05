# Jarvis_system_control.py
import os
import logging
from livekit.agents import function_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detect Hindi (Devanagari script)
def is_hindi(text: str) -> bool:
    devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return devanagari_count > len(text) // 4

@function_tool
def system_shutdown(command: str = "") -> str:
    """Shutdown the computer (Windows only). Accepts Hindi and English commands."""
    try:
        os.system('shutdown /s /t 1')
        logger.info("Shutdown command executed.")
        return "🛑 सिस्टम शटडाउन शुरू कर दिया गया है।" if is_hindi(command) else "🛑 System shutdown initiated."
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")
        return f"❌ शटडाउन असफल रहा: {e}" if is_hindi(command) else f"❌ Shutdown failed: {e}"

@function_tool
def system_restart(command: str = "") -> str:
    """Restart the computer (Windows only). Accepts Hindi and English commands."""
    try:
        os.system('shutdown /r /t 1')
        logger.info("Restart command executed.")
        return "🔄 सिस्टम रीस्टार्ट शुरू कर दिया गया है।" if is_hindi(command) else "🔄 System restart initiated."
    except Exception as e:
        logger.error(f"Restart failed: {e}")
        return f"❌ रीस्टार्ट असफल रहा: {e}" if is_hindi(command) else f"❌ Restart failed: {e}"

@function_tool
def system_lock(command: str = "") -> str:
    """Lock the computer (Windows only). Accepts Hindi and English commands."""
    try:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        logger.info("Lock command executed.")
        return "🔒 सिस्टम लॉक कर दिया गया है।" if is_hindi(command) else "🔒 System locked."
    except Exception as e:
        logger.error(f"Lock failed: {e}")
        return f"❌ लॉक असफल रहा: {e}" if is_hindi(command) else f"❌ Lock failed: {e}"
