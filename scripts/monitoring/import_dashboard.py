#!/usr/bin/env python3
"""
Script to manually import the Grafana dashboard if provisioning doesn't work.
"""
import requests
import json
import time

def import_dashboard():
    """Import the RAG dashboard into Grafana."""
    
    # Grafana configuration
    grafana_url = "http://localhost:3000"
    username = "admin"
    password = "admin"
    
    # Load dashboard JSON
    try:
        with open("monitoring/dashboards/rag-dashboard.json", "r") as f:
            dashboard_data = json.load(f)
    except FileNotFoundError:
        print("❌ Dashboard file not found!")
        return False
    
    # Create session
    session = requests.Session()
    session.auth = (username, password)
    
    # Check if Grafana is running
    try:
        response = session.get(f"{grafana_url}/api/health")
        if response.status_code != 200:
            print("❌ Grafana is not running or not accessible")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Grafana: {e}")
        return False
    
    # Import dashboard
    try:
        # Remove the 'dashboard' wrapper if it exists
        if 'dashboard' in dashboard_data:
            dashboard = dashboard_data['dashboard']
        else:
            dashboard = dashboard_data
            
        # Set dashboard to be overwritable
        dashboard['overwrite'] = True
        
        # Import the dashboard
        response = session.post(
            f"{grafana_url}/api/dashboards/db",
            json=dashboard,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard imported successfully!")
            print(f"   Dashboard ID: {result.get('id')}")
            print(f"   Dashboard URL: {grafana_url}{result.get('url')}")
            return True
        else:
            print(f"❌ Failed to import dashboard: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing dashboard: {e}")
        return False

def check_dashboard_exists():
    """Check if the dashboard already exists."""
    grafana_url = "http://localhost:3000"
    username = "admin"
    password = "admin"
    
    session = requests.Session()
    session.auth = (username, password)
    
    try:
        response = session.get(f"{grafana_url}/api/search?query=RAG")
        if response.status_code == 200:
            dashboards = response.json()
            for dashboard in dashboards:
                if "RAG Demo" in dashboard.get('title', ''):
                    print(f"✅ Dashboard already exists: {dashboard['title']}")
                    print(f"   URL: {grafana_url}{dashboard['url']}")
                    return True
        return False
    except Exception as e:
        print(f"❌ Error checking existing dashboards: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking if RAG dashboard exists...")
    
    if check_dashboard_exists():
        print("✅ Dashboard already exists, no need to import!")
    else:
        print("📥 Dashboard not found, importing...")
        if import_dashboard():
            print("\n🎉 Dashboard import completed!")
            print("   Go to http://localhost:3000 to view your dashboard")
        else:
            print("\n❌ Dashboard import failed!")
            print("   Make sure Grafana is running and accessible")
