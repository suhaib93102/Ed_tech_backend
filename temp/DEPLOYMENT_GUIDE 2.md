# Backend Deployment Guide

## Render Deployment (Cloud)

### Quick Deploy to Render

1. **Connect Repository**: Connect your GitHub repo to Render
2. **Create Web Service**: Choose "Web Service" from Render dashboard
3. **Configure Build**:
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `python -m uvicorn edtech_project.asgi:application --host 0.0.0.0 --port $PORT --workers 2`

4. **Environment Variables**: Add these in Render dashboard:
   ```
   DJANGO_SETTINGS_MODULE=edtech_project.settings
   DEBUG=False
   SECRET_KEY=your-generated-secret-key
   ALLOWED_HOSTS=your-app.onrender.com
   ```

5. **Deploy**: Click "Create Web Service"

### Troubleshooting Render Builds

#### Pillow Build Error (Fixed)
- Updated `requirements.txt` to use `Pillow>=10.2.0`
- Added build script with system dependencies
- Uses Python 3.12 runtime (compatible with Pillow)

#### Common Issues
- **Port Error**: Use `$PORT` environment variable
- **Static Files**: Build script handles `collectstatic`
- **Database**: SQLite works on Render free tier

## Quick Start Commands

### Option 1: Use Deployment Script (Recommended)
```bash
cd backend
./deploy_backend.sh
```

### Option 2: Manual Commands

#### 1. Setup Environment
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Database Setup
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 3. Create Admin User (Optional)
```bash
python manage.py createsuperuser
# Or use default: admin/admin123
```

#### 4. Start Server
```bash
# Development mode (with auto-reload)
python -m uvicorn edtech_project.asgi:application --host 0.0.0.0 --port 8003 --reload

# Production mode (multiple workers)
python -m uvicorn edtech_project.asgi:application --host 0.0.0.0 --port 8003 --workers 4
```

## Access Points

- **Main App**: http://ed-tech-05bu.onrender.com
- **Admin Panel**: http://ed-tech-05bu.onrender.com/admin/
- **API Endpoints**: http://ed-tech-05bu.onrender.com/api/
- **API Docs**: http://ed-tech-05bu.onrender.com/api/docs/

## Environment Variables

Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Production Deployment

For production servers, use a process manager like systemd or supervisor:

### Using systemd (Linux)
Create `/etc/systemd/system/edtech-backend.service`:
```ini
[Unit]
Description=EdTech Backend Service
After=network.target

[Service]
User=your-user
Group=your-group
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/.venv/bin"
ExecStart=/path/to/backend/.venv/bin/python -m uvicorn edtech_project.asgi:application --host 0.0.0.0 --port 8003 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable edtech-backend
sudo systemctl start edtech-backend
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8003
lsof -ti:8003 | xargs kill -9
```

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

### Permission Issues
```bash
# Fix permissions
chmod +x deploy_backend.sh
chmod 755 -R .
```