# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 09:18:06 2025

@author: laure
"""
import hospitalDB
import psycopg2
import sys
import pandas as pd
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QPushButton, QLabel, QFormLayout, QSizePolicy, QFrame, QHBoxLayout, QGroupBox, QMessageBox, QListWidget
from PyQt5.QtCore import QTimer, QEvent, QObject, QRect
import string
import EncryptionKey
import SearchDB

class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("MainScreen.ui", self)
        self.enterApplication.clicked.connect(self.openLogin)

    def openLogin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login1.ui", self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        user = self.userField.text()
        password = self.passwordField.text()

        if len(user) == 0 or len(password) == 0:
            self.errorMsg.setText("Missing field.")
        else:
            keys = EncryptionKey.getKeys()
            encryption_key = keys[0]
            fixed_salt = keys[1]
            result_pass = hospitalDB.userLogin(user, password, fixed_salt)
            if result_pass:
                self.errorMsg.setText("")
                userType = hospitalDB.getCurrentUserType()
                current_user_id = hospitalDB.getCurrentUserID()
                if userType == "Administrator":
                    self.gotoadmin()
                else:
                    self.gotosearch()
            else:
                self.errorMsg.setText("Invalid username or password")

    def gotosearch(self):
        search = SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def gotoadmin(self):
        admin=AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex()+1)
class AdminScreen(QDialog):
    def __init__(self):
        super(AdminScreen,self).__init__()
        loadUi("admin.ui",self)
        self.insStaff.clicked.connect(self.insertStaffFunction)
        self.insPat.clicked.connect(self.insertPatientFunction)
        self.searchStaff.clicked.connect(self.searchStaffFunction)
        self.searchPatient.clicked.connect(self.searchPatFunction)

    def insertStaffFunction(self):
        insertStaff=InsertStaff()
        widget.addWidget(insertStaff)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def insertPatientFunction(self):
        insertPatient=InsertPatient()
        widget.addWidget(insertPatient)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def searchStaffFunction(self):
        searchStaff=SearchStaff()
        widget.addWidget(searchStaff)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def searchPatFunction(self):
        search=SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex()+1)

class InsertStaff(QDialog):
    def __init__(self):
        super(InsertStaff,self).__init__()
        loadUi("insertstaff.ui",self)
        self.backTo.clicked.connect(self.toAdmin)
        self.addStaff.clicked.connect(self.addStaff)
    def addStaff(self):
        for i in range(0,5):
            firstName=self.tableWidget.item(i, 0)
            lastName=self.tableWidget.item(i,0)
            username = self.tableWidget.item(i,0)
            password = self.tableWidget.item(i,0)
            staffType = self.tableWidget.item(i,0)
            #do sql stuff here
            self.insertStaffFunction()
    #takes you back to add staff screen where user can go back to admin/add more staff if they choose
    def insertStaffFunction(self):
        insertStaff=InsertStaff()
        widget.addWidget(insertStaff)
        widget.setCurrentIndex(widget.currentIndex()+1)            

    def toAdmin(self):
        admin=AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex()+1)
class InsertPatient(QDialog):
    def __init__(self):
        super(InsertPatient,self).__init__()
        loadUi("insertpat.ui",self)
        self.back.clicked.connect(self.toAdmin)
        self.addPatient.clicked.connect(self.addPatient)

    def addPatient(self):
        for i in range(0,15):
            lastName=self.tableWidget.item(i,0)
            firstName=self.tableWidget.item(i,0)
            midInit=self.tableWidget.item(i,0)
            address=self.tableWidget.item(i,0)
            hPhone=self.tableWidget.item(i,0)
            cPhone=self.tableWidget.item(i,0)
            wPhone=self.tableWidget.item(i,0)
            c1Name=self.tableWidget.item(i,0)
            c1Phone=self.tableWidget.item(i,0)
            c2Name=self.tableWidget.item(i,0)
            c2Phone=self.tableWidget.item(i,0)
            doctor=self.tableWidget.item(i,0)
            insurance=self.tableWidget.item(i,0)
            insAcct=self.tableWidget.item(i,0)
            insGNum=self.tableWidget.item(i,0)
            #do sql here
            self.insertPatientFunction()
        #takes you back to insert patient screen where user can add more/go back to admin space    
    def insertPatientFunction(self):
        insertPatient=InsertPatient()
        widget.addWidget(insertPatient)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def toAdmin(self):
        admin=AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex()+1)
class SearchStaff(QDialog):
    def __init__(self):
        super(SearchStaff,self).__init__()
        loadUi("stafflookup.ui",self)
        self.search.clicked.connect(self.searchfunction)
        self.logout.clicked.connect(self.logoutfxn)
        self.resultsTable.hide()

    def logoutfxn(self):
        hospitalDB.userLogout()
        login=LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def searchfunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        firstBox = self.firstBox.isChecked()
        lastBox = self.lastBox.isChecked()
        partials = {}
        if len(lastName) == 0 and len(firstName) == 0:
            self.error.setText("Input at least one field.")
        else:
            keys = EncryptionKey.getKeys()
            encryption_key = keys[0]
            fixed_salt = keys[1]
            df = None
            #set a bool value for checkbox and insert checkbox var into SearchDB function params
            checkbox = False
            #check whether checkbox for last name or first name is checked, and if so, sets checkbox to true
            if lastBox:
                partials.append('lname')
            if firstBox:
                partials.append('fname')
            if firstName and lastName:
                df = pd.DataFrame(SearchDB.searchStaffWithName(firstName, None, lastName, encryption_key, fixed_salt, checkbox))
            else:
                df = pd.DataFrame(SearchDB.searchStaffWithName(firstName, None, None, encryption_key, fixed_salt, checkbox))
                if df.empty:
                    df = pd.DataFrame(SearchDB.searchStaffWithName(None, None, lastName, encryption_key, fixed_salt, checkbox))

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
                self.resultsTable.cellDoubleClicked.connect(self.openStaffDetails)
                self.df = df

    def openStaffDetails(self, row, column):
        staff_id = str(self.df.iat[row, 0])
        details = StaffDetailsScreen(staff_id)
        widget.addWidget(details)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class StaffDetailsScreen(QDialog):
    def __init__(self, staff_id):
        super(PatientDetailsScreen, self).__init__()
        self.setWindowTitle("Staff Details")
        self.setGeometry(100, 100, 800, 600)

class SearchScreen(QDialog):
    def __init__(self):
        super(SearchScreen, self).__init__()
        loadUi("patientsearch.ui", self)
        self.showMaximized()
        
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
        self.search.clicked.connect(self.searchfunction)
        self.logout.clicked.connect(LogOut)
        self.resultsTable.hide()

    def centerUI(self, screen_width, screen_height):
        """Center all UI elements properly"""
        # Center the title
        title_width = 401  # From original UI
        self.label.setGeometry((screen_width - title_width) // 2, 170, title_width, 61)
        
        # Position logout button in top right
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        
        # Center the form grid
        form_width = 600  # Increased width for better alignment
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
        table_width = min(screen_width - 100, 1000)  # Limit width with padding
        table_height = min(screen_height - 600, 400)  # Limit height with padding
        table_x = (screen_width - table_width) // 2  # Center horizontally
        self.resultsTable.setGeometry(table_x, 550, table_width, table_height)
        self.resultsTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def searchfunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        middleInitial = self.midField.text()
        lastBox = self.lastBox.isChecked()
        firstBox = self.firstBox.isChecked()
        partials = set()
        
        if len(lastName) == 0 and len(firstName) == 0 and len(middleInitial) == 0:
            self.error.setText("Input at least one field.")
        else:
            keys = EncryptionKey.getKeys()
            encryption_key = keys[0]
            fixed_salt = keys[1]
            df = None
            #set a bool value for checkbox and insert checkbox var into SearchDB function params
            #check whether checkbox for last name or first name is checked, and if so, sets checkbox to true
            if firstBox:
                partials.add('fname')
            if lastBox:
                partials.add('lname')
            df = pd.DataFrame(SearchDB.searchPatientWithName(fixed_salt, 
                                                            fname=firstName if firstName else None,
                                                            mname=middleInitial if middleInitial else None,
                                                            lname=lastName if lastName else None,
                                                            partial_fields=partials))
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


class PatientDetailsScreen(QDialog):
    def __init__(self, patient_id):
        super(PatientDetailsScreen, self).__init__()
        self.setWindowTitle("Patient Details")
        self.setGeometry(100, 100, 900, 700)
        self.patient_id = patient_id
        self.usertype = hospitalDB.getCurrentUserType()
        
        layout = QVBoxLayout()
        
        # Create a header with patient info
        self.header_frame = QFrame()
        self.header_layout = QHBoxLayout()
        self.patient_info_label = QLabel()
        self.patient_info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.header_layout.addWidget(self.patient_info_label)
        self.header_frame.setLayout(self.header_layout)
        layout.addWidget(self.header_frame)
        
        # Create tabs - different tabs will be shown based on user type
        self.tabs = QTabWidget()
        
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
        """Configure tabs based on user type"""
        if self.usertype == "Volunteer":
            self.tabs.addTab(self.basic_info_tab, "Patient Info")
            self.tabs.addTab(self.location_tab, "Location")
            self.tabs.addTab(self.visitors_tab, "Approved Visitors")
            
        elif self.usertype == "Office Staff":
            self.tabs.addTab(self.basic_info_tab, "Basic Info")
            self.tabs.addTab(self.insurance_tab, "Insurance")
            self.tabs.addTab(self.contacts_tab, "Contacts")
            
        elif self.usertype in ["Medical Personnel", "Physician"]:
            self.tabs.addTab(self.basic_info_tab, "Basic Info")
            self.tabs.addTab(self.admissions_tab, "Admissions")
            self.tabs.addTab(self.notes_tab, "Notes")
            self.tabs.addTab(self.medications_tab, "Medications")
            self.tabs.addTab(self.procedures_tab, "Procedures")
            
    def loadPatientData(self):
        try:
            # Get data using the new search function
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            
            if not patient_data or len(patient_data) == 0:
                QMessageBox.warning(self, "No Data", "No patient data found.")
                return
                
            # Process data based on user type
            if self.usertype == "Volunteer":
                self.loadVolunteerData(patient_data[0])
            elif self.usertype == "Office Staff":
                self.loadOfficeStaffData(patient_data[0])
            elif self.usertype in ["Medical Personnel", "Physician"]:
                self.loadMedicalData(patient_data[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading patient data: {str(e)}")
            print(f"Error: {e}")
    
    def loadVolunteerData(self, data):
        """Load data for Volunteer view"""
        # Volunteer view has: patient_id, first_name, middle_name, last_name, 
        # facility, floor, room_number, bed_number, visitors
        
        # Set header
        name = f"{data[1]} {data[2] or ''} {data[3]}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data[1] or ""))
        basic_layout.addRow("Middle Name:", QLabel(data[2] or ""))
        basic_layout.addRow("Last Name:", QLabel(data[3] or ""))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Location Tab
        location_layout = QFormLayout()
        location_layout.addRow("Facility:", QLabel(data[4] or ""))
        location_layout.addRow("Floor:", QLabel(str(data[5] or "")))
        location_layout.addRow("Room Number:", QLabel(str(data[6] or "")))
        location_layout.addRow("Bed Number:", QLabel(str(data[7] or "")))
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
        
        # Set header
        name = f"{data[1]} {data[2] or ''} {data[3]}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data[1] or ""))
        basic_layout.addRow("Middle Name:", QLabel(data[2] or ""))
        basic_layout.addRow("Last Name:", QLabel(data[3] or ""))
        basic_layout.addRow("Mailing Address:", QLabel(data[4] or ""))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Insurance Tab
        insurance_layout = QFormLayout()
        insurance_layout.addRow("Insurance Carrier:", QLabel(data[5] or ""))
        insurance_layout.addRow("Account Number:", QLabel(data[6] or ""))
        insurance_layout.addRow("Group Number:", QLabel(data[7] or ""))
        self.insurance_tab.setLayout(insurance_layout)
        
        # Contacts Tab
        contacts_layout = QVBoxLayout()
        
        # Phone numbers
        phone_group = QGroupBox("Phone Numbers")
        phone_layout = QFormLayout()
        phone_layout.addRow("Home Phone:", QLabel(data[8] or ""))
        phone_layout.addRow("Work Phone:", QLabel(data[9] or ""))
        phone_layout.addRow("Mobile Phone:", QLabel(data[10] or ""))
        phone_group.setLayout(phone_layout)
        contacts_layout.addWidget(phone_group)
        
        # Emergency contacts
        ec_group = QGroupBox("Emergency Contacts")
        ec_layout = QFormLayout()
        ec_layout.addRow("Contact 1 Name:", QLabel(data[11] or ""))
        ec_layout.addRow("Contact 1 Phone:", QLabel(data[12] or ""))
        ec_layout.addRow("Contact 2 Name:", QLabel(data[13] or ""))
        ec_layout.addRow("Contact 2 Phone:", QLabel(data[14] or ""))
        ec_group.setLayout(ec_layout)
        contacts_layout.addWidget(ec_group)
        
        self.contacts_tab.setLayout(contacts_layout)
    
    def loadMedicalData(self, data):
        """Load data for Medical Personnel and Physician view"""
        # Medical view has: patient_id, first_name, middle_name, last_name, admissions
        # where admissions is a JSON array containing all admissions with notes, prescriptions, procedures
        
        # Set header
        name = f"{data[1]} {data[2] or ''} {data[3]}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data[1] or ""))
        basic_layout.addRow("Middle Name:", QLabel(data[2] or ""))
        basic_layout.addRow("Last Name:", QLabel(data[3] or ""))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Process admissions data which is in position 4
        admissions = data[4] if len(data) > 4 else []
        
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
                if discharge:
                    display_text += f" (Discharged: {discharge})"
                
                admissions_list.addItem(display_text)
            
            admissions_layout.addWidget(admissions_list)
        else:
            admissions_layout.addWidget(QLabel("No admissions found"))
        self.admissions_tab.setLayout(admissions_layout)
        
        # Notes Tab
        notes_layout = QVBoxLayout()
        all_notes = []
        
        for admission in admissions:
            if 'details' in admission and 'notes' in admission['details']:
                for note in admission['details']['notes']:
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
        
        # Medications Tab
        medications_layout = QVBoxLayout()
        all_meds = []
        
        for admission in admissions:
            if 'details' in admission and 'prescriptions' in admission['details']:
                for med in admission['details']['prescriptions']:
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
                for proc in admission['details']['procedures']:
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
    
    def printPatientDetails(self):
        """Print patient details to a file"""
        try:
            # Get the patient data again
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            
            if not patient_data or len(patient_data) == 0:
                QMessageBox.warning(self, "No Data", "No patient data to print.")
                return
            
            data = patient_data[0]
            lines = []
            lines.append("PATIENT DETAILS REPORT")
            lines.append("=" * 50)
            
            # Format based on user type
            if self.usertype == "Volunteer":
                name = f"{data[1]} {data[2] or ''} {data[3]}"
                lines.append(f"Patient: {name}")
                lines.append(f"Location: {data[4]}, Floor {data[5]}, Room {data[6]}, Bed {data[7]}")
                lines.append("\nApproved Visitors:")
                if data[8] and len(data[8]) > 0:
                    for visitor in data[8]:
                        lines.append(f"- {visitor}")
                else:
                    lines.append("No approved visitors")
                    
            elif self.usertype == "Office Staff":
                name = f"{data[1]} {data[2] or ''} {data[3]}"
                lines.append(f"Patient: {name}")
                lines.append(f"Mailing Address: {data[4] or 'Not provided'}")
                lines.append("\nInsurance Information:")
                lines.append(f"Carrier: {data[5] or 'Not provided'}")
                lines.append(f"Account #: {data[6] or 'Not provided'}")
                lines.append(f"Group #: {data[7] or 'Not provided'}")
                lines.append("\nPhone Numbers:")
                lines.append(f"Home: {data[8] or 'Not provided'}")
                lines.append(f"Work: {data[9] or 'Not provided'}")
                lines.append(f"Mobile: {data[10] or 'Not provided'}")
                lines.append("\nEmergency Contacts:")
                lines.append(f"Contact 1: {data[11] or 'Not provided'} - {data[12] or 'Not provided'}")
                lines.append(f"Contact 2: {data[13] or 'Not provided'} - {data[14] or 'Not provided'}")
                
            elif self.usertype in ["Medical Personnel", "Physician"]:
                name = f"{data[1]} {data[2] or ''} {data[3]}"
                lines.append(f"Patient: {name}")
                
                admissions = data[4] if len(data) > 4 else []
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
                        if discharge:
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
            
            # Write to file
            filename = f"patient_{self.patient_id}_details.txt"
            with open(filename, 'w') as f:
                f.write("\n".join(lines))
            
            QMessageBox.information(self, "Success", f"Patient details saved to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error printing patient data: {str(e)}")
            print(f"Error: {e}")
    
    def goBack(self):
        # Navigate back to the search screen
        current_index = widget.currentIndex()
        current_widget = widget.widget(current_index)
        widget.removeWidget(current_widget)
        current_widget.deleteLater()
        search_screen = SearchScreen()
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.count() - 1)

class ListScreen(QDialog):
    def __init__(self):
        super(ListScreen, self).__init__()
        loadUi("list.ui", self)


def LogOut():
    hospitalDB.userLogout()
    home = MainScreen()
    widget.addWidget(home)
    widget.setCurrentIndex(widget.currentIndex() + 1)

app = QApplication(sys.argv)
app.setStyleSheet("""
    QWidget {
        font-size: 16px;
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
login = LoginScreen()
home = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
#widget.resize(1200, 800)
widget.showMaximized()
try:
    sys.exit(app.exec())
except:
    print("Exiting")