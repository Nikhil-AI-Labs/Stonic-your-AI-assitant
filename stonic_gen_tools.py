import os
import logging
import requests
from dotenv import load_dotenv
from livekit.agents import function_tool


def get_api_key(service: str) -> str:
    if service.lower() == "huggingface":
        return (
            os.getenv("HUGGINGFACE_API_TOKEN") or 
            os.getenv("HUGGINGFACE_API") or 
            "hf_ugBMfsQqgQlZmRSIwjeaqf8b1ce49880f3474eb83577b15401db669ca909869b5aca73148ebbc6790662eqXzGtEgSENZpf"
        )
    elif service.lower() == "groq":
        return os.getenv("GROQ_API_KEY", "")
    return ""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper to detect Hindi (Devanagari script)
def is_hindi(text: str) -> bool:
    devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return devanagari_count > len(text) // 4

# IMAGE GENERATOR TOOL - Using Hugging Face API
@function_tool
def generate_image(prompt: str) -> str:
    """Generate an image from a prompt (Hindi or English) using Hugging Face API. Returns image URL or file path."""
    hf_token = get_api_key("huggingface")
    
    if not hf_token:
        return "❌ Hugging Face API token missing. Please check your configuration."
    
    # Translate Hindi to English if needed
    if is_hindi(prompt):
        try:
            trans = requests.post(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "hi", "tl": "en", "dt": "t", "q": prompt}
            )
            prompt_en = trans.json()[0][0][0]
        except Exception:
            prompt_en = prompt
    else:
        prompt_en = prompt

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt_en,
        "parameters": {
            "negative_prompt": "blurry, bad quality, distorted, ugly, deformed, pixelated, low resolution, oversaturated, undersaturated",
            "num_inference_steps": 30,  # Increased steps for better quality
            "guidance_scale": 8.5,  # Adjusted for better adherence to prompt
            "width": 1024,  # Increased resolution
            "height": 1024,
            "seed": int(time.time()),  # Random seed for variety
            "safety_checker": True,
            "enhance_prompt": True,
            "upscale": True
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)  # Increased timeout

        if response.status_code == 200:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            
            # Create images directory if it doesn't exist
            os.makedirs("generated_images", exist_ok=True)
            filepath = os.path.join("generated_images", filename)

            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return f"🖼️ Image generated successfully!\n📂 Saved as: {filepath}" if not is_hindi(prompt) else f"🖼️ आपकी image तैयार है!\n📂 यहाँ सेव की गई: {filepath}"
            else:
                try:
                    json_data = response.json()
                    image_url = json_data.get("url") or json_data.get("image_url")
                    if image_url:
                        # Download image from URL
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(img_response.content)
                            return f"🖼️ Image generated and downloaded!\n📂 Saved as: {filepath}"
                    return f"❌ Unexpected response: {json_data}"
                except Exception as e:
                    return f"❌ Failed to process image: {e}"
        
        elif response.status_code == 503:
            return "⏳ Model is loading, please try again in a few seconds." if not is_hindi(prompt) else "⏳ मॉडल लोड हो रहा है, कृपया कुछ सेकंड बाद दोबारा कोशिश करें।"
        else:
            try:
                error_msg = response.json().get('error', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            return f"❌ Image generation failed: {error_msg}" if not is_hindi(prompt) else f"❌ इमेज जनरेट नहीं हो पाई: {error_msg}"

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return f"❌ Image generation failed: {e}" if not is_hindi(prompt) else f"❌ इमेज जनरेट नहीं हो पाई: {e}"

# Alternative image generation function with different models
@function_tool
def generate_image_alternative(prompt: str, model: str = "runwayml/stable-diffusion-v1-5") -> str:
    """Generate image with custom model selection from Hugging Face."""
    # Get Hugging Face API key
    hf_token = get_api_key("huggingface")
    
    if not hf_token:
        return "❌ Hugging Face API token missing. Please check your configuration."
    
    # Translate Hindi to English if needed
    if is_hindi(prompt):
        try:
            trans = requests.post(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "hi", "tl": "en", "dt": "t", "q": prompt}
            )
            prompt_en = trans.json()[0][0][0]
        except Exception:
            prompt_en = prompt
    else:
        prompt_en = prompt
    
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt_en}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            
            with open(filename, "wb") as f:
                f.write(response.content)
            
            if is_hindi(prompt):
                return f"🖼️ आपकी image '{filename}' में तैयार है।"
            else:
                return f"🖼️ Image saved as '{filename}'."
        else:
            if is_hindi(prompt):
                return f"❌ इमेज जनरेट नहीं हो पाई: Status {response.status_code}"
            else:
                return f"❌ Image generation failed: Status {response.status_code}"
                
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        if is_hindi(prompt):
            return f"❌ इमेज जनरेट नहीं हो पाई: {e}"
        else:
            return f"❌ Image generation failed: {e}"

# CODE GENERATOR TOOL - Updated to use Groq API
@function_tool
def generate_code(prompt: str, language: str = "python") -> str:
    """Generate code from a prompt (Hindi or English) using Groq API. Returns code as string."""
    # Get Groq API key
    groq_api_key = get_api_key("groq")
    
    if not groq_api_key:
        return "❌ Groq API key missing. Get one from https://console.groq.com and set it in api_config.py"
    
    # Translate Hindi to English if needed
    if is_hindi(prompt):
        try:
            trans = requests.post(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "hi", "tl": "en", "dt": "t", "q": prompt}
            )
            prompt_en = trans.json()[0][0][0]
        except Exception:
            prompt_en = prompt
    else:
        prompt_en = prompt
    
    # Create a more specific prompt for code generation
    code_prompt = f"""Write a {language} program that {prompt_en}. 
Please provide only clean, working code with minimal comments. 
Make sure the code is properly formatted and follows best practices."""
    
    # Call Groq API
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-70b-versatile",  # Using Llama 3.1 70B for better code generation
                "messages": [
                    {
                        "role": "system", 
                        "content": f"You are an expert {language} programmer. Generate clean, efficient, and well-structured code. Only return the code without explanations unless specifically asked."
                    },
                    {
                        "role": "user", 
                        "content": code_prompt
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.1,  # Low temperature for more consistent code generation
                "top_p": 1,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            code = data["choices"][0]["message"]["content"]
            
            # Save code to file
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_code_{timestamp}.{_get_file_extension(language)}"
            
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(code)
            except Exception as save_error:
                logger.warning(f"Could not save code to file: {save_error}")
            
            if is_hindi(prompt):
                return f"💻 आपका {language} कोड तैयार है:\n\n```{language}\n{code}\n```\n\n📁 कोड '{filename}' में भी सेव किया गया है।"
            else:
                return f"💻 Here is your {language} code:\n\n```{language}\n{code}\n```\n\n📁 Code also saved as '{filename}'."
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
            
            if is_hindi(prompt):
                return f"❌ कोड जनरेट नहीं हो पाया: {error_msg}"
            else:
                return f"❌ Code generation failed: {error_msg}"
                
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        if is_hindi(prompt):
            return f"❌ कोड जनरेट नहीं हो पाया: {e}"
        else:
            return f"❌ Code generation failed: {e}"

# Helper function to get file extension based on language
def _get_file_extension(language: str) -> str:
    """Get appropriate file extension for programming language."""
    extensions = {
        "python": "py",
        "javascript": "js",
        "java": "java",
        "cpp": "cpp",
        "c++": "cpp",
        "c": "c",
        "html": "html",
        "css": "css",
        "php": "php",
        "ruby": "rb",
        "go": "go",
        "rust": "rs",
        "swift": "swift",
        "kotlin": "kt",
        "typescript": "ts",
        "bash": "sh",
        "shell": "sh",
        "sql": "sql",
        "r": "r",
        "matlab": "m",
        "scala": "scala",
        "perl": "pl",
        "lua": "lua",
        "dart": "dart",
        "json": "json",
        "xml": "xml",
        "yaml": "yml",
        "dockerfile": "dockerfile"
    }
    return extensions.get(language.lower(), "txt")

# Enhanced code generation with specific model selection
@function_tool
def generate_code_advanced(prompt: str, language: str = "python", model: str = "llama-3.1-70b-versatile") -> str:
    """Advanced code generation with custom model selection using Groq API."""
    # Get Groq API key
    groq_api_key = get_api_key("groq")
    
    if not groq_api_key:
        return "❌ Groq API key missing. Get one from https://console.groq.com and set it in api_config.py"
    
    # Available Groq models
    available_models = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant", 
        "llama-3.2-11b-text-preview",
        "llama-3.2-3b-preview",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    if model not in available_models:
        model = "llama-3.1-70b-versatile"  # Default fallback
    
    # Translate Hindi to English if needed
    if is_hindi(prompt):
        try:
            trans = requests.post(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "hi", "tl": "en", "dt": "t", "q": prompt}
            )
            prompt_en = trans.json()[0][0][0]
        except Exception:
            prompt_en = prompt
    else:
        prompt_en = prompt
    
    # Create detailed system prompt
    system_prompt = f"""You are an expert {language} developer with years of experience. 
Generate clean, efficient, production-ready code that follows best practices and industry standards.
Include error handling where appropriate and write self-documenting code.
Only return the code without additional explanations unless specifically requested."""
    
    user_prompt = f"Create a {language} solution for: {prompt_en}"
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.9,
                "stream": False
            },
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            code = data["choices"][0]["message"]["content"]
            
            # Save code to file
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_code_{timestamp}.{_get_file_extension(language)}"
            
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(code)
            except Exception as save_error:
                logger.warning(f"Could not save code to file: {save_error}")
            
            if is_hindi(prompt):
                return f"🚀 आपका एडवांस {language} कोड ({model} मॉडल से) तैयार है:\n\n```{language}\n{code}\n```\n\n📁 कोड '{filename}' में सेव किया गया है।"
            else:
                return f"🚀 Your advanced {language} code (generated using {model}):\n\n```{language}\n{code}\n```\n\n📁 Code saved as '{filename}'."
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
            
            if is_hindi(prompt):
                return f"❌ एडवांस कोड जनरेट नहीं हो पाया: {error_msg}"
            else:
                return f"❌ Advanced code generation failed: {error_msg}"
                
    except Exception as e:
        logger.error(f"Advanced code generation failed: {e}")
        if is_hindi(prompt):
            return f"❌ एडवांस कोड जनरेट नहीं हो पाया: {e}"
        else:
            return f"❌ Advanced code generation failed: {e}"

@function_tool
def save_output(content: str, file_type: str = "txt") -> str:
    """Save the given content to a file. Supports Hindi and English commands."""
    import datetime
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if file_type == "code":
        filename = f"saved_code_{now}.txt"
    elif file_type == "image":
        filename = f"saved_image_url_{now}.txt"
    else:
        filename = f"saved_output_{now}.{file_type}"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        if is_hindi(content):
            return f"💾 आपकी जानकारी '{filename}' में सेव कर दी गई है।"
        else:
            return f"💾 Your content has been saved to '{filename}'."
    except Exception as e:
        if is_hindi(content):
            return f"❌ सेव करने में समस्या: {e}"
        else:
            return f"❌ Error saving file: {e}"