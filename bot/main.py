import os
import discord
import re
import logging
import requests
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb_client import MongoDBClient


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

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS = os.getenv('GUILD_IDS', '').split(',')
API_URL = os.getenv('API_URL', 'http://localhost:8000')
BOT_API_KEY = os.getenv('BOT_API_KEY', 'your_bot_api_key_here')

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize database client
db_client = MongoDBClient()

# Deadline detection patterns
deadline_patterns = [
    r'due\s+(?:on|by)?\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    r'deadline[: ]\s*(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    r'submit\s+(?:before|by)?\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    # New pattern to match "REMINDER: Project proposal deadline: December 1st"
    r'REMINDER:.*?deadline:?\s*(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
    # More general pattern to catch various formats
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
    await general_channel.send("bot just started")


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
                await general_channel.send(f"{message.content}\n\n## This message came from {message.guild.name}")
            else:
                logger.error(f"Could not find general channel with ID 1358156201208315958")
        except Exception as e:
            logger.error(f"Error forwarding announcement: {e}")
    
    # Only process messages from monitored guilds
    if not GUILD_IDS or str(message.guild.id) in GUILD_IDS:
        await process_message_for_deadlines(message)


async def process_message_for_deadlines(message):
    """Process a message to extract deadline information"""
    content = message.content
    logger.info(f"Processing message for deadlines: '{content[:50]}...' in channel '{message.channel.name}'")
    
    # Check if it's in a monitored guild
    if GUILD_IDS and str(message.guild.id) not in GUILD_IDS:
        logger.info(f"Skipping message - guild {message.guild.id} is not in monitored guilds: {GUILD_IDS}")
        return
    
    # Extract deadline information
    deadline_found = False
    for pattern in deadline_patterns:
        matches = re.search(pattern, content, re.IGNORECASE)
        if matches:
            deadline_found = True
            # Extract deadline date from the match
            deadline_date_str = matches.group(1)
            
            # Extract event title/description
            title = extract_title(content)
            
            # Extract course name from channel name
            course = extract_course_from_channel(message.channel.name)
            
            # Log the detected deadline
            logger.info(f"Detected deadline: {title} due on {deadline_date_str}")
            
            # Parse deadline date
            try:
                # Try to parse the date string into a datetime object
                # This is a simple approach - in production, you'd want more robust date parsing
                due_date = parse_date_string(deadline_date_str)
                
                # Store in database
                deadline_data = {
                    "title": title,
                    "course": course,
                    "description": content[:500],  # Truncate long descriptions
                    "due_date": due_date,
                    "date_str": deadline_date_str,
                    "raw_content": content,
                    "channel_name": message.channel.name,
                    "guild_name": message.guild.name,
                    "message_id": message.id,
                    "author_id": message.author.id,
                    "author_name": str(message.author),
                    "timestamp": datetime.now(),
                    "link": message.jump_url,
                    "source": "discord_bot",
                    "category": "assignment"
                }
                
                # Attempt to save to database with better error handling
                try:
                    db_client.save_deadline(deadline_data)
                    logger.info(f"Successfully saved deadline to local MongoDB")
                    
                    # Reply to the message if deadline was detected and saved
                    await message.reply(f"✅ I've tracked this deadline: **{title}** due on **{deadline_date_str}**")
                    
                except Exception as db_error:
                    logger.error(f"Failed to save to MongoDB: {db_error}")
                    # Notify the user there was an issue
                    await message.reply(f"⚠️ Detected deadline: **{title}** due on **{deadline_date_str}**, but couldn't save it (MongoDB connection issue)")
                
                # Try to send to backend API
                try:
                    send_deadline_to_api(deadline_data)
                except Exception as api_error:
                    logger.error(f"Failed to send to API independently: {api_error}")
                
            except Exception as e:
                logger.error(f"Error processing deadline: {e}")
                logger.exception("Full traceback:")
            
            break
    
    if not deadline_found:
        # Debug why the pattern didn't match
        logger.info(f"No deadline found in message. Testing patterns individually:")
        for i, pattern in enumerate(deadline_patterns):
            logger.info(f"Pattern {i+1}: {pattern}")
            if re.search(pattern, content, re.IGNORECASE):
                logger.info(f"  - Pattern {i+1} matched, but full processing failed")
            else:
                logger.info(f"  - Pattern {i+1} did not match")


def extract_title(content):
    """Extract a title from the message content"""
    # Simple extraction: first sentence or first 50 characters
    title = content.split('.')[0]
    if len(title) > 50:
        title = title[:47] + "..."
    return title


def extract_course_from_channel(channel_name):
    """Extract course name from the channel name"""
    # Simple approach - in production, you'd want more robust course extraction
    if '-' in channel_name:
        parts = channel_name.split('-')
        return parts[0].strip().upper()
    return channel_name.upper()


def parse_date_string(date_str):
    """Parse a date string into a datetime object"""
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


def send_deadline_to_api(deadline_data):
    """Send deadline data to the backend API"""
    try:
        # Create API-compatible data structure
        api_data = {
            "course": deadline_data["course"],
            "title": deadline_data["title"],
            "description": deadline_data["description"],
            "due_date": deadline_data["due_date"].isoformat(),
            "link": deadline_data["link"],
            "category": deadline_data["category"],
            "source": deadline_data["source"]
        }
        
        # Include API key for authorization
        payload = {
            "deadline": api_data,
            "api_key": BOT_API_KEY
        }
        
        # Send POST request to API
        response = requests.post(
            f"{API_URL}/bot/deadlines",
            json=payload
        )
        
        # Check response
        if response.status_code == 201:
            logger.info(f"Successfully sent deadline to API: {response.json()}")
        else:
            logger.error(f"Failed to send deadline to API: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending deadline to API: {e}")


@bot.command(name='deadlines')
async def list_deadlines(ctx):
    """Command to list upcoming deadlines"""
    await ctx.send("Upcoming deadlines (placeholder - will be implemented by the team)")


@bot.command(name='help_bot')
async def help_command(ctx):
    """Display help information"""
    help_text = """
**Deadline Tracker Bot Commands**
`!deadlines` - List upcoming deadlines
`!help_bot` - Display this help message

This bot automatically detects and tracks deadlines mentioned in conversations.
    """
    await ctx.send(help_text)


def main():
    """Main function to start the bot"""
    if not TOKEN:
        logger.error("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
        return
    
    # Check MongoDB connection before starting
    try:
        # Test connection by getting server info
        db_info = db_client.test_connection()
        logger.info(f"Successfully connected to MongoDB: {db_info}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.error("Please make sure MongoDB is running with: mongod --dbpath /path/to/data/directory")
        # Continue anyway to allow Discord functionality
    
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