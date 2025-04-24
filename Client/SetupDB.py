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

class ConfigureDatabaseScreen(QDialog):
    def __init__(self):
        super(ConfigureDatabaseScreen, self).__init__()
        loadUi("setup.ui", self)
        
        # Store the widget reference
        self.widget = widget
        
        # Set up the screen
        self.setWindowTitle("Configure Database Connection - Hospital Management System")
        
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget_ui = self.findChild(QWidget, "widget")
        if self.widget_ui:
            self.widget_ui.setGeometry(0, 0, screen_width, screen_height)
        
        # Hide progress bar initially
        self.progressBar.setVisible(False)
        
        # Hide admin account setup section
        self.adminGroupBox.setVisible(False)
        self.confirmPasswordLabel.setVisible(False)
        self.confirmPasswordField.setVisible(False)
        
        # Adjust layout for connection-only setup and center elements
        self.centerUI(screen_width, screen_height)
        self.initializeButton.setText("Save & Connect")
    
    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 500
        self.label.setGeometry((screen_width - title_width) // 2, 40, title_width, 61)
        
        # Center the subtitle
        self.label_2.setGeometry((screen_width - title_width) // 2, 100, title_width, 20)
        
        # Center the connection group box
        group_width = 800
        group_height = 300
        self.connectionGroupBox.setGeometry((screen_width - group_width) // 2, 140, group_width, group_height)
        
        # Center the test connection button and label
        button_width = 200
        button_height = 40
        button_spacing = 70
        
        test_y_position = 500
        self.testConnectionButton.setGeometry((screen_width - button_width) // 2, test_y_position, button_width, button_height)
        self.testConnectionLabel.setGeometry((screen_width - 600) // 2, test_y_position - 40, 600, 30)
        
        # Center the initialize button and error message
        init_y_position = test_y_position + button_height + button_spacing
        self.initializeButton.setGeometry((screen_width - button_width) // 2, init_y_position, button_width, button_height)
        self.errorMsg.setGeometry((screen_width - 800) // 2, init_y_position - 40, 800, 30)
        
        # Position the progress bar below the initialize button
        self.progressBar.setGeometry((screen_width - 600) // 2, init_y_position + button_height + 20, 600, 23)
        
        # Load saved connection parameters if available
        self.load_saved_connection_params()
        
        # Connect buttons
        self.testConnectionButton.clicked.connect(self.test_connection)
        self.initializeButton.clicked.connect(self.save_and_connect)
        
        # Set tab order for connection parameters
        self.setTabOrder(self.hostField, self.portField)
        self.setTabOrder(self.portField, self.databaseField)
        self.setTabOrder(self.databaseField, self.usernameField)
        self.setTabOrder(self.usernameField, self.passwordField)
        self.setTabOrder(self.passwordField, self.testConnectionButton)
        self.setTabOrder(self.testConnectionButton, self.initializeButton)
    
    def load_saved_connection_params(self):
        """Load saved connection parameters into the form"""
        connection_params = load_connection_params()
        
        self.hostField.setText(connection_params.get('host', 'localhost'))
        self.portField.setText(connection_params.get('port', '5432'))
        self.databaseField.setText(connection_params.get('database', 'huntsvillehospital'))
        self.usernameField.setText(connection_params.get('user', 'postgres'))
        self.passwordField.setText(connection_params.get('password', ''))
    
    def get_connection_params(self):
        """Get the connection parameters from the form"""
        return {
            'host': self.hostField.text().strip(),
            'port': self.portField.text().strip(),
            'database': self.databaseField.text().strip(),
            'user': self.usernameField.text().strip(),
            'password': self.passwordField.text().strip()
        }
    
    def test_connection(self):
        """Test the database connection with provided credentials"""
        self.errorMsg.setText("")
        self.testConnectionLabel.setText("")
        
        connection_params = self.get_connection_params()
        
        # Validate inputs
        if not connection_params['host'] or not connection_params['port'] or not connection_params['database'] or not connection_params['user']:
            self.errorMsg.setText("All connection fields are required except password (if not needed).")
            return
        
        try:
            # Test connection to the database
            conn = psycopg2.connect(
                host=connection_params['host'],
                port=connection_params['port'],
                database=connection_params['database'],
                user=connection_params['user'],
                password=connection_params['password']
            )
            
            # Test that this is a hospital database by checking if the Staff table exists
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'staff');")
            table_exists = cursor.fetchone()[0]
            
            # Close connections
            cursor.close()
            conn.close()
            
            if table_exists:
                # Connection successful
                self.testConnectionLabel.setStyleSheet("color: green;")
                self.testConnectionLabel.setText("Connection successful! Hospital database verified.")
            else:
                # Connection successful but not a hospital database
                self.testConnectionLabel.setStyleSheet("color: orange;")
                self.testConnectionLabel.setText("Connection successful, but this does not appear to be a hospital database.")
            
        except Exception as e:
            self.errorMsg.setText(f"Connection failed: {str(e)}")
    
    def save_and_connect(self):
        # Clear any previous error message
        self.errorMsg.setText("")
        self.testConnectionLabel.setText("")
        
        # Get connection parameters
        connection_params = self.get_connection_params()
        
        # Validate inputs
        if not connection_params['host'] or not connection_params['port'] or not connection_params['database'] or not connection_params['user']:
            self.errorMsg.setText("All connection fields are required except password (if not needed).")
            return
        
        # Test the connection first
        try:
            conn = psycopg2.connect(
                host=connection_params['host'],
                port=connection_params['port'],
                database=connection_params['database'],
                user=connection_params['user'],
                password=connection_params['password']
            )
            
            # Test that this is a hospital database by checking if the Staff table exists
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'staff');")
            table_exists = cursor.fetchone()[0]
            
            # Close connections
            cursor.close()
            conn.close()
            
            if not table_exists:
                self.errorMsg.setText("Connected successfully, but this does not appear to be a hospital database.")
                return
                
        except Exception as e:
            self.errorMsg.setText(f"Connection failed: {str(e)}")
            return
            
        # Save the connection parameters
        if save_connection_params(connection_params):
            # Show success message
            QMessageBox.information(self, "Success", 
                "Connection parameters saved successfully.\n\n"
                "You can now log in to the hospital management system.")
            
            # Transition to login screen
            from GUI499 import MainScreen
            while self.widget.count() > 0:
                self.widget.removeWidget(self.widget.widget(0))
                
            mainScreen = MainScreen()
            self.widget.addWidget(mainScreen)
            self.widget.setCurrentIndex(0)
        else:
            self.errorMsg.setText("Failed to save connection parameters.")

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