import os
import re
import logging
import asyncio
import builtins
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import google, noise_cancellation
from datetime import datetime

# Your existing imports...
from stonic_prompts import behavior_prompts, Reply_prompts
from stonic_google_search import google_search, get_current_datetime
from stonic_get_whether import get_weather
from stonic_window_CTRL import open as open_window, close as close_window, folder_file
from stonic_file_opner import Play_file
from stonic_youtube_control import YouTube_control
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool,
    press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
)
from stonic_gen_tools import (
    generate_image, generate_image_alternative,
    generate_code_advanced, generate_code, save_output
)
from stonic_state import set_sleep_state, get_sleep_state, is_jarvis_sleeping
from stonic_system_control import system_shutdown, system_restart, system_lock
from stonic_code_fixer import (
    check_and_fix_code, paste_fixed_code, test_groq_connection
)
from stonic_schedule_manager import (
    get_todays_schedule, get_tomorrows_schedule,
    get_schedule_for_date, get_schedule_info
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NikhilPersonalAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=behavior_prompts,
            tools=[
                set_sleep_state, get_sleep_state, is_jarvis_sleeping,
                google_search, get_current_datetime,
                YouTube_control, get_weather, open_window, close_window, folder_file, Play_file,
                move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool,
                press_key_tool, press_hotkey_tool, control_volume_tool, swipe_gesture_tool,
                generate_image, generate_image_alternative, generate_code_advanced, generate_code, save_output,
                system_shutdown, system_restart, system_lock,
                check_and_fix_code, paste_fixed_code, test_groq_connection,
                get_todays_schedule, get_tomorrows_schedule, get_schedule_for_date, get_schedule_info,
            ]
        )


async def entrypoint(ctx: agents.JobContext):
    assistant = NikhilPersonalAssistant()
    
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Charon",
            temperature=0.2
        )
    )

    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True
        ),
    )

    await ctx.connect()
    await session.generate_reply(instructions=Reply_prompts)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
