
import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Add Django project to Python path
sys.path.append('/path/to/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')

import django
django.setup()

def send_order_reminders():
    """Query GraphQL for orders with order_date within the last 7 days and log reminders"""
    
    # GraphQL endpoint
    transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    date_filter = seven_days_ago.strftime('%Y-%m-%d')
    
    # GraphQL query for orders with order_date within the last 7 days
    query = gql("""
    query GetRecentOrders($dateAfter: String!) {
        orders(orderDateAfter: $dateAfter) {
            id
            orderDate
            customer {
                email
                name
            }
            status
        }
    }
    """)
    
    try:
        # Execute the query
        result = client.execute(query, variable_values={"dateAfter": date_filter})
        
        orders = result.get('orders', [])
        
        # Log to /tmp/order_reminders_log.txt
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open("/tmp/order_reminders_log.txt", 'a') as f:
            f.write(f"\n[{timestamp}] Processing order reminders:\n")
            
            for order in orders:
                order_id = order['id']
                customer_email = order['customer']['email']
                
                # Log each order's ID and customer email with timestamp
                log_entry = f"Order ID: {order_id}, Customer Email: {customer_email}\n"
                f.write(log_entry)
            
            f.write(f"Total orders processed: {len(orders)}\n")
        
        # Print required message to console
        print("Order reminders processed!")
        
    except Exception as e:
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing order reminders: {str(e)}\n"
        with open("/tmp/order_reminders_log.txt", 'a') as f:
            f.write(error_msg)
        print(f"Error: {e}")

if __name__ == "__main__":
    send_order_reminders()