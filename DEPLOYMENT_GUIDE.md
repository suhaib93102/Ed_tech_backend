# Django Backend Deployment Guide

## Overview
This guide covers the deployment of the EdTech Django backend application to Render.

## Prerequisites
- Render account
- PostgreSQL database (Supabase recommended)
- API keys for external services

## Environment Variables
Copy `.env.example.template` to `.env` and fill in the required values:

```bash
cp .env.example.template .env
```

Required environment variables:
- `SUPABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- API keys for Bing, SerpAPI, YouTube, Firecrawl, Gemini
- OAuth credentials for Google
- JWT settings
- Razorpay payment credentials

## Local Development
1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start development server:
```bash
python manage.py runserver
```

## Render Deployment
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure the following settings:
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `python -m uvicorn edtech_project.asgi:application --host 0.0.0.0 --port $PORT --workers 1 --log-level info`
   - **Environment Variables**: Add all required env vars

4. Deploy the service

## Database Migration
The application uses PostgreSQL. To migrate from SQLite:

1. Dump data from SQLite:
```bash
SUPABASE_URL=sqlite:///db.sqlite3 python manage.py dumpdata --exclude contenttypes --exclude auth.Permission > backup_clean.json
```

2. Load data into PostgreSQL:
```bash
python manage.py loaddata backup_clean.json
```

## Testing
Run the comprehensive test script:
```bash
./test_deployed_api.sh
```

## Troubleshooting
- Check Render logs for deployment errors
- Verify all environment variables are set
- Ensure database connectivity
- Check file permissions and encoding

## API Endpoints
The application provides the following main endpoints:
- `/api/health/` - Health check
- `/api/auth/` - Authentication
- `/api/quiz/` - Quiz functionality
- `/api/subscription/` - Subscription management
- `/api/payment/` - Payment processing
- `/api/daily-quiz/` - Daily quiz features
- `/api/youtube/` - YouTube summarization

## Security Notes
- Never commit `.env` files
- Use strong, unique secret keys
- Keep API keys secure
- Regularly update dependencies