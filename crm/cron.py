# File: crm/cron.py

from datetime import datetime
import requests
import json

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm CRM health
    """
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = "/tmp/crm_heartbeat_log.txt"
    
    # Basic heartbeat message
    heartbeat_msg = f"{timestamp} CRM is alive"
    
    # Optional: Test GraphQL endpoint responsiveness
    try:
        # Simple GraphQL hello query
        graphql_query = {
            "query": "{ hello }"
        }
        
        response = requests.post(
            "http://localhost:8000/graphql",
            json=graphql_query,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and 'hello' in result['data']:
                heartbeat_msg += " - GraphQL endpoint responsive"
            else:
                heartbeat_msg += " - GraphQL endpoint returned unexpected response"
        else:
            heartbeat_msg += f" - GraphQL endpoint error (HTTP {response.status_code})"
            
    except requests.RequestException as e:
        heartbeat_msg += f" - GraphQL endpoint unavailable ({str(e)})"
    except Exception as e:
        heartbeat_msg += f" - Heartbeat check error ({str(e)})"
    
    # Append to log file
    with open(log_file, 'a') as f:
        f.write(heartbeat_msg + '\n')
    
    print(f"Heartbeat logged: {heartbeat_msg}")


def update_low_stock():
    """
    Updates low-stock products using GraphQL mutation
    Runs every 12 hours
    """
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = "/tmp/low_stock_updates_log.txt"
    
    try:
        # GraphQL mutation for updating low stock products
        mutation = {
            "query": """
            mutation UpdateLowStockProducts {
                updateLowStockProducts {
                    result {
                        success
                        message
                        updatedProducts {
                            id
                            name
                            stock
                        }
                    }
                }
            }
            """
        }
        
        response = requests.post(
            "http://localhost:8000/graphql",
            json=mutation,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'updateLowStockProducts' in result['data']:
                mutation_result = result['data']['updateLowStockProducts']['result']
                updated_products = mutation_result.get('updatedProducts', [])
                
                with open(log_file, 'a') as f:
                    f.write(f"\n[{timestamp}] Low stock update process:\n")
                    f.write(f"Success: {mutation_result.get('success', False)}\n")
                    f.write(f"Message: {mutation_result.get('message', 'No message')}\n")
                    
                    if updated_products:
                        f.write(f"Updated {len(updated_products)} products:\n")
                        for product in updated_products:
                            f.write(f"  - {product['name']}: new stock level {product['stock']}\n")
                    else:
                        f.write("No products needed updating\n")
                
                print(f"Low stock update completed - {len(updated_products)} products updated")
            else:
                error_msg = f"[{timestamp}] GraphQL mutation failed - unexpected response format\n"
                with open(log_file, 'a') as f:
                    f.write(error_msg)
                print("Low stock update failed - unexpected response")
        else:
            error_msg = f"[{timestamp}] HTTP error {response.status_code} during low stock update\n"
            with open(log_file, 'a') as f:
                f.write(error_msg)
            print(f"Low stock update failed - HTTP {response.status_code}")
            
    except Exception as e:
        error_msg = f"[{timestamp}] Exception during low stock update: {str(e)}\n"
        with open(log_file, 'a') as f:
            f.write(error_msg)
        print(f"Low stock update error: {e}")