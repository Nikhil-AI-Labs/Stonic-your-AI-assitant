# 🤖 Stonic AI Assistant 2.0

A powerful AI assistant with an integrated web-based GUI interface, combining LiveKit voice capabilities with a modern sci-fi themed web interface.

## ✨ Features

### 🎤 Voice & AI Capabilities
- **LiveKit Integration**: Real-time voice communication with Google's AI models
- **Voice Recognition**: Natural language processing for commands
- **Multi-language Support**: English and Hindi command support
- **Sleep Mode**: Energy-saving sleep/wake functionality

### 🖥️ System Control
- **File Operations**: Open, close, and manage files and folders
- **Application Control**: Launch and control applications
- **System Commands**: Shutdown, restart, and lock system
- **Volume Control**: Adjust system volume with voice commands

### 🌐 Web & Media
- **Google Search**: Voice-activated web searches
- **YouTube Control**: Search and play videos
- **Weather Information**: Get current weather updates
- **Time & Date**: Real-time clock and date information

### 🎨 Creative Tools
- **Code Generation**: Generate code from natural language descriptions
- **Image Generation**: Create images using AI
- **Code Fixing**: Automatic code error detection and fixing
- **File Management**: Advanced file operations and monitoring

### 🎮 Input Control
- **Mouse Control**: Move cursor, click, scroll
- **Keyboard Control**: Type text, press keys, hotkeys
- **Gesture Support**: Swipe gestures and touch controls

## 🚀 Quick Start

### Method 1: Simple Launcher (Recommended)
```bash
python run_jarvis.py
```

### Method 2: Direct Agent Launch
```bash
python agent.py
```

### Method 3: Web Server Only
```bash
python jarvis_web_server.py
```

## 📋 Prerequisites

### Required Dependencies
Install all required packages:
```bash
pip install -r requirements.txt
```

### Key Dependencies
- `livekit-agents` - Voice AI capabilities
- `flask` & `flask-socketio` - Web interface
- `pyautogui` & `pynput` - System control
- `requests` - Web services
- `python-dotenv` - Environment management

## 🎯 Usage

### Starting Stonic
1. **Run the launcher**: `python run_jarvis.py`
2. **Browser opens automatically** to `http://localhost:5000`
3. **GUI interface loads** with sci-fi themed design
4. **Voice agent starts** in background

### Web Interface Features

#### 🎤 Voice Control
- **Listen Button**: Click to start voice recognition
- **Status Indicator**: Shows current state (Ready/Listening/Speaking)
- **Voice Visualization**: Real-time microphone wave display

#### 🖥️ Control Panel
- **Home**: Return to main interface
- **Documents**: Quick access to file operations
- **AI Mode**: Toggle advanced AI features
- **Listen**: Voice command activation
- **Logout**: Exit the interface

#### 💻 Terminal Mode
- **AI Mode Button**: Toggle terminal interface
- **Command Input**: Type commands directly
- **Response Display**: See Stonic responses in real-time

### Voice Commands

#### 🌐 Web & Information
```
"Search for [query]"
"Google [query]"
"What's the weather?"
"What time is it?"
"Play [video] on YouTube"
```

#### 🖥️ System Control
```
"Open [application]"
"Close [application]"
"Shutdown computer"
"Restart computer"
"Lock computer"
"Volume up/down/mute"
```

#### 🎨 Creative Tasks
```
"Generate code for [description]"
"Create image of [description]"
"Fix code errors"
"Save output"
```

#### 😴 Sleep Mode
```
"Stonic go to sleep"
"Wake up Stonic"
"Sleep mode"
```

#### 🎮 Input Control
```
"Move cursor to [position]"
"Click [location]"
"Type [text]"
"Press [key]"
```

## 🏗️ Architecture

### File Structure
```
jarvis 2.0/
├── agent.py              # Main agent with GUI integration
├── run_jarvis.py         # Simple launcher script
├── jarvis_web_server.py  # Web server (standalone)
├── jarvis-ui/           # Web interface files
│   ├── index.html       # Main HTML interface
│   ├── script.js        # JavaScript functionality
│   ├── styles.css       # Sci-fi styling
│   └── image.png        # AI core image
├── Jarvis_*.py          # Individual tool modules
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Components
- **LiveKit Agent**: Voice AI processing
- **Flask Web Server**: Web interface backend
- **Socket.IO**: Real-time communication
- **Tool Modules**: Individual functionality modules
- **Web UI**: Modern sci-fi themed interface

## 🔧 Configuration

### Environment Variables
Create a `.env` file for API keys:
```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
LIVEKIT_API_KEY=your_livekit_api_key
```

### Customization
- **UI Theme**: Modify `jarvis-ui/styles.css`
- **Commands**: Edit command processing in `agent.py`
- **Tools**: Add new tools to the `JarvisWebInterface` class

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

#### Missing Dependencies
```bash
pip install -r requirements.txt
```

#### Browser Not Opening
- Manually navigate to `http://localhost:5000`
- Check firewall settings
- Ensure port 5000 is available

#### Voice Not Working
- Check microphone permissions
- Verify LiveKit configuration
- Ensure Google API key is set

### Debug Mode
Run with debug logging:
```bash
python agent.py --debug
```

## 🔒 Security

- **Local Server**: Runs on localhost only
- **No External Access**: Web interface is local
- **API Key Protection**: Use environment variables
- **Secure Communication**: HTTPS for production

## 📈 Performance

### Optimization Tips
- **Close unused applications** for better performance
- **Use SSD storage** for faster file operations
- **Adequate RAM** (4GB+ recommended)
- **Stable internet** for web services

### Resource Usage
- **CPU**: Moderate (voice processing)
- **Memory**: ~200-500MB
- **Network**: Minimal (local server)
- **Storage**: ~50MB (application + dependencies)

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Make changes** and test thoroughly
4. **Submit pull request** with description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LiveKit** for voice AI capabilities
- **Google AI** for language models
- **Flask** for web framework
- **OpenAI** for creative AI tools

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with details
4. Include system information and error logs

---

**Made with ❤️ for AI enthusiasts** 