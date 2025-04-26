# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 09:18:06 2025

@author: laure
"""
from SetupDB import check_database_exists, DatabaseInitWorker
import hospitalDB
import InsertData
import UpdateDB
import psycopg2
import sys
import traceback
import pandas as pd
from InactivityTimer import InactivityTimer
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QTableWidgetItem, QComboBox, QTextEdit, QLineEdit, QFileDialog, QTabBar, QTabWidget, QVBoxLayout, QPushButton, QLabel, QFormLayout, QSizePolicy, QFrame, QHBoxLayout, QGroupBox, QMessageBox, QListWidget, QTableWidget, QDialogButtonBox, QDateTimeEdit, QListWidgetItem
from PyQt5.QtCore import QTimer, QEvent, QObject, QRect, Qt, QDateTime
from PyQt5.QtGui import QBrush
import csv
import os
from decimal import Decimal
import json
import string
import EncryptionKey
import SearchDB
"""def locate_ui_file(ui_filename):

    Locate a UI file, works for both development and packaged environments

    # If running as frozen executable
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        
        # Try in the executable directory
        if os.path.exists(os.path.join(base_path, ui_filename)):
            return os.path.join(base_path, ui_filename)
            
        # Try in the _internal directory and its subdirectories
        internal_dir = os.path.join(base_path, '_internal')
        if os.path.exists(internal_dir):
            # Walk through all directories in _internal
            for root, dirs, files in os.walk(internal_dir):
                if ui_filename in files:
                    return os.path.join(root, ui_filename)
                    
        # Print debug info about the _internal directory structure
        if os.path.exists(internal_dir):
            print(f"Contents of _internal directory:")
            for root, dirs, files in os.walk(internal_dir):
                print(f"Directory: {root}")
                for file in files:
                    if file.endswith('.ui'):
                        print(f"  UI file: {file}")
    else:
        # If running as script, use the original path
        if os.path.exists(ui_filename):
            return ui_filename
    
    # If UI file still not found, print out available files for debugging
    print(f"UI file not found: {ui_filename}")
    print("Available files in current directory:", os.listdir('.'))
    
    # Return the original filename and let PyQt raise a proper error
    return ui_filename"""
keys = EncryptionKey.getKeys()
encryption_key = keys[0]
fixed_salt = keys[1]
class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        #loadUi(locate_ui_file("MainScreen.ui"), self)
        loadUi("MainScreen.ui", self)
         #self.enterApplication = QPushButton("Enter Application", self)
        
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Style the enter button
        self.styleElements()
        
        # Connect button
        self.enterApplication.clicked.connect(self.openLogin)

    
    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the welcome message
        label_width = 600
        self.label_3.setGeometry((screen_width - label_width) // 2, 
                                 screen_height // 3, 
                                 label_width, 100)
        
        # Center the enter button and make it appropriately sized
        button_width = 250
        button_height = 60
        self.enterApplication.setGeometry((screen_width - button_width) // 2, 
                                          (screen_height // 2) + 50, 
                                          button_width, button_height)
    
    def styleElements(self):
        """Apply consistent styling to elements"""
        # Style for the welcome message
        self.label_3.setStyleSheet("""
            font: bold 24pt "MS Shell Dlg 2";
            color: #333333;
        """)
        
        # Style for the enter button
        self.enterApplication.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 10px;
                font: bold 14pt "MS Shell Dlg 2";
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)

    def openLogin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

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
                
            mainScreen = MainScreen()
            self.widget.addWidget(mainScreen)
            self.widget.setCurrentIndex(widget.currentIndex() + 1)
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

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login1.ui", self)
        
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Style form fields and button
        self.styleElements()
        
        # Set password echo mode
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        
        # Connect button
        self.login.clicked.connect(self.loginfunction)

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Calculate a container area in the center of screen
        container_width = 400
        container_height = 350
        
        # Center position of the container
        container_x = (screen_width - container_width) // 2
        container_y = (screen_height - container_height) // 2
        
        # Calculate spacing and sizes
        field_height = 40
        label_width = 120
        field_width = 250
        spacing = 20
        
        # Position the PIMS title at the top of container
        self.label.setGeometry(container_x, container_y, container_width, 60)
        
        # Position username label and field
        self.labelUser.setGeometry(container_x, 
                                  container_y + 90, 
                                  label_width, field_height)
        
        self.userField.setGeometry(container_x + label_width + 10, 
                                  container_y + 90, 
                                  field_width, field_height)
        
        # Position password label and field
        self.labelPass.setGeometry(container_x, 
                                  container_y + 90 + field_height + spacing, 
                                  label_width, field_height)
        
        self.passwordField.setGeometry(container_x + label_width + 10, 
                                      container_y + 90 + field_height + spacing, 
                                      field_width, field_height)
        
        # Position login button
        button_width = 150
        button_height = 50
        self.login.setGeometry((screen_width - button_width) // 2, 
                              container_y + 90 + (field_height + spacing) * 2 + 20, 
                              button_width, button_height)
        
        # Position error message
        error_width = 400
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 
                                 container_y + 90 + (field_height + spacing) * 2 + 20 + button_height + 20, 
                                 error_width, 30)
    
    def styleElements(self):
        """Apply consistent styling to all elements"""
        # Style title
        self.label.setStyleSheet("""
            font: bold 36pt "MS Shell Dlg 2";
            color: #333333;
            padding-bottom: 20px;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        
        # Style for labels
        for label in [self.labelUser, self.labelPass]:
            label.setStyleSheet("""
                font: 14pt "MS Shell Dlg 2";
                padding-right: 10px;
            """)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Style for input fields
        for field in [self.userField, self.passwordField]:
            field.setStyleSheet("""
                font: 12pt "MS Shell Dlg 2";
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            """)
            field.setMinimumHeight(40)
        
        # Style for login button
        self.login.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 10px;
                font: bold 14pt "MS Shell Dlg 2";
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        
        # Style for error message
        self.errorMsg.setStyleSheet("""
            font: 12pt "MS Shell Dlg 2";
            color: rgb(255, 0, 0);
        """)
        self.errorMsg.setAlignment(Qt.AlignCenter)
        self.errorMsg.setWordWrap(True)

    def loginfunction(self):
        user = self.userField.text()
        password = self.passwordField.text()

        if len(user) == 0 or len(password) == 0:
            self.errorMsg.setText("Please enter both username and password.")
        else:
            result_pass = hospitalDB.userLogin(user, password, fixed_salt)
            if result_pass:
                self.errorMsg.setText("")
                userType = hospitalDB.getCurrentUserType()
                current_user_id = hospitalDB.getCurrentUserID()
                if userType == "Administrator":
                    self.gotoadmin()
                else:
                    self.gotoapplication()
            else:
                self.errorMsg.setText("Invalid username or password. Please try again.")

    def gotoapplication(self):
        eventFilter.enabled = True
        application = ApplicationScreen()
        widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def gotoadmin(self):
        eventFilter.enabled = True
        admin = AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class ApplicationScreen(QDialog):
    def __init__(self):
        super(ApplicationScreen, self).__init__()
         #loadUi(locate_ui_file("ApplicationScreen.ui"), self)
        loadUi("ApplicationScreen.ui", self)
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Get current user role to determine button visibility
        self.usertype = hospitalDB.getCurrentUserType()
        
        # Show/hide buttons based on user role
        self.configureButtonVisibility()
        
        # Connect button signals to slots
        self.connectButtons()
        
        # Apply button styling
        self.styleButtons()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title and subtitle
        title_width = 1700
        self.label.setGeometry((screen_width - title_width) // 2, 20, title_width, 250)
        self.label_2.setGeometry((screen_width - title_width) // 2, 150, title_width, 250)
        
        # Position logout button in top right
        self.logout.setGeometry(screen_width - 250, 70, 200, 100)
        
        # Center the gridLayoutWidget
        grid_width = 1000
        grid_height = 400
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 260, grid_width, grid_height)

    def configureButtonVisibility(self):
        """Show/hide buttons based on user role"""
        # Search Patient - Volunteer, Physician, Office Staff, Medical Personnel (all roles)
        self.PatientSearch.setVisible(True)
        
        # Register Patient - Medical Personnel, Physician, Office Staff
        if self.usertype in ["Medical Personnel", "Physician", "Office Staff"]:
            self.RegisterPatient.setVisible(True)
        else:
            self.RegisterPatient.setVisible(False)
        
        # Register Admission - Medical Personnel, Physician
        if self.usertype in ["Medical Personnel", "Physician"]:
            self.RegisterAdmission.setVisible(True)
        else:
            self.RegisterAdmission.setVisible(False)

    def connectButtons(self):
        """Connect button signals to slots"""
        self.PatientSearch.clicked.connect(self.goToPatientSearch)
        self.RegisterPatient.clicked.connect(self.goToRegisterPatient)
        self.RegisterAdmission.clicked.connect(self.goToRegisterAdmission)
        self.logout.clicked.connect(self.logoutFunction)

    def styleButtons(self):
        """Apply consistent styling to all buttons"""
        button_style = """
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 10px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """
        
        # Apply style to all operation buttons
        for button in [self.PatientSearch, self.RegisterPatient, self.RegisterAdmission]:
            button.setStyleSheet(button_style)
            button.setMinimumHeight(60)
            
        # Style for logout button
        self.logout.setStyleSheet(button_style)

    def goToPatientSearch(self):
        search = SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def goToRegisterPatient(self):
        insertPatient = InsertPatient()
        widget.addWidget(insertPatient)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def goToRegisterAdmission(self):
        registerAdmission = RegisterAdmission()
        widget.addWidget(registerAdmission)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        
        # Clear all widgets from the stack except the first one
        while widget.count() > 1:
            # Remove the last widget in the stack
            last_widget = widget.widget(widget.count() - 1)
            widget.removeWidget(last_widget)
            
            # Free up resources by scheduling widget for deletion
            last_widget.deleteLater()
        
        # Create a new login screen
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(1)
        
        # Remove the initial screen now that we have login in position 1
        first_widget = widget.widget(0)
        widget.removeWidget(first_widget)
        first_widget.deleteLater()

class AdminScreen(QDialog):
    def __init__(self):
        super(AdminScreen, self).__init__()
        #loadUi(locate_ui_file("admin.ui"), self)
        loadUi("admin.ui", self)

        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Connect buttons
        self.insStaff.clicked.connect(self.insertStaffFunction)
        self.insPat.clicked.connect(self.insertPatientFunction)
        self.searchStaff.clicked.connect(self.searchStaffFunction)
        self.searchPatient.clicked.connect(self.searchPatFunction)
        self.regLocation.clicked.connect(self.registerLocationFunction)
        self.regAdmission.clicked.connect(self.registerAdmissionFunction)
        self.auditLog.clicked.connect(self.viewAuditLog)
        self.logout.clicked.connect(self.logoutFunction)
        self.printAllAdmissions.clicked.connect(self.printAllAdmissionsSummary)
        # Apply button styling
        self.styleButtons()

    # Update the styleButtons method to include the new audit log button
    def styleButtons(self):
        """Apply consistent styling to all buttons"""
        button_style = """
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 10px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """
        
        # Apply style to all operation buttons
        for button in [self.insStaff, self.insPat, self.searchStaff, self.searchPatient, 
                      self.regLocation, self.regAdmission, self.auditLog]:
            button.setStyleSheet(button_style)
            button.setMinimumHeight(60)
            
        # Style for logout button
        self.logout.setStyleSheet(button_style)

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title and subtitle
        title_width = 600
        self.label.setGeometry((screen_width - title_width) // 2, 120, title_width, 61)
        self.label_2.setGeometry((screen_width - title_width) // 2, 200, title_width, 41)
        
        # Position logout button in top right
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        
        # Center the gridLayoutWidget
        grid_width = 700
        grid_height = 400
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 260, grid_width, grid_height)
    
    def styleButtons(self):
        """Apply consistent styling to all buttons"""
        button_style = """
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 10px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d6d6d6;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """
        
        # Apply style to all operation buttons
        for button in [self.insStaff, self.insPat, self.searchStaff, self.searchPatient, 
                      self.regLocation, self.regAdmission, self.auditLog]:
            button.setStyleSheet(button_style)
            button.setMinimumHeight(60)
            
        # Style for logout button - same as other buttons now
        self.logout.setStyleSheet(button_style)

    def insertStaffFunction(self):
        insertStaff = InsertStaff()
        widget.addWidget(insertStaff)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def insertPatientFunction(self):
        insertPatient = InsertPatient()
        widget.addWidget(insertPatient)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def searchStaffFunction(self):
        searchStaff = SearchStaff()
        widget.addWidget(searchStaff)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def searchPatFunction(self):
        search = SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def registerLocationFunction(self):
        registerLocation = RegisterLocation()
        widget.addWidget(registerLocation)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def registerAdmissionFunction(self):
        registerAdmission = RegisterAdmission()
        widget.addWidget(registerAdmission)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def viewAuditLog(self):
        auditLog = AuditLogScreen()
        widget = self.parent()
        widget.addWidget(auditLog)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        
        # Clear all widgets from the stack except the first one
        while widget.count() > 1:
            # Remove the last widget in the stack
            last_widget = widget.widget(widget.count() - 1)
            widget.removeWidget(last_widget)
            
            # Free up resources by scheduling widget for deletion
            last_widget.deleteLater()
        
        # Create a new login screen
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(1)
        
        # Remove the initial screen now that we have login in position 1
        first_widget = widget.widget(0)
        widget.removeWidget(first_widget)
        first_widget.deleteLater()

    def printAllAdmissionsSummary(self):
        try:
            from SearchDB import getAllPatientsWithAdmissions
            keys = EncryptionKey.getKeys()
            encryption_key = keys[0]

            patients = getAllPatientsWithAdmissions()
            if not patients:
                QMessageBox.information(self, "Info", "No active patients found.")
                return

            summaries = []
            for p in patients:
                admissions = p[-1]
                if not admissions:
                    continue

                first = p[1]
                middle = p[2]
                last = p[3]
                name = f"{first} {middle} {last}" if middle else f"{first} {last}"
                for admission in admissions:
                    if admission.get("admittance_discharge"):
                        continue

                    notes = admission.get("details", {}).get("notes", [])
                    meds = admission.get("details", {}).get("prescriptions", [])
                    procedures = admission.get("details", {}).get("procedures", [])

                    notes_text = "\n\n".join([
                        f"{n['datetime']} - {n['type']} by {n['author']}:\n{n['text']}"
                        for n in notes
                    ]) if notes else "No notes."

                    meds_text = "\n".join([
                        f"- {m['medication']} ({m['amount']}), schedule: {m['schedule']}"
                        for m in meds
                    ]) if meds else "No medications."

                    proc_text = "\n".join([
                        f"- {p['name']} scheduled for {p['scheduled']}"
                        for p in procedures
                    ]) if procedures else "No procedures."

                    summaries.append(f"""
                    Patient: {name}
                    Admission ID: {admission['admission_id']}
                    Admitted: {admission.get('admittance_date')}
                    Reason: {admission.get('admission_reason')}

                    Notes:
                    {notes_text}

                    Medications:
                    {meds_text}

                    Procedures:
                    {proc_text}
                    ---------------------------
                    """)
            final_output = "\n".join(summaries)
            self.showPrintDialog(final_output)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to print all summaries: {str(e)}")

    def showPrintDialog(self, text):
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument

        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setPlainText(text)
            doc.print_(printer)
            
class AuditLogScreen(QDialog):
    def __init__(self):
        super(AuditLogScreen, self).__init__()
        #loadUi(locate_ui_file("auditlog.ui"), self)
        loadUi("auditlog.ui", self)
        
        # Get screen dimensions
        screen_size = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Set up date filters with default values (last 7 days)
        current_datetime = QDateTime.currentDateTime()
        self.toDateFilter.setDateTime(current_datetime)
        self.fromDateFilter.setDateTime(current_datetime.addDays(-7))
        
        # Connect buttons
        self.backTo.clicked.connect(self.goBack)
        self.logout.clicked.connect(self.logoutFunction)
        self.filterButton.clicked.connect(self.applyFilters)
        self.clearButton.clicked.connect(self.clearFilters)
        self.exportButton.clicked.connect(self.exportToCSV)
        
        # Initialize the table
        self.initTable()
        
        # Load initial data
        self.loadAuditLogData()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 600
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        
        # Position back button in top left
        self.backTo.setGeometry(50, 70, 120, 40)
        
        # Position logout button in top right
        self.logout.setGeometry(screen_width - 170, 70, 120, 40)
        
        # Center and resize the filter section
        filter_width = min(1100, screen_width - 100)
        self.gridLayoutWidget.setGeometry((screen_width - filter_width) // 2, 150, filter_width, 80)
        
        # Center and resize the table
        table_width = min(1100, screen_width - 100)
        table_height = min(480, screen_height - 320)
        self.auditTable.setGeometry((screen_width - table_width) // 2, 250, table_width, table_height)
        
        # Position export button at bottom right
        self.exportButton.setGeometry(screen_width - 230, screen_height - 60, 180, 40)
        
        # Position status label at bottom left
        self.statusLabel.setGeometry(50, screen_height - 60, screen_width - 330, 40)

    def initTable(self):
        """Initialize the table with appropriate column widths"""
        # Set column widths
        self.auditTable.setColumnWidth(0, 80)    # ID
        self.auditTable.setColumnWidth(1, 200)   # Username
        self.auditTable.setColumnWidth(2, 600)   # Action
        self.auditTable.setColumnWidth(3, 200)   # Timestamp
        
        # Ensure the table headers are visible
        self.auditTable.horizontalHeader().setVisible(True)
        
        # Set the text alignment for columns
        for i in range(4):
            self.auditTable.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
    
    def loadAuditLogData(self, username=None, action=None, from_date=None, to_date=None):
        """Load audit log data with optional filters"""
        try:
            # Build the SQL query with parameters
            params = []
            conditions = []
            
            # Start with a base query
            sql = "SELECT log_id, username, action_text, timestamp FROM auditlog"
            
            # Add filters if provided
            if username:
                conditions.append("username LIKE %s")
                params.append(f"%{username}%")
            
            if action:
                conditions.append("action_text LIKE %s")
                params.append(f"%{action}%")
            
            if from_date:
                conditions.append("timestamp >= %s")
                params.append(from_date)
            
            if to_date:
                conditions.append("timestamp <= %s")
                params.append(to_date)
            
            # Add WHERE clause if needed
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            # Order by timestamp (most recent first)
            sql += " ORDER BY timestamp DESC"
            
            # Execute the query
            with hospitalDB.get_cursor() as cursor:
                cursor.execute(sql, params)
                audit_logs = cursor.fetchall()
            
            # Clear the table
            self.auditTable.setRowCount(0)
            
            # Populate the table with data
            for row_num, row_data in enumerate(audit_logs):
                self.auditTable.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.auditTable.setItem(row_num, col_num, item)
            
            # Update status message
            self.statusLabel.setText(f"Displaying {len(audit_logs)} audit log entries")
            
        except Exception as e:
            self.statusLabel.setText(f"Error loading audit log data: {str(e)}")
            print(f"Error loading audit log: {e}")
    
    def applyFilters(self):
        """Apply filters to the audit log data"""
        username = self.usernameFilter.text().strip() if self.usernameFilter.text().strip() else None
        action = self.actionFilter.text().strip() if self.actionFilter.text().strip() else None
        from_date = self.fromDateFilter.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.fromDateFilter.dateTime().isValid() else None
        to_date = self.toDateFilter.dateTime().toString("yyyy-MM-dd HH:mm:ss") if self.toDateFilter.dateTime().isValid() else None
        
        self.loadAuditLogData(username, action, from_date, to_date)
    
    def clearFilters(self):
        """Clear all filters and reload the data"""
        self.usernameFilter.clear()
        self.actionFilter.clear()
        
        # Reset date filters to default (last 7 days)
        current_datetime = QDateTime.currentDateTime()
        self.toDateFilter.setDateTime(current_datetime)
        self.fromDateFilter.setDateTime(current_datetime.addDays(-7))
        
        # Reload data without filters
        self.loadAuditLogData()
    
    def exportToCSV(self):
        """Export the current table contents to a CSV file"""
        try:
            # Get the file path from a save dialog
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, 
                                                       "Save Audit Log", 
                                                       "audit_log_export.csv", 
                                                       "CSV Files (*.csv);;All Files (*)", 
                                                       options=options)
            
            if not file_name:  # User canceled
                return
            
            # Ensure the file has .csv extension
            if not file_name.endswith('.csv'):
                file_name += '.csv'
            
            # Open the file for writing
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write the header row
                headers = []
                for i in range(self.auditTable.columnCount()):
                    headers.append(self.auditTable.horizontalHeaderItem(i).text())
                writer.writerow(headers)
                
                # Write the data rows
                for row in range(self.auditTable.rowCount()):
                    row_data = []
                    for col in range(self.auditTable.columnCount()):
                        item = self.auditTable.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            self.statusLabel.setText(f"Audit log exported successfully to {file_name}")
            
        except Exception as e:
            self.statusLabel.setText(f"Error exporting data: {str(e)}")
            QMessageBox.warning(self, "Export Error", f"An error occurred while exporting the data: {str(e)}")
    
    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")
    
    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        
        # Clear all widgets from the stack except the first one
        while widget.count() > 1:
            # Remove the last widget in the stack
            last_widget = widget.widget(widget.count() - 1)
            widget.removeWidget(last_widget)
            
            # Free up resources by scheduling widget for deletion
            last_widget.deleteLater()
        
        # Create a new login screen
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(1)
        
        # Remove the initial screen now that we have login in position 1
        first_widget = widget.widget(0)
        widget.removeWidget(first_widget)
        first_widget.deleteLater()

class InsertStaff(QDialog):
    def __init__(self):
        super(InsertStaff, self).__init__()
        loadUi("insertstaff.ui", self)

        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Set up the combo box for staff type
        self.staffTypeCombo.addItems(["", "Administrator", "Medical Personnel", "Physician", "Volunteer", "Office Staff"])
        
        # Connect buttons
        self.backTo.clicked.connect(self.goBack)
        self.addStaff.clicked.connect(self.addStaffMember)
        
        # Style form fields
        for field in [self.firstNameField, self.lastNameField, self.usernameField, self.passwordField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        
        # Style combo box
        self.staffTypeCombo.setMinimumHeight(35)
        self.staffTypeCombo.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401  # From original UI
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        
        # Position back button in top left
        self.backTo.setGeometry(50, 70, 120, 40)
        
        # Center the form layout
        form_width = 600  # Increased width for better alignment
        form_height = 350  # Increased height for the form
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)
        
        # Center the add staff button
        button_width = 200
        button_height = 50
        self.addStaff.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)
        
        # Center and resize the error message to be wider
        error_width = 600  # Increased from 400
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)  # Increased height from 31 to 40
        
        # Configure the error message to wrap text
        self.errorMsg.setWordWrap(True)
    
    def addStaffMember(self):
        firstName = self.firstNameField.text()
        lastName = self.lastNameField.text()
        username = self.usernameField.text()
        password = self.passwordField.text()
        staffType = self.staffTypeCombo.currentText()
        
        # Check if all fields are filled
        if not firstName or not lastName or not username or not password or not staffType:
            self.errorMsg.setText("All fields are required.")
            return
        else:
            try:
                InsertData.insertStaff(firstName, lastName, username, password, staffType, fixed_salt)

                self.errorMsg.setStyleSheet("color: green;")
                self.errorMsg.setText(f"Staff member {firstName} {lastName} added successfully!")
                # Clear the form fields
                self.firstNameField.clear()
                self.lastNameField.clear()
                self.usernameField.clear()
                self.passwordField.clear()
                self.staffTypeCombo.setCurrentIndex(0)
            except Exception as e:
                self.errorMsg.setStyleSheet("color: red;")
                # Check for specific error types
                error_message = str(e)
                if "duplicate key value violates unique constraint" in error_message:
                    self.errorMsg.setText("Username already exists. Please choose a different username.")
                elif "not-null constraint" in error_message:
                    self.errorMsg.setText("Missing required information. Please fill all fields.")
                elif "foreign key constraint" in error_message:
                    self.errorMsg.setText("Invalid staff type selected.")
                else:
                    self.errorMsg.setText(f"Error: {error_message}")

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")
    

    def showPrintDialog(self, text):
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument

        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setPlainText(text)
            doc.print_(printer)


class InsertPatient(QDialog):
    def __init__(self):
        super(InsertPatient, self).__init__()
        loadUi("insertpat.ui", self)  # Load the new UI file
        
        
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Populate the doctor dropdown
        self.populateDoctors()
        
        # Connect buttons
        self.back.clicked.connect(self.goBack)
        self.addPatient.clicked.connect(self.addPatientData)
        
        # Highlight required fields
        self.firstNameField.setStyleSheet("border: 1px solid red;")
        self.lastNameField.setStyleSheet("border: 1px solid red;")

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        
        # Position back button in top left
        self.back.setGeometry(50, 70, 120, 40)
        
        # Center the required fields note
        note_width = 400
        self.requiredNote.setGeometry((screen_width - note_width) // 2, 140, note_width, 20)
        
        # Center the grid layout with adequate size
        grid_width = min(900, screen_width - 100)  # Allow for margins
        grid_height = min(550, screen_height - 250)  # Allow for header and footer
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 170, grid_width, grid_height)
        
        # Center the add patient button
        button_width = 200
        button_height = 50
        button_y = 170 + grid_height + 10  # Position below the grid
        self.addPatient.setGeometry((screen_width - button_width) // 2, button_y, button_width, button_height)
        
        # Center the error message label
        error_width = 600
        error_y = button_y + button_height + 10
        self.errorMsg.setGeometry((screen_width - error_width) // 2, error_y, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def populateDoctors(self):
        """Populate the doctor dropdown with physicians from the database"""
        try:
            keys = EncryptionKey.getKeys()
            doctors = SearchDB.getDoctors(keys[0])
            
            # Add empty first item
            self.doctorCombo.addItem("", "")
            
            # Add doctors to combo box
            if doctors and doctors != "Error":
                for doctor in doctors:
                    # Format: ID - Last Name, First Name
                    display_text = f"{doctor[0]} - {doctor[3]}, {doctor[2]}"
                    self.doctorCombo.addItem(display_text, doctor[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")
    
    def validateRequiredFields(self):
        """Validate that all required fields are filled"""
        firstName = self.firstNameField.text().strip()
        lastName = self.lastNameField.text().strip()
        
        if not firstName:
            self.errorMsg.setText("First name is required.")
            self.firstNameField.setFocus()
            return False
        
        if not lastName:
            self.errorMsg.setText("Last name is required.")
            self.lastNameField.setFocus()
            return False
        
        return True
    
    def addPatientData(self):
        """Add a new patient to the database"""
        # Validate required fields first
        if not self.validateRequiredFields():
            return
            
        keys = EncryptionKey.getKeys()
        fixed_salt = keys[1]
        
        # Get values from form fields
        firstName = self.firstNameField.text()
        middleInit = self.middleInitField.text()
        lastName = self.lastNameField.text()
        address = self.addressField.text()
        
        # Get doctor ID from combo box
        doctorIndex = self.doctorCombo.currentIndex()
        doctorID = self.doctorCombo.itemData(doctorIndex) if doctorIndex > 0 else None
        
        try:
            # Insert the patient
            InsertData.insertPatient(firstName, middleInit, lastName, address, doctorID, fixed_salt)
            
            # Get the newly inserted patient ID (most recent patient)
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT MAX(patient_id) FROM patient;")
                patientID = cursor.fetchone()[0]
            
            # Insert phone numbers if provided
            homePhone = self.homePhoneField.text()
            cellPhone = self.cellPhoneField.text()
            workPhone = self.workPhoneField.text()
            
            if homePhone:
                UpdateDB.patientUpdatePhone(patientID, "Home", homePhone)
            
            if cellPhone:
                UpdateDB.patientUpdatePhone(patientID, "Mobile", cellPhone)
            
            if workPhone:
                UpdateDB.patientUpdatePhone(patientID, "Work", workPhone)
            
            # Insert emergency contacts if provided
            contact1Name = self.contact1NameField.text()
            contact1Phone = self.contact1PhoneField.text()
            contact2Name = self.contact2NameField.text()
            contact2Phone = self.contact2PhoneField.text()
            
            if contact1Name and contact1Phone:
                UpdateDB.patientUpdateContact(patientID, contact1Name, contact1Phone, "1")
            
            if contact2Name and contact2Phone:
                UpdateDB.patientUpdateContact(patientID, contact2Name, contact2Phone, "2")
            
            # Insert insurance information if provided
            insurance = self.insuranceField.text()
            accountNumber = self.accountNumberField.text()
            groupNumber = self.groupNumberField.text()
            
            if insurance or accountNumber or groupNumber:
                UpdateDB.patientUpdateInsurance(patientID, insurance, accountNumber, groupNumber)
            
            # Display success message
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText(f"Patient {firstName} {lastName} added successfully!")
            
            # Clear the form fields
            self.clearFields()
            
        except psycopg2.errors.UniqueViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("A database constraint was violated. Please check your data.")
        except psycopg2.errors.NotNullViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Missing required information. Please check all required fields.")
        except psycopg2.errors.ForeignKeyViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Invalid doctor selection.")
        except psycopg2.OperationalError:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Connection to database failed. Please try again later.")
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")
    
    def clearFields(self):
        """Clear all form fields"""
        self.firstNameField.clear()
        self.middleInitField.clear()
        self.lastNameField.clear()
        self.addressField.clear()
        self.homePhoneField.clear()
        self.cellPhoneField.clear()
        self.workPhoneField.clear()
        self.contact1NameField.clear()
        self.contact1PhoneField.clear()
        self.contact2NameField.clear()
        self.contact2PhoneField.clear()
        self.insuranceField.clear()
        self.accountNumberField.clear()
        self.groupNumberField.clear()
        self.doctorCombo.setCurrentIndex(0)
    
    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class RegisterLocation(QDialog):
    def __init__(self):
        super(RegisterLocation, self).__init__()
        loadUi("registerlocation.ui", self)

        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Connect buttons
        self.backTo.clicked.connect(self.goBack)
        self.addLocation.clicked.connect(self.addLocationFunction)
        
        # Style form fields
        self.styleFormFields()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401  # From original UI
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        
        # Position back button in top left
        self.backTo.setGeometry(50, 70, 120, 40)
        
        # Center the form layout
        form_width = 600  # Increased width for better alignment
        form_height = 350  # Increased height for the form
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)
        
        # Center the add location button
        button_width = 200
        button_height = 50
        self.addLocation.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)
        
        # Center and resize the error message to be wider
        error_width = 600  # Increased from 400
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        
        # Configure the error message to wrap text
        self.errorMsg.setWordWrap(True)
    
    def styleFormFields(self):
        """Style all form fields for better UI"""
        # Set form layout properties
        self.formLayout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.formLayout.setHorizontalSpacing(20)
        self.formLayout.setVerticalSpacing(20)
        
        # Style text fields
        self.facilityField.setMinimumHeight(35)
        self.facilityField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.roomField.setMinimumHeight(35)
        self.roomField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.bedField.setMinimumHeight(35)
        self.bedField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        
        # Style the spin box
        self.floorField.setMinimumHeight(35)
        self.floorField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
    
    def addLocationFunction(self):
        """Add a new location to the database"""
        # Get values from form fields
        facility = self.facilityField.text()
        floor = self.floorField.value()
        room = self.roomField.text()
        bed = self.bedField.text()
        
        # Validate required fields
        if not facility or not room or not bed:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return
        
        try:
            # Insert the location
            InsertData.insertLocation(facility, floor, room, bed)
            
            # Display success message
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText(f"Location added successfully!")
            
            # Clear the form fields
            self.facilityField.clear()
            self.floorField.setValue(1)
            self.roomField.clear()
            self.bedField.clear()
            
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            error_message = str(e)
            # Check for specific error patterns in the exception message
            if "duplicate key value violates unique constraint" in error_message or "unique_location" in error_message:
                self.errorMsg.setText("This location already exists. Please try a different combination.")
            elif "not-null constraint" in error_message:
                self.errorMsg.setText("Missing required information. Please fill all fields.")
            else:
                self.errorMsg.setText(f"Error: {error_message}")

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class RegisterAdmission(QDialog):
    def __init__(self):
        super(RegisterAdmission, self).__init__()
        loadUi("registeradmission.ui", self)

        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        
        # Center the UI elements
        self.centerUI(screen_width, screen_height)
        
        # Set current date time for admission
        self.admissionDateTime.setDateTime(QDateTime.currentDateTime())
        
        # Populate the dropdowns
        self.populatePatients()
        self.populateLocations()
        self.populateDoctors()
        
        # Connect buttons
        self.backTo.clicked.connect(self.goBack)
        self.addAdmission.clicked.connect(self.addAdmissionFunction)
        
        # Style form fields
        self.styleFormFields()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401  # From original UI
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        
        # Position back button in top left
        self.backTo.setGeometry(50, 70, 120, 40)
        
        # Center the form layout
        form_width = 600  # Increased for better alignment
        form_height = 350  # Increased height for the form
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)
        
        # Center the add admission button
        button_width = 200
        button_height = 50
        self.addAdmission.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)
        
        # Center and resize the error message
        error_width = 600
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        
        # Configure the error message to wrap text
        self.errorMsg.setWordWrap(True)
    
    def styleFormFields(self):
        """Style all form fields for better UI"""
        # Style combo boxes
        for combo in [self.patientCombo, self.locationCombo, self.doctorCombo]:
            combo.setMinimumHeight(35)
            combo.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        
        # Style date time edit
        self.admissionDateTime.setMinimumHeight(35)
        self.admissionDateTime.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        
        # Style text edit
        self.reasonField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
    
    def populatePatients(self):
        """Populate the patient dropdown with all patients from the database"""
        try:
            # Get all patients
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT patient_id, first_name, middle_name, last_name FROM patientsearchview ORDER BY last_name;")
                patients = cursor.fetchall()
            
            # Add empty first item
            self.patientCombo.addItem("", "")
            
            # Add patients to combo box
            for patient in patients:
                patient_id = patient[0]
                first_name = patient[1]
                middle_name = patient[2] or ""
                last_name = patient[3]
                
                # Format: ID - Last Name, First Name Middle Name
                display_text = f"{patient_id} - {last_name}, {first_name} {middle_name}"
                self.patientCombo.addItem(display_text, patient_id)
                
        except Exception as e:
            self.errorMsg.setText(f"Error loading patients: {str(e)}")
    
    def populateLocations(self):
        """Populate the location dropdown with available locations"""
        try:
            # Get available locations (not currently assigned to an admission)
            locations = SearchDB.getAvailableLocations()
            
            # Add empty first item
            self.locationCombo.addItem("", "")
            
            # Add locations to combo box
            for location in locations:
                location_id = location[0]
                facility = location[1]
                floor = location[2]
                room = location[3]
                bed = location[4]
                
                # Format: ID - Facility, Floor, Room, Bed
                display_text = f"{location_id} - {facility}, Floor {floor}, Room {room}, Bed {bed}"
                self.locationCombo.addItem(display_text, location_id)
                
        except Exception as e:
            self.errorMsg.setText(f"Error loading locations: {str(e)}")
    
    def populateDoctors(self):
        """Populate the doctor dropdown with physicians from the database"""
        try:
            keys = EncryptionKey.getKeys()
            doctors = SearchDB.getDoctors(keys[0])
            
            # Add empty first item
            self.doctorCombo.addItem("", "")
            
            # Add doctors to combo box
            if doctors and doctors != "Error":
                for doctor in doctors:
                    # Format: ID - Last Name, First Name
                    display_text = f"{doctor[0]} - {doctor[3]}, {doctor[2]}"
                    self.doctorCombo.addItem(display_text, doctor[0])
                    
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")
    
    def addAdmissionFunction(self):
        """Add a new admission to the database"""
        # Get values from form fields
        patient_index = self.patientCombo.currentIndex()
        patient_id = self.patientCombo.itemData(patient_index) if patient_index > 0 else None
        
        location_index = self.locationCombo.currentIndex()
        location_id = self.locationCombo.itemData(location_index) if location_index > 0 else None
        
        doctor_index = self.doctorCombo.currentIndex()
        doctor_id = self.doctorCombo.itemData(doctor_index) if doctor_index > 0 else None
        
        admission_date = self.admissionDateTime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        reason = self.reasonField.toPlainText()
        
        # Validate required fields
        if not patient_id or not location_id or not doctor_id or not reason:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return
        
        try:
            # Insert the admission
            InsertData.insertAdmission(patient_id, location_id, doctor_id, admission_date, reason)
            
            # Display success message
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText("Admission registered successfully!")
            
            # Clear form (except date) and refresh locations (since one is now taken)
            self.patientCombo.setCurrentIndex(0)
            self.doctorCombo.setCurrentIndex(0)
            self.reasonField.clear()
            
            # Refresh the locations dropdown as the selected location is now occupied
            self.locationCombo.clear()
            self.populateLocations()
            
        except psycopg2.errors.UniqueViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("A constraint was violated. Please check your data.")
        except psycopg2.errors.NotNullViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Missing required information. Please fill all fields.")
        except psycopg2.errors.ForeignKeyViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Invalid selection. Please check patient, location, and doctor choices.")
        except psycopg2.OperationalError:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Connection to database failed. Please try again later.")
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class SearchStaff(QDialog):
    def __init__(self):
        super(SearchStaff, self).__init__()
        loadUi("stafflookup.ui", self)
        
        
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        # Center the form elements
        self.centerUI(screen_width, screen_height)
        
        # Style form fields
        for field in [self.lastField, self.firstField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
            
        # Style checkboxes
        for checkbox in [self.lastBox, self.firstBox]:
            checkbox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
    
        # Connect event handlers
        self.search.clicked.connect(self.searchFunction)
        self.logout.clicked.connect(self.logoutFunction)
        self.backButton.clicked.connect(self.goBack)  # Add back button functionality
        self.resultsTable.hide()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401  # From original UI
        self.label.setGeometry((screen_width - title_width) // 2, 200, title_width, 71)
        
        # Position logout button in top right
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        
        # Position back button in top left
        self.backButton.setGeometry(50, 70, 120, 50)
        
        # Center the form grid
        form_width = 600  # Increased width for better alignment
        form_height = 151
        self.gridLayoutWidget.setGeometry((screen_width - form_width) // 2, 290, form_width, form_height)
        
        # Center the error message
        error_width = 300
        self.error.setGeometry((screen_width - error_width) // 2, 450, error_width, 31)
        
        # Center search button
        search_width = 151
        search_height = 40
        self.search.setGeometry((screen_width - search_width) // 2, 490, search_width, search_height)
        
        table_width = min(screen_width - 100, 700)  # Limit width with padding
        table_height = min(screen_height - 600, 500)  # Limit height with padding
        
        # Center the table horizontally
        table_x = (screen_width - table_width) // 2
        self.resultsTable.setGeometry(table_x, 550, table_width, table_height)
        
        # Make columns resize to content
        self.resultsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # Hide the table initially - will be shown after search
        self.resultsTable.hide()

    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        
        # Clear all widgets from the stack except the first one
        while widget.count() > 1:
            # Remove the last widget in the stack
            last_widget = widget.widget(widget.count() - 1)
            widget.removeWidget(last_widget)
            
            # Free up resources by scheduling widget for deletion
            last_widget.deleteLater()
        
        # Create a new login screen
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(1)
        
        # Remove the initial screen now that we have login in position 1
        first_widget = widget.widget(0)
        widget.removeWidget(first_widget)
        first_widget.deleteLater()

    def searchFunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        firstBox = self.firstBox.isChecked()
        lastBox = self.lastBox.isChecked()
        partials = set()
        
        if len(lastName) == 0 and len(firstName) == 0:
            self.error.setText("Input at least one field.")
        else:
            df = None

            # Check whether checkbox for last name or first name is checked
            if lastBox:
                partials.add('lname')
            if firstBox:
                partials.add('fname')

            df = pd.DataFrame(SearchDB.searchStaffWithName(fixed_salt,
                                                          firstName if firstName else None,
                                                          lastName if lastName else None,
                                                          partials))

            if df.empty:
                self.error.setText("No results found.")
            else:
                self.error.setText("")
                self.resultsTable.show()
                self.resultsTable.setRowCount(len(df))
                self.resultsTable.setColumnCount(len(df.columns))
                self.resultsTable.setHorizontalHeaderLabels(["ID", "Username", "First Name", "Last Name", "Role"])
                for i in range(len(df)):
                    for j in range(len(df.columns)):
                        item = QTableWidgetItem(str(df.iat[i, j]))
                        self.resultsTable.setItem(i, j, item)
                self.resultsTable.cellDoubleClicked.connect(self.openStaffDetails)
                self.df = df

    def openStaffDetails(self, row, column):
        staff_id = str(self.df.iat[row, 0])
        details = StaffDetailsScreen(staff_id)
        widget.addWidget(details)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class StaffDetailsScreen(QDialog):
    def __init__(self, staff_id):
        super(StaffDetailsScreen, self).__init__()
        self.setWindowTitle("Staff Details")
        self.setGeometry(100, 100, 900, 700)
        self.staff_id = staff_id
        self.usertype = hospitalDB.getCurrentUserType()
        
        layout = QVBoxLayout()
        
        # Create a header with patient info
        self.header_frame = QWidget()
        self.header_layout = QHBoxLayout()
        self.staff_info_label = QLabel()
        self.staff_info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.header_layout.addWidget(self.staff_info_label)
        self.header_frame.setLayout(self.header_layout)
        layout.addWidget(self.header_frame)
        
        # Create tabs - different tabs will be shown based on user type
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        # Create tabs for different user types
        self.basic_info_tab = QWidget()
        
        # Only add the relevant tabs based on user type
        self.setupTabs()
        
        layout.addWidget(self.tabs)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.goBack)
        button_layout.addWidget(self.back_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load the patient data
        self.loadStaffData()
    
    def setupTabs(self):
        self.num_static_tabs = 0  # Initialize
        self.tabs.addTab(self.basic_info_tab, "Basic Info")
        self.num_static_tabs = self.tabs.count()  # Store default tab count
    def closeTab(self, index):
        # Prevent closing the default tabs (index < num_static_tabs)
        if index < self.num_static_tabs:
            QMessageBox.information(self, "Protected Tab", "You cannot close the default staff tabs.")
            return
        self.tabs.removeTab(index)
    def loadStaffData(self):
        try:
            # Get data using the search function
            data = SearchDB.searchStaffWithID(self.staff_id, encryption_key)
            print("DEBUG - Staff data:", data)

            name = f"{data[1]} {data[2]}"
            self.staff_info_label.setText(f"Staff Member: {name}")
            
            # Basic Info Tab
            basic_layout = QFormLayout()
            basic_layout.addRow("Username:", QLabel(data[0]))
            basic_layout.addRow("First Name:", QLabel(data[1]))
            basic_layout.addRow("Last Name:", QLabel(data[2]))
            basic_layout.addRow("Type:", QLabel(data[3]))
            self.basic_info_tab.setLayout(basic_layout)

            if not data:
                QMessageBox.warning(self, "No Data", "No staff data found.")
                return

        except Exception as e:
            traceback.print_exc()  # Add this line for full stack trace in terminal
            QMessageBox.critical(self, "Error", f"Error loading staff data: {str(e)}")
            print(f"Error: {e}")

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class SearchScreen(QDialog):
    def __init__(self):
        super(SearchScreen, self).__init__()
        loadUi("patientsearch.ui", self)
        
        
        # Get screen dimensions
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()  
        screen_height = screen_size.height()
        
        # Set main widget to fill the entire screen
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        # Center the form elements
        self.centerUI(screen_width, screen_height)
        
        # Style form fields
        for field in [self.lastField, self.firstField, self.midField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
            
        # Style checkboxes
        for checkbox in [self.lastBox, self.firstBox]:
            checkbox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
    
        # Connect event handlers
        self.search.clicked.connect(self.searchFunction)
        self.logout.clicked.connect(self.logoutFunction)
        self.backButton.clicked.connect(self.goBack)  # Add back button functionality
        self.resultsTable.hide()
        self.activeAdmissionsBox = QtWidgets.QCheckBox("Only Active Admissions")
        self.activeAdmissionsBox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
        self.gridLayoutWidget.layout().addWidget(self.activeAdmissionsBox, 3, 2)
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Volunteer":
            self.activeAdmissionsBox.hide()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 170, title_width, 61)
        
        # Position logout button in top right
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        
        # Position back button in top left
        self.backButton.setGeometry(50, 70, 120, 50)
        
        # Center the form grid
        form_width = 600
        form_height = 200
        self.gridLayoutWidget.setGeometry((screen_width - form_width) // 2, 270, form_width, form_height)
        
        # Center the error message
        error_width = 300
        self.error.setGeometry((screen_width - error_width) // 2, 470, error_width, 31)
        
        # Center search button
        search_width = 116
        search_height = 40
        self.search.setGeometry((screen_width - search_width) // 2, 510, search_width, search_height)
        
        # Center the results table
        table_width = min(screen_width - 100, 700)  # Limit width with padding
        table_height = min(screen_height - 600, 500)  # Limit height with padding
        
        # Center the table horizontally
        table_x = (screen_width - table_width) // 2
        self.resultsTable.setGeometry(table_x, 550, table_width, table_height)
        
        # Make columns resize to content
        self.resultsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # Hide the table initially - will be shown after search
        self.resultsTable.hide()

    def searchFunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        middleName = self.midField.text()
        lastBox = self.lastBox.isChecked()
        firstBox = self.firstBox.isChecked()
        activeAdmissionsOnly = False
        
        # Check if the activeAdmissionsBox exists and is visible
        if hasattr(self, 'activeAdmissionsBox') and self.activeAdmissionsBox.isVisible():
            activeAdmissionsOnly = self.activeAdmissionsBox.isChecked()
        
        partials = set()
        
        if len(lastName) == 0 and len(firstName) == 0 and len(middleName) == 0:
            self.error.setText("Input at least one field.")
        else:
            df = None

            # Check whether checkbox for last name or first name is checked
            if firstBox:
                partials.add('fname')
            if lastBox:
                partials.add('lname')

            df = pd.DataFrame(SearchDB.searchPatientWithName(fixed_salt, 
                                                        fname=firstName.title() if firstName else None,
                                                        mname=middleName.title() if middleName else None,
                                                        lname=lastName.title() if lastName else None,
                                                        partial_fields=partials,
                                                        active_admissions_only=activeAdmissionsOnly))

            if df.empty:
                self.error.setText("No results found.")
            else:
                self.error.setText("")
                self.resultsTable.show()
                self.resultsTable.setRowCount(len(df))
                self.resultsTable.setColumnCount(len(df.columns))
                self.resultsTable.setHorizontalHeaderLabels(["ID", "First Name", "Middle Name", "Last Name"])
                for i in range(len(df)):
                    for j in range(len(df.columns)):
                        item = QTableWidgetItem(str(df.iat[i, j]))
                        self.resultsTable.setItem(i, j, item)
                self.resultsTable.cellDoubleClicked.connect(self.openPatientDetails)
                self.df = df

    def openPatientDetails(self, row, column):
        patient_id = str(self.df.iat[row, 0])
        details = PatientDetailsScreen(patient_id)
        widget.addWidget(details)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        
        # Clear all widgets from the stack except the first one
        while widget.count() > 1:
            # Remove the last widget in the stack
            last_widget = widget.widget(widget.count() - 1)
            widget.removeWidget(last_widget)
            
            # Free up resources by scheduling widget for deletion
            last_widget.deleteLater()
        
        # Create a new login screen
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(1)
        
        # Remove the initial screen now that we have login in position 1
        first_widget = widget.widget(0)
        widget.removeWidget(first_widget)
        first_widget.deleteLater()

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class PatientDetailsScreen(QDialog):
    def __init__(self, patient_id):
        super(PatientDetailsScreen, self).__init__()
        self.setWindowTitle("Patient Details")
        self.setGeometry(100, 100, 900, 700)
        self.patient_id = patient_id
        self.usertype = hospitalDB.getCurrentUserType()
        
        layout = QVBoxLayout()
        
        # Create a header with patient info
        self.header_frame = QWidget()
        self.header_layout = QHBoxLayout()
        self.patient_info_label = QLabel()
        self.patient_info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.header_layout.addWidget(self.patient_info_label)
        self.header_frame.setLayout(self.header_layout)
        layout.addWidget(self.header_frame)
        
        # Create tabs - different tabs will be shown based on user type
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        # Create tabs for different user types
        self.basic_info_tab = QWidget()
        self.insurance_tab = QWidget()
        self.contacts_tab = QWidget()
        self.notes_tab = QWidget()
        self.medications_tab = QWidget()
        self.procedures_tab = QWidget()
        self.location_tab = QWidget()
        self.admissions_tab = QWidget()
        self.visitors_tab = QWidget()
        self.billing_tab = QWidget()  # Add billing tab
        
        # Only add the relevant tabs based on user type
        self.setupTabs()
        
        layout.addWidget(self.tabs)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.goBack)
        button_layout.addWidget(self.back_button)
        
        self.print_button = QPushButton("Print to File")
        self.print_button.clicked.connect(self.printPatientDetails)
        button_layout.addWidget(self.print_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load the patient data
        self.loadPatientData()
    
    def setupTabs(self):
        self.num_static_tabs = 0  # Initialize count
    
        if self.usertype == "Volunteer":
            self.tabs.addTab(self.basic_info_tab, "Patient Info")
            self.tabs.addTab(self.location_tab, "Location")
            self.tabs.addTab(self.visitors_tab, "Approved Visitors")
            
        elif self.usertype == "Office Staff":
            self.basic_info_tab = QWidget()
            layout = QFormLayout()
            self.firstNameEdit = QLineEdit()
            self.middleNameEdit = QLineEdit()
            self.lastNameEdit = QLineEdit()
            self.addressEdit = QTextEdit()
            # Insurance tab inputs
            self.insurance_provider_input = QLineEdit()
            self.policy_number_input = QLineEdit()
            self.group_number_input = QLineEdit()


            # Contacts tab inputs
            self.emergency_contact_name_input = QLineEdit()
            self.emergency_contact_phone_input = QLineEdit()
            for widget in [self.insurance_provider_input, self.policy_number_input,
               self.emergency_contact_name_input, self.emergency_contact_phone_input, self.group_number_input]:
                widget.setDisabled(True)


            self.firstNameEdit.setReadOnly(True)
            self.middleNameEdit.setReadOnly(True)
            self.lastNameEdit.setReadOnly(True)
            self.addressEdit.setReadOnly(True)

            layout.addRow("First Name:", self.firstNameEdit)
            layout.addRow("Middle Name:", self.middleNameEdit)
            layout.addRow("Last Name:", self.lastNameEdit)
            layout.addRow("Mailing Address:", self.addressEdit)

                        # Insurance Fields
            self.insuranceProviderEdit = QLineEdit()
            self.insuranceProviderEdit.setReadOnly(True)
            self.policyNumberEdit = QLineEdit()
            self.policyNumberEdit.setReadOnly(True)
            self.groupNumberEdit = QLineEdit()
            self.groupNumberEdit.setReadOnly(True)
            layout.addRow("Insurance Provider:", self.insuranceProviderEdit)
            layout.addRow("Policy Number:", self.policyNumberEdit)
            layout.addRow("Group Number:", self.groupNumberEdit)


            # Emergency Contact Fields
            self.emergencyNameEdit = QLineEdit()
            self.emergencyNameEdit.setReadOnly(True)
            self.emergencyPhoneEdit = QLineEdit()
            self.emergencyPhoneEdit.setReadOnly(True)
            layout.addRow("Emergency Contact Name:", self.emergencyNameEdit)
            layout.addRow("Emergency Contact Phone:", self.emergencyPhoneEdit)

            

            self.editBasicInfoBtn = QPushButton("Edit")
            self.saveBasicInfoBtn = QPushButton("Save")
            self.saveBasicInfoBtn.setEnabled(False)
            self.editBasicInfoBtn.clicked.connect(self.enableBasicInfoEdit)
            self.saveBasicInfoBtn.clicked.connect(self.saveBasicInfo)

            layout.addRow(self.editBasicInfoBtn, self.saveBasicInfoBtn)
            self.basic_info_tab.setLayout(layout)

            self.tabs.addTab(self.basic_info_tab, "Basic Info")
            self.tabs.addTab(self.insurance_tab, "Insurance")
            self.tabs.addTab(self.contacts_tab, "Contacts")
            self.tabs.addTab(self.billing_tab, "Billing")  # Add billing tab for Office Staff
            
        elif self.usertype in ["Medical Personnel", "Physician", "Administrator"]:
            self.tabs.addTab(self.basic_info_tab, "Basic Info")
            self.tabs.addTab(self.insurance_tab, "Insurance")
            self.tabs.addTab(self.contacts_tab, "Contacts")
            self.tabs.addTab(self.admissions_tab, "Admissions")
            self.tabs.addTab(self.notes_tab, "Notes")
            self.tabs.addTab(self.medications_tab, "Medications")
            self.tabs.addTab(self.procedures_tab, "Procedures")
            self.tabs.addTab(self.visitors_tab, "Approved Visitors")
            self.tabs.addTab(self.billing_tab, "Billing")  # Add billing tab for Medical Personnel and Physicians

        self.num_static_tabs = self.tabs.count()  # Store default tab count

    
    # 👇 Add the new slot functions here
    def enableInsuranceEdit(self):
        self.groupNumberEdit.setReadOnly(False)
        self.insuranceProviderEdit.setReadOnly(False)
        self.policyNumberEdit.setReadOnly(False)
        self.editInsuranceBtn.setEnabled(False)
        self.saveInsuranceBtn.setEnabled(True)

    def saveInsurance(self):
        provider = self.insuranceProviderEdit.text()
        policy = self.policyNumberEdit.text()
        # TODO: save to database
        self.insuranceProviderEdit.setReadOnly(True)
        self.policyNumberEdit.setReadOnly(True)
        self.groupNumberEdit.setReadOnly(True)
        self.editInsuranceBtn.setEnabled(True)
        self.saveInsuranceBtn.setEnabled(False)

    def enableContactsEdit(self):
        self.emergencyNameEdit.setReadOnly(False)
        self.emergencyPhoneEdit.setReadOnly(False)
        self.editContactsBtn.setEnabled(False)
        self.saveContactsBtn.setEnabled(True)

    def saveContacts(self):
        name = self.emergencyNameEdit.text()
        phone = self.emergencyPhoneEdit.text()
        # TODO: save to database
        self.emergencyNameEdit.setReadOnly(True)
        self.emergencyPhoneEdit.setReadOnly(True)
        self.editContactsBtn.setEnabled(True)
        self.saveContactsBtn.setEnabled(False)

    def reloadAdmissionDetails(self):
        try:
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            self.patient_data = patient_data

            # Re-load all tabs for the patient
            self.loadPatientData()

            # Look for the dynamic admission tab by its title
            if hasattr(self, 'current_admission_id'):
                admissions = patient_data[15]
                for idx, admission in enumerate(admissions):
                    if admission.get("admission_id") == self.current_admission_id:
                        tab_title = f"Admission #{self.current_admission_id}"
                        
                        # Remove tab if it already exists
                        for i in range(self.tabs.count()):
                            if self.tabs.tabText(i) == tab_title:
                                self.tabs.removeTab(i)
                                break
                        
                        # Reopen the updated tab
                        admission_id = self.admissions_data[idx].get('admission_id')
                        self.openAdmissionDetails(admission_id)
                        break

        except Exception as e:
            print("Error reloading admission details:", e)
            traceback.print_exc()



    def loadPatientData(self):
        try:
            # Get data using the search function
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            print("DEBUG - Patient data:", patient_data)

            if not patient_data:
                QMessageBox.warning(self, "No Data", "No patient data found.")
                return

            # Process data based on user type
            if self.usertype == "Volunteer":
                self.loadVolunteerData(patient_data)
            elif self.usertype == "Office Staff":
                self.loadOfficeStaffData(patient_data)
            elif self.usertype in ["Medical Personnel", "Physician", "Administrator"]:
                self.loadMedicalData(patient_data)

        except Exception as e:
            traceback.print_exc()  # Add this line for full stack trace in terminal
            QMessageBox.critical(self, "Error", f"Error loading patient data: {str(e)}")
            print(f"Error: {e}")

    def enableBasicInfoEdit(self):
        self.firstNameEdit.setReadOnly(False)
        self.middleNameEdit.setReadOnly(False)
        self.lastNameEdit.setReadOnly(False)
        self.addressEdit.setReadOnly(False)
        self.insuranceProviderEdit.setReadOnly(False)
        self.policyNumberEdit.setReadOnly(False)
        self.emergencyNameEdit.setReadOnly(False)
        self.emergencyPhoneEdit.setReadOnly(False)
        self.editBasicInfoBtn.setEnabled(False)
        self.saveBasicInfoBtn.setEnabled(True)
        self.groupNumberEdit.setReadOnly(False)


    def saveBasicInfo(self):
        first = self.firstNameEdit.text().strip()
        middle = self.middleNameEdit.text().strip()
        last = self.lastNameEdit.text().strip()
        address = self.addressEdit.toPlainText().strip()
        
        group_number = self.groupNumberEdit.text().strip()
        insurance_provider = self.insuranceProviderEdit.text().strip()
        policy_number = self.policyNumberEdit.text().strip()
        emergency_name = self.emergencyNameEdit.text().strip()
        emergency_phone = self.emergencyPhoneEdit.text().strip()

        try:
            if first != self.original_data['first_name']:
                UpdateDB.patientUpdateFirstName(self.patient_id, first, fixed_salt)
            if middle != self.original_data['middle_name']:
                UpdateDB.patientUpdateMiddleName(self.patient_id, middle, fixed_salt)
            if last != self.original_data['last_name']:
                UpdateDB.patientUpdateLastName(self.patient_id, last, fixed_salt)
            if address != self.original_data['address']:
                UpdateDB.patientUpdateAddress(self.patient_id, address)

            # Insurance updates
            if insurance_provider != self.original_data.get('insurance_provider', ''):
                UpdateDB.patientUpdateInsuranceCarrierName(self.patient_id, insurance_provider, encryption_key)
            if policy_number != self.original_data.get('policy_number', ''):
                UpdateDB.patientUpdateInsuranceAccountNumber(self.patient_id, policy_number, encryption_key)
            if group_number != self.original_data.get('group_number', ''):
                UpdateDB.patientUpdateInsuranceGroupNumber(self.patient_id, group_number, encryption_key)

            # Emergency contact updates
            if emergency_name != self.original_data.get('emergency_name', ''):
                UpdateDB.patientUpdateContactName(self.patient_id, emergency_name, encryption_key)
            if emergency_phone != self.original_data.get('emergency_phone', ''):
                UpdateDB.patientUpdateContactPhone(self.patient_id, emergency_phone, encryption_key)

            QMessageBox.information(self, "Success", "Patient info updated.")
            self.firstNameEdit.setReadOnly(True)
            self.middleNameEdit.setReadOnly(True)
            self.lastNameEdit.setReadOnly(True)
            self.addressEdit.setReadOnly(True)
            self.insuranceProviderEdit.setReadOnly(True)
            self.policyNumberEdit.setReadOnly(True)
            self.emergencyNameEdit.setReadOnly(True)
            self.emergencyPhoneEdit.setReadOnly(True)
            self.groupNumberEdit.setReadOnly(True)

            self.saveBasicInfoBtn.setEnabled(False)
            self.editBasicInfoBtn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update info: {e}")
    def loadVolunteerData(self, data):
        """Load data for Volunteer view"""
        # Volunteer view has: patient_id, first_name, middle_name, last_name, 
        # facility, floor, room_number, bed_number, visitors
        
        # Set header
        name = f"{data[1]} {data[2]} {data[3]}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data[1]))
        basic_layout.addRow("Middle Name:", QLabel(data[2]))
        basic_layout.addRow("Last Name:", QLabel(data[3]))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Location Tab
        location_layout = QFormLayout()
        location_layout.addRow("Facility:", QLabel(data[4]))
        location_layout.addRow("Floor:", QLabel(str(data[5])))
        location_layout.addRow("Room Number:", QLabel(str(data[6])))
        location_layout.addRow("Bed Number:", QLabel(str(data[7])))

        self.location_tab.setLayout(location_layout)
        
        # Visitors Tab
        visitors_layout = QVBoxLayout()
        if data[8] and len(data[8]) > 0:
            visitors_list = QListWidget()
            for visitor in data[8]:
                visitors_list.addItem(visitor)
            visitors_layout.addWidget(visitors_list)
        else:
            visitors_layout.addWidget(QLabel("No approved visitors"))
        self.visitors_tab.setLayout(visitors_layout)
    
    def loadOfficeStaffData(self, data):
        """Load data for Office Staff view"""
        # Office staff view has: patient_id, first_name, middle_name, last_name, 
        # mailing_address, insurance, phones, emergency contacts
        self.original_data = {
            'first_name': data[1],
            'middle_name': data[2],
            'last_name': data[3],
            'address': data[4]
        }
        # Set header
        name = f"{data[1]} {data[2]} {data[3]}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Populate the Basic Info form fields
        self.firstNameEdit.setText(data[1])
        self.middleNameEdit.setText(data[2])
        self.lastNameEdit.setText(data[3])
        self.addressEdit.setText(data[4])
        
        # Insurance Tab
        insurance_layout = QFormLayout()
        insurance_layout.addRow("Insurance Carrier:", QLabel(data[5]))
        insurance_layout.addRow("Account Number:", QLabel(data[6]))
        insurance_layout.addRow("Group Number:", QLabel(data[7]))
        self.insurance_tab.setLayout(insurance_layout)
        
        # Contacts Tab
        contacts_layout = QVBoxLayout()
        
        # Phone numbers
        phone_group = QGroupBox("Phone Numbers")
        phone_layout = QFormLayout()
        phone_layout.addRow("Home Phone:", QLabel(data[8]))
        phone_layout.addRow("Work Phone:", QLabel(data[9]))
        phone_layout.addRow("Mobile Phone:", QLabel(data[10]))
        phone_group.setLayout(phone_layout)
        contacts_layout.addWidget(phone_group)
        
        # Emergency contacts
        ec_group = QGroupBox("Emergency Contacts")
        ec_layout = QFormLayout()
        ec_layout.addRow("Contact 1 Name:", QLabel(data[11]))
        ec_layout.addRow("Contact 1 Phone:", QLabel(data[12]))
        ec_layout.addRow("Contact 2 Name:", QLabel(data[13]))
        ec_layout.addRow("Contact 2 Phone:", QLabel(data[14]))

        ec_group.setLayout(ec_layout)
        contacts_layout.addWidget(ec_group)
        
        self.contacts_tab.setLayout(contacts_layout)
        
        admissions = SearchDB.getAdmissionsWithPatientID(self.patient_id)
        
        self.loadBillingData(admissions)
        

    def loadMedicalData(self, data):
        """Load data for Medical Personnel and Physician view"""
        # Medical view has: patient_id, first_name, middle_name, last_name, address, insurance, phones, emergency contacts, admissions
        
        # Set header
        name = f"{data[1]} {data[2]} {data[3]}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data[1]))
        basic_layout.addRow("Middle Name:", QLabel(data[2]))
        basic_layout.addRow("Last Name:", QLabel(data[3]))
        basic_layout.addRow("Mailing Address:", QLabel(data[4]))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Insurance Tab
        insurance_layout = QFormLayout()
        insurance_layout.addRow("Insurance Carrier:", QLabel(data[5]))
        insurance_layout.addRow("Account Number:", QLabel(data[6]))
        insurance_layout.addRow("Group Number:", QLabel(data[7]))
        self.insurance_tab.setLayout(insurance_layout)
        
        # Contacts Tab
        contacts_layout = QVBoxLayout()
        
        # Phone numbers
        phone_group = QGroupBox("Phone Numbers")
        phone_layout = QFormLayout()
        phone_layout.addRow("Home Phone:", QLabel(data[8]))
        phone_layout.addRow("Work Phone:", QLabel(data[9]))
        phone_layout.addRow("Mobile Phone:", QLabel(data[10]))
        phone_group.setLayout(phone_layout)
        contacts_layout.addWidget(phone_group)
        
        # Emergency contacts
        ec_group = QGroupBox("Emergency Contacts")
        ec_layout = QFormLayout()
        ec_layout.addRow("Contact 1 Name:", QLabel(data[11]))
        ec_layout.addRow("Contact 1 Phone:", QLabel(data[12]))
        ec_layout.addRow("Contact 2 Name:", QLabel(data[13]))
        ec_layout.addRow("Contact 2 Phone:", QLabel(data[14]))

        ec_group.setLayout(ec_layout)
        contacts_layout.addWidget(ec_group)
        
        self.contacts_tab.setLayout(contacts_layout)
        
        # Process admissions data which is in position 15
        admissions = data[15]
        
        # Admissions Tab - List of admissions
        admissions_layout = QVBoxLayout()
        if admissions and len(admissions) > 0:
            admissions_list = QListWidget()
            for admission in admissions:
                admission_id = admission.get('admission_id', '')
                admit_date = admission.get('admittance_date', '')
                reason = admission.get('admission_reason', '')
                discharge = admission.get('admittance_discharge', '')
                
                display_text = f"Admission #{admission_id}: {admit_date} - Reason: {reason}"
                if discharge and discharge.lower() != 'none':
                    display_text += f" (Discharged: {discharge})"
                
                admissions_list.addItem(display_text)

            admissions_layout.addWidget(admissions_list)

            admissions_list.itemDoubleClicked.connect(self.openAdmissionDetails)
            self.admissions_list_widget = admissions_list
            self.admissions_data = admissions

        else:
            admissions_layout.addWidget(QLabel("No admissions found"))
        self.admissions_tab.setLayout(admissions_layout)
        
        # Notes Tab
        notes_layout = QVBoxLayout()
        
        all_notes = []
        if admissions:
            for admission in admissions:
                if 'details' in admission and 'notes' in admission['details']:
                    for note in admission['details']['notes'] or []:
                        note_text = note.get('text', '')
                        note_type = note.get('type', '')
                        note_author = note.get('author', '')
                        note_datetime = note.get('datetime', '')
                        
                        all_notes.append((note_datetime, f"{note_type} note by {note_author}: {note_text}"))
        
            # Sort notes by datetime
            all_notes.sort(key=lambda x: x[0])
            
            if all_notes:
                notes_list = QListWidget()
                for _, note_text in all_notes:
                    notes_list.addItem(note_text)
                notes_layout.addWidget(notes_list)
            else:
                notes_layout.addWidget(QLabel("No notes found"))
            
            self.notes_tab.setLayout(notes_layout)
            
            note_entry_group = QGroupBox("Add Note")
            note_entry_layout = QVBoxLayout()


            note_text_edit = QTextEdit()
            note_text_edit.setPlaceholderText("Enter your note here...")

            save_note_button = QPushButton("Save Note")

            def saveNote():
                note_text = note_text_edit.toPlainText().strip()
                
                if not note_text:
                    QMessageBox.warning(self, "Empty Note", "Please enter note content.")
                    return

                try:
                    InsertData.insertNote(admission_id, note_text)
                    notes_list.addItem(f"New Note: {note_text}")
                    QMessageBox.information(self, "Success", "Note added successfully!")
                    note_text_edit.clear()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save note: {str(e)}")

            save_note_button.clicked.connect(saveNote)

            note_entry_layout.addWidget(note_text_edit)
            note_entry_layout.addWidget(save_note_button)
            note_entry_group.setLayout(note_entry_layout)

            notes_layout.addWidget(note_entry_group)

            # Medications Tab
            medications_layout = QVBoxLayout()
            all_meds = []
            
            for admission in admissions:
                if 'details' in admission and 'prescriptions' in admission['details']:
                    for med in admission['details']['prescriptions'] or []:
                        medication = med.get('medication', '')
                        amount = med.get('amount', '')
                        schedule = med.get('schedule', '')
                        
                        all_meds.append(f"Medication: {medication}, Amount: {amount}, Schedule: {schedule}")
            
            if all_meds:
                meds_list = QListWidget()
                for med in all_meds:
                    meds_list.addItem(med)
                medications_layout.addWidget(meds_list)
            else:
                medications_layout.addWidget(QLabel("No medications found"))
            
            self.medications_tab.setLayout(medications_layout)
            
            # Procedures Tab
            procedures_layout = QVBoxLayout()
            all_procedures = []
            
            for admission in admissions:
                if 'details' in admission and 'procedures' in admission['details']:
                    for proc in admission['details']['procedures'] or []:
                        name = proc.get('name', '')
                        scheduled = proc.get('scheduled', '')
                        
                        all_procedures.append(f"Procedure: {name}, Scheduled: {scheduled}")
            
            if all_procedures:
                proc_list = QListWidget()
                for proc in all_procedures:
                    proc_list.addItem(proc)
                procedures_layout.addWidget(proc_list)
            else:
                procedures_layout.addWidget(QLabel("No procedures found"))
            
            self.procedures_tab.setLayout(procedures_layout)

             # Visitors Tab
            visitors_layout = QVBoxLayout()
            
            # Find the active admission (one without discharge date)
            active_admission = None
            active_admission_id = None  # Store admission ID for updates
            for admission in admissions:
                discharge = admission.get('admittance_discharge', '')
                if not discharge or discharge.lower() == 'none':
                    active_admission = admission
                    active_admission_id = admission.get('admission_id')
                    break
            
            # Display current visitors
            current_visitors = []
            if active_admission and 'approved_visitors' in active_admission and active_admission['approved_visitors']:
                current_visitors = active_admission['approved_visitors']
            
            visitors_group = QGroupBox("Current Approved Visitors")
            visitors_group_layout = QVBoxLayout()
            
            self.visitors_list = QListWidget()
            for visitor in current_visitors:
                self.visitors_list.addItem(visitor)
            visitors_group_layout.addWidget(self.visitors_list)
            visitors_group.setLayout(visitors_group_layout)
            visitors_layout.addWidget(visitors_group)
            
            # Add visitor management section if there's an active admission
            if active_admission_id:
                add_visitor_group = QGroupBox("Add/Remove Visitors")
                add_visitor_layout = QHBoxLayout()
                
                visitor_name_input = QLineEdit()
                visitor_name_input.setPlaceholderText("Enter visitor name")
                
                add_visitor_button = QPushButton("Add Visitor")
                remove_visitor_button = QPushButton("Remove Selected")
                
                def addVisitor():
                    visitor_name = visitor_name_input.text().strip()
                    if not visitor_name:
                        QMessageBox.warning(self, "Error", "Please enter a visitor name.")
                        return
                    if len(current_visitors) > 0:
                    # Add to the current list
                        try:
                            current_visitors.append(visitor_name)
                            self.visitors_list.addItem(visitor_name)
                            UpdateDB.updateVisitors(active_admission_id, current_visitors, encryption_key)
                            visitor_name_input.clear()
                            QMessageBox.information(self, "Success", f"Added {visitor_name} to approved visitors.")
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Failed to add visitor: {str(e)}")
                            # Roll back the list changes
                            self.visitors_list.takeItem(self.visitors_list.count() - 1)
                            current_visitors.pop()
                    
                    # Update in the database
                    else:
                        try:
                            current_visitors.append(visitor_name)
                            self.visitors_list.addItem(visitor_name)
                            InsertData.insertVisitors(active_admission_id, current_visitors, encryption_key)
                            visitor_name_input.clear()
                            QMessageBox.information(self, "Success", f"Added {visitor_name} to approved visitors.")
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Failed to add visitor: {str(e)}")
                            # Roll back the list changes
                            self.visitors_list.takeItem(self.visitors_list.count() - 1)
                            current_visitors.pop()
                
                def removeVisitor():
                    selected_items = self.visitors_list.selectedItems()
                    if not selected_items:
                        QMessageBox.warning(self, "Error", "Please select a visitor to remove.")
                        return
                    
                    visitor_name = selected_items[0].text()
                    
                    # Remove from the current list
                    current_visitors.remove(visitor_name)
                    self.visitors_list.takeItem(self.visitors_list.row(selected_items[0]))
                    
                    # Update in the database
                    try:
                        UpdateDB.updateVisitors(active_admission_id, current_visitors, encryption_key)
                        QMessageBox.information(self, "Success", f"Removed {visitor_name} from approved visitors.")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to remove visitor: {str(e)}")
                        # Roll back the list changes
                        current_visitors.append(visitor_name)
                        self.visitors_list.addItem(visitor_name)
                
                add_visitor_button.clicked.connect(addVisitor)
                remove_visitor_button.clicked.connect(removeVisitor)
                
                add_visitor_layout.addWidget(visitor_name_input)
                add_visitor_layout.addWidget(add_visitor_button)
                add_visitor_layout.addWidget(remove_visitor_button)
                add_visitor_group.setLayout(add_visitor_layout)
                visitors_layout.addWidget(add_visitor_group)
            else:
                no_active_label = QLabel("No active admission. Cannot modify visitors.")
                no_active_label.setStyleSheet("color: red; font-weight: bold;")
                visitors_layout.addWidget(no_active_label)
            
            # Show all historical visitors across all admissions
            historical_group = QGroupBox("Historical Visitors (All Admissions)")
            historical_layout = QVBoxLayout()
            
            all_historical_visitors = set()  # Use a set to avoid duplicates
            for admission in admissions:
                if 'approved_visitors' in admission and admission['approved_visitors']:
                    for visitor in admission['approved_visitors']:
                        all_historical_visitors.add(visitor)
            
            if all_historical_visitors:
                historical_list = QListWidget()
                for visitor in sorted(all_historical_visitors):
                    historical_list.addItem(visitor)
                historical_layout.addWidget(historical_list)
            else:
                historical_layout.addWidget(QLabel("No historical visitors"))
            
            historical_group.setLayout(historical_layout)
            visitors_layout.addWidget(historical_group)
            
            self.visitors_tab.setLayout(visitors_layout)
            
            admissions = SearchDB.getAdmissionsWithPatientID(self.patient_id)
        
            self.loadBillingData(admissions)
    
    def openAdmissionDetails(self, item):
        index = self.admissions_list_widget.row(item)
        if index < 0 or index >= len(self.admissions_data):
            QMessageBox.warning(self, "Error", "Invalid admission selected.")
            return

        admission = self.admissions_data[index]
        admission_id = admission.get('admission_id', 'N/A')
        tab_title = f"Admission #{admission_id}"

        # Check if this tab already exists
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_title:
                self.tabs.setCurrentIndex(i)
                return

        # Create new tab content
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>Admission Date:</b> {admission.get('admittance_date', '')}"))
        layout.addWidget(QLabel(f"<b>Discharge Date:</b> {admission.get('admittance_discharge', 'Not yet discharged')}"))
        layout.addWidget(QLabel(f"<b>Reason:</b> {admission.get('admission_reason', '')}"))

        # Medications
        meds_group = QGroupBox("Medications")
        meds_layout = QVBoxLayout()
        prescriptions = admission['details'].get('prescriptions', [])
        if prescriptions:
            for med in prescriptions:
                meds_layout.addWidget(QLabel(f"{med['medication']} - {med['amount']} ({med['schedule']})"))
        meds_group.setLayout(meds_layout)
        layout.addWidget(meds_group)

        # Procedures
        proc_group = QGroupBox("Procedures")
        proc_layout = QVBoxLayout()
        procedures = admission['details'].get('procedures', [])
        if procedures:
            for proc in procedures:
                proc_layout.addWidget(QLabel(f"{proc['name']} (Scheduled: {proc['scheduled']})"))
        proc_group.setLayout(proc_layout)
        layout.addWidget(proc_group)

        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        notes = admission['details'].get('notes', [])
        if notes:
            for note in notes:
                notes_layout.addWidget(QLabel(
                    f"{note['datetime']} - {note['type']} by {note['author']}: {note['text']}"
                ))
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Finalize layout and tab
        tab.setLayout(layout)
        new_index = self.tabs.addTab(tab, tab_title)
        self.tabs.setCurrentWidget(tab)

        discharge_btn = QPushButton("Discharge Patient")
        discharge_btn.clicked.connect(
            lambda _, adm_id=admission_id: self.dischargePatient(adm_id)
        )
        layout.addWidget(discharge_btn)

        # Add Medication Button
        add_meds_btn = QPushButton("Add Medication")
        add_meds_btn.clicked.connect(lambda: self.addMedication(admission_id))
        layout.addWidget(add_meds_btn)

        add_proc_btn = QPushButton("Add Procedure")
        add_proc_btn.clicked.connect(lambda: self.addProcedure(admission_id))
        layout.addWidget(add_proc_btn)



        close_button = QPushButton("✕")
        close_button.setFixedSize(18, 18)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        close_button.clicked.connect(lambda _, tab=tab: self.tabs.removeTab(self.tabs.indexOf(tab)))

        # Set button on the tab
        self.tabs.tabBar().setTabButton(new_index, QTabBar.RightSide, close_button)

    def addMedication(self, admission_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Medication")
        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        amount_input = QLineEdit()
        schedule_input = QLineEdit()

        layout.addRow("Medication Name:", name_input)
        layout.addRow("Amount:", amount_input)
        layout.addRow("Schedule:", schedule_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        # Move submission/refresh inside accept lambda
        def handleSubmit():
            self.submitMedication(
                dialog,
                admission_id,
                name_input.text(),
                amount_input.text(),
                schedule_input.text()
            )
            self.reloadAdmissionDetails()  # only call if medication was submitted

        buttons.accepted.connect(handleSubmit)
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()



    def submitMedication(self, dialog, admission_id, name, amount, schedule):
        try:
            UpdateDB.addPrescription(admission_id, name, amount, schedule, self.encryption_key)
            QMessageBox.information(self, "Success", "Medication added.")
            dialog.accept()
            self.loadPatientData()  # Refresh
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def addProcedure(self, admission_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Procedure")
        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        datetime_input = QDateTimeEdit()
        datetime_input.setCalendarPopup(True)
        datetime_input.setDateTime(QDateTime.currentDateTime())

        layout.addRow("Procedure Name:", name_input)
        layout.addRow("Scheduled Time:", datetime_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(lambda: self.submitProcedure(dialog, admission_id, name_input.text(), datetime_input.dateTime().toString(Qt.ISODate)))
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()
        self.reloadAdmissionDetails()


    def submitProcedure(self, dialog, admission_id, name, scheduled_time):
        try:
            UpdateDB.addProcedure(admission_id, name, scheduled_time, self.encryption_key)
            QMessageBox.information(self, "Success", "Procedure added.")
            dialog.accept()
            self.loadPatientData()  # Refresh
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def loadBillingData(self, admissions):
        """Load all billing information for the patient using the predefined BillingInformationView"""
        # Create the billing tab layout
        billing_layout = QVBoxLayout()
        
        # Container widget for billing info
        billing_list_container = QGroupBox("Billing Information")
        billing_list_layout = QVBoxLayout()
        
        # Create a table for billing info
        self.billing_table = QTableWidget()
        self.billing_table.setColumnCount(5)
        self.billing_table.setHorizontalHeaderLabels(["Admission ID", "Total Amount", "Paid", "Insurance Paid", "Balance"])
        self.billing_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Make sure table is not editable
        self.billing_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.billing_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        # Initialize an empty billing data list
        self.billing_data = []
        
        # Check if any admission has billing info
        has_billing = False
        
        if admissions:
            row = 0
            for admission in admissions:
                # Make sure we have the admission_id
                admission_id = None
                
                # Handle different possible formats of admission data
                if isinstance(admission, dict) and 'admission_id' in admission:
                    admission_id = admission['admission_id']
                elif hasattr(admission, 'get'):
                    admission_id = admission.get('admission_id')
                    if admission_id is None and isinstance(admission, dict) and len(admission) > 0:
                        # Try to get the first item if it's a dict without 'admission_id'
                        admission_id = list(admission.values())[0]
                elif isinstance(admission, (list, tuple)) and len(admission) > 0:
                    admission_id = admission[0]
                
                if admission_id is None:
                    continue
                
                # Use the predefined searchBillingWithAdmission function
                try:
                    billing = SearchDB.searchBillingWithAdmission(admission_id)
                    
                    if billing:  # If billing info exists
                        has_billing = True
                        self.billing_table.insertRow(row)
                        
                        # Admission ID
                        self.billing_table.setItem(row, 0, QTableWidgetItem(str(billing[1])))
                        
                        # Total Amount Owed
                        self.billing_table.setItem(row, 1, QTableWidgetItem(f"${float(billing[2]):.2f}"))
                        
                        # Amount Paid
                        self.billing_table.setItem(row, 2, QTableWidgetItem(f"${float(billing[3]):.2f}"))
                        
                        # Insurance Paid
                        self.billing_table.setItem(row, 3, QTableWidgetItem(f"${float(billing[4]):.2f}"))
                        
                        # Balance Due
                        balance = float(billing[5])
                        balance_item = QTableWidgetItem(f"${balance:.2f}")
                        if balance > 0:
                            balance_item.setForeground(QtGui.QBrush(QtGui.QColor("red")))
                        self.billing_table.setItem(row, 4, balance_item)
                        
                        # Store billing data for reference
                        bill_items = []
                        if billing[6]:  # billing_items from BillingInformationView
                            if isinstance(billing[6], str):
                                # If it's returned as a string, parse it as JSON
                                try:
                                    bill_items = json.loads(billing[6])
                                except:
                                    bill_items = []
                            else:
                                # It might already be a list/dict
                                bill_items = billing[6]
                        
                        self.billing_data.append({
                            'billing_id': billing[0],
                            'admission_id': billing[1],
                            'total': float(billing[2]),
                            'paid': float(billing[3]),
                            'insurance_paid': float(billing[4]),
                            'balance': float(billing[5]),
                            'items': bill_items
                        })
                        
                        row += 1
                except Exception as e:
                    print(f"Error fetching billing data for admission {admission_id}: {e}")
                    continue
        
        if has_billing:
            # Double click to view details
            self.billing_table.cellDoubleClicked.connect(self.openBillingDetails)
            billing_list_layout.addWidget(self.billing_table)
            
            # Add payment processing button
            payment_button = QPushButton("Process Payment")
            payment_button.clicked.connect(self.processPayment)
            billing_list_layout.addWidget(payment_button)
        else:
            no_billing_label = QLabel("No billing information found")
            no_billing_label.setAlignment(Qt.AlignCenter)
            billing_list_layout.addWidget(no_billing_label)
        
        billing_list_container.setLayout(billing_list_layout)
        billing_layout.addWidget(billing_list_container)
        
        # Add buttons for adding new billing items
        buttons_layout = QHBoxLayout()
        
        if self.usertype in ["Medical Personnel", "Physician", "Administrator"]:
            add_bill_button = QPushButton("Add Billing Item")
            add_bill_button.clicked.connect(self.addBillingItem)
            buttons_layout.addWidget(add_bill_button)
        
        billing_layout.addLayout(buttons_layout)
        
        # Set the layout to the billing tab
        self.billing_tab.setLayout(billing_layout)


    # 2. Now let's add the processPayment method to handle payment processing
    # Add this to the PatientDetailsScreen class

    def processPayment(self):
        """Process a payment for a selected billing record"""
        selected_rows = self.billing_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a billing record to process payment.")
            return
        
        selected_row = selected_rows[0].row()
        
        if selected_row < 0 or selected_row >= len(self.billing_data):
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid billing record.")
            return
        
        billing_data = self.billing_data[selected_row]
        billing_id = billing_data['billing_id']
        admission_id = billing_data['admission_id']
        total_owed = billing_data['total']
        current_paid = billing_data['paid']
        current_insurance = billing_data['insurance_paid']
        remaining_balance = billing_data['balance']
        
        if remaining_balance <= 0:
            QMessageBox.information(self, "No Balance Due", "This bill has been fully paid.")
            return
        
        # Create payment dialog
        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Process Payment")
        payment_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout()
        
        # Summary information
        summary_group = QGroupBox("Billing Summary")
        summary_layout = QFormLayout()
        summary_layout.addRow("Billing ID:", QLabel(f"{billing_id}"))
        summary_layout.addRow("Admission ID:", QLabel(f"{admission_id}"))
        summary_layout.addRow("Total Amount:", QLabel(f"${total_owed:.2f}"))
        summary_layout.addRow("Amount Paid:", QLabel(f"${current_paid:.2f}"))
        summary_layout.addRow("Insurance Paid:", QLabel(f"${current_insurance:.2f}"))
        
        balance_label = QLabel(f"${remaining_balance:.2f}")
        if remaining_balance > 0:
            balance_label.setStyleSheet("color: red; font-weight: bold;")
        summary_layout.addRow("Balance Due:", balance_label)
        
        summary_group.setLayout(summary_layout)
        dialog_layout.addWidget(summary_group)
        
        # Payment form
        payment_group = QGroupBox("Payment Information")
        payment_form = QFormLayout()
        
        # Payment type selection
        payment_type = QComboBox()
        payment_type.addItems(["Patient Payment", "Insurance Payment"])
        
        # Amount input
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        amount_input.setValidator(QtGui.QDoubleValidator(0.01, remaining_balance, 2))
        amount_input.setText(f"{remaining_balance:.2f}")  # Default to full balance
        
        # Payment method (for patient payments)
        payment_method = QComboBox()
        payment_method.addItems(["Cash", "Credit Card", "Check", "Electronic Transfer"])
        
        # Add widgets to form
        payment_form.addRow("Payment Type:", payment_type)
        payment_form.addRow("Amount ($):", amount_input)
        payment_form.addRow("Payment Method:", payment_method)
        
        # Set up conditional display for payment method
        def onPaymentTypeChanged(index):
            is_patient = index == 0  # Patient Payment
            payment_method.setEnabled(is_patient)
            payment_method_label = payment_form.labelForField(payment_method)
            if payment_method_label:
                payment_method_label.setEnabled(is_patient)
        
        payment_type.currentIndexChanged.connect(onPaymentTypeChanged)
        
        payment_group.setLayout(payment_form)
        dialog_layout.addWidget(payment_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        process_button = QPushButton("Process Payment")
        process_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(process_button)
        
        dialog_layout.addLayout(button_layout)
        
        payment_dialog.setLayout(dialog_layout)
        
        # Connect buttons
        cancel_button.clicked.connect(payment_dialog.reject)
        
        def processPaymentAction():
            payment_amount_text = amount_input.text().strip()
            is_insurance = payment_type.currentIndex() == 1
            method = payment_method.currentText() if payment_method.isEnabled() else "Insurance"
            
            try:
                payment_amount = float(payment_amount_text)
                
                if payment_amount <= 0:
                    QMessageBox.warning(self, "Invalid Amount", "Payment amount must be greater than zero.")
                    return
                    
                if payment_amount > remaining_balance:
                    QMessageBox.warning(self, "Invalid Amount", f"Payment amount cannot exceed remaining balance (${remaining_balance:.2f}).")
                    return
                
                # Update the database with the payment
                self.updateBillingPayment(billing_id, payment_amount, is_insurance, method)
                
                payment_dialog.accept()
                
                # Refresh the billing data
                self.refreshBillingTab()
                
            except ValueError:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid payment amount.")
        
        process_button.clicked.connect(processPaymentAction)
        
        # Show dialog
        payment_dialog.exec_()


    # 3. Add the updateBillingPayment method to update the database with payment information

    def updateBillingPayment(self, billing_id, payment_amount, is_insurance, payment_method):
        """Update billing record with new payment information"""
        try:
            UpdateDB.updateBillingPayment(billing_id, payment_amount, is_insurance, payment_method)
                
            QMessageBox.information(self, "Success", f"{payment_method} payment of ${payment_amount:.2f} processed successfully.")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process payment: {str(e)}")
            return False


    # 4. Let's modify the openBillingDetails method to ensure all fields are not editable

    def openBillingDetails(self, row, column):
        if row < 0 or row >= len(self.billing_data):
            QMessageBox.warning(self, "Error", "Invalid billing selected.")
            return

        billing = self.billing_data[row]
        billing_id = billing.get('billing_id')
        admission_id = billing.get('admission_id')
        tab_title = f"Bill #{billing_id}"

        # Check if this tab already exists
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_title:
                self.tabs.setCurrentIndex(i)
                return

        # Create new tab content
        tab = QWidget()
        layout = QVBoxLayout()

        # Billing overview
        overview_group = QGroupBox("Billing Overview")
        overview_layout = QFormLayout()
        overview_layout.addRow("Admission ID:", QLabel(f"{admission_id}"))
        overview_layout.addRow("Total Amount:", QLabel(f"${billing['total']:.2f}"))
        overview_layout.addRow("Amount Paid:", QLabel(f"${billing['paid']:.2f}"))
        overview_layout.addRow("Insurance Paid:", QLabel(f"${billing['insurance_paid']:.2f}"))
        
        balance_label = QLabel(f"${billing['balance']:.2f}")
        if billing['balance'] > 0:
            balance_label.setStyleSheet("color: red;")
        overview_layout.addRow("Balance Due:", balance_label)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)

        # Itemized bill
        items_group = QGroupBox("Itemized Bill")
        items_layout = QVBoxLayout()
        
        items_table = QTableWidget()
        items_table.setColumnCount(3)
        items_table.setHorizontalHeaderLabels(["ID", "Description", "Amount"])
        items_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        items_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Ensure table is not editable
        
        if billing['items'] and len(billing['items']) > 0:
            items_table.setRowCount(len(billing['items']))
            total_amount = 0.0
            
            for row, item in enumerate(billing['items']):
                # BillingInformationView returns items with these field names
                item_id = item.get('item_id', 'N/A')
                description = item.get('description', 'N/A')
                amount = item.get('charge', 0.0)
                
                items_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
                items_table.setItem(row, 1, QTableWidgetItem(str(description)))
                items_table.setItem(row, 2, QTableWidgetItem(f"${float(amount):.2f}"))
                
                total_amount += float(amount)
                
            # Add total row
            items_table.insertRow(len(billing['items']))
            items_table.setItem(len(billing['items']), 0, QTableWidgetItem(""))
            items_table.setItem(len(billing['items']), 1, QTableWidgetItem("Total"))
            total_item = QTableWidgetItem(f"${total_amount:.2f}")
            total_item.setFont(QtGui.QFont("MS Shell Dlg 2", 10, QtGui.QFont.Bold))
            items_table.setItem(len(billing['items']), 2, total_item)
        else:
            items_table.setRowCount(1)
            items_table.setItem(0, 0, QTableWidgetItem(""))
            items_table.setItem(0, 1, QTableWidgetItem("No items found"))
            items_table.setItem(0, 2, QTableWidgetItem("$0.00"))
        
        items_layout.addWidget(items_table)
        
        # Add payment button to this view as well
        if billing['balance'] > 0:
            payment_button = QPushButton("Process Payment")
            payment_button.clicked.connect(lambda: self.processPaymentForBilling(billing))
            items_layout.addWidget(payment_button)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)

        # Finalize layout and tab
        tab.setLayout(layout)
        new_index = self.tabs.addTab(tab, tab_title)
        self.tabs.setCurrentWidget(tab)

        # Add a close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(18, 18)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        close_button.clicked.connect(lambda _, tab=tab: self.tabs.removeTab(self.tabs.indexOf(tab)))

        # Set button on the tab
        self.tabs.tabBar().setTabButton(new_index, QTabBar.RightSide, close_button)


    # 5. Add helper method to process payment from the billing details tab

    def processPaymentForBilling(self, billing_data):
        """Process payment for a specific billing record from the details view"""
        billing_id = billing_data['billing_id']
        admission_id = billing_data['admission_id']
        total_owed = billing_data['total']
        current_paid = billing_data['paid']
        current_insurance = billing_data['insurance_paid']
        remaining_balance = billing_data['balance']
        
        if remaining_balance <= 0:
            QMessageBox.information(self, "No Balance Due", "This bill has been fully paid.")
            return
        
        # Create payment dialog
        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Process Payment")
        payment_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout()
        
        # Summary information
        summary_group = QGroupBox("Billing Summary")
        summary_layout = QFormLayout()
        summary_layout.addRow("Billing ID:", QLabel(f"{billing_id}"))
        summary_layout.addRow("Admission ID:", QLabel(f"{admission_id}"))
        summary_layout.addRow("Total Amount:", QLabel(f"${total_owed:.2f}"))
        summary_layout.addRow("Amount Paid:", QLabel(f"${current_paid:.2f}"))
        summary_layout.addRow("Insurance Paid:", QLabel(f"${current_insurance:.2f}"))
        
        balance_label = QLabel(f"${remaining_balance:.2f}")
        if remaining_balance > 0:
            balance_label.setStyleSheet("color: red; font-weight: bold;")
        summary_layout.addRow("Balance Due:", balance_label)
        
        summary_group.setLayout(summary_layout)
        dialog_layout.addWidget(summary_group)
        
        # Payment form
        payment_group = QGroupBox("Payment Information")
        payment_form = QFormLayout()
        
        # Payment type selection
        payment_type = QComboBox()
        payment_type.addItems(["Patient Payment", "Insurance Payment"])
        
        # Amount input
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        amount_input.setValidator(QtGui.QDoubleValidator(0.01, remaining_balance, 2))
        amount_input.setText(f"{remaining_balance:.2f}")  # Default to full balance
        
        # Payment method (for patient payments)
        payment_method = QComboBox()
        payment_method.addItems(["Cash", "Credit Card", "Check", "Electronic Transfer"])
        
        # Add widgets to form
        payment_form.addRow("Payment Type:", payment_type)
        payment_form.addRow("Amount ($):", amount_input)
        payment_form.addRow("Payment Method:", payment_method)
        
        # Set up conditional display for payment method
        def onPaymentTypeChanged(index):
            is_patient = index == 0  # Patient Payment
            payment_method.setEnabled(is_patient)
            payment_method_label = payment_form.labelForField(payment_method)
            if payment_method_label:
                payment_method_label.setEnabled(is_patient)
        
        payment_type.currentIndexChanged.connect(onPaymentTypeChanged)
        
        payment_group.setLayout(payment_form)
        dialog_layout.addWidget(payment_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        process_button = QPushButton("Process Payment")
        process_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(process_button)
        
        dialog_layout.addLayout(button_layout)
        
        payment_dialog.setLayout(dialog_layout)
        
        # Connect buttons
        cancel_button.clicked.connect(payment_dialog.reject)
        
        def processPaymentAction():
            payment_amount_text = amount_input.text().strip()
            is_insurance = payment_type.currentIndex() == 1
            method = payment_method.currentText() if payment_method.isEnabled() else "Insurance"
            
            try:
                payment_amount = float(payment_amount_text)
                
                if payment_amount <= 0:
                    QMessageBox.warning(self, "Invalid Amount", "Payment amount must be greater than zero.")
                    return
                    
                if payment_amount > remaining_balance:
                    QMessageBox.warning(self, "Invalid Amount", f"Payment amount cannot exceed remaining balance (${remaining_balance:.2f}).")
                    return
                
                # Update the database with the payment
                self.updateBillingPayment(billing_id, payment_amount, is_insurance, method)
                
                payment_dialog.accept()
                
                # Refresh tabs
                self.refreshBillingTab()
                
            except ValueError:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid payment amount.")
            
        process_button.clicked.connect(processPaymentAction)
        
        # Show dialog
        payment_dialog.exec_()

    
    # 4. Let's modify the openBillingDetails method to ensure all fields are not editable
    def openBillingDetails(self, row, column):
        if row < 0 or row >= len(self.billing_data):
            QMessageBox.warning(self, "Error", "Invalid billing selected.")
            return

        billing = self.billing_data[row]
        billing_id = billing.get('billing_id')
        admission_id = billing.get('admission_id')
        tab_title = f"Bill #{billing_id}"

        # Check if this tab already exists
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_title:
                self.tabs.setCurrentIndex(i)
                return

        # Create new tab content
        tab = QWidget()
        layout = QVBoxLayout()

        # Billing overview
        overview_group = QGroupBox("Billing Overview")
        overview_layout = QFormLayout()
        overview_layout.addRow("Admission ID:", QLabel(f"{admission_id}"))
        overview_layout.addRow("Total Amount:", QLabel(f"${billing['total']:.2f}"))
        overview_layout.addRow("Amount Paid:", QLabel(f"${billing['paid']:.2f}"))
        overview_layout.addRow("Insurance Paid:", QLabel(f"${billing['insurance_paid']:.2f}"))
        
        balance_label = QLabel(f"${billing['balance']:.2f}")
        if billing['balance'] > 0:
            balance_label.setStyleSheet("color: red;")
        overview_layout.addRow("Balance Due:", balance_label)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)

        # Itemized bill
        items_group = QGroupBox("Itemized Bill")
        items_layout = QVBoxLayout()
        
        items_table = QTableWidget()
        items_table.setColumnCount(3)
        items_table.setHorizontalHeaderLabels(["ID", "Description", "Amount"])
        items_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        items_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Ensure table is not editable
        
        if billing['items'] and len(billing['items']) > 0:
            items_table.setRowCount(len(billing['items']))
            total_amount = 0.0
            
            for row, item in enumerate(billing['items']):
                # BillingInformationView returns items with these field names
                item_id = item.get('item_id', 'N/A')
                description = item.get('description', 'N/A')
                amount = item.get('charge', 0.0)
                
                items_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
                items_table.setItem(row, 1, QTableWidgetItem(str(description)))
                items_table.setItem(row, 2, QTableWidgetItem(f"${float(amount):.2f}"))
                
                total_amount += float(amount)
                
            # Add total row
            items_table.insertRow(len(billing['items']))
            items_table.setItem(len(billing['items']), 0, QTableWidgetItem(""))
            items_table.setItem(len(billing['items']), 1, QTableWidgetItem("Total"))
            total_item = QTableWidgetItem(f"${total_amount:.2f}")
            total_item.setFont(QtGui.QFont("MS Shell Dlg 2", 10, QtGui.QFont.Bold))
            items_table.setItem(len(billing['items']), 2, total_item)
        else:
            items_table.setRowCount(1)
            items_table.setItem(0, 0, QTableWidgetItem(""))
            items_table.setItem(0, 1, QTableWidgetItem("No items found"))
            items_table.setItem(0, 2, QTableWidgetItem("$0.00"))
        
        items_layout.addWidget(items_table)
        
        # Add payment button to this view as well
        if billing['balance'] > 0:
            payment_button = QPushButton("Process Payment")
            payment_button.clicked.connect(lambda: self.processPaymentForBilling(billing))
            items_layout.addWidget(payment_button)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)

        # Finalize layout and tab
        tab.setLayout(layout)
        new_index = self.tabs.addTab(tab, tab_title)
        self.tabs.setCurrentWidget(tab)

        # Add a close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(18, 18)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        close_button.clicked.connect(lambda _, tab=tab: self.tabs.removeTab(self.tabs.indexOf(tab)))

        # Set button on the tab
        self.tabs.tabBar().setTabButton(new_index, QTabBar.RightSide, close_button)


    # 5. Add helper method to process payment from the billing details tab

    def processPaymentForBilling(self, billing_data):
        """Process payment for a specific billing record from the details view"""
        billing_id = billing_data['billing_id']
        admission_id = billing_data['admission_id']
        total_owed = billing_data['total']
        current_paid = billing_data['paid']
        current_insurance = billing_data['insurance_paid']
        remaining_balance = billing_data['balance']
        
        if remaining_balance <= 0:
            QMessageBox.information(self, "No Balance Due", "This bill has been fully paid.")
            return
        
        # Create payment dialog
        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Process Payment")
        payment_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout()
        
        # Summary information
        summary_group = QGroupBox("Billing Summary")
        summary_layout = QFormLayout()
        summary_layout.addRow("Billing ID:", QLabel(f"{billing_id}"))
        summary_layout.addRow("Admission ID:", QLabel(f"{admission_id}"))
        summary_layout.addRow("Total Amount:", QLabel(f"${total_owed:.2f}"))
        summary_layout.addRow("Amount Paid:", QLabel(f"${current_paid:.2f}"))
        summary_layout.addRow("Insurance Paid:", QLabel(f"${current_insurance:.2f}"))
        
        balance_label = QLabel(f"${remaining_balance:.2f}")
        if remaining_balance > 0:
            balance_label.setStyleSheet("color: red; font-weight: bold;")
        summary_layout.addRow("Balance Due:", balance_label)
        
        summary_group.setLayout(summary_layout)
        dialog_layout.addWidget(summary_group)
        
        # Payment form
        payment_group = QGroupBox("Payment Information")
        payment_form = QFormLayout()
        
        # Payment type selection
        payment_type = QComboBox()
        payment_type.addItems(["Patient Payment", "Insurance Payment"])
        
        # Amount input
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("0.00")
        amount_input.setValidator(QtGui.QDoubleValidator(0.01, remaining_balance, 2))
        amount_input.setText(f"{remaining_balance:.2f}")  # Default to full balance
        
        # Payment method (for patient payments)
        payment_method = QComboBox()
        payment_method.addItems(["Cash", "Credit Card", "Check", "Electronic Transfer"])
        
        # Add widgets to form
        payment_form.addRow("Payment Type:", payment_type)
        payment_form.addRow("Amount ($):", amount_input)
        payment_form.addRow("Payment Method:", payment_method)
        
        # Set up conditional display for payment method
        def onPaymentTypeChanged(index):
            is_patient = index == 0  # Patient Payment
            payment_method.setEnabled(is_patient)
            payment_method_label = payment_form.labelForField(payment_method)
            if payment_method_label:
                payment_method_label.setEnabled(is_patient)
        
        payment_type.currentIndexChanged.connect(onPaymentTypeChanged)
        
        payment_group.setLayout(payment_form)
        dialog_layout.addWidget(payment_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        process_button = QPushButton("Process Payment")
        process_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(process_button)
        
        dialog_layout.addLayout(button_layout)
        
        payment_dialog.setLayout(dialog_layout)
        
        # Connect buttons
        cancel_button.clicked.connect(payment_dialog.reject)
        
        def processPaymentAction():
            payment_amount_text = amount_input.text().strip()
            is_insurance = payment_type.currentIndex() == 1
            method = payment_method.currentText() if payment_method.isEnabled() else "Insurance"
            
            try:
                payment_amount = float(payment_amount_text)
                
                if payment_amount <= 0:
                    QMessageBox.warning(self, "Invalid Amount", "Payment amount must be greater than zero.")
                    return
                    
                if payment_amount > remaining_balance:
                    QMessageBox.warning(self, "Invalid Amount", f"Payment amount cannot exceed remaining balance (${remaining_balance:.2f}).")
                    return
                
                # Update the database with the payment
                self.updateBillingPayment(billing_id, payment_amount, is_insurance, method)
                
                payment_dialog.accept()
                
                # Refresh the billing data
                self.refreshBillingTab()
                
            except ValueError:
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid payment amount.")
        
        process_button.clicked.connect(processPaymentAction)
        
        # Show dialog
        payment_dialog.exec_()
    def addBillingItem(self):
        # Show dialog to select an admission
        admission_dialog = QDialog(self)
        admission_dialog.setWindowTitle("Add Billing Item")
        admission_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout()
        
        # Get all admissions for this patient
        admissions = []
        with hospitalDB.get_cursor() as cursor:
            sql = """SELECT a.admission_id,
                    pgp_sym_decrypt(a.admittance_datetime, %s) AS admit_date
                FROM admission a
                WHERE a.patient_id = %s
                ORDER BY a.admission_id DESC;"""
            params = (EncryptionKey.getKeys()[0], self.patient_id)
            cursor.execute(sql, params)
            admissions = cursor.fetchall()
        
        # Create form
        form_layout = QFormLayout()
        
        admission_combo = QComboBox()
        for admission in admissions:
            admission_combo.addItem(f"Admission #{admission[0]} - {admission[1]}", admission[0])
        
        item_description = QLineEdit()
        item_amount = QLineEdit()
        item_amount.setPlaceholderText("0.00")
        item_amount.setValidator(QtGui.QDoubleValidator(0.01, 9999999.99, 2))
        
        form_layout.addRow("Admission:", admission_combo)
        form_layout.addRow("Item Description:", item_description)
        form_layout.addRow("Amount ($):", item_amount)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        add_button = QPushButton("Add Item")
        add_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(add_button)
        
        dialog_layout.addLayout(form_layout)
        dialog_layout.addLayout(button_layout)
        
        admission_dialog.setLayout(dialog_layout)
        
        # Connect buttons
        cancel_button.clicked.connect(admission_dialog.reject)
        
        def addItem():
            admission_id = admission_combo.currentData()
            description = item_description.text().strip()
            amount_text = item_amount.text().strip()
            
            if not admission_id:
                QMessageBox.warning(self, "Error", "Please select an admission.")
                return
                
            if not description:
                QMessageBox.warning(self, "Error", "Please enter an item description.")
                return
                
            if not amount_text:
                QMessageBox.warning(self, "Error", "Please enter an amount.")
                return
                
            try:
                amount = float(amount_text)
                if amount <= 0:
                    QMessageBox.warning(self, "Error", "Amount must be greater than zero.")
                    return
                    
                # Add the billing item to the database
                self.addBillingItemToDatabase(admission_id, description, amount)
                
                admission_dialog.accept()
                
                # Refresh the data
                self.loadPatientData()
                
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid amount.")
        
        add_button.clicked.connect(addItem)
        
        # Show dialog
        admission_dialog.exec_()
    def addBillingItemToDatabase(self, admission_id, description, amount):
        try:
            # Use the existing InsertData.insertBilledItem function
            InsertData.insertBilledItem(admission_id, description, amount)
            
            # Log the billing action
            InsertData.log_action(f"Added billing item '{description}' for ${amount:.2f} to admission #{admission_id}")
            
            # Refresh the billing tab
            self.refreshBillingTab()
            
            QMessageBox.information(self, "Success", f"Billing item '{description}' added successfully.")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add billing item: {str(e)}")
            return False
        
    def refreshBillingTab(self):
        """Properly refresh the billing tab with updated data"""
        # Find the billing tab index
        billing_tab_index = -1
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Billing":
                billing_tab_index = i
                break
        
        if billing_tab_index >= 0:
            # Create a completely new tab widget for billing
            new_billing_tab = QWidget()
            
            # Get fresh admissions data 
            admissions = [] 
            with hospitalDB.get_cursor() as cursor:
                sql = """SELECT a.admission_id 
                        FROM admission a 
                        WHERE a.patient_id = %s;"""
                params = (self.patient_id,)
                cursor.execute(sql, params)
                admission_ids = cursor.fetchall()
                
                for admission_id in admission_ids:
                    # Use the billing view directly
                    sql = """SELECT * FROM BillingInformationView 
                            WHERE admission_id = %s;"""
                    cursor.execute(sql, (admission_id[0],))
                    billing = cursor.fetchone()
                    if billing:
                        admissions.append({'admission_id': admission_id[0]})
            
            # Create a new layout for the refreshed tab
            billing_layout = QVBoxLayout()
            
            # Container widget for billing info
            billing_list_container = QGroupBox("Billing Information")
            billing_list_layout = QVBoxLayout()
            
            # Create a table for billing info
            self.billing_table = QTableWidget()
            self.billing_table.setColumnCount(5)
            self.billing_table.setHorizontalHeaderLabels(["Admission ID", "Total Amount", "Paid", "Insurance Paid", "Balance"])
            self.billing_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.billing_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.billing_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            
            # Initialize an empty billing data list
            self.billing_data = []
            
            # Check if any admission has billing info
            has_billing = False
            
            if admissions:
                row = 0
                for admission in admissions:
                    admission_id = admission.get('admission_id')
                    
                    if admission_id is None:
                        continue
                    
                    # Use the predefined searchBillingWithAdmission function
                    try:
                        billing = SearchDB.searchBillingWithAdmission(admission_id)
                        
                        if billing:  # If billing info exists
                            has_billing = True
                            self.billing_table.insertRow(row)
                            
                            # Admission ID
                            self.billing_table.setItem(row, 0, QTableWidgetItem(str(billing[1])))
                            
                            # Total Amount Owed
                            self.billing_table.setItem(row, 1, QTableWidgetItem(f"${float(billing[2]):.2f}"))
                            
                            # Amount Paid
                            self.billing_table.setItem(row, 2, QTableWidgetItem(f"${float(billing[3]):.2f}"))
                            
                            # Insurance Paid
                            self.billing_table.setItem(row, 3, QTableWidgetItem(f"${float(billing[4]):.2f}"))
                            
                            # Balance Due
                            balance = float(billing[5])
                            balance_item = QTableWidgetItem(f"${balance:.2f}")
                            if balance > 0:
                                balance_item.setForeground(QtGui.QBrush(QtGui.QColor("red")))
                            self.billing_table.setItem(row, 4, balance_item)
                            
                            # Store billing data for reference
                            bill_items = []
                            if billing[6]:  # billing_items from BillingInformationView
                                if isinstance(billing[6], str):
                                    # If it's returned as a string, parse it as JSON
                                    try:
                                        bill_items = json.loads(billing[6])
                                    except:
                                        bill_items = []
                                else:
                                    # It might already be a list/dict
                                    bill_items = billing[6]
                            
                            self.billing_data.append({
                                'billing_id': billing[0],
                                'admission_id': billing[1],
                                'total': float(billing[2]),
                                'paid': float(billing[3]),
                                'insurance_paid': float(billing[4]),
                                'balance': float(billing[5]),
                                'items': bill_items
                            })
                            
                            row += 1
                    except Exception as e:
                        print(f"Error fetching billing data for admission {admission_id}: {e}")
                        continue
            
            if has_billing:
                # Double click to view details
                self.billing_table.cellDoubleClicked.connect(self.openBillingDetails)
                billing_list_layout.addWidget(self.billing_table)
                
                # Add payment processing button
                payment_button = QPushButton("Process Payment")
                payment_button.clicked.connect(self.processPayment)
                billing_list_layout.addWidget(payment_button)
            else:
                no_billing_label = QLabel("No billing information found")
                no_billing_label.setAlignment(Qt.AlignCenter)
                billing_list_layout.addWidget(no_billing_label)
            
            billing_list_container.setLayout(billing_list_layout)
            billing_layout.addWidget(billing_list_container)
            
            # Add buttons for adding new billing items
            buttons_layout = QHBoxLayout()
            
            if self.usertype in ["Medical Personnel", "Physician", "Administrator"]:
                add_bill_button = QPushButton("Add Billing Item")
                add_bill_button.clicked.connect(self.addBillingItem)
                buttons_layout.addWidget(add_bill_button)
            
            billing_layout.addLayout(buttons_layout)
            
            # Set the new layout to the new tab widget
            new_billing_tab.setLayout(billing_layout)
            
            # Replace the old tab with the new one
            self.tabs.removeTab(billing_tab_index)
            self.tabs.insertTab(billing_tab_index, new_billing_tab, "Billing")
            self.tabs.setCurrentIndex(billing_tab_index)
            
            # Update the billing_tab reference to the new widget
            self.billing_tab = new_billing_tab

    def closeTab(self, index):
        # Prevent closing the default tabs (index < num_static_tabs)
        if index < self.num_static_tabs:
            QMessageBox.information(self, "Protected Tab", "You cannot close the default patient tabs.")
            return
        self.tabs.removeTab(index)

    def printPatientDetails(self):
        """Print patient details to a file"""
        try:
            # Get the patient data again
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            
            if not patient_data or len(patient_data) == 0:
                QMessageBox.warning(self, "No Data", "No patient data to print.")
                return
            
            lines = []
            lines.append("PATIENT DETAILS REPORT")
            lines.append("=" * 50)
            
            # Format based on user type
            if self.usertype == "Volunteer":
                name = f"{patient_data[1]} {patient_data[2]} {patient_data[3]}"
                lines.append(f"Patient: {name}")
                lines.append(f"Location: {patient_data[4]}, Floor {patient_data[5]}, Room {patient_data[6]}, Bed {patient_data[7]}")
                lines.append("\nApproved Visitors:")
                if patient_data[8] and len(patient_data[8]) > 0:
                    for visitor in patient_data[8]:
                        lines.append(f"- {visitor}")
                else:
                    lines.append("No approved visitors")
                    
            elif self.usertype == "Office Staff":
                name = f"{patient_data[1]} {patient_data[2]} {patient_data[3]}"
                lines.append(f"Patient: {name}")
                lines.append(f"Mailing Address: {patient_data[4] or 'Not provided'}")
                lines.append("\nInsurance Information:")
                lines.append(f"Carrier: {patient_data[5] or 'Not provided'}")
                lines.append(f"Account #: {patient_data[6] or 'Not provided'}")
                lines.append(f"Group #: {patient_data[7] or 'Not provided'}")
                lines.append("\nPhone Numbers:")
                lines.append(f"Home: {patient_data[8] or 'Not provided'}")
                lines.append(f"Work: {patient_data[9] or 'Not provided'}")
                lines.append(f"Mobile: {patient_data[10] or 'Not provided'}")
                lines.append("\nEmergency Contacts:")
                lines.append(f"Contact 1: {patient_data[11] or 'Not provided'} - {patient_data[12] or 'Not provided'}")
                lines.append(f"Contact 2: {patient_data[13] or 'Not provided'} - {patient_data[14] or 'Not provided'}")
                
                # Add billing information
                if hasattr(self, 'billing_data') and self.billing_data:
                    lines.append("\nBilling Information:")
                    for billing in self.billing_data:
                        lines.append(f"Billing #{billing['billing_id']} (Admission #{billing['admission_id']})")
                        lines.append(f"  Total Amount: ${billing['total']:.2f}")
                        lines.append(f"  Amount Paid: ${billing['paid']:.2f}")
                        lines.append(f"  Insurance Paid: ${billing['insurance_paid']:.2f}")
                        lines.append(f"  Balance Due: ${billing['balance']:.2f}")
                        
                        if 'items' in billing and billing['items']:
                            lines.append("  Itemized Bill:")
                            for item in billing['items']:
                                lines.append(f"    - {item['description']}: ${float(item['charge']):.2f}")
                
            elif self.usertype in ["Medical Personnel", "Physician", "Administrator"]:
                name = f"{patient_data[1]} {patient_data[2]} {patient_data[3]}"
                lines.append(f"Patient: {name}")
                lines.append(f"Mailing Address: {patient_data[4] or 'Not provided'}")
                
                lines.append("\nInsurance Information:")
                lines.append(f"Carrier: {patient_data[5] or 'Not provided'}")
                lines.append(f"Account #: {patient_data[6] or 'Not provided'}")
                lines.append(f"Group #: {patient_data[7] or 'Not provided'}")
                
                lines.append("\nPhone Numbers:")
                lines.append(f"Home: {patient_data[8] or 'Not provided'}")
                lines.append(f"Work: {patient_data[9] or 'Not provided'}")
                lines.append(f"Mobile: {patient_data[10] or 'Not provided'}")
                
                lines.append("\nEmergency Contacts:")
                lines.append(f"Contact 1: {patient_data[11] or 'Not provided'} - {patient_data[12] or 'Not provided'}")
                lines.append(f"Contact 2: {patient_data[13] or 'Not provided'} - {patient_data[14] or 'Not provided'}")
                
                admissions = patient_data[15] if len(patient_data) > 15 else []
                lines.append("\nAdmissions:")
                
                if admissions and len(admissions) > 0:
                    for admission in admissions:
                        admission_id = admission.get('admission_id', '')
                        admit_date = admission.get('admittance_date', '')
                        reason = admission.get('admission_reason', '')
                        discharge = admission.get('admittance_discharge', '')
                        
                        lines.append(f"\nAdmission #{admission_id}")
                        lines.append(f"Date: {admit_date}")
                        lines.append(f"Reason: {reason}")
                        if discharge and discharge.lower() != 'none':
                            lines.append(f"Discharged: {discharge}")
                        
                        # Notes
                        if 'details' in admission and 'notes' in admission['details'] and admission['details']['notes']:
                            lines.append("\n  Notes:")
                            for note in admission['details']['notes']:
                                note_text = note.get('text', '')
                                note_type = note.get('type', '')
                                note_author = note.get('author', '')
                                note_datetime = note.get('datetime', '')
                                lines.append(f"  - {note_datetime} {note_type} by {note_author}: {note_text}")
                        
                        # Medications
                        if 'details' in admission and 'prescriptions' in admission['details'] and admission['details']['prescriptions']:
                            lines.append("\n  Medications:")
                            for med in admission['details']['prescriptions']:
                                medication = med.get('medication', '')
                                amount = med.get('amount', '')
                                schedule = med.get('schedule', '')
                                lines.append(f"  - {medication}, {amount}, {schedule}")
                        
                        # Procedures
                        if 'details' in admission and 'procedures' in admission['details'] and admission['details']['procedures']:
                            lines.append("\n  Procedures:")
                            for proc in admission['details']['procedures']:
                                name = proc.get('name', '')
                                scheduled = proc.get('scheduled', '')
                                lines.append(f"  - {name}, Scheduled for {scheduled}")
                else:
                    lines.append("No admissions found")
                
                # Add billing information
                if hasattr(self, 'billing_data') and self.billing_data:
                    lines.append("\nBilling Information:")
                    for billing in self.billing_data:
                        lines.append(f"Billing #{billing['billing_id']} (Admission #{billing['admission_id']})")
                        lines.append(f"  Total Amount: ${billing['total']:.2f}")
                        lines.append(f"  Amount Paid: ${billing['paid']:.2f}")
                        lines.append(f"  Insurance Paid: ${billing['insurance_paid']:.2f}")
                        lines.append(f"  Balance Due: ${billing['balance']:.2f}")
                        
                        if 'items' in billing and billing['items']:
                            lines.append("  Itemized Bill:")
                            for item in billing['items']:
                                # Use the correct field names from BillingInformationView
                                description = item.get('description')
                                amount = item.get('charge')
                                lines.append(f"    - {description}: ${float(amount):.2f}")
            
            # Write to file
            filename = f"patient_{self.patient_id}_details.txt"
            with open(filename, 'w') as f:
                f.write("\n".join(lines))
            
            QMessageBox.information(self, "Success", f"Patient details saved to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error printing patient data: {str(e)}")
            print(f"Error: {e}")

    def dischargePatient(self, admission_id):
        from datetime import datetime
        discharge_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            UpdateDB.admissionUpdateDischarge(admission_id, discharge_time, encryption_key)
            QMessageBox.information(self, "Success", f"Admission {admission_id} discharged.")
            self.reloadAdmissionTab(admission_id)  # Optional: refresh to reflect discharge
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to discharge patient: {str(e)}")

    def reloadAdmissionTab(self, admission_id):
        self.tabs.clear()
        self.setupTabs()
        self.loadPatientData()

    def goBack(self):
        # Get the current index
        current_index = widget.currentIndex()
        
        # Only go back if we're not on the first screen
        if current_index > 0:
            # Get the current widget and explicitly disconnect any signals
            # that might be preventing proper event handling
            current_widget = widget.widget(current_index)
            
            # If this is a tabbed widget, you might need to disconnect tab signals
            if hasattr(current_widget, 'tabs'):
                try:
                    # Disconnect any tab signals that might be causing issues
                    current_widget.tabs.currentChanged.disconnect()
                except TypeError:
                    # Ignore if no connections exist
                    pass
            
            # Remove the current widget from stack
            widget.removeWidget(current_widget)
            
            # Ensure the widget is properly deleted
            current_widget.deleteLater()
            
            # Show a debug message to confirm the action is happening
            print(f"Navigating back from index {current_index} to {widget.currentIndex()}")
        else:
            # We're at the first screen
            print("Already at first screen, cannot go back further")

class LockScreen(QtWidgets.QDialog):
    def __init__(self, exitAction, widget, eventFilter, currentUser):
        super(LockScreen, self).__init__()
        #loadUi(locate_ui_file("lockScreen.ui"), self)
        loadUi("lockScreen.ui", self)
        self.exitAction = exitAction
        self.widget = widget
        self.eventFilter = eventFilter
        self.usernameField.setText(currentUser)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.resumeButton.clicked.connect(self.resumePressed)
        self.exitButton.clicked.connect(self.exitPressed)
        self.setWindowFlag(True)
        self.setWindowModality(True)
        # self.setFixedSize(400, 150)
        self.label.setAlignment(Qt.AlignCenter)

    def resumePressed(self):
        user = self.usernameField.text()
        password = self.passwordField.text()
        result_pass = SearchDB.passwordMatch(user, password)
        if result_pass:
            self.errorMsg.setText("")
            self.eventFilter.enabled = True
            self.widget.removeWidget(self)
            self.deleteLater()
        else:
            self.errorMsg.setText("Invalid username or password")
        
    def exitPressed(self):
        self.exitAction()

def LogOut():
    eventFilter.enabled = False
    hospitalDB.userLogout()
    
    # Clear all widgets from the stack except the first one
    while widget.count() > 1:
        # Remove the last widget in the stack
        last_widget = widget.widget(widget.count() - 1)
        widget.removeWidget(last_widget)
        
        # Free up resources by scheduling widget for deletion
        last_widget.deleteLater()
    
    # Create a new login screen
    login = LoginScreen()
    widget.addWidget(login)
    widget.setCurrentIndex(1)
    
    # Remove the initial screen now that we have login in position 1
    first_widget = widget.widget(0)
    widget.removeWidget(first_widget)
    first_widget.deleteLater()

def lockScreen():
    print("here")
    eventFilter.enabled = False
    lock = LockScreen(LogOut, widget, eventFilter, hospitalDB.getCurrentUserID())
    widget.addWidget(lock)
    widget.setCurrentIndex(widget.currentIndex() + 1)

class ApplicationCleanup:
    def __init__(self):
        # Connect to the aboutToQuit signal
        QCoreApplication.instance().aboutToQuit.connect(self.cleanup)
        
    def cleanup(self):
        # This function will be called when the app is closing
        print("Application closing, cleaning up user session...")
        try:
            # Check if any user is logged in
            if hospitalDB.getCurrentUsername():
                hospitalDB.userLogout()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            
app = QApplication(sys.argv)
app.setStyleSheet("""
    QPushButton {
        outline: none;
    }
    QPushButton:focus {
        outline: none;
    }
    QWidget {
        font-size: 32px;
        font-family: Arial, sans-serif;
    }
    QLabel {
        padding: 2px;
    }
    QPushButton {
        padding: 6px 12px;
        font-weight: bold;
        background-color: #e0e0e0;
        border: 1px solid #aaa;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #d6d6d6;
    }
    QTableWidget {
        gridline-color: #ccc;
        font-size: 15px;
    }
    QTabWidget::pane {
        border: 1px solid #ccc;
    }
    QTabBar::tab {
        padding: 6px;
        margin: 2px;
        border: 1px solid #aaa;
        border-radius: 4px;
        background: #f0f0f0;
    }
    QTabBar::tab:selected {
        background: #dcdcdc;
        font-weight: bold;
    }
""")
if not check_database_exists():
    # Database doesn't exist, show initialization screen
    widget = QtWidgets.QStackedWidget()
    init_screen = InitializeDatabaseScreen(widget)
    widget.addWidget(init_screen)
    widget.showMaximized()
else:
    home = MainScreen()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(home)
    widget.showMaximized()
eventFilter = InactivityTimer(lockScreen)
app.installEventFilter(eventFilter)
try:
    sys.exit(app.exec())
except:
    print("Exiting")
