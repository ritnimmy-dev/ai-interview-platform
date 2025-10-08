# Interview Platform Setup Guide

## Quick Start (For Beginners)

### 1. Database Setup
You need PostgreSQL installed and running. Here's how to set it up:

**On Mac (using Homebrew):**
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create database
createdb interviews

# Run the database setup
psql interviews -f backend/database_setup.sql
```

**On Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/
2. Install it with default settings
3. Open pgAdmin or command line
4. Create a database called "interviews"
5. Run the SQL file: `backend/database_setup.sql`

### 2. Environment Variables
Create a file called `.env` in your project root with:

```
DB_URL=postgresql://your_username:your_password@localhost:5432/interviews
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

### 3. Running the Platform

**Backend (Terminal 1):**
```bash
cd backend
python main.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Platform
- Open your browser to: http://localhost:3000
- The backend will run on: http://localhost:8000

## What Each Part Does

### Backend (Python/FastAPI)
- Handles all the server logic
- Stores data in PostgreSQL database
- Sends emails with results
- Manages the quiz questions and scoring

### Frontend (Next.js/React)
- The user interface that candidates see
- Handles form submissions
- Shows the quiz questions
- Manages the timer

### Database (PostgreSQL)
- Stores quiz questions
- Stores candidate results
- Tracks anti-cheat events

## Troubleshooting

**If the backend won't start:**
- Check if PostgreSQL is running
- Verify your database connection in the `.env` file
- Make sure all Python packages are installed: `pip install -r requirements.txt`

**If the frontend won't start:**
- Make sure you're in the frontend directory
- Run `npm install` to install dependencies
- Check if port 3000 is available

**If questions don't load:**
- Make sure you ran the database setup SQL file
- Check if the database has the `round1_questions` table with data
