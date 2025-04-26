import sys
import traceback
import os
import json
import psycopg2
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QWidget
from PyQt5.QtCore import Qt, QTimer

# Define the path for storing connection settings
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".HospitalManagementSystem")
CONFIG_FILE = os.path.join(CONFIG_DIR, "connection_config.json")

def save_connection_params(connection_params):
    """Save connection parameters to a configuration file"""
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # Write connection parameters to file
        with open(CONFIG_FILE, 'w') as f:
            json.dump(connection_params, f)
        
        return True
    except Exception as e:
        print(f"Error saving connection parameters: {e}")
        return False

def load_connection_params():
    """Load connection parameters from a configuration file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            'host': 'localhost',
            'port': '5432',
            'database': 'huntsvillehospital',
            'user': 'postgres',
            'password': ''
        }
    except Exception as e:
        print(f"Error loading connection parameters: {e}")
        return {
            'host': 'localhost',
            'port': '5432',
            'database': 'huntsvillehospital',
            'user': 'postgres',
            'password': ''
        }


def check_database_exists():
    """Check if we can connect to the database with saved parameters"""
    try:
        # Load connection parameters
        connection_params = load_connection_params()
        
        # Connect to the specified database
        conn = psycopg2.connect(
            host=connection_params['host'],
            port=connection_params['port'],
            database=connection_params['database'],
            user=connection_params['user'],
            password=connection_params['password']
        )
        
        # Check that the Staff table exists
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'staff');")
        table_exists = cursor.fetchone()[0]
        
        # Close connections
        cursor.close()
        conn.close()
        
        # Return True if it's a valid hospital database
        return table_exists
    
    except Exception as e:
        # If there's an error connecting to the database, return False
        print(f"Error checking database connection: {e}")
        return False