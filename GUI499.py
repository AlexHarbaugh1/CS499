# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 09:18:06 2025

@author: laure
"""

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
            result_pass = SearchDB.passwordMatch(user, password, fixed_salt)
            if result_pass:
                self.errorMsg.setText("")
                self.gotosearch()
            else:
                self.errorMsg.setText("Invalid username or password")

    def gotosearch(self):
        search = SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class SearchScreen(QDialog):
    def __init__(self):
        super(SearchScreen, self).__init__()
        loadUi("patientsearch.ui", self)
        self.search.clicked.connect(self.searchfunction)
        self.logout.clicked.connect(LogOut)
        monitor = InactivityMonitor(timeout=3000, callback=LogOut)
        app.installEventFilter(monitor)
        self.resultsTable.hide()

    def searchfunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()

        if len(lastName) == 0 and len(firstName) == 0:
            self.error.setText("Input at least one field.")
        else:
            keys = EncryptionKey.getKeys()
            encryption_key = keys[0]
            fixed_salt = keys[1]
            df = None
            if firstName and lastName:
                df = pd.DataFrame(SearchDB.searchPatientWithName(firstName, None, lastName, encryption_key, fixed_salt, True))
            else:
                df = pd.DataFrame(SearchDB.searchPatientWithName(firstName, None, None, encryption_key, fixed_salt, True))
                if df.empty:
                    df = pd.DataFrame(SearchDB.searchPatientWithName(None, None, lastName, encryption_key, fixed_salt, True))

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

    def gotolist(self):
        plist = ListScreen()
        widget.addWidget(plist)
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

class InactivityMonitor(QObject):
    def __init__(self, timeout=300000, callback=None, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.timer = QTimer(self)
        self.timer.setInterval(timeout)
        self.timer.timeout.connect(self.handleTimeout)
        self.timer.start()

    def handleTimeout(self):
        if self.callback:
            self.callback()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseMove, QEvent.KeyPress, QEvent.MouseButtonPress, QEvent.Wheel):
            self.timer.start()
        return super().eventFilter(obj, event)

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
widget.resize(1200, 800)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")
