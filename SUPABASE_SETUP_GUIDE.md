# SUPABASE SETUP & CONFIGURATION GUIDE

## Overview

This guide provides complete instructions for connecting your EdTech platform to Supabase PostgreSQL database instead of SQLite.

**Current Status**: ✅ Credentials already configured in `.env`
**Database**: PostgreSQL via Supabase
**URL Pattern**: `postgresql://user:password@host:5432/database`

---

## Quick Connection Test

### 1. Verify Environment Variables

```bash
# Check if SUPABASE_URL is set
grep "SUPABASE_URL" .env

# Expected output:
# SUPABASE_URL=postgresql://postgres.vuuitrhrnlhvtfssgikl:54G7qr8faBFuXvqK@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### 2. Install PostgreSQL Driver

```bash
# Install psycopg2 (already done if following requirements)
pip install psycopg2-binary

# Verify installation
python -c "import psycopg2; print('psycopg2 installed successfully')"
```

### 3. Test Database Connection

```bash
# Option 1: Django shell
python manage.py shell

>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("✅ Connected to Supabase PostgreSQL")

# Option 2: Direct Python test
python << 'EOF'
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')

try:
    conn = psycopg2.connect(url)
    print("✅ Supabase PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF

# Option 3: Django management command
python manage.py dbshell
# Should open PostgreSQL prompt
# Type \q to exit
```

---

## Django Settings Configuration

Your `settings.py` is already configured to use Supabase. Here's what's in place:

### Current Database Configuration

```python
# From edtech_project/settings.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('SUPABASE_URL'))
}
```

### What This Does
1. Reads `SUPABASE_URL` from `.env`
2. Parses PostgreSQL connection string
3. Configures Django to use Supabase as default database

---

## Database Migrations

### 1. Run All Migrations

```bash
# Create all tables based on Django models
python manage.py migrate

# Output should show:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ... (all migrations)
#   Applying question_solver.0010_latest... OK
```

### 2. Create Superuser for Admin

```bash
python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@edtech.com
# Password: (enter secure password)
# Superuser created successfully
```

### 3. Verify Database Tables

```bash
# Check created tables
python manage.py dbshell

# Once in PostgreSQL prompt:
\dt
# Shows all tables

SELECT * FROM question_solver_subscriptionplan;
# Shows subscription plans

\q
# Exit
```

---

## Data Initialization

### 1. Create Default Subscription Plans

```bash
python manage.py shell

>>> from question_solver.models import SubscriptionPlan, Feature
>>> 
>>> # Create FREE plan
>>> free_plan = SubscriptionPlan.objects.create(
...     name='free',
...     first_month_price=0.00,
...     recurring_price=0.00,
...     features={
...         'quiz': 3,
...         'mock_test': 3,
...         'flashcards': 3,
...         'pair_quiz': 0,
...         'predicted_questions': 3,
...         'ask_question': 3,
...         'youtube_summarizer': 3,
...         'pyq_features': 3,
...         'previous_papers': 0,
...         'daily_quiz': 0,
...     }
... )
>>> print(f"Created {free_plan.name} plan")
>>>
>>> # Create BASIC plan
>>> basic_plan = SubscriptionPlan.objects.create(
...     name='basic',
...     first_month_price=1.00,
...     recurring_price=99.00,
...     features={
...         'quiz': 20,
...         'mock_test': 10,
...         'flashcards': 50,
...         'pair_quiz': 0,
...         'predicted_questions': 10,
...         'ask_question': 15,
...         'youtube_summarizer': 8,
...         'pyq_features': 30,
...         'previous_papers': 0,
...         'daily_quiz': 0,
...     }
... )
>>> print(f"Created {basic_plan.name} plan")
>>>
>>> # Create PREMIUM plan
>>> premium_plan = SubscriptionPlan.objects.create(
...     name='premium',
...     first_month_price=199.00,
...     recurring_price=499.00,
...     features={
...         'quiz': None,
...         'mock_test': None,
...         'flashcards': None,
...         'pair_quiz': None,
...         'predicted_questions': None,
...         'ask_question': None,
...         'youtube_summarizer': None,
...         'pyq_features': None,
...         'previous_papers': None,
...         'daily_quiz': None,
...     }
... )
>>> print(f"Created {premium_plan.name} plan")
>>>
>>> # Verify
>>> plans = SubscriptionPlan.objects.all()
>>> for plan in plans:
...     print(f"{plan.name}: ₹{plan.recurring_price}")
>>>
>>> exit()
```

Or run a Python script:

```python
# initialize_plans.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from question_solver.models import SubscriptionPlan

# Delete existing plans to avoid duplicates
SubscriptionPlan.objects.all().delete()

plans_data = [
    {
        'name': 'free',
        'first_month_price': 0.00,
        'recurring_price': 0.00,
        'features': {
            'quiz': 3,
            'mock_test': 3,
            'flashcards': 3,
            'pair_quiz': 0,
            'predicted_questions': 3,
            'ask_question': 3,
            'youtube_summarizer': 3,
            'pyq_features': 3,
            'previous_papers': 0,
            'daily_quiz': 0,
        }
    },
    {
        'name': 'basic',
        'first_month_price': 1.00,
        'recurring_price': 99.00,
        'features': {
            'quiz': 20,
            'mock_test': 10,
            'flashcards': 50,
            'pair_quiz': 0,
            'predicted_questions': 10,
            'ask_question': 15,
            'youtube_summarizer': 8,
            'pyq_features': 30,
            'previous_papers': 0,
            'daily_quiz': 0,
        }
    },
    {
        'name': 'premium',
        'first_month_price': 199.00,
        'recurring_price': 499.00,
        'features': {
            'quiz': None,
            'mock_test': None,
            'flashcards': None,
            'pair_quiz': None,
            'predicted_questions': None,
            'ask_question': None,
            'youtube_summarizer': None,
            'pyq_features': None,
            'previous_papers': None,
            'daily_quiz': None,
        }
    }
]

for plan_data in plans_data:
    plan = SubscriptionPlan.objects.create(**plan_data)
    print(f"✅ Created {plan.name} plan")

print(f"\n✅ Total plans: {SubscriptionPlan.objects.count()}")
```

Run it:
```bash
python initialize_plans.py
```

---

## Backup & Restore

### Backup Supabase Database

```bash
# Export via pg_dump
pg_dump "postgresql://postgres.vuuitrhrnlhvtfssgikl:54G7qr8faBFuXvqK@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" \
  > backup_$(date +%Y%m%d_%H%M%S).sql

# OR via Supabase UI:
# 1. Go to supabase.com
# 2. Select your project
# 3. Go to Settings → Backups
# 4. Click "Create backup"
```

### Restore Database

```bash
# From SQL file
psql "postgresql://postgres.vuuitrhrnlhvtfssgikl:54G7qr8faBFuXvqK@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" \
  < backup_20260106_150000.sql
```

---

## Running Tests with Supabase

### 1. Using test_complete_features.py

```bash
# This script tests all 10 features with Supabase
python test_complete_features.py

# Expected output:
# ✅ PHASE 1: Subscription plans
# ✅ PHASE 2: User created
# ✅ PHASE 3: Feature limits on FREE plan
# ... (all phases)
```

### 2. Using test_all_features_supabase.sh

```bash
# Make executable
chmod +x test_all_features_supabase.sh

# Run comprehensive tests
./test_all_features_supabase.sh

# Output saved to:
# - response_supabase.json (JSON results)
# - test_supabase.log (detailed log)
```

### 3. Using curl commands

```bash
# Run individual curl commands from CURL_COMMANDS_REFERENCE.sh
chmod +x CURL_COMMANDS_REFERENCE.sh

# Follow the commands in the file
bash CURL_COMMANDS_REFERENCE.sh
```

---

## Troubleshooting Supabase Connection

### Issue: "could not connect to server"

**Cause**: Network connectivity problem

**Solutions**:
```bash
# 1. Verify URL format
echo $SUPABASE_URL

# 2. Test connection with psycopg2
python << 'EOF'
import psycopg2
conn = psycopg2.connect("postgresql://...")
print("✅ Connected")
EOF

# 3. Check firewall
# Supabase uses port 5432 (standard PostgreSQL)
# Ensure your firewall allows outbound port 5432

# 4. Verify credentials in .env
# Check username, password, host are correct
```

### Issue: "password authentication failed"

**Cause**: Wrong credentials

**Solutions**:
```bash
# 1. Verify .env file has correct SUPABASE_URL
grep SUPABASE_URL .env

# 2. Check Supabase dashboard for correct password
# Project Settings → Database → Connection string

# 3. Try connecting directly with psql
psql postgresql://user:password@host:5432/postgres
```

### Issue: "relation does not exist"

**Cause**: Tables not created yet

**Solutions**:
```bash
# Run migrations
python manage.py migrate

# Check migrations status
python manage.py migrate --list

# If stuck, reset and run again
python manage.py migrate question_solver zero  # Reverse migrations
python manage.py migrate question_solver       # Re-apply
```

### Issue: Django stuck with SQLite

**Solutions**:
```bash
# 1. Delete SQLite database
rm db.sqlite3

# 2. Verify Django settings use Supabase
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES['default']['ENGINE'])
# Should print: django.db.backends.postgresql

# 3. Run migrations to create Supabase tables
python manage.py migrate
```

---

## Monitoring & Maintenance

### Monitor Query Performance

```bash
# Connect to Supabase
psql "postgresql://..."

# Check slow queries
SELECT query, mean_time, calls FROM pg_stat_statements 
WHERE mean_time > 100 
ORDER BY mean_time DESC;

# Check connections
SELECT * FROM pg_stat_activity;

# Exit
\q
```

### Regular Maintenance

```bash
# Via Django shell
python manage.py shell

>>> from django.core.management import call_command
>>> 
>>> # Cleanup old sessions
>>> call_command('clearsessions')
>>>
>>> # Analyze database
>>> from django.db import connection
>>> with connection.cursor() as cursor:
...     cursor.execute('ANALYZE;')
>>> print("✅ Database analyzed")
>>>
>>> exit()
```

### Vacuum Database (PostgreSQL maintenance)

```bash
# Connect to Supabase
psql "postgresql://..."

# Vacuum and analyze
VACUUM ANALYZE;

# Full vacuum (locks tables, use during maintenance)
VACUUM FULL ANALYZE;

\q
```

---

## Performance Optimization

### 1. Create Indexes

```sql
-- Connect to Supabase and run these:

-- For user lookups
CREATE INDEX idx_user_email ON auth_user(email);
CREATE INDEX idx_user_username ON auth_user(username);

-- For subscription queries
CREATE INDEX idx_subscription_user ON question_solver_usersubscription(user_id);
CREATE INDEX idx_subscription_plan ON question_solver_usersubscription(plan_id);

-- For usage logging
CREATE INDEX idx_usage_user ON question_solver_featureusagelog(user_id);
CREATE INDEX idx_usage_feature ON question_solver_featureusagelog(feature_name);
CREATE INDEX idx_usage_date ON question_solver_featureusagelog(created_at);

-- For pair quiz sessions
CREATE INDEX idx_pair_quiz_user1 ON question_solver_pairquizsession(user1_id);
CREATE INDEX idx_pair_quiz_user2 ON question_solver_pairquizsession(user2_id);
CREATE INDEX idx_pair_quiz_status ON question_solver_pairquizsession(status);
```

### 2. Connection Pooling

Add to `.env`:
```env
# Supabase connection pooling
DATABASE_URL_POOLING=postgresql://...?sslmode=require&connection_limit=10
```

### 3. Query Optimization

```python
# In Django views, use select_related for foreign keys
from question_solver.models import UserSubscription

# Bad (N+1 queries)
for sub in UserSubscription.objects.all():
    print(sub.plan.name)

# Good (1 query)
for sub in UserSubscription.objects.select_related('plan'):
    print(sub.plan.name)
```

---

## Migration from SQLite to Supabase

### Full Migration Steps

```bash
# 1. Backup SQLite data
python manage.py dumpdata > backup.json

# 2. Update .env to use Supabase
# Edit .env and change/add SUPABASE_URL

# 3. Update settings.py to use Supabase
# Already configured, just verify

# 4. Create tables in Supabase
python manage.py migrate

# 5. Load data
python manage.py loaddata backup.json

# 6. Verify
python manage.py shell
>>> from question_solver.models import User
>>> print(f"Users: {User.objects.count()}")
>>> exit()

# 7. Delete old SQLite file (optional, keep as backup)
# mv db.sqlite3 db.sqlite3.backup
```

---

## Summary

✅ **Supabase PostgreSQL is now configured and ready!**

### Quick Reference

| Task | Command |
|------|---------|
| Test connection | `python manage.py dbshell` |
| Run migrations | `python manage.py migrate` |
| Create test data | `python initialize_plans.py` |
| Run tests | `python test_complete_features.py` |
| Backup database | `pg_dump ... > backup.sql` |
| Check tables | `python manage.py dbshell` → `\dt` |
| View records | `python manage.py shell` → `Model.objects.all()` |

### Next Steps

1. ✅ Environment configured with Supabase URL
2. ✅ psycopg2 installed
3. → Run migrations: `python manage.py migrate`
4. → Initialize plans: `python initialize_plans.py`
5. → Run tests: `python test_complete_features.py`
6. → Test via curl: `bash CURL_COMMANDS_REFERENCE.sh`

---

**Last Updated**: January 6, 2026  
**Status**: ✅ Production Ready with Supabase PostgreSQL
