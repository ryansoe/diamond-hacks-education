# School Deadline Tracker

A comprehensive solution for tracking school deadlines, featuring a Discord bot that detects deadlines in conversations and a web app for viewing and managing them.

## Components

The system consists of three main components:

1. **Discord Bot**: Monitors Discord channels for mentions of deadlines and assignments
2. **Backend API**: FastAPI server that stores and provides deadline data
3. **Frontend**: React web application for viewing and managing deadlines

## Setup Instructions

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Discord Bot
DISCORD_TOKEN=your_discord_bot_token
GUILD_IDS=comma,separated,guild,ids

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=deadline_tracker

# Bot to API Integration
API_URL=http://localhost:8000
BOT_API_KEY=your_secret_api_key
```

### Backend Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start MongoDB:
   ```
   mongod --dbpath /path/to/data/directory
   ```

3. Run the backend server:
   ```
   python -m backend.main
   ```

### Discord Bot Setup

1. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications)
2. Add the bot to your server with the necessary permissions
3. Set the `DISCORD_TOKEN` in your `.env` file
4. Run the bot:
   ```
   python -m bot.main
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

## Integration Between Bot and Backend

The Discord bot now directly communicates with the backend API to share deadline information:

1. The bot detects deadlines in Discord messages using regex patterns
2. It extracts important information like course, title, description, and due date
3. The data is stored locally in MongoDB for redundancy
4. The bot also sends the deadline data to the backend API via HTTP POST
5. The backend has a special `/bot/deadlines` endpoint that accepts this data
6. Authentication is handled via a shared API key

### Integration Configuration

- `API_URL`: URL where the backend is running (default: http://localhost:8000)
- `BOT_API_KEY`: Secret key for authenticating the bot with the API

## Features

- Automatic deadline detection from Discord messages
- Secure API for storing and retrieving deadline information
- Web interface for viewing deadlines
- Authentication system for accessing sensitive data

## Contributing

Please fork the repository and submit a pull request for any improvements 