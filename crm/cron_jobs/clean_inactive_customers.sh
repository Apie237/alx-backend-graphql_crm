#!/bin/bash

# Customer cleanup script - removes customers with no orders since a year ago
# File: crm/cron_jobs/clean_inactive_customers.sh

# Get current date and timestamp
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Change to project directory
cd /path/to/alx-backend-graphql_crm

# Use Django's manage.py shell to execute a Python command that deletes customers with no orders since a year ago
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer, Order
from django.utils import timezone
from datetime import timedelta

# Get date one year ago using 365 days
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the last year
inactive_customers = Customer.objects.exclude(
    order__order_date__gte=one_year_ago
).distinct()

# Count before deletion
count = inactive_customers.count()

# Delete inactive customers
inactive_customers.delete()

# Print count for capture
print(count)
")

# Log the result with timestamp to /tmp/customer_cleanup_log.txt
echo "[$CURRENT_DATE] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt

echo "Customer cleanup completed. Deleted $DELETED_COUNT customers."