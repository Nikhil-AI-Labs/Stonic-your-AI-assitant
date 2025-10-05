# Stonic 2.0 Integrated System

This is an integrated version of Stonic that combines the web UI with the LiveKit agent for voice interaction.

## 🚀 Quick Start

1. **Run the integrated system:**
   ```bash
   python run_jarvis.py
   ```

2. **The web interface will automatically open in your browser**

3. **Use the UI to control Stonic:**
   - Click "Start Agent" to enable voice interaction
   - Use "Chat History" to view past conversations
   - Use "AI Mode" for terminal-style interaction
   - Use "Listen" for voice commands

## 🎯 Features

### Web Interface
- **Chat History**: View and manage conversation history
- **Agent Control**: Start/stop the LiveKit voice agent
- **AI Mode**: Terminal-style command interface
- **Voice Commands**: Real-time voice interaction
- **Status Monitoring**: Real-time status updates

### Voice Commands
- "Start agent" - Enable voice interaction
- "Stop agent" - Disable voice interaction
- "Weather" - Get current weather
- "Time" - Get current time
- "Search for [query]" - Google search
- "Open [app]" - Open applications
- "Volume up/down" - Control system volume
- "Generate code [description]" - Generate code
- "Generate image [description]" - Generate images

### Agent Integration
The system now properly integrates the web UI with the LiveKit agent:
- Web server handles UI and basic commands
- LiveKit agent handles voice interaction
- Seamless switching between modes
- Real-time status synchronization

## 📁 File Structure

```
jarvis 2.0/
├── run_jarvis.py              # Main launcher
├── jarvis_integrated.py       # Integrated server
├── agent.py                   # LiveKit agent
├── jarvis-ui/                 # Web interface
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   └── image.png
└── [other Jarvis modules]
```

## 🔧 How It Works

1. **Web Server** (`jarvis_integrated.py`):
   - Serves the UI
   - Handles basic commands
   - Manages agent process
   - Provides real-time updates

2. **LiveKit Agent** (`agent.py`):
   - Handles voice interaction
   - Processes voice commands
   - Provides real-time responses

3. **Integration**:
   - Web server can start/stop the agent
   - Both systems share the same tools
   - Real-time communication via WebSocket

## 🎮 Usage

### Starting the System
```bash
python run_jarvis.py
```

### Using Voice Commands
1. Click "Start Agent" in the UI
2. Wait for agent to initialize
3. Speak commands naturally
4. Agent will respond with voice and text

### Using Text Commands
1. Use the terminal in "AI Mode"
2. Type commands directly
3. Get instant responses

### Managing History
1. Click "Chat History" button
2. View all past conversations
3. History is automatically saved

## 🛠️ Troubleshooting

### Agent Won't Start
- Check if LiveKit is properly configured
- Ensure all dependencies are installed
- Check the console for error messages

### Web Interface Issues
- Clear browser cache
- Check if port 5000 is available
- Ensure all UI files are present

### Voice Issues
- Check microphone permissions
- Ensure audio drivers are working
- Try restarting the agent

## 🔄 Updates

The system now includes:
- ✅ Removed Home/Documents buttons
- ✅ Added Chat History functionality
- ✅ Integrated agent control
- ✅ Real-time status updates
- ✅ Seamless UI/Agent integration

## 📝 Notes

- The agent runs as a separate process for stability
- Chat history is stored locally in the browser
- All commands work in both voice and text modes
- The system maintains state between sessions 