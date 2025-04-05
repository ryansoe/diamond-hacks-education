import os
import discord
import re
import logging
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
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
    r'submit\s+(?:before|by)?\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)'
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

    if("announcement" in message.channel.name):
        general_channel = bot.get_channel(1358156201208315958)
        await general_channel.send(message.content + "\n\n## This message came from " + message.guild.name)
        await general_channel.send()
    
    # Only process messages from monitored guilds
    if not GUILD_IDS or str(message.guild.id) in GUILD_IDS:
        await process_message_for_deadlines(message)


async def process_message_for_deadlines(message):
    """Process a message to extract deadline information"""
    content = message.content
    
    # Extract deadline information
    for pattern in deadline_patterns:
        matches = re.search(pattern, content, re.IGNORECASE)
        if matches:
            # Extract deadline date from the match
            deadline_date_str = matches.group(1)
            
            # Extract event title/description
            title = extract_title(content)
            
            # Log the detected deadline
            logger.info(f"Detected deadline: {title} due on {deadline_date_str}")
            
            # Store in database
            deadline_data = {
                "title": title,
                "date_str": deadline_date_str,
                "raw_content": content,
                "channel_name": message.channel.name,
                "guild_name": message.guild.name,
                "message_id": message.id,
                "author_id": message.author.id,
                "author_name": str(message.author),
                "timestamp": datetime.now(),
                "source_link": message.jump_url,
            }
            
            # Save to database
            db_client.save_deadline(deadline_data)
            break


def extract_title(content):
    """Extract a title from the message content"""
    # Simple extraction: first sentence or first 50 characters
    title = content.split('.')[0]
    if len(title) > 50:
        title = title[:47] + "..."
    return title


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
    
    logger.info("Starting Discord bot...")
    bot.run(TOKEN)


if __name__ == "__main__":
    main() 