import os
import discord
import re
import logging
import requests
import time
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb_client import MongoDBClient
from bot.gemini_processor import init_gemini, extract_deadline_with_fallback


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('deadline-bot')

# Load environment variables with explicit file path
dotenv_path = find_dotenv()
logger.info(f"Loading environment variables from: {dotenv_path}")
load_dotenv(dotenv_path)

# Get configuration from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
logger.info(f"Token found: {'Yes' if TOKEN else 'No'} (First 5 chars: {TOKEN[:5] if TOKEN else 'None'}... Length: {len(TOKEN) if TOKEN else 0})")

# Fix GUILD_IDS parsing to handle empty string properly
guild_ids_str = os.getenv('GUILD_IDS', '')
GUILD_IDS = [gid.strip() for gid in guild_ids_str.split(',') if gid.strip()]
logger.info(f"Guild IDs monitoring: {GUILD_IDS if GUILD_IDS else 'ALL GUILDS'}")

API_URL = os.getenv('API_URL', 'http://localhost:8000')
BOT_API_KEY = os.getenv('BOT_API_KEY', 'your_bot_api_key_here')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize database client
db_client = MongoDBClient()

# Flag to track if Gemini is available
gemini_available = False

# Legacy deadline detection patterns (kept as fallback)
deadline_patterns = [
    r'due\s+(?:on|by)?\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    r'deadline[: ]\s*(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    r'submit\s+(?:before|by)?\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    r'REMINDER:.*?deadline:?\s*(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    r'([A-Z][a-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)'
]


@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    logger.info(f'{bot.user.name} has connected to Discord!')
    logger.info(f'Bot is active in {len(bot.guilds)} guilds')
    
    for guild in bot.guilds:
        logger.info(f'Connected to {guild.name} (id: {guild.id})')
    
    general_channel = bot.get_channel(1358156201208315958)
    #await general_channel.send("bot just started")


@bot.event
async def on_message(message):
    """Event triggered when a message is sent in a channel"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

    # Forward announcements to a specific channel
    if "announcement" in message.channel.name:
        try:
            # Get the general channel - if not found, log an error but don't crash
            general_channel = bot.get_channel(1358156201208315958)
            if general_channel:
                pass
                #await general_channel.send(f"{message.content}\n\n## This message came from {message.guild.name}")
            else:
                logger.error(f"Could not find general channel with ID 1358156201208315958")
        except Exception as e:
            logger.error(f"Error forwarding announcement: {e}")
    
    # Process messages from all guilds if GUILD_IDS is empty,
    # otherwise only process from specific guilds
    if not GUILD_IDS or str(message.guild.id) in GUILD_IDS:
        logger.info(f"Processing message from guild: {message.guild.name} (ID: {message.guild.id})")
        await process_message_for_deadlines(message)
    else:
        logger.debug(f"Skipping message from unmonitored guild: {message.guild.name} (ID: {message.guild.id})")


async def process_message_for_deadlines(message):
    """Process a message to extract event information using Gemini AI"""
    content = message.content
    logger.info(f"Processing message for events: '{content[:50]}...' in channel '{message.channel.name}'")
    
    # Check if it's in a monitored guild
    if GUILD_IDS and str(message.guild.id) not in GUILD_IDS:
        logger.info(f"Skipping message - guild {message.guild.id} is not in monitored guilds: {GUILD_IDS}")
        return
    
    # Prepare message info for Gemini
    message_info = {
        "channel_name": message.channel.name,
        "guild_name": message.guild.name,
        "message_id": str(message.id),
        "author_id": str(message.author.id),
        "author_name": str(message.author),
        "link": message.jump_url,
    }
    
    # First check if we've already processed this message (to prevent duplicate processing)
    existing_event = db_client.check_exists_by_message_id(message_info["message_id"])
    if existing_event:
        logger.info(f"Skipping already processed message with ID: {message_info['message_id']}")
        return
    
    # Try to extract event with Gemini AI (with fallback to regex if needed)
    event_found, event_data = extract_deadline_with_fallback(content, message_info)
    
    if event_found and event_data:
        date_str = event_data.get('date_str', 'unknown date')
        title = event_data.get('title', 'Untitled Event')
        category = event_data.get('category', 'event')
        
        logger.info(f"Detected {category}: {title} on {date_str}")
        
        # Always save to the backend API first, as it has proper date formatting
        api_success = False
        try:
            api_success = send_deadline_to_api(event_data)
            if not api_success:
                logger.warning("API storage failed, will try saving to local MongoDB instead")
        except Exception as api_error:
            logger.error(f"Failed to send to API independently: {api_error}")
            
        # Only save to local MongoDB if the date is properly formatted in YYYY-MM-DD
        # or if the API storage failed
        if not api_success:
            try:
                # Save to database
                db_result = db_client.save_deadline(event_data)
                
                if db_result:
                    logger.info(f"Successfully saved event to local MongoDB")
                else:
                    logger.warning(f"Skipped saving to MongoDB (likely due to date format or duplicate)")
                
            except Exception as db_error:
                logger.error(f"Failed to save to MongoDB: {db_error}")
                # Notify the user there was an issue
                await message.reply(f"⚠️ Detected {category}: **{title}** on **{date_str}**, but couldn't save it (MongoDB connection issue)")
                return
        
        # Reply to the message if event was detected and saved
        if category == 'deadline':
            reply_msg = f"✅ I've tracked this deadline: **{title}** due on **{date_str}**"
        else:
            reply_msg = f"✅ I've tracked this {category}: **{title}** on **{date_str}**"
            
        await message.reply(reply_msg)
    else:
        logger.info("No event detected in message")


def extract_title(content):
    """Extract a title from the message content (legacy function kept for compatibility)"""
    # Simple extraction: first sentence or first 50 characters
    title = content.split('.')[0]
    if len(title) > 50:
        title = title[:47] + "..."
    return title


def extract_course_from_channel(channel_name):
    """Extract course name from the channel name (legacy function kept for compatibility)"""
    # Simple approach - in production, you'd want more robust course extraction
    if '-' in channel_name:
        parts = channel_name.split('-')
        return parts[0].strip().upper()
    return channel_name.upper()


def parse_date_string(date_str):
    """Parse a date string into a datetime object (legacy function kept for compatibility)"""
    try:
        # Add current year if not specified
        if not re.search(r'\d{4}', date_str):
            date_str = f"{date_str}, {datetime.now().year}"
            
        # Try common date formats
        for fmt in ["%B %d, %Y", "%b %d, %Y", "%B %dth, %Y", "%B %dst, %Y", "%B %dnd, %Y", "%B %drd, %Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        # If all formats fail, raise exception
        raise ValueError(f"Could not parse date: {date_str}")
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        # Return current date + 7 days as fallback
        return datetime.now() + timedelta(days=7)


def send_deadline_to_api(event_data):
    """Send event data to the backend API
    
    Returns:
        bool: True if the event was successfully sent to the API, False otherwise
    """
    try:
        # Verify we have an API key and URL
        if not BOT_API_KEY or BOT_API_KEY == "your_bot_api_key_here":
            logger.error("Missing or default BOT_API_KEY - cannot send to API. Check your .env file.")
            return False
            
        # Create API-compatible data structure
        api_data = {
            "course": event_data.get("course", ""),
            "club": event_data.get("club", event_data.get("course", "")),  # Use club field if available
            "title": event_data.get("title", ""),
            "description": event_data.get("description", ""),
            "due_date": event_data["due_date"].isoformat() if isinstance(event_data.get("due_date"), datetime) else event_data.get("due_date", ""),
            "link": event_data.get("link", ""),
            "location": event_data.get("location", ""),
            "time": event_data.get("time", ""),
            "category": event_data.get("category", "event"),
            "source": event_data.get("source", "discord_bot"),
            # Ensure message_id is always included and passed to API for deduplication
            "message_id": event_data.get("message_id", f"msg_{int(time.time())}"),
            # Always include the standardized date format
            "date_str": event_data.get("date_str", "")
        }
        
        # Include API key for authorization
        payload = {
            "deadline": api_data,  # Keep as "deadline" for backward compatibility with API
            "api_key": BOT_API_KEY
        }
        
        # Better log output before sending
        logger.info(f"Sending event to API at: {API_URL}/bot/deadlines")
        logger.debug(f"API data: {api_data}")
        
        # Send POST request to API
        response = requests.post(
            f"{API_URL}/bot/deadlines",
            json=payload,
            timeout=10  # Add a timeout to prevent hanging
        )
        
        # Check response
        if response.status_code == 201:
            logger.info(f"Successfully sent event to API: {response.json()}")
            return True
        elif response.status_code == 401:
            logger.error(f"API Key rejected (401): {response.text}")
            logger.error(f"Please check that BOT_API_KEY matches between bot and backend .env files")
        else:
            logger.error(f"Failed to send event to API: {response.status_code} - {response.text}")
            return False
            
    except requests.RequestException as re:
        logger.error(f"Network error sending event to API: {re}")
        logger.error(f"Please check that the backend API is running at {API_URL}")
        return False
    except Exception as e:
        logger.error(f"Error sending event to API: {e}")
        return False


@bot.command(name='deadlines')
async def list_deadlines(ctx):
    """Command to list upcoming deadlines"""
    await ctx.send("Upcoming deadlines (placeholder - will be implemented by the team)")


@bot.command(name='help_bot')
async def help_command(ctx):
    """Display help information"""
    help_text = """
**Club Announcement Tracker Bot Commands**
`!deadlines` - List upcoming deadlines and events
`!help_bot` - Display this help message

This bot automatically detects and tracks:
• Club events and meetings
• Application and registration deadlines 
• General club announcements
• Important dates and times
    """
    await ctx.send(help_text)


def main():
    """Main function to start the bot"""
    global gemini_available
    
    # Better token validation
    if not TOKEN:
        logger.error("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
        logger.error("Make sure your .env file exists and contains DISCORD_TOKEN=your_token_here")
        logger.error("No quotes, no spaces around the equals sign.")
        return
    
    # Validate token format
    if len(TOKEN) < 50 or " " in TOKEN or TOKEN.startswith('"') or TOKEN.startswith("'"):
        logger.error("Discord token appears malformed.")
        logger.error("Token should be ~59-70 characters without quotes or spaces.")
        logger.error("Please check your .env file format and token value.")
        return
    
    # Explicitly test MongoDB Atlas connection
    try:
        # Get MongoDB URI for troubleshooting
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            logger.error("MONGODB_URI not found in environment variables!")
            logger.error("Please ensure your .env file contains the MongoDB Atlas connection string")
            logger.error("Should start with: mongodb+srv://")
        else:
            logger.info(f"Found MongoDB URI starting with: {mongodb_uri[:15]}...")
        
        # Test connection by getting server info
        db_info = db_client.test_connection()
        logger.info(f"Successfully connected to MongoDB Atlas: {db_info}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.error("If using MongoDB Atlas, please check:")
        logger.error("1. The connection string is correct in your .env file")
        logger.error("2. Your username, password, and network access are properly configured")
        logger.error("3. You've whitelisted your IP address in MongoDB Atlas network settings")
        # Continue anyway to allow Discord functionality
    
    # Initialize Gemini AI
    if GEMINI_API_KEY:
        gemini_available = init_gemini(GEMINI_API_KEY)
        if gemini_available:
            logger.info("Gemini AI initialized successfully")
        else:
            logger.warning("Failed to initialize Gemini AI - will fall back to regex patterns")
    else:
        logger.warning("No GEMINI_API_KEY found in environment variables - will fall back to regex patterns")
    
    # Check API connection
    try:
        response = requests.get(f"{API_URL}")
        if response.status_code == 200:
            logger.info(f"Successfully connected to backend API at {API_URL}")
        else:
            logger.warning(f"Backend API responded with status code {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to connect to backend API: {e}")
        logger.error(f"Please make sure the backend API is running at {API_URL}")
    
    logger.info("Starting Discord bot...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        if "Improper token" in str(e):
            logger.error("Please check your Discord token. It may be expired or invalid.")
            logger.error("Go to Discord Developer Portal and reset your token if needed.")


if __name__ == "__main__":
    main() 