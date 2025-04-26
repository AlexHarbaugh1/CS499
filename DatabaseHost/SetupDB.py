import sys
import traceback
import psycopg2
import hashlib
from contextlib import contextmanager
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread

import hospitalDB
import InsertData
import EncryptionKey

class DatabaseInitWorker(QThread):
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, first_name, last_name, username, password):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username 
        self.password = password
        
    def run(self):
        try:
            # Get encryption keys
            self.update_progress.emit(10, "Generating encryption keys...")
            keys = EncryptionKey.getKeys()
            encryption_key = keys[0]
            fixed_salt = keys[1]
            
            # Initialize the database
            self.update_progress.emit(30, "Creating database schema...")
            hospitalDB.run()
            
            # Generate hashed prefixes for first and last name
            self.update_progress.emit(60, "Creating administrator account...")
            
            # Insert the administrator
            InsertData.insertStaff(
                self.first_name, 
                self.last_name, 
                self.username, 
                self.password, 
                "Administrator", 
                fixed_salt
            )
            
            self.update_progress.emit(90, "Finishing setup...")
            
            # Signal that the work is complete
            self.update_progress.emit(100, "Database initialization complete!")
            self.finished.emit(True, "Database successfully initialized with administrator account.")
            
        except Exception as e:
            error_msg = f"Error initializing database: {str(e)}"
            self.finished.emit(False, error_msg)
            traceback.print_exc()

class InitializeDatabaseScreen(QDialog):
    def __init__(self, widget):
        super(InitializeDatabaseScreen, self).__init__()
        loadUi("setup.ui", self)
        
        # Store the widget reference
        self.widget = widget
        
        # Set up the screen
        self.setWindowTitle("Initialize Database - Hospital Management System")
        
        # Hide progress bar initially
        self.progressBar.setVisible(False)
        
        # Connect button
        self.initializeButton.clicked.connect(self.initialize_database)
        
        # Set tab order
        self.setTabOrder(self.firstNameField, self.lastNameField)
        self.setTabOrder(self.lastNameField, self.usernameField)
        self.setTabOrder(self.usernameField, self.passwordField)
        self.setTabOrder(self.passwordField, self.confirmPasswordField)
        self.setTabOrder(self.confirmPasswordField, self.initializeButton)
    
    def initialize_database(self):
        # Clear any previous error message
        self.errorMsg.setText("")
        
        # Get form data
        first_name = self.firstNameField.text().strip()
        last_name = self.lastNameField.text().strip()
        username = self.usernameField.text().strip()
        password = self.passwordField.text()
        confirm_password = self.confirmPasswordField.text()
        
        # Validate inputs
        if not first_name or not last_name or not username or not password:
            self.errorMsg.setText("All fields are required.")
            return
        
        if password != confirm_password:
            self.errorMsg.setText("Passwords do not match.")
            return
        
        if len(password) < 8:
            self.errorMsg.setText("Password must be at least 8 characters.")
            return
            
        # Disable form fields and show progress
        self.set_form_enabled(False)
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)
        
        # Create and start the worker thread
        self.worker = DatabaseInitWorker(first_name, last_name, username, password)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.finished.connect(self.initialization_finished)
        self.worker.start()
    
    def update_progress(self, value, message):
        self.progressBar.setValue(value)
        self.errorMsg.setStyleSheet("font: 12pt \"MS Shell Dlg 2\"; color: #003366;")
        self.errorMsg.setText(message)
    
    def initialization_finished(self, success, message):
        if success:
            # Display success message with green text
            self.errorMsg.setStyleSheet("font: 12pt \"MS Shell Dlg 2\"; color: green;")
            self.errorMsg.setText(message)
            
            # Show a dialog that database was initialized successfully
            QMessageBox.information(self, "Success", 
                "Database has been initialized successfully.\n\n"
                "You can now log in with the administrator account you created.")
            
            # Transition to login screen
            from GUI499 import MainScreen
            while self.widget.count() > 0:
                self.widget.removeWidget(self.widget.widget(0))
                
            mainScreen = MainScreen()
            self.widget.addWidget(mainScreen)
            self.widget.setCurrentIndex(0)
        else:
            # Display error message
            self.errorMsg.setStyleSheet("font: 12pt \"MS Shell Dlg 2\"; color: red;")
            self.errorMsg.setText(message)
            
            # Re-enable form
            self.set_form_enabled(True)
        
    def set_form_enabled(self, enabled):
        self.firstNameField.setEnabled(enabled)
        self.lastNameField.setEnabled(enabled)
        self.usernameField.setEnabled(enabled)
        self.passwordField.setEnabled(enabled)
        self.confirmPasswordField.setEnabled(enabled)
        self.initializeButton.setEnabled(enabled)

def check_database_exists():
    """Check if the hospital database exists already"""
    try:
        # Connect to postgres database
        conn = psycopg2.connect(
            database="postgres",
            user='postgres',
            password='49910',
            host='localhost',
            port='5432'
        )
        conn.autocommit = True
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if huntsvillehospital database exists
        cursor.execute("""SELECT EXISTS 
                      (SELECT datname FROM pg_catalog.pg_database
                      WHERE datname='huntsvillehospital')""")
        
        exists = cursor.fetchone()[0]
        
        # Close connections
        cursor.close()
        conn.close()
        
        return exists
    
    except Exception as e:
        # If there's an error connecting to postgres, return False
        # to trigger database creation
        print(f"Error checking if database exists: {e}")
        return False