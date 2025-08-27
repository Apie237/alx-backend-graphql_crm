# CRM Celery Task Scheduler Setup

This document provides step-by-step instructions to set up Celery with Celery Beat for automated CRM report generation.

## Overview

The system generates weekly CRM reports every Monday at 6:00 AM UTC, including:
- Total number of customers
- Total number of orders  
- Total revenue (sum of all order amounts)

Reports are logged to `/tmp/crm_report_log.txt` with timestamps.

## Prerequisites

- Python 3.8+
- Django project with GraphQL endpoint
- Redis server

## Installation Steps

### 1. Install Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### Windows:
Download and install Redis from the official website or use Docker:
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 2. Verify Redis Installation

```bash
redis-cli ping
# Should return: PONG
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Django Migrations

```bash
python manage.py migrate
```

This creates the necessary database tables for django-celery-beat to store periodic tasks.

### 5. Start the Services

Open multiple terminal windows/tabs for the following commands:

#### Terminal 1: Start Django Development Server
```bash
python manage.py runserver
```

#### Terminal 2: Start Celery Worker
```bash
celery -A crm worker -l info
```

#### Terminal 3: Start Celery Beat Scheduler
```bash
celery -A crm beat -l info
```

## Verification

### 1. Check Celery Worker Status
The worker terminal should show:
```
-------------- celery@hostname v5.x.x
---- **** -----
--- * ***  * -- [Configuration]
-- * - **** ---
- ** ---------- .> app:         crm:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF
--- ***** -----
-------------- [queues]
               .> celery exchange=celery(direct) key=celery
```

### 2. Check Celery Beat Status
The beat terminal should show:
```
celery beat v5.x.x is starting.
LocalTime -> 2024-XX-XX XX:XX:XX
Configuration ->
    . broker -> redis://localhost:6379/0
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> django_celery_beat.schedulers.DatabaseScheduler
```

### 3. Test Manual Task Execution
```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

### 4. Check Log File
```bash
tail -f /tmp/crm_report_log.txt
```

Expected format:
```
2024-01-15 06:00:01 - Report: 150 customers, 45 orders, 12500.50 revenue
```

## Troubleshooting

### Common Issues

#### Redis Connection Error
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
```

#### Task Not Executing
```bash
# Check if task is registered
python manage.py shell -c "from crm.tasks import generate_crm_report; print(generate_crm_report)"

# Check scheduled tasks in Django admin
python manage.py createsuperuser
# Visit http://localhost:8000/admin/django_celery_beat/
```

#### Permission Issues
```bash
# Ensure log file permissions
sudo touch /tmp/crm_report_log.txt
sudo chmod 666 /tmp/crm_report_log.txt
```

### Monitoring

```bash
# View active tasks
celery -A crm inspect active

# View scheduled tasks  
celery -A crm inspect scheduled

# View worker statistics
celery -A crm inspect stats
```

## GraphQL Schema Requirements

Ensure your GraphQL schema includes:

```graphql
type Query {
    customers: [Customer]
    orders: [Order]
}

type Customer {
    id: ID!
}

type Order {
    id: ID!
    totalAmount: Float!
}
```

## File Structure

Your project should have these files:
```
crm/
├── __init__.py
├── celery.py
├── tasks.py
├── settings.py
└── README.md
requirements.txt
```