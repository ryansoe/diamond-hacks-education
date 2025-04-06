# Eventory

A comprehensive AI-powered platform for tracking academic and club events, featuring a Discord bot that intelligently detects deadlines, events, and announcements from conversations.

## Overview

Eventory streamlines event tracking for students by automatically capturing important deadlines and events shared on Discord servers. Using Google's Gemini AI, our system can understand natural language announcements and extract structured data for easy reference.

## Components

The system consists of three main components:

1. **Discord Bot**: Monitors Discord channels for mentions of deadlines, events, and announcements
2. **Backend API**: FastAPI server that stores and provides event data
3. **Frontend**: React web application for viewing and managing events

## Key Features

- **AI-Powered Event Detection**: Uses Gemini AI to intelligently parse messages for events, deadlines, and announcements
- **Multi-Source Event Collection**: Consolidates events from various Discord channels and servers
- **Comprehensive Event Information**: Extracts title, date, time, location, club name, and more
- **MongoDB Integration**: Reliable cloud storage using MongoDB Atlas
- **Modern Web Interface**: Clean, responsive UI for viewing and managing events
- **Secure API**: Protected endpoints with authentication and API keys

## Setup Instructions

### Environment Variables

Create a `.env` file in the `/bot` directory with the following variables:

```
# Discord Bot
DISCORD_TOKEN=your_discord_bot_token
GUILD_IDS=comma,separated,guild,ids

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# API Configuration
API_URL=http://localhost:8000
BOT_API_KEY=your_secret_api_key

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

Create another `.env` file in the `/backend` directory:

```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
DATABASE_NAME=eventory

# Bot to API Integration
BOT_API_KEY=your_secret_api_key
```

### Backend Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the backend server:
   ```
   cd backend
   python main.py
   ```

### Discord Bot Setup

1. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications)
2. Add the bot to your server with the necessary permissions (message content, read messages)
3. Set the `DISCORD_TOKEN` in your `.env` file
4. Run the bot:
   ```
   cd bot
   python main.py
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

## How It Works

### Event Detection Flow

1. The bot monitors Discord messages in configured channels
2. When a message is detected, it's sent to the Gemini AI for analysis
3. Gemini AI extracts structured data (event title, date, time, location, etc.)
4. If an event is detected, it's saved to MongoDB and the bot acknowledges with a reply
5. The data is also sent to the backend API for access through the web interface
6. Authentication between components is handled via a shared API key

## Message Types Detected

Eventory can detect various types of announcements:
- Club events and meetings
- Application and registration deadlines
- General club announcements
- Important dates and activities

## Technologies Used

- **Backend**: Python, FastAPI, MongoDB
- **Discord Bot**: Discord.py, Google Gemini AI
- **Frontend**: React, JavaScript
- **Database**: MongoDB Atlas
- **Authentication**: JWT, API keys

## Contributing

Please fork the repository and submit a pull request for any improvements 