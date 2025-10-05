import os
import json
import logging
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import queue
import time

# Import your existing Stonic components
from stonic_state import set_sleep_state, get_sleep_state, is_jarvis_sleeping
from stonic_google_search import google_search, get_current_datetime
from stonic_get_whether import get_weather
from stonic_window_CTRL import open, close, folder_file
from stonic_file_opner import Play_file
from stonic_youtube_control import YouTube_control
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool,
    press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
)
from stonic_gen_tools import generate_image, generate_image_alternative, generate_code_advanced, generate_code, save_output
from stonic_system_control import system_shutdown, system_restart, system_lock
from stonic_code_fixer import check_code_errors, paste_fixed_code, start_code_monitoring, stop_code_monitoring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state management
jarvis_state = {
    'is_listening': False,
    'is_speaking': False,
    'current_status': 'Ready',
    'last_command': '',
    'last_response': '',
    'sleep_state': False
}

# Command queue for processing
command_queue = queue.Queue()
response_queue = queue.Queue()

class JarvisWebInterface:
    def __init__(self):
        self.tools = {
            'google_search': google_search,
            'get_current_datetime': get_current_datetime,
            'get_weather': get_weather,
            'open': open,
            'close': close,
            'folder_file': folder_file,
            'play_file': Play_file,
            'youtube_control': YouTube_control,
            'move_cursor': move_cursor_tool,
            'mouse_click': mouse_click_tool,
            'scroll_cursor': scroll_cursor_tool,
            'type_text': type_text_tool,
            'press_key': press_key_tool,
            'press_hotkey': press_hotkey_tool,
            'control_volume': control_volume_tool,
            'swipe_gesture': swipe_gesture_tool,
            'generate_image': generate_image,
            'generate_code': generate_code,
            'generate_code_advanced': generate_code_advanced,
            'save_output': save_output,
            'system_shutdown': system_shutdown,
            'system_restart': system_restart,
            'system_lock': system_lock,
            'check_code_errors': check_code_errors,
            'paste_fixed_code': paste_fixed_code,
            'start_code_monitoring': start_code_monitoring,
            'stop_code_monitoring': stop_code_monitoring,
            'set_sleep_state': set_sleep_state,
            'get_sleep_state': get_sleep_state,
            'is_jarvis_sleeping': is_jarvis_sleeping
        }
    
    def process_command(self, command):
        """Process user commands and return responses"""
        try:
            # Check sleep state first
            sleep_state = get_sleep_state()
            jarvis_state['sleep_state'] = sleep_state
            
            if sleep_state:
                # Check for wake-up commands
                wake_commands = ["wake up stonic", "uth jao", "jaago", "stonic uth jao", "wake up stonic"]
                if any(wake_cmd in command.lower() for wake_cmd in wake_commands):
                    set_sleep_state(False)
                    jarvis_state['sleep_state'] = False
                    return "Stonic is now awake and ready to assist you."
                else:
                    return None  # Silent in sleep mode
            
            # Process commands when awake
            command_lower = command.lower()
            
            # Sleep commands
            sleep_commands = ["stonic go to sleep", "so jao", "sone chalo", "sleep now", "stonic so jao", "sleep mode", "sleep stonic", "chup ho jao"]
            if any(sleep_cmd in command_lower for sleep_cmd in sleep_commands):
                set_sleep_state(True)
                jarvis_state['sleep_state'] = True
                return "Going to sleep mode..."
            
            # Weather commands
            if "weather" in command_lower or "mausam" in command_lower:
                return get_weather()
            
            # Time commands
            if "time" in command_lower or "samay" in command_lower or "kitne baje" in command_lower:
                return get_current_datetime()
            
            # Google search
            if "search" in command_lower or "google" in command_lower or "dhundho" in command_lower:
                # Extract search query
                search_terms = ["search for", "google", "dhundho"]
                query = command
                for term in search_terms:
                    if term in command_lower:
                        query = command[command_lower.find(term) + len(term):].strip()
                        break
                return google_search(query)
            
            # YouTube commands
            if "youtube" in command_lower or "video" in command_lower:
                # Extract video query
                video_terms = ["play", "search", "dikhao"]
                query = command
                for term in video_terms:
                    if term in command_lower:
                        query = command[command_lower.find(term) + len(term):].strip()
                        break
                return YouTube_control(query)
            
            # File operations
            if "open" in command_lower or "kholo" in command_lower:
                # Extract file/app name
                open_terms = ["open", "kholo"]
                target = command
                for term in open_terms:
                    if term in command_lower:
                        target = command[command_lower.find(term) + len(term):].strip()
                        break
                return open(target)
            
            # Volume control
            if "volume" in command_lower or "aawaz" in command_lower:
                if "up" in command_lower or "badhao" in command_lower:
                    return control_volume_tool("up")
                elif "down" in command_lower or "kam karo" in command_lower:
                    return control_volume_tool("down")
                elif "mute" in command_lower or "band karo" in command_lower:
                    return control_volume_tool("mute")
            
            # System controls
            if "shutdown" in command_lower or "band karo" in command_lower:
                return system_shutdown()
            elif "restart" in command_lower or "restart karo" in command_lower:
                return system_restart()
            elif "lock" in command_lower or "lock karo" in command_lower:
                return system_lock()
            
            # Code generation
            if "generate code" in command_lower or "code banao" in command_lower:
                # Extract code description
                code_terms = ["generate code", "code banao"]
                description = command
                for term in code_terms:
                    if term in command_lower:
                        description = command[command_lower.find(term) + len(term):].strip()
                        break
                return generate_code(description)
            
            # Image generation
            if "generate image" in command_lower or "image banao" in command_lower:
                # Extract image description
                image_terms = ["generate image", "image banao"]
                description = command
                for term in image_terms:
                    if term in command_lower:
                        description = command[command_lower.find(term) + len(term):].strip()
                        break
                return generate_image(description)
            
            # Default response for unrecognized commands
            return f"I understand you said: '{command}'. I'm still learning to process this type of request. Please try a different command or be more specific."
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I encountered an error while processing your command: {str(e)}"

# Initialize Stonic interface
jarvis_interface = JarvisWebInterface()

@app.route('/')
def index():
    """Serve the main Stonic UI"""
    return send_from_directory('jarvis-ui', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from jarvis-ui directory"""
    return send_from_directory('jarvis-ui', filename)

@app.route('/api/status')
def get_status():
    """Get current Stonic status"""
    return jsonify({
        'status': jarvis_state['current_status'],
        'is_listening': jarvis_state['is_listening'],
        'is_speaking': jarvis_state['is_speaking'],
        'sleep_state': jarvis_state['sleep_state'],
        'last_command': jarvis_state['last_command'],
        'last_response': jarvis_state['last_response']
    })

@app.route('/api/command', methods=['POST'])
def process_command():
    """Process a command from the web interface"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Update state
        jarvis_state['last_command'] = command
        jarvis_state['current_status'] = 'Processing'
        
        # Process command
        response = jarvis_interface.process_command(command)
        
        if response:
            jarvis_state['last_response'] = response
            jarvis_state['current_status'] = 'Ready'
            
            # Emit response to connected clients
            socketio.emit('jarvis_response', {
                'command': command,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'response': response,
                'status': jarvis_state['current_status']
            })
        else:
            # Silent response (sleep mode)
            jarvis_state['current_status'] = 'Ready'
            return jsonify({
                'success': True,
                'response': '',
                'status': jarvis_state['current_status'],
                'silent': True
            })
            
    except Exception as e:
        logger.error(f"Error in process_command: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/listen', methods=['POST'])
def toggle_listening():
    """Toggle listening mode"""
    try:
        data = request.get_json()
        should_listen = data.get('listen', False)
        
        if should_listen:
            jarvis_state['is_listening'] = True
            jarvis_state['current_status'] = 'Listening'
        else:
            jarvis_state['is_listening'] = False
            jarvis_state['current_status'] = 'Ready'
        
        # Emit status update
        socketio.emit('status_update', {
            'is_listening': jarvis_state['is_listening'],
            'status': jarvis_state['current_status']
        })
        
        return jsonify({
            'success': True,
            'is_listening': jarvis_state['is_listening'],
            'status': jarvis_state['current_status']
        })
        
    except Exception as e:
        logger.error(f"Error in toggle_listening: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sleep', methods=['POST'])
def toggle_sleep():
    """Toggle sleep mode"""
    try:
        data = request.get_json()
        should_sleep = data.get('sleep', False)
        
        set_sleep_state(should_sleep)
        jarvis_state['sleep_state'] = should_sleep
        
        if should_sleep:
            jarvis_state['current_status'] = 'Sleeping'
        else:
            jarvis_state['current_status'] = 'Ready'
        
        # Emit status update
        socketio.emit('status_update', {
            'sleep_state': jarvis_state['sleep_state'],
            'status': jarvis_state['current_status']
        })
        
        return jsonify({
            'success': True,
            'sleep_state': jarvis_state['sleep_state'],
            'status': jarvis_state['current_status']
        })
        
    except Exception as e:
        logger.error(f"Error in toggle_sleep: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('status_update', {
        'is_listening': jarvis_state['is_listening'],
        'is_speaking': jarvis_state['is_speaking'],
        'status': jarvis_state['current_status'],
        'sleep_state': jarvis_state['sleep_state']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

@socketio.on('command')
def handle_command(data):
    """Handle commands from WebSocket"""
    command = data.get('command', '').strip()
    if command:
        response = jarvis_interface.process_command(command)
        if response:
            emit('jarvis_response', {
                'command': command,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })

def start_server(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask server"""
    logger.info(f"Starting Stonic Web Server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_server(debug=True) 