# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 09:18:06 2025

@author: laure
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QTabWidget, QWidget, QFormLayout, QApplication
from PyQt5.QtCore import QObject, QTimer, QEvent
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
import sys
import EncryptionKey
import SearchDB

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
            info_layout.addRow("First Name:", QLabel(str(patientData[0])))
            info_layout.addRow("Middle Name:", QLabel(str(patientData[1])))
            info_layout.addRow("Last Name:", QLabel(str(patientData[2])))
            info_layout.addRow("Mailing Address:", QLabel(str(patientData[3])))
            info_layout.addRow(QLabel("<b>Doctor Info</b>"))
            info_layout.addRow("Doctor Username:", QLabel(str(doctorUsername[0])))
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
        search_screen = QDialog()
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.count() - 1)

class InactivityMonitor(QObject):
    def __init__(self, timeout=30000, callback=None, parent=None):
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
            print("User activity detected. Resetting timer.")
            self.timer.start()
        return False

def LogOut():
    print("User inactive. Logging out...")
    while widget.count() > 1:
        widget.removeWidget(widget.widget(1))
    widget.setCurrentIndex(0)

app = QApplication(sys.argv)
monitor = InactivityMonitor(timeout=30000, callback=LogOut)
app.installEventFilter(monitor)
widget = QtWidgets.QStackedWidget()
login_screen = QDialog()
loadUi("login1.ui", login_screen)
widget.addWidget(login_screen)
widget.resize(1200, 800)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")
