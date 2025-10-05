#!/usr/bin/env python3
"""
Stonic Integrated Launcher
This script starts the integrated Stonic web server with agent capabilities.
"""

import sys
import os
import webbrowser
import time
import threading

def open_browser():
    """Open the browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    print("🤖 Starting Stonic Integrated System...")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        'jarvis_integrated.py',
        'jarvis-ui/index.html',
        'jarvis-ui/script.js',
        'jarvis-ui/styles.css'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are present in the current directory.")
        return False
    
    print("✅ All required files found")
    print("🚀 Starting Stonic Web Server...")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Import and run the integrated server
        from stonic_integrated import start_server
        print("🌐 Server starting on http://localhost:5000")
        print("📱 UI will open automatically in your browser")
        print("🎤 Use the 'Start Agent' button to enable voice interaction")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        start_server(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Stonic...")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 