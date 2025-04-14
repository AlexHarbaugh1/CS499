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
from PyQt5.QtWidgets import (
    QDialog, QApplication, QWidget, QTableWidgetItem, QTabWidget, QVBoxLayout,
    QPushButton, QLabel, QFormLayout, QTextEdit, QComboBox, QMessageBox
)
from PyQt5.QtCore import QTimer, QEvent, QObject
import EncryptionKey
import SearchDB

current_user_id = None

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

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
        self.showMaximized()
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        global current_user_id
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
                #current_user_id = SearchDB.getUserID(user)
               # print("Logged in user ID:", current_user_id)
                self.errorMsg.setText("")
                self.gotoapplication()
            else:
                self.errorMsg.setText("Invalid username or password")

    def gotoapplication(self):
        application = ApplicationScreen()
        widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class ApplicationScreen(QDialog):
    def __init__(self):
        super(ApplicationScreen, self).__init__()
        loadUi("ApplicationScreen.ui", self)
        self.PatientSearch.clicked.connect(self.gotosearch)

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
        self.admissions_tab = QWidget()

        self.tabs.addTab(self.info_tab, "Info")
        self.tabs.addTab(self.insurance_tab, "Insurance")
        self.tabs.addTab(self.contacts_tab, "Contacts")
        self.tabs.addTab(self.notes_tab, "Notes")
        self.tabs.addTab(self.medications_tab, "Medications")
        self.tabs.addTab(self.procedures_tab, "Procedures")
        self.tabs.addTab(self.admissions_tab, "Admissions")

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

            admissions_layout = QVBoxLayout()
            if patientAdmissions:
                for admission in patientAdmissions:
                    admission_id = admission[0]
                    try:
                        ad_data, loc, doc, meds, procs, notes = SearchDB.searchAdmissionWithID(admission_id, keys[0])
                        admit_date, discharge_date, reason = ad_data
                        button_text = f"Admission on {admit_date} (ID: {admission_id})"
                        btn = QPushButton(button_text)
                        btn.clicked.connect(lambda _, aid=admission_id: self.openAdmissionDetails(aid))
                        admissions_layout.addWidget(btn)
                    except Exception as e:
                        admissions_layout.addWidget(QLabel(f"Error loading admission {admission_id}: {e}"))
            else:
                admissions_layout.addWidget(QLabel("No admission records found."))
            self.admissions_tab.setLayout(admissions_layout)

        except Exception as e:
            print(f"Error loading patient data: {e}")

    def openAdmissionDetails(self, admission_id):
        details_window = AdmissionDetailWindow(admission_id)
        details_window.exec_()

    def printPatientDetails(self, patient_id):
        # Implementation can mirror the earlier print logic
        pass

    def goBack(self):
        current_index = widget.currentIndex()
        current_widget = widget.widget(current_index)
        widget.removeWidget(current_widget)
        current_widget.deleteLater()
        search_screen = SearchScreen()
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.count() - 1)

class AdmissionDetailWindow(QDialog):
    def __init__(self, admission_id):
        super(AdmissionDetailWindow, self).__init__()
        self.setWindowTitle(f"Admission Details - ID {admission_id}")
        self.setGeometry(150, 150, 600, 500)

        layout = QVBoxLayout()
        tabs = QTabWidget()

        self.notes_tab = QWidget()
        self.medications_tab = QWidget()
        self.procedures_tab = QWidget()
        self.billing_tab = QWidget()

        tabs.addTab(self.billing_tab, "Billing")
        tabs.addTab(self.notes_tab, "Notes")
        tabs.addTab(self.medications_tab, "Medications")
        tabs.addTab(self.procedures_tab, "Procedures")

        layout.addWidget(tabs)
        self.setLayout(layout)

        self.loadAdmissionData(admission_id)

    def insertNote(self, admission_id):
        note_type = self.note_type_select.currentText()
        note_text = self.new_note_text.toPlainText()
        if note_text.strip():
            if current_user_id:
                SearchDB.insertPatientNote(admission_id, current_user_id, note_type, note_text)
                QMessageBox.information(self, "Success", "Note added.")
                self.new_note_text.clear()
                self.loadAdmissionData(admission_id)
            else:
                QMessageBox.warning(self, "Error", "No logged-in user found.")
        else:
            QMessageBox.warning(self, "Error", "Note text cannot be empty.")

    def loadAdmissionData(self, admission_id):
        keys = EncryptionKey.getKeys()
        try:
            ad_data, loc, doc, meds, procs, notes = SearchDB.searchAdmissionWithID(admission_id, keys[0])

            notes_layout = QVBoxLayout()
            clearLayout(self.notes_tab.layout())
            self.notes_tab.setLayout(notes_layout)
            for n in notes:
                author = f"{n[0]} {n[1]}"
                note_type = n[2]
                text = n[3]
                time = n[4]
                notes_layout.addWidget(QLabel(f"{note_type} by {author} on {time}: {text}"))

            self.note_type_select = QComboBox()
            self.note_type_select.addItems(["Doctor", "Nurse"])
            self.new_note_text = QTextEdit()
            submit_btn = QPushButton("Add Note")
            submit_btn.clicked.connect(lambda: self.insertNote(admission_id))

            notes_layout.addWidget(QLabel("Add a new note:"))
            notes_layout.addWidget(self.note_type_select)
            notes_layout.addWidget(self.new_note_text)
            notes_layout.addWidget(submit_btn)

            meds_layout = QVBoxLayout()
            for med in meds:
                meds_layout.addWidget(QLabel(f"{med[0]} - {med[1]} ({med[2]})"))
            self.medications_tab.setLayout(meds_layout)

            procs_layout = QVBoxLayout()
            for proc in procs:
                procs_layout.addWidget(QLabel(f"{proc[0]} at {proc[1]}"))
            self.procedures_tab.setLayout(procs_layout)

            billing_layout = QVBoxLayout()
            clearLayout(self.billing_tab.layout())
            summary, details = SearchDB.getBillingSummaryAndDetails(admission_id)
            if summary:
                owed, paid, insurance = summary
                billing_layout.addWidget(QLabel(f"Total Amount Owed: ${owed:.2f}"))
                billing_layout.addWidget(QLabel(f"Total Amount Paid: ${paid:.2f}"))
                billing_layout.addWidget(QLabel(f"Insurance Paid: ${insurance:.2f}"))
                billing_layout.addWidget(QLabel("Itemized Charges:"))
                for desc, amount in details:
                    billing_layout.addWidget(QLabel(f"• {desc}: ${amount:.2f}"))
            else:
                billing_layout.addWidget(QLabel("No billing data found for this admission."))
            self.billing_tab.setLayout(billing_layout)

        except Exception as e:
            print(f"Error loading admission details: {e}")

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
        font-size: 20px;
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
        font-size: 20px;
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
home = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
widget.showMaximized()
try:
    sys.exit(app.exec())
except:
    print("Exiting")
