import requests
from celery import shared_task
from datetime import datetime

@shared_task
def generate_crm_report():
    """
    Generate weekly CRM report using GraphQL queries.
    Fetches total customers, orders, and revenue.
    """
    try:
        from gql import gql, Client
        from gql.transport.requests import RequestsHTTPTransport
        
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to fetch CRM statistics
        query = gql("""
            query GetCRMStats {
                customers {
                    id
                }
                orders {
                    id
                    totalAmount
                }
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Calculate statistics
        total_customers = len(result.get('customers', []))
        orders = result.get('orders', [])
        total_orders = len(orders)
        
        # Calculate total revenue (sum of totalAmount from all orders)
        total_revenue = 0
        for order in orders:
            try:
                total_revenue += float(order.get('totalAmount', 0))
            except (ValueError, TypeError):
                continue
        
        # Create timestamp and report message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue"
        
        # Log the report to file
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(report_message + '\n')
        
        return {
            'success': True,
            'message': report_message,
            'data': {
                'customers': total_customers,
                'orders': total_orders,
                'revenue': total_revenue
            }
        }
        
    except Exception as e:
        error_message = f"Error generating CRM report: {str(e)}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_log = f"{timestamp} - ERROR: {error_message}"
        
        # Log error to file
        try:
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(error_log + '\n')
        except IOError:
            pass
        
        return {
            'success': False,
            'message': error_message,
            'data': None
        }