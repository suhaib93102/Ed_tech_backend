# Supabase PostgreSQL Integration Guide

## Overview
This guide covers complete integration of Supabase PostgreSQL database with your Django EdTech platform, replacing SQLite with production-grade PostgreSQL.

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- **PostgreSQL Database** - Powerful relational database
- **Real-time Updates** - WebSocket support for live data
- **Authentication** - Built-in user management
- **Storage** - File storage for media
- **Edge Functions** - Serverless backend functions

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Your Django App                           │
│  (edtech_project - running on localhost:8000)               │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     │ PostgreSQL Driver (psycopg2)
                     │
┌────────────────────v─────────────────────────────────────────┐
│              Supabase PostgreSQL (Cloud)                     │
│  Host: aws-1-ap-southeast-1.pooler.supabase.com:5432        │
│  Database: postgres                                          │
│  User: postgres                                              │
└──────────────────────────────────────────────────────────────┘
```

## Current Configuration

Your `.env` file already contains Supabase credentials:

```
SUPABASE_URL=postgresql://postgres.vuuitrhrnlhvtfssgikl:54G7qr8faBFuXvqK@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### Connection String Breakdown:
- **User**: `postgres`
- **Password**: `54G7qr8faBFuXvqK`
- **Host**: `aws-1-ap-southeast-1.pooler.supabase.com`
- **Port**: `5432` (standard PostgreSQL port)
- **Database**: `postgres`
- **Region**: `ap-southeast-1` (Asia Pacific - Singapore)

## Step 1: Verify Supabase Connection

### Test Connection with psql

```bash
# Install PostgreSQL client (if not already installed)
brew install postgresql  # macOS

# Test connection
PGPASSWORD="54G7qr8faBFuXvqK" psql \
  -h aws-1-ap-southeast-1.pooler.supabase.com \
  -p 5432 \
  -U postgres \
  -d postgres \
  -c "SELECT version();"

# Expected output:
# PostgreSQL 14.x on x86_64-pc-linux-gnu...
```

### Test with Python

```python
import psycopg2

conn = psycopg2.connect(
    host="aws-1-ap-southeast-1.pooler.supabase.com",
    port=5432,
    database="postgres",
    user="postgres",
    password="54G7qr8faBFuXvqK"
)

cursor = conn.cursor()
cursor.execute("SELECT 1")
print("Connected to Supabase!")
cursor.close()
conn.close()
```

## Step 2: Configure Django to Use Supabase

### Update `settings.py`

```python
# File: edtech_project/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

# Parse Supabase connection string
SUPABASE_URL = os.getenv('SUPABASE_URL')

def parse_database_url(url):
    """Parse PostgreSQL connection string from Supabase"""
    # Example: postgresql://user:password@host:port/database
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', '')
    
    auth, rest = url.split('@')
    user, password = auth.split(':')
    host_port, database = rest.split('/')
    host, port = host_port.split(':')
    
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': database,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port,
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',  # Supabase requires SSL
        }
    }

# Database Configuration
DATABASES = {
    'default': parse_database_url(SUPABASE_URL) if SUPABASE_URL else {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Ensure PostgreSQL is used
if 'postgresql' not in DATABASES['default']['ENGINE']:
    raise ImproperlyConfigured(
        "This project requires PostgreSQL. "
        "Set SUPABASE_URL environment variable."
    )

print(f"Using database: {DATABASES['default']['NAME']} @ {DATABASES['default']['HOST']}")
```

### Install PostgreSQL Adapter

```bash
# Install psycopg2 (PostgreSQL adapter for Python)
pip install psycopg2-binary

# Or compile version (recommended for production)
pip install psycopg2

# Verify installation
python -c "import psycopg2; print(psycopg2.__version__)"
```

## Step 3: Migrate Database from SQLite to PostgreSQL

### Backup Current Data (SQLite)

```bash
# Backup SQLite database
cp db.sqlite3 db.sqlite3.backup

# Export data as JSON (optional)
python manage.py dumpdata > data_backup.json
```

### Create Schema on Supabase

```bash
# Run migrations on Supabase
python manage.py migrate --database=default

# Create tables (if first time)
python manage.py migrate --run-syncdb

# Verify tables created
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute(\"\"\"
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
\"\"\")
for table in cursor.fetchall():
    print(f'✓ {table[0]}')
"
```

### Restore Data to Supabase (if needed)

```bash
# Load data from JSON backup
python manage.py loaddata data_backup.json

# Or use SQL directly
python manage.py dbshell < backup.sql
```

## Step 4: Verify Tables and Schema

### List All Tables

```bash
python manage.py dbshell << EOF
\dt public.*;
EOF
```

### Check Specific Tables

```python
# Python script to verify tables
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.apps import apps

print("Django Apps and Models:")
for app_config in apps.get_app_configs():
    print(f"\n{app_config.label}:")
    for model in app_config.get_models():
        print(f"  • {model.__name__}")

# Verify table exists
from question_solver.models import SubscriptionPlan
plans = SubscriptionPlan.objects.all()
print(f"\nSubscription Plans in Database: {plans.count()}")
for plan in plans:
    print(f"  • {plan.name}: ₹{plan.first_price}")
```

## Step 5: Create Indexes for Performance

```sql
-- Connect to Supabase and run these SQL commands
-- For better query performance

-- Index on user ID (most queries filter by user)
CREATE INDEX CONCURRENTLY idx_user_subscriptions_user_id 
ON question_solver_usersubscription(user_id);

-- Index on feature name (feature access checks)
CREATE INDEX CONCURRENTLY idx_feature_usage_feature 
ON question_solver_featureusagelog(feature_name);

-- Index on user and feature (combined lookups)
CREATE INDEX CONCURRENTLY idx_feature_usage_user_feature 
ON question_solver_featureusagelog(user_id, feature_name);

-- Index on created_at (time-based queries)
CREATE INDEX CONCURRENTLY idx_feature_usage_created 
ON question_solver_featureusagelog(created_at DESC);

-- Index on session_id (pair quiz lookups)
CREATE INDEX CONCURRENTLY idx_pair_quiz_session_id 
ON question_solver_pairquizsession(session_id);
```

### Verify Indexes

```python
from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT indexname 
    FROM pg_indexes 
    WHERE tablename NOT LIKE 'pg_%' 
    ORDER BY tablename, indexname
""")

print("Created Indexes:")
for index in cursor.fetchall():
    print(f"  ✓ {index[0]}")
```

## Step 6: Enable Real-time Updates (Optional)

Supabase provides real-time updates via WebSocket. To enable:

```python
# Install Supabase client library
pip install supabase

# Use in your Django code
from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Listen to real-time updates
def listen_to_subscriptions():
    subscription = supabase.realtime.on(
        'question_solver_usersubscription',
        'INSERT',
        callback=on_subscription_created
    ).subscribe()

def on_subscription_created(payload):
    print(f"New subscription: {payload['new']}")
```

## Step 7: Environment Variables

### Complete `.env` Configuration

```bash
# Supabase PostgreSQL
SUPABASE_URL=postgresql://postgres.vuuitrhrnlhvtfssgikl:54G7qr8faBFuXvqK@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres

# Django Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-256-bits
ALLOWED_HOSTS=localhost,127.0.0.1,ed-tech-05bu.onrender.com

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-256-bits
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Keys
RAZORPAY_KEY_ID=rzp_live_RpW8iXPZdjGo6y
RAZORPAY_KEY_SECRET=bxPr9jrDfrQcCZHfpHmDIURD
GEMINI_API_KEY=AIzaSyBhDptUGKf0q3g5KmkU9ghntXWdF_49_mA
YOUTUBE_API_KEY=AIzaSyCfTI56S7y49YbdOyD76_8F0lUDRnSCBFU
BING_SEARCH_API_KEY=BU6Jztgz9McNbMT8Vo9UwTfT
SERP_API_KEY=VCkVRCJu88Uwr5xTvXnuWSNC
FIRECRAWL_API_KEY=fc-3d9f98b485264031971abb4ab1c36d3e

# Frontend
FRONTEND_REDIRECT_URI=http://localhost:8081

# Tokens
REFRESH_TOKEN_EXPIRATION_DAYS=7
```

## Step 8: Connection Pooling

For production, use connection pooling to handle multiple concurrent connections:

```python
# Add to settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... other settings ...
        'CONN_MAX_AGE': 600,  # Persistent connections
        'ATOMIC_REQUESTS': True,  # Wrap each request in transaction
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',
            'options': '-c statement_timeout=30000'  # 30 second timeout
        }
    }
}

# Enable PgBouncer for connection pooling (optional)
# Configure at Supabase dashboard
```

## Step 9: Backup and Recovery

### Automated Backups

Supabase provides daily automated backups. Check them:

```bash
# Via Supabase Dashboard:
# 1. Go to Database → Backups
# 2. View daily automated backups
# 3. Download full backup if needed
```

### Manual Backup

```bash
# Backup to file
PGPASSWORD="54G7qr8faBFuXvqK" pg_dump \
  -h aws-1-ap-southeast-1.pooler.supabase.com \
  -p 5432 \
  -U postgres \
  -d postgres \
  -f backup_$(date +%Y%m%d).sql

# Restore from backup
PGPASSWORD="54G7qr8faBFuXvqK" psql \
  -h aws-1-ap-southeast-1.pooler.supabase.com \
  -p 5432 \
  -U postgres \
  -d postgres \
  -f backup_20260106.sql
```

## Step 10: Monitoring and Metrics

### Monitor Database Performance

```python
# Add to Django views for monitoring
from django.db import connection
from django.http import JsonResponse

def db_stats(request):
    with connection.cursor() as cursor:
        # Check active connections
        cursor.execute("""
            SELECT count(*) as connection_count 
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        connections = cursor.fetchone()[0]
        
        # Check slow queries
        cursor.execute("""
            SELECT query, calls, mean_time 
            FROM pg_stat_statements 
            ORDER BY mean_time DESC 
            LIMIT 5
        """)
        slow_queries = cursor.fetchall()
        
        return JsonResponse({
            'active_connections': connections,
            'slow_queries': [
                {
                    'query': q[0][:100],
                    'calls': q[1],
                    'avg_time_ms': q[2]
                } for q in slow_queries
            ]
        })
```

### View Supabase Metrics

```bash
# Via Supabase Dashboard:
# 1. Database → Monitoring
# 2. View real-time metrics:
#    - Active Connections
#    - Database Size
#    - Read/Write Operations
#    - Query Performance
```

## Troubleshooting

### Connection Refused

```bash
# Problem: "could not connect to server"
# Solution: Check network access

# Test connection
nc -zv aws-1-ap-southeast-1.pooler.supabase.com 5432

# If fails, whitelist IP in Supabase:
# Database → Networking → Add IP
```

### SSL Certificate Error

```bash
# Problem: "certificate verify failed"
# Solution: Update settings.py

DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'sslmode': 'require',  # or 'allow' if certificate issues
        }
    }
}
```

### Slow Queries

```bash
# Monitor slow queries
PGPASSWORD="password" psql -c "
  SELECT query, calls, mean_time 
  FROM pg_stat_statements 
  WHERE mean_time > 100 
  ORDER BY mean_time DESC
"

# Create indexes for slow queries
CREATE INDEX idx_name ON table(column);
```

### Out of Connections

```bash
# Problem: "remaining connection slots are reserved"
# Solution: Increase connection limit or use connection pooling

# Check current connections
psql -c "
  SELECT count(*) 
  FROM pg_stat_activity 
  WHERE datname = 'postgres'
"

# In settings.py, reduce CONN_MAX_AGE or use PgBouncer
```

## Performance Tips

1. **Use EXPLAIN ANALYZE**
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM question_solver_usersubscription WHERE user_id = 123;
   ```

2. **Enable Query Cache**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **Use Batch Operations**
   ```python
   # Instead of loops
   SubscriptionPlan.objects.bulk_create([...])
   ```

4. **Enable Connection Pooling**
   ```python
   'CONN_MAX_AGE': 600  # Keep connections alive
   ```

## Production Checklist

- ✅ SUPABASE_URL configured in environment
- ✅ psycopg2 installed and configured
- ✅ All migrations run successfully
- ✅ Indexes created for common queries
- ✅ SSL mode enabled (sslmode=require)
- ✅ Connection pooling configured
- ✅ Backup strategy in place
- ✅ Monitoring enabled
- ✅ Error logging configured
- ✅ Whitelist IP addresses (if needed)

## Migration from SQLite to Supabase

```bash
# Step-by-step migration
1. Backup SQLite:
   cp db.sqlite3 db.sqlite3.backup

2. Configure settings.py to use Supabase

3. Run migrations:
   python manage.py migrate

4. Export SQLite data:
   python manage.py dumpdata > data.json

5. Load into Supabase:
   python manage.py loaddata data.json

6. Verify data:
   python manage.py shell
   >>> from question_solver.models import *
   >>> SubscriptionPlan.objects.count()
   3

7. Delete db.sqlite3 to force Supabase usage
   rm db.sqlite3
```

## Summary

Your Supabase PostgreSQL database is now fully integrated! You have:

✅ Cloud-based PostgreSQL database in Asia Pacific region
✅ Automatic daily backups
✅ SSL-encrypted connections
✅ Production-ready performance
✅ Real-time capabilities (optional)
✅ Advanced monitoring and metrics
✅ Scalable for growth

## Next Steps

1. Test all API endpoints with Supabase backend
2. Verify all 10 features work correctly
3. Monitor performance metrics
4. Set up automated backups
5. Configure Redis caching for optimization
6. Deploy to production environment
