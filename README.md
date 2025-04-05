# School Deadline Tracker

A web application with a Discord bot that automatically scrapes important deadlines and dates from school Discord servers, then presents them in an organized dashboard.

## Project Structure

- `bot/` - Discord bot for scraping deadline information
- `backend/` - API server for processing and storing data
- `frontend/` - React web interface for viewing deadlines
- `database/` - Database models and connection utilities

## Technology Stack

- **Backend**: Python with discord.py and FastAPI
- **Database**: MongoDB
- **Frontend**: React with Tailwind CSS

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB

### Discord Bot Setup

1. Create a Discord application at https://discord.com/developers/applications
2. Create a bot for your application and copy the token
3. Add the bot to your server with the required permissions
4. Copy `.env.example` to `.env` and add your Discord bot token

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Features

- Discord bot to automatically scrape deadline information
- Data processing and storage in MongoDB
- User dashboard to view deadlines in list and calendar formats
- Filtering and search functionality
- Optional email notifications
- Admin panel for data management

## Development

This project template is designed for your team to start implementing the full functionality. Key areas to focus on:

1. Implementing the Discord message scanning logic
2. Building the data extraction and processing pipeline
3. Developing the frontend dashboard views
4. Creating the notification system
5. Building the admin controls 