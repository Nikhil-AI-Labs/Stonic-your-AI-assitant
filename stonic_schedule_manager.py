import os
import json
from datetime import datetime, timedelta
from livekit.agents import function_tool
import logging

logger = logging.getLogger(__name__)

# ✅ Your complete timetable data embedded in code
TIMETABLE_DATA = [
    # Monday
    {"day": "Monday", "time": "8:30-9:20", "subject": "Analog Circuits"},
    {"day": "Monday", "time": "9:30-10:20", "subject": "Signals and Systems"},
    {"day": "Monday", "time": "10:30-11:20", "subject": "Microprocessors and Microcontrollers"},
    {"day": "Monday", "time": "11:30-12:20", "subject": "Principles of Communication Systems"},
    {"day": "Monday", "time": "02:00-02:50", "subject": "Principles of Communication Systems Lab"},
    
    # Tuesday
    {"day": "Tuesday", "time": "8:30-9:20", "subject": "Signals and Systems"},
    {"day": "Tuesday", "time": "9:30-10:20", "subject": "Microprocessors and Microcontrollers"},
    {"day": "Tuesday", "time": "10:30-11:20", "subject": "Principles of Communication Systems"},
    {"day": "Tuesday", "time": "11:30-12:20", "subject": "Professional Ethics Economics and Business Management"},
    
    # Wednesday
    {"day": "Wednesday", "time": "8:30-9:20", "subject": "Signals and Systems"},
    {"day": "Wednesday", "time": "9:30-10:20", "subject": "Principles of Communication Systems"},
    {"day": "Wednesday", "time": "10:30-12:20", "subject": "Analog Circuits"},
    {"day": "Wednesday", "time": "2:00-2:50", "subject": "Professional Ethics Economics and Business Management"},
    {"day": "Wednesday", "time": "3:00-3:50", "subject": "Microprocessors and Microcontrollers"},
    
    # Thursday
    {"day": "Thursday", "time": "8:30-9:20", "subject": "Professional Ethics Economics and Business Management"},
    {"day": "Thursday", "time": "9:30-10:20", "subject": "Signals and Systems"},
    {"day": "Thursday", "time": "10:30-11:20", "subject": "Analog Circuits"},
    
    # Friday
    {"day": "Friday", "time": "8:30-10:30", "subject": "Microprocessors Lab"},
    {"day": "Friday", "time": "2:00-2:50", "subject": "Professional Ethics Economics and Business Management"},
    {"day": "Friday", "time": "3:00-3:50", "subject": "Analog Circuits"},
]

def get_classes_for_date(target_date):
    """Get classes for a specific date"""
    target_day = target_date.strftime("%A")  # Monday, Tuesday, etc.
    
    classes = []
    for entry in TIMETABLE_DATA:
        if entry['day'] == target_day:
            classes.append(entry)
    
    # Sort by time
    return sorted(classes, key=lambda x: x['time'])

def detect_language_from_query(query):
    """Detect if the query is in Hindi or English"""
    hindi_keywords = ['aaj', 'kal', 'kis', 'hai', 'class', 'classes', 'schedule', 'batao', 'kya', 'ki', 'ka']
    query_lower = query.lower()
    
    hindi_count = sum(1 for keyword in hindi_keywords if keyword in query_lower)
    return 'hindi' if hindi_count >= 2 else 'english'

def format_schedule_response(classes, language="english", date_str=""):
    """Format schedule response in specified language"""
    if language.lower() in ['hindi', 'hi']:
        return format_hindi_response(classes, date_str)
    else:
        return format_english_response(classes, date_str)

def format_english_response(classes, date_str=""):
    if not classes:
        return f"No classes scheduled for {date_str}."
    
    response = f"📅 **Schedule for {date_str}:**\n\n"
    
    for class_info in classes:
        time = class_info.get('time', 'Time not specified')
        subject = class_info.get('subject', 'Subject not specified')
        response += f"🕐 {time} - {subject}\n"
    
    return response

def format_hindi_response(classes, date_str=""):
    if not classes:
        date_hindi = "Aaj" if 'today' in date_str.lower() else "Kal" if 'tomorrow' in date_str.lower() else date_str
        return f"{date_hindi} koi class nahi hai."
    
    day_text = "Aaj ki" if 'today' in date_str.lower() else "Kal ki" if 'tomorrow' in date_str.lower() else f"{date_str} ki"
    response = f"📅 **{day_text} classes:**\n\n"
    
    for class_info in classes:
        time = class_info.get('time', 'Time not specified')
        subject = class_info.get('subject', 'Subject not specified')
        response += f"🕐 {time} - {subject}\n"
    
    return response

# ✅ Function tools for LiveKit Agent

@function_tool
async def get_todays_schedule(query: str = "") -> str:
    """Get today's class schedule
    
    Args:
        query: The user's original query to detect language preference
    """
    today = datetime.now()
    classes = get_classes_for_date(today)
    
    # Auto-detect language from query
    language = detect_language_from_query(query) if query else "english"
    
    return format_schedule_response(classes, language, "today")

@function_tool
async def get_tomorrows_schedule(query: str = "") -> str:
    """Get tomorrow's class schedule
    
    Args:
        query: The user's original query to detect language preference
    """
    tomorrow = datetime.now() + timedelta(days=1)
    classes = get_classes_for_date(tomorrow)
    
    # Auto-detect language from query
    language = detect_language_from_query(query) if query else "english"
    
    return format_schedule_response(classes, language, "tomorrow")

@function_tool
async def get_schedule_for_date(date: str, query: str = "") -> str:
    """Get class schedule for a specific date
    
    Args:
        date: Date in format 'YYYY-MM-DD' or day name like 'Monday'
        query: The user's original query to detect language preference
    """
    try:
        # Handle day names
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if date.lower() in days:
            # Find the next occurrence of this day
            today = datetime.now()
            target_day_num = days.index(date.lower())
            days_ahead = target_day_num - today.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
        else:
            # Try to parse as date
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                try:
                    target_date = datetime.strptime(date, "%d/%m/%Y")
                except ValueError:
                    return "Invalid date format. Please use YYYY-MM-DD, DD/MM/YYYY, or day name like 'Monday'."
        
        classes = get_classes_for_date(target_date)
        
        # Auto-detect language from query
        language = detect_language_from_query(query) if query else "english"
        
        date_str = target_date.strftime("%A, %B %d")
        return format_schedule_response(classes, language, date_str)
    
    except Exception as e:
        return f"Error getting schedule: {str(e)}"

@function_tool
async def get_schedule_info() -> str:
    """Get information about the loaded timetable"""
    total_classes = len(TIMETABLE_DATA)
    
    # Count classes per day
    day_counts = {}
    subjects = set()
    
    for entry in TIMETABLE_DATA:
        day = entry['day']
        subject = entry['subject']
        
        day_counts[day] = day_counts.get(day, 0) + 1
        subjects.add(subject)
    
    info = f"📚 **Timetable Information:**\n\n"
    info += f"Total classes per week: {total_classes}\n\n"
    info += "**Classes per day:**\n"
    
    for day, count in day_counts.items():
        info += f"• {day}: {count} classes\n"
    
    info += f"\n**Subjects:**\n"
    for subject in sorted(subjects):
        info += f"• {subject}\n"
    
    return info
