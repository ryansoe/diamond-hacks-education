import os
import logging
import json
from datetime import datetime
import google.generativeai as genai
from typing import Optional, Dict, Any, Tuple
import re

# Configure logging
logger = logging.getLogger('deadline-bot.gemini')

# Initialize Gemini AI
def init_gemini(api_key: str = None):
    """Initialize the Gemini AI client with API key"""
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
        
    if not api_key:
        logger.error("No Gemini API key found. Please set the GEMINI_API_KEY environment variable.")
        return False
        
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini AI initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI: {e}")
        return False

def detect_deadline(message_content: str, channel_name: str = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Detect club announcements and events from a message using Gemini AI
    
    Args:
        message_content: The content of the message to analyze
        channel_name: The name of the channel where the message was posted
    
    Returns:
        Tuple with (success, event_info)
        - success: Boolean indicating if an event or announcement was found
        - event_info: Dictionary with extracted information or None if no event found
    """
    try:
        # Create a system prompt that instructs Gemini to extract event information
        system_prompt = """
        You are a helpful assistant that detects club announcements, events, and deadlines in messages.
        
        TASK:
        Analyze the provided message and extract information about:
        1. Club events or meetings
        2. Application deadlines
        3. Registration deadlines 
        4. Any important dates mentioned
        5. General club announcements
        
        If any event, deadline, or announcement is found:
        1. Extract the title/name of the event or announcement
        2. Extract any dates mentioned (event date, deadline date, etc.)
        3. Determine the club or organization name
        4. Extract location information if available
        5. Extract time information if available
        6. Extract any links/URLs mentioned
        
        OUTPUT FORMAT (JSON):
        {
          "has_event": true/false,
          "title": "The title or name of the event/announcement",
          "date_str": "The primary date mentioned (event date or deadline)",
          "club": "Club or organization name",
          "description": "Brief description of the event/announcement",
          "location": "Location of the event if mentioned",
          "time": "Time of the event if mentioned",
          "links": ["array", "of", "links"],
          "category": "event/deadline/meeting/announcement"
        }
        
        DATE EXTRACTION GUIDANCE:
        - For specific dates, capture the full date expression (e.g., "April 15th, 2023")
        - For relative dates:
          - Use "today" for events happening on the current day
          - Use "tomorrow" for events happening the next day
          - For other relative dates, interpret them relative to the current date
        - If a date has no year specified, assume it's for the current year
        - If no specific date is mentioned but the event is clearly upcoming, use today's date
        
        IMPORTANT:
        - Return only the JSON without any markdown formatting or code blocks
        - If no event or announcement is detected, return {"has_event": false}
        - Extract any club name if present (e.g., "Chess Club", "ACM")
        - If the channel name contains club info, use it
        """
        
        # Include channel name if available
        input_text = message_content
        if channel_name:
            input_text = f"Channel: {channel_name}\nMessage: {message_content}"
        
        # Configure Gemini model
        generation_config = {
            "temperature": 0.1,  # Low temperature for more deterministic responses
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 1024,
        }
        
        # Get models
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config
            )
        except Exception as e:
            logger.error(f"Error accessing Gemini model: {e}")
            logger.info("Falling back to gemini-1.0-pro model")
            model = genai.GenerativeModel(
                model_name="gemini-1.0-pro",
                generation_config=generation_config
            )
        
        # Generate response
        response = model.generate_content(
            [system_prompt, input_text]
        )
        
        # Extract and parse the JSON response - fix markdown formatting
        try:
            response_text = response.text
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif "```" in response_text:
                response_text = response_text.replace("```", "").strip()
                
            # Parse the JSON
            result = json.loads(response_text)
            logger.info(f"Gemini AI response (processed): {result}")
            
            # Check if an event was detected (backwards compatible with "has_deadline" key)
            if result.get("has_event", False) or result.get("has_deadline", False):
                # For backward compatibility
                if "has_deadline" in result and "has_event" not in result:
                    result["has_event"] = result["has_deadline"]
                
                return True, result
            else:
                logger.info("No event or announcement detected by Gemini AI")
                return False, None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {response.text}")
            logger.error(f"JSON error: {e}")
            
            # Try to extract the JSON from the response manually as a fallback
            try:
                # Try to find JSON content between curly braces
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    logger.info(f"Successfully extracted JSON using regex: {result}")
                    
                    # Check if an event was detected
                    if result.get("has_event", False) or result.get("has_deadline", False):
                        return True, result
            except Exception:
                pass
                
            return False, None
            
    except Exception as e:
        logger.error(f"Error using Gemini AI to detect event: {e}")
        return False, None

def format_deadline_data(
    gemini_result: Dict[str, Any],
    message_content: str,
    message_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format the Gemini AI result into the expected MongoDB schema
    
    Args:
        gemini_result: The result from Gemini AI
        message_content: The original message content
        message_info: Dictionary with additional message information
    
    Returns:
        Dictionary formatted for MongoDB storage
    """
    # Get the current date for default and relative date handling
    today = datetime.now()
    
    # Attempt to parse the date string
    due_date = None
    date_str = gemini_result.get("date_str", "")
    standardized_date_str = ""
    
    try:
        from dateutil import parser
        
        # Handle special cases
        if date_str:
            # Case: "today" - use current date
            if re.search(r'\btoday\b', date_str.lower()):
                due_date = today
                standardized_date_str = today.strftime("%Y-%m-%d")
            
            # Case: "tomorrow" - use next day
            elif re.search(r'\btomorrow\b', date_str.lower()):
                from datetime import timedelta
                due_date = today + timedelta(days=1)
                standardized_date_str = due_date.strftime("%Y-%m-%d")
            
            # General case: try to parse the date
            else:
                # Handle dates without year
                if not re.search(r'\b\d{4}\b', date_str):
                    # Add current year and try parsing
                    modified_date_str = f"{date_str}, {today.year}"
                    try:
                        due_date = parser.parse(modified_date_str)
                    except:
                        # If that fails, try original string
                        due_date = parser.parse(date_str)
                else:
                    # Parse with year included
                    due_date = parser.parse(date_str)
                
                if due_date:
                    standardized_date_str = due_date.strftime("%Y-%m-%d")
        
        # Fallback: if no date or parsing failed, use today's date
        if not due_date:
            due_date = today
            standardized_date_str = today.strftime("%Y-%m-%d")
            
    except Exception as e:
        logger.error(f"Failed to parse date: {e}")
        due_date = today  # Fallback
        standardized_date_str = today.strftime("%Y-%m-%d")
    
    # Use club from Gemini or fallback to channel name extraction
    club = gemini_result.get("club", "")
    if not club:
        club = gemini_result.get("course", "")  # backward compatibility
        
    if not club and message_info.get("channel_name"):
        # Extract from channel name as fallback
        channel_name = message_info.get("channel_name", "")
        if '-' in channel_name:
            club = channel_name.split('-')[0].strip().upper()
        else:
            club = channel_name.upper()
    
    # Get links if available
    links = gemini_result.get("links", [])
    link = ""
    if links and isinstance(links, list) and len(links) > 0:
        link = links[0]  # Use the first link
    elif "link" in gemini_result:
        link = gemini_result.get("link", "")
    else:
        link = message_info.get("link", "")
    
    # Get title with fallbacks
    title = gemini_result.get("title", "Untitled Event")
    
    # Get category with fallbacks
    category = gemini_result.get("category", "event")
    
    # Get location and time if available
    location = gemini_result.get("location", "")
    time = gemini_result.get("time", "")
    
    # Create description
    description = gemini_result.get("description", message_content[:500])
    
    # Add location and time to description if available
    if location:
        description += f"\nLocation: {location}"
    if time:
        description += f"\nTime: {time}"
    
    # Create the deadline data with the same structure as before
    deadline_data = {
        "title": title,
        "course": club,  # Keep "course" for backward compatibility
        "club": club,    # Add "club" field
        "description": description,
        "due_date": due_date,
        "date_str": standardized_date_str,  # Use the standardized date string
        "raw_content": message_content,
        "channel_name": message_info.get("channel_name", ""),
        "guild_name": message_info.get("guild_name", ""),
        "message_id": message_info.get("message_id", ""),
        "author_id": message_info.get("author_id", ""),
        "author_name": message_info.get("author_name", ""),
        "timestamp": datetime.now(),
        "link": link,
        "source": "discord_bot",
        "category": category,
        "location": location,
        "time": time
    }
    
    return deadline_data


def extract_deadline_with_fallback(
    message_content: str,
    message_info: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Extract event information with fallback to regex if Gemini fails
    
    Args:
        message_content: The content of the message
        message_info: Dictionary with additional message information
    
    Returns:
        Tuple with (success, event_data)
    """
    # Try with Gemini AI first
    has_event, gemini_result = detect_deadline(
        message_content, 
        message_info.get("channel_name", "")
    )
    
    if has_event and gemini_result:
        logger.info("Event/announcement detected using Gemini AI")
        return True, format_deadline_data(gemini_result, message_content, message_info)
    
    # If Gemini fails or finds no deadline, we could add a regex fallback here
    # This would reuse the existing regex patterns from main.py
    logger.info("No event detected with Gemini AI, could implement regex fallback")
    return False, None 