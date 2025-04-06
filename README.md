# Eventory

A comprehensive AI-powered platform for tracking academic and club events, featuring a Discord bot that intelligently detects deadlines, events, and announcements from conversations.

## Overview

Eventory streamlines event tracking for students by automatically capturing important deadlines and events shared on Discord servers. Using Google's Gemini AI, our system can understand natural language announcements and extract structured data for easy reference.

## Project Structure

The project is organized into three main components:

1. **Discord Bot**: Monitors Discord channels for mentions of deadlines, events, and announcements
2. **Backend API**: FastAPI server that stores and provides event data
3. **Frontend**: React web application for viewing and managing events

## Key Features

- **AI-Powered Event Detection**: Uses Gemini AI to intelligently parse messages for events, deadlines, and announcements
- **Smart Date Processing**: Converts relative dates ("tomorrow", "next week") to standardized YYYY-MM-DD format
- **Multi-Source Event Collection**: Consolidates events from various Discord channels and servers
- **Comprehensive Event Information**: Extracts title, date, time, location, club name, and more
- **MongoDB Integration**: Reliable cloud storage using MongoDB Atlas
- **Calendar View**: Visual calendar interface to see events by date
- **Event Categorization**: Automatically categorizes events (club meetings, academic deadlines, etc.)
- **Modern Web Interface**: Clean, responsive UI built with React and Tailwind CSS
- **Secure API**: Protected endpoints with authentication and API keys

## Setup Instructions

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- MongoDB Atlas account (or local MongoDB instance)
- Discord Bot Token (from Discord Developer Portal)
- Google Gemini API Key

### Environment Variables

Create a `.env` file in the root directory for shared environment variables:

```
# Shared environment variables
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
```

Create a `.env` file in the `/bot` directory with the following variables:

```
# Discord Bot
DISCORD_TOKEN=your_discord_bot_token
GUILD_IDS=comma,separated,guild,ids

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
DATABASE_NAME=eventory

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

# JWT Authentication
JWT_SECRET=your_jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Create a `.env` file in the `/frontend` directory:

```
REACT_APP_API_URL=http://localhost:8000
```

### Installation

1. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

### Running the Project

You can run all components at once using the provided start script:

```
./start-dev.sh
```

Or start each component individually:

1. Start the backend:
   ```
   cd backend
   python main.py
   ```

2. Start the Discord bot:
   ```
   cd bot
   python main.py
   ```

3. Start the frontend:
   ```
   cd frontend
   npm start
   ```

## How It Works

### Event Detection Flow

1. The Discord bot monitors messages in configured channels
2. When an announcement is detected, it's processed using Gemini AI
3. The AI extracts structured data (event title, date, time, location, etc.)
4. Dates are standardized to YYYY-MM-DD format for consistent handling
5. The event is saved to MongoDB with deduplication checks
6. The bot acknowledges by replying to the original message (only for properly formatted dates)
7. Events can be viewed through the web interface in list or calendar view

## Event Types Detected

Eventory can detect various types of announcements:
- Club events and meetings
- Academic deadlines
- Career opportunities (internships, job fairs)
- Registration deadlines
- Social events with food/refreshments
- General club announcements

## Technologies Used

- **Discord Bot**: Python, Discord.py, Google Gemini AI
- **Backend**: FastAPI, Python, PyMongo, JWT authentication
- **Frontend**: React, Tailwind CSS, Axios
- **Database**: MongoDB Atlas
- **Authentication**: JWT tokens, API keys
- **Date Processing**: Python dateutil, custom formatters
- **Error Handling**: Comprehensive logging and error recovery

## Development and Contribution

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgements

- Google Gemini for the AI capabilities
- MongoDB Atlas for database services
- Discord Developer Platform for bot integration 
