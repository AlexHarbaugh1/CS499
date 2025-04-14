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
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QPushButton, QLabel, QFormLayout
from PyQt5.QtCore import QTimer, QEvent, QObject
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
        self.search.clicked.connect(self.searchfunction)
        self.logout.clicked.connect(LogOut)
        self.resultsTable.hide()

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
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.info_tab = QWidget()
        self.insurance_tab = QWidget()
        self.contacts_tab = QWidget()
        self.notes_tab = QWidget()
        self.medications_tab = QWidget()
        self.procedures_tab = QWidget()

        self.tabs.addTab(self.info_tab, "Info")
        self.tabs.addTab(self.insurance_tab, "Insurance")
        self.tabs.addTab(self.contacts_tab, "Contacts")
        self.tabs.addTab(self.notes_tab, "Notes")
        self.tabs.addTab(self.medications_tab, "Medications")
        self.tabs.addTab(self.procedures_tab, "Procedures")

        layout.addWidget(self.tabs)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.goBack)
        layout.addWidget(self.back_button)

        self.print_button = QPushButton("Print to File")
        self.print_button.clicked.connect(lambda: self.printPatientDetails(patient_id))
        layout.addWidget(self.print_button)

        self.setLayout(layout)

        self.loadPatientData(patient_id)

    def loadPatientData(self, patient_id):
        keys = EncryptionKey.getKeys()
        try:
            result = SearchDB.searchPatientWithID(patient_id, keys[0])
            if not result:
                return

            (patientData, doctorUsername, patientAdmissions, patientInsurance, phoneNumbers, emergencyContacts, locationInfo, doctorNotes, nurseNotes, prescriptions, procedures) = result

            info_layout = QFormLayout()
            info_layout.setSpacing(10)
            info_layout.setContentsMargins(20, 20, 20, 20)
            info_layout.addRow(QLabel("<b>Patient Information</b>"))
            info_layout.addRow("First Name:", QLabel(patientData[0]))
            info_layout.addRow("Middle Name:", QLabel(patientData[1]))
            info_layout.addRow("Last Name:", QLabel(patientData[2]))
            info_layout.addRow("Mailing Address:", QLabel(patientData[3]))
            info_layout.addRow(QLabel("<b>Doctor Info</b>"))
            info_layout.addRow("Doctor Username:", QLabel(doctorUsername[0]))
            info_layout.addRow("Doctor Name:", QLabel(f"{doctorUsername[1]} {doctorUsername[2]}"))
            if locationInfo:
                info_layout.addRow(QLabel("<b>Room Info</b>"))
                info_layout.addRow("Facility:", QLabel(str(locationInfo[0])))
                info_layout.addRow("Floor:", QLabel(str(locationInfo[1])))
                info_layout.addRow("Room Number:", QLabel(str(locationInfo[2])))
                info_layout.addRow("Bed Number:", QLabel(str(locationInfo[3])))
            self.info_tab.setLayout(info_layout)

            insurance_layout = QVBoxLayout()
            if patientInsurance:
                insurance_fields = [("Carrier", patientInsurance[0]), ("Account #", patientInsurance[1]), ("Group #", patientInsurance[2])]
                for label, value in insurance_fields:
                    insurance_layout.addWidget(QLabel(f"{label}: {value}"))
            else:
                insurance_layout.addWidget(QLabel("No insurance info found."))
            self.insurance_tab.setLayout(insurance_layout)

            contacts_layout = QVBoxLayout()
            if phoneNumbers:
                for phone in phoneNumbers:
                    contacts_layout.addWidget(QLabel(f"{phone[0].capitalize()} Phone: {phone[1]}"))
            else:
                contacts_layout.addWidget(QLabel("No phone numbers found."))
            if emergencyContacts:
                for i, contact in enumerate(emergencyContacts):
                    label = f"Emergency Contact {i + 1}"
                    name, phone = contact
                    contacts_layout.addWidget(QLabel(f"{label}: {name} - {phone}"))
            else:
                contacts_layout.addWidget(QLabel("No emergency contacts found."))
            self.contacts_tab.setLayout(contacts_layout)

            notes_layout = QVBoxLayout()
            if doctorNotes:
                for note in doctorNotes:
                    notes_layout.addWidget(QLabel(f"Doctor Note: {note[0]} (Time: {note[1]})"))
            if nurseNotes:
                for note in nurseNotes:
                    notes_layout.addWidget(QLabel(f"Nurse Note: {note[0]} (Time: {note[1]})"))
            if not doctorNotes and not nurseNotes:
                notes_layout.addWidget(QLabel("No notes found."))
            self.notes_tab.setLayout(notes_layout)

            meds_layout = QVBoxLayout()
            if prescriptions:
                for prescription in prescriptions:
                    meds_layout.addWidget(QLabel(f"Medication: {prescription[0]}, Amount: {prescription[1]}, Schedule: {prescription[2]}"))
            else:
                meds_layout.addWidget(QLabel("No prescriptions found."))
            self.medications_tab.setLayout(meds_layout)

            procedures_layout = QVBoxLayout()
            if procedures:
                for procedure in procedures:
                    procedures_layout.addWidget(QLabel(f"Procedure: {procedure[0]} at {procedure[1]}"))
            else:
                procedures_layout.addWidget(QLabel("No procedures found."))
            self.procedures_tab.setLayout(procedures_layout)

        except Exception as e:
            print(f"Error loading patient data: {e}")

    def printPatientDetails(self, patient_id):
        keys = EncryptionKey.getKeys()
        result = SearchDB.searchPatientWithID(patient_id, keys[0])
        if not result:
            return

        (patientData, doctorUsername, patientAdmissions, patientInsurance, phoneNumbers, emergencyContacts, locationInfo, doctorNotes, nurseNotes, prescriptions, procedures) = result

        lines = []
        lines.append("Patient Details")
        lines.append(f"Name: {patientData[0]} {patientData[1]} {patientData[2]}")
        lines.append(f"Address: {patientData[3]}")
        lines.append(f"Doctor: {doctorUsername[1]} {doctorUsername[2]} ({doctorUsername[0]})")
        if locationInfo:
            lines.append(f"Location: {locationInfo[0]}, Floor {locationInfo[1]}, Room {locationInfo[2]}, Bed {locationInfo[3]}")
        if patientInsurance:
            lines.append(f"Insurance: {patientInsurance[0]}, Account #: {patientInsurance[1]}, Group #: {patientInsurance[2]}")
        if phoneNumbers:
            for phone in phoneNumbers:
                lines.append(f"{phone[0]} Phone: {phone[1]}")
        if emergencyContacts:
            for contact in emergencyContacts:
                lines.append(f"Emergency Contact: {contact[0]} - {contact[1]}")
        if doctorNotes:
            for note in doctorNotes:
                lines.append(f"Doctor Note: {note[0]} (Time: {note[1]})")
        if nurseNotes:
            for note in nurseNotes:
                lines.append(f"Nurse Note: {note[0]} (Time: {note[1]})")
        if prescriptions:
            for med in prescriptions:
                lines.append(f"Medication: {med[0]} {med[1]} ({med[2]})")
        if procedures:
            for proc in procedures:
                lines.append(f"Procedure: {proc[0]} at {proc[1]}")

        filename = f"patient_details_{patient_id}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(lines))
        print(f"Patient details written to {filename}\n")

    def goBack(self):
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