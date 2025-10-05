import asyncio
import re
import logging
import pyautogui
import pyperclip
import pygetwindow as gw
from livekit.agents import function_tool
import requests
import os
import cv2
import numpy as np
import time
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class CodeFixerCore:
    def __init__(self):
        self.monitoring = False
        self.last_analyzed_code = ""
        self.monitoring_thread = None
        self.tesseract_available = self._setup_tesseract()
        
    def _setup_tesseract(self):
        """Setup Tesseract OCR with automatic path detection"""
        try:
            import pytesseract
            
            # Try to detect Tesseract automatically
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
                r'tesseract',  # If in PATH
            ]
            
            for path in possible_paths:
                try:
                    if path == 'tesseract':
                        # Test if tesseract is in PATH
                        pytesseract.get_tesseract_version()
                        logger.info("✅ Tesseract found in PATH")
                        return True
                    elif os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        pytesseract.get_tesseract_version()
                        logger.info(f"✅ Tesseract found at: {path}")
                        return True
                except:
                    continue
            
            logger.warning("❌ Tesseract not found. Using clipboard fallback method.")
            return False
            
        except ImportError:
            logger.warning("❌ pytesseract not installed. Using clipboard fallback method.")
            return False
    
    def detect_language(self, code: str) -> str:
        """Enhanced language detection with better patterns"""
        code_lower = code.lower().strip()
        
        patterns = {
            'python': [
                r'def\s+\w+\s*\(',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'print\s*\(',
                r'if\s+__name__\s*==\s*["\']__main__["\']',
                r'class\s+\w+\s*:',
                r'#.*python',
                r'\.py\b'
            ],
            'cpp': [
                r'#include\s*<.*?>',
                r'using\s+namespace\s+std',
                r'\bcout\s*<<',
                r'\bcin\s*>>',
                r'int\s+main\s*\(',
                r'std::',
                r'#include\s*".*"'
            ],
            'java': [
                r'public\s+class\s+\w+',
                r'public\s+static\s+void\s+main',
                r'System\.out\.print',
                r'import\s+java\.',
                r'@Override',
                r'public\s+static'
            ],
            'javascript': [
                r'function\s+\w+\s*\(',
                r'console\.log',
                r'document\.',
                r'window\.',
                r'=>',
                r'const\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'let\s+\w+\s*='
            ],
            'html': [
                r'<html.*?>',
                r'<head.*?>',
                r'<body.*?>',
                r'<!DOCTYPE\s+html>',
                r'<div.*?>',
                r'<script.*?>'
            ],
            'css': [
                r'\.\w+\s*\{',
                r'#\w+\s*\{',
                r':\s*\w+;',
                r'@media',
                r'background-color',
                r'font-family'
            ]
        }
        
        # Count pattern matches
        for lang, lang_patterns in patterns.items():
            matches = sum(1 for pattern in lang_patterns if re.search(pattern, code, re.IGNORECASE))
            if matches >= 1:  # Lowered threshold for better detection
                return lang
        
        return 'python'  # Default to python if unknown

    def capture_code_from_screen(self) -> dict:
        """Main method to capture code from screen using multiple strategies"""
        logger.info("🔍 Capturing code from screen...")
        
        # Strategy 1: Try OCR if available
        if self.tesseract_available:
            code_text = self._capture_with_ocr()
            if code_text and len(code_text.strip()) > 10:
                return {
                    'success': True,
                    'code': code_text,
                    'method': 'OCR',
                    'message': "Code captured using OCR"
                }
        
        # Strategy 2: Use clipboard method
        logger.info("📋 Using clipboard capture method...")
        code_text = self._capture_from_clipboard()
        if code_text and len(code_text.strip()) > 5:
            return {
                'success': True,
                'code': code_text,
                'method': 'Clipboard',
                'message': "Code captured from clipboard"
            }
        
        # Strategy 3: Manual selection instruction
        return {
            'success': False,
            'code': '',
            'method': 'Manual',
            'message': """🔧 कृपया manually कोड select करें:
1. अपने कोड को select करें (Ctrl+A)
2. Copy करें (Ctrl+C)
3. दोबारा "Stonic check my code" कहें

📋 Please manually select your code:
1. Select your code (Ctrl+A)
2. Copy it (Ctrl+C)  
3. Say "Stonic check my code" again"""
        }

    def _capture_with_ocr(self) -> str:
        """Capture code using OCR from active editor"""
        try:
            import pytesseract
            
            # Find active code editor
            editors = self.find_code_editors()
            if not editors:
                logger.info("No code editor found for OCR")
                return ""
            
            editor_info = editors[0]
            window = editor_info['window']
            
            # Focus the window
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.5)
            
            # Capture screenshot of the editor
            region = (window.left, window.top, window.width, window.height)
            screenshot = pyautogui.screenshot(region=region)
            
            # Process image for better OCR
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            
            # Enhance image for better text recognition
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR with better configuration
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ(){}[].,;:=+-*/\'"#_<>!@$%^&|~`? \t\n'
            text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # Clean and format the captured text
            cleaned_text = self._clean_captured_code(text)
            
            logger.info(f"OCR captured {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"OCR capture failed: {e}")
            return ""

    def _capture_from_clipboard(self) -> str:
        """Capture code from clipboard with user instruction"""
        try:
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Show instruction message
            logger.info("📋 Waiting for user to copy code...")
            
            # Wait for clipboard change or timeout
            timeout = 10  # seconds
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                current_clipboard = pyperclip.paste()
                if current_clipboard != original_clipboard and len(current_clipboard.strip()) > 5:
                    logger.info("✅ New code detected in clipboard")
                    return current_clipboard
                time.sleep(0.5)
            
            # If no new content, return current clipboard
            current_clipboard = pyperclip.paste()
            if len(current_clipboard.strip()) > 5:
                return current_clipboard
            
            return ""
            
        except Exception as e:
            logger.error(f"Clipboard capture failed: {e}")
            return ""

    def _clean_captured_code(self, code_text: str) -> str:
        """Clean captured code text from OCR artifacts"""
        if not code_text:
            return ""
        
        # Remove non-printable characters but keep newlines and tabs
        code_text = ''.join(char for char in code_text if char.isprintable() or char in '\n\t')
        
        # Fix common OCR mistakes
        replacements = {
            'prlnt': 'print',
            'pr1nt': 'print',
            '1mport': 'import',
            'lmport': 'import',
            'deflnition': 'definition',
            'def1n': 'defin',
            '1f ': 'if ',
            'e1se': 'else',
            'wh1le': 'while',
            'c1ass': 'class',
            'se1f': 'self',
            'retu_rn': 'return',
            'retum': 'return',
        }
        
        for wrong, correct in replacements.items():
            code_text = code_text.replace(wrong, correct)
        
        # Clean up spacing around operators and punctuation
        code_text = re.sub(r'\s*([(){}[\],;:])\s*', r'\1', code_text)
        code_text = re.sub(r'\s*([=+\-*/])\s*', r' \1 ', code_text)
        
        # Normalize whitespace but preserve code structure
        lines = code_text.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip():  # Only process non-empty lines
                cleaned_lines.append(line.rstrip())
        
        return '\n'.join(cleaned_lines)

    def send_code_to_groq_ai(self, code: str, language: str = None) -> dict:
        """Send captured code to Groq AI for analysis and fixing"""
        if not GROQ_API_KEY:
            return {
                'success': False,
                'message': "❌ GROQ_API_KEY not found in environment variables"
            }
        
        if not code or len(code.strip()) < 3:
            return {
                'success': False,
                'message': "❌ No code to analyze"
            }
        
        # Auto-detect language if not provided
        if not language:
            language = self.detect_language(code)
        
        # Enhanced prompt for better analysis
        prompt = f"""You are Stonic, an expert code assistant. Analyze this {language} code for errors and provide fixes.

Code to analyze:
```{language}
{code}
```

Please provide a detailed response in both Hindi and English with:

1. **Error Detection (एरर खोजना):**
   - List all syntax errors, logical errors, and potential issues
   - Explain each error clearly

2. **Fixed Code (सुधारा गया कोड):**
   - Provide the complete corrected code
   - Ensure all errors are fixed

3. **Explanation (व्याख्या):**
   - Explain what was wrong and why
   - Provide best practices

4. **Summary (सारांश):**
   - Quick summary of changes made

Format your response clearly with sections and use code blocks for the fixed code."""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are Stonic, an expert code assistant who helps Indian developers. Always provide explanations in both Hindi and English. Be thorough in error detection and provide complete, working solutions."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Lower temperature for more consistent code analysis
            "max_tokens": 3000   # Increased for detailed analysis
        }

        try:
            logger.info("🤖 Sending code to Groq AI for analysis...")
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            ai_response = response.json()["choices"][0]["message"]["content"].strip()
            
            return {
                'success': True,
                'analysis': ai_response,
                'language': language,
                'original_code': code,
                'message': f"✅ Code analysis complete using Groq AI"
            }
            
        except Exception as e:
            logger.error(f"Groq AI request failed: {e}")
            return {
                'success': False,
                'message': f"❌ AI analysis failed: {e}"
            }

    def extract_fixed_code_from_ai_response(self, ai_response: str) -> str:
        """Extract the fixed code from AI response"""
        # Look for code blocks in the response
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', ai_response, re.DOTALL)
        
        if code_blocks:
            # Return the first substantial code block
            for block in code_blocks:
                if len(block.strip()) > 10:
                    return block.strip()
        
        # If no code blocks found, try to extract from sections
        lines = ai_response.split('\n')
        in_fixed_section = False
        fixed_code_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['fixed code', 'corrected code', 'सुधारा गया कोड']):
                in_fixed_section = True
                continue
            elif any(keyword in line.lower() for keyword in ['explanation', 'व्याख्या', 'summary', 'सारांश']):
                in_fixed_section = False
                continue
                
            if in_fixed_section and line.strip():
                # Skip markdown or header lines
                if not line.startswith('#') and not line.startswith('*'):
                    fixed_code_lines.append(line)
        
        if fixed_code_lines:
            return '\n'.join(fixed_code_lines).strip()
        
        return ""

    def find_code_editors(self):
        """Find active code editor windows including notebooks"""
        desktop_editors = ['Visual Studio Code', 'PyCharm', 'Sublime Text', 'Notepad++', 
                          'Atom', 'IntelliJ IDEA', 'Eclipse', 'Code', 'vim', 'emacs',
                          'WebStorm', 'PhpStorm', 'RubyMine', 'CLion', 'Thonny']
        
        notebook_keywords = [
            'jupyter', 'colab', 'kaggle', 'notebook',
            'localhost:8888', 'localhost:8889', 'localhost:8080',
            'colab.research.google.com', 'www.kaggle.com',
            'github.dev', 'codepen.io', 'repl.it', 'glitch.com'
        ]
        
        browsers = ['chrome', 'firefox', 'edge', 'safari', 'opera', 'brave']
        
        active_editors = []
        try:
            windows = gw.getAllWindows()
            for window in windows:
                if not window.visible or window.width < 100:
                    continue
                    
                window_title_lower = window.title.lower()
                
                # Check desktop editors
                for editor in desktop_editors:
                    if editor.lower() in window_title_lower:
                        active_editors.append({
                            'window': window,
                            'type': 'desktop',
                            'name': editor
                        })
                        break
                
                # Check for web-based notebooks in browsers
                is_browser = any(browser in window_title_lower for browser in browsers)
                if is_browser:
                    for keyword in notebook_keywords:
                        if keyword in window_title_lower:
                            active_editors.append({
                                'window': window,
                                'type': 'web_notebook',
                                'name': self._identify_notebook_type(window_title_lower)
                            })
                            break
                            
        except Exception as e:
            logger.error(f"Error finding editors: {e}")
        
        return active_editors
    
    def _identify_notebook_type(self, title_lower):
        """Identify the type of notebook from window title"""
        if 'colab' in title_lower:
            return 'Google Colab'
        elif 'kaggle' in title_lower:
            return 'Kaggle Notebook'
        elif 'jupyter' in title_lower or 'localhost' in title_lower:
            return 'Jupyter Notebook'
        elif 'github.dev' in title_lower:
            return 'GitHub Codespaces'
        else:
            return 'Web Notebook'

    def paste_code_to_active_window(self, text: str) -> bool:
        """Paste fixed code to active editor"""
        try:
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Copy new code to clipboard
            pyperclip.copy(text)
            time.sleep(0.2)
            
            # Find and focus active editor
            editors = self.find_code_editors()
            if editors:
                window = editors[0]['window']
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(0.3)
            
            # Select all and paste
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            
            # Restore original clipboard
            time.sleep(0.5)
            pyperclip.copy(original_clipboard)
            
            logger.info("✅ Code pasted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Paste failed: {e}")
            return False

# Initialize the core
code_fixer_core = CodeFixerCore()

@function_tool(name="check_and_fix_code", description="Capture code from screen and send to Groq AI for error detection and fixing")
async def check_and_fix_code() -> str:
    """
    Main function that captures code from screen and sends to Groq AI for analysis
    """
    try:
        logger.info("🚀 Stonic is analyzing your code...")
        
        # Step 1: Capture code from screen
        capture_result = code_fixer_core.capture_code_from_screen()
        
        if not capture_result['success']:
            return capture_result['message']
        
        code = capture_result['code']
        method = capture_result['method']
        
        logger.info(f"📝 Code captured using {method}: {len(code)} characters")
        
        # Step 2: Send to Groq AI for analysis
        ai_result = code_fixer_core.send_code_to_groq_ai(code)
        
        if not ai_result['success']:
            return ai_result['message']
        
        # Step 3: Format and return the response
        response = f"""🔧 **Stonic Code Analysis Complete**

**Capture Method:** {method}
**Language Detected:** {ai_result['language']}
**Code Length:** {len(code)} characters

---

{ai_result['analysis']}

---

✨ **क्या आप चाहते हैं कि मैं fixed code को आपके एडिटर में paste कर दूं?**
**Would you like me to paste the fixed code to your editor?**

बोलें "Stonic paste the code" / Say "Stonic paste the code"
"""
        
        # Store the result for pasting later
        code_fixer_core.last_analyzed_code = ai_result
        
        return response
        
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        return f"❌ कोड एनालिसिस में एरर: {e}\nCode analysis error: {e}"

@function_tool(name="paste_fixed_code", description="Paste the AI-fixed code to the active editor")
async def paste_fixed_code() -> str:
    """
    Paste the last AI-analyzed and fixed code to the active editor
    """
    try:
        if not code_fixer_core.last_analyzed_code:
            return "❌ कोई fixed code उपलब्ध नहीं है। पहले code analyze करें।\nNo fixed code available. Please analyze code first."
        
        ai_result = code_fixer_core.last_analyzed_code
        
        # Extract fixed code from AI response
        fixed_code = code_fixer_core.extract_fixed_code_from_ai_response(ai_result['analysis'])
        
        if not fixed_code:
            return "❌ AI response से fixed code extract नहीं हो सका।\nCouldn't extract fixed code from AI response."
        
        # Paste to active window
        success = code_fixer_core.paste_code_to_active_window(fixed_code)
        
        if success:
            return f"""✅ **Fixed Code Pasted Successfully!**

**Language:** {ai_result['language']}
**Fixed Code:**
```{ai_result['language']}
{fixed_code[:200]}{'...' if len(fixed_code) > 200 else ''}
```

🎉 **आपका code fix हो गया है!**
**Your code has been fixed!**"""
        else:
            return f"❌ Paste में समस्या हुई। कृपया manually copy करें:\n\n```{ai_result['language']}\n{fixed_code}\n```"
            
    except Exception as e:
        logger.error(f"Paste failed: {e}")
        return f"❌ Paste में एरर: {e}\nPaste error: {e}"

@function_tool(name="test_groq_connection", description="Test connection to Groq AI")
async def test_groq_connection() -> str:
    """Test if Groq AI connection is working"""
    test_result = code_fixer_core.send_code_to_groq_ai("print('hello world')", "python")
    
    if test_result['success']:
        return "✅ Groq AI connection working perfectly!\nGroq AI कनेक्शन सही तरीके से काम कर रहा है!"
    else:
        return f"❌ Groq AI connection failed: {test_result['message']}"