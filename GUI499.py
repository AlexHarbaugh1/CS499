# -*- coding: utf-8 -*-
"""
Merged GUI499.py - Part 1
"""

import hospitalDB
import InsertData
import UpdateDB
import psycopg2
import sys
import traceback
import pandas as pd
from InactivityTimer import InactivityTimer
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QDialog, QApplication, QWidget, QTableWidgetItem, QTabBar, QTabWidget,
    QVBoxLayout, QPushButton, QLabel, QFormLayout, QSizePolicy, QFrame,
    QHBoxLayout, QGroupBox, QMessageBox, QListWidget, QLineEdit, QComboBox, QTextEdit
)
from PyQt5.QtCore import QTimer, QEvent, QObject, QRect, Qt, QDateTime
import string
import EncryptionKey
import SearchDB

keys = EncryptionKey.getKeys()
encryption_key = keys[0]
fixed_salt = keys[1]

class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("MainScreen.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)
        self.styleElements()
        self.enterApplication.clicked.connect(self.openLogin)

    def centerUI(self, screen_width, screen_height):
        label_width = 600
        self.label_3.setGeometry((screen_width - label_width) // 2,
                                 screen_height // 3,
                                 label_width, 100)

        button_width = 250
        button_height = 60
        self.enterApplication.setGeometry((screen_width - button_width) // 2,
                                          (screen_height // 2) + 50,
                                          button_width, button_height)

    def styleElements(self):
        self.label_3.setStyleSheet("""
            font: bold 24pt "MS Shell Dlg 2";
            color: #333333;
        """)
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

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login1.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)
        self.styleElements()

        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def centerUI(self, screen_width, screen_height):
        container_width = 400
        container_height = 350
        container_x = (screen_width - container_width) // 2
        container_y = (screen_height - container_height) // 2
        field_height = 40
        label_width = 120
        field_width = 250
        spacing = 20

        self.label.setGeometry(container_x, container_y, container_width, 60)

        self.labelUser.setGeometry(container_x,
                                   container_y + 90,
                                   label_width, field_height)
        self.userField.setGeometry(container_x + label_width + 10,
                                   container_y + 90,
                                   field_width, field_height)

        self.labelPass.setGeometry(container_x,
                                   container_y + 90 + field_height + spacing,
                                   label_width, field_height)
        self.passwordField.setGeometry(container_x + label_width + 10,
                                       container_y + 90 + field_height + spacing,
                                       field_width, field_height)

        button_width = 150
        button_height = 50
        self.login.setGeometry((screen_width - button_width) // 2,
                               container_y + 90 + (field_height + spacing) * 2 + 20,
                               button_width, button_height)

        error_width = 400
        self.errorMsg.setGeometry((screen_width - error_width) // 2,
                                  container_y + 90 + (field_height + spacing) * 2 + 20 + button_height + 20,
                                  error_width, 30)

    def styleElements(self):
        self.label.setStyleSheet("""
            font: bold 36pt "MS Shell Dlg 2";
            color: #333333;
            padding-bottom: 20px;
        """)
        self.label.setAlignment(Qt.AlignCenter)

        for label in [self.labelUser, self.labelPass]:
            label.setStyleSheet("""
                font: 14pt "MS Shell Dlg 2";
                padding-right: 10px;
            """)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for field in [self.userField, self.passwordField]:
            field.setStyleSheet("""
                font: 12pt "MS Shell Dlg 2";
                border: 1px solid #aaa;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            """)
            field.setMinimumHeight(40)

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
        loadUi("ApplicationScreen.ui", self)
        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)

        self.usertype = hospitalDB.getCurrentUserType()
        self.configureButtonVisibility()
        self.connectButtons()
        self.styleButtons()

    def centerUI(self, screen_width, screen_height):
        title_width = 600
        self.label.setGeometry((screen_width - title_width) // 2, 120, title_width, 61)
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)

        grid_width = 700
        grid_height = 400
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 260, grid_width, grid_height)

    def configureButtonVisibility(self):
        self.PatientSearch.setVisible(True)
        self.RegisterPatient.setVisible(self.usertype in ["Medical Personnel", "Physician", "Office Staff"])
        self.RegisterAdmission.setVisible(self.usertype in ["Medical Personnel", "Physician"])

    def connectButtons(self):
        self.PatientSearch.clicked.connect(self.goToPatientSearch)
        self.RegisterPatient.clicked.connect(self.goToRegisterPatient)
        self.RegisterAdmission.clicked.connect(self.goToRegisterAdmission)
        self.logout.clicked.connect(self.logoutFunction)

    def styleButtons(self):
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
        for button in [self.PatientSearch, self.RegisterPatient, self.RegisterAdmission]:
            button.setStyleSheet(button_style)
            button.setMinimumHeight(60)
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
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class AdminScreen(QDialog):
    def __init__(self):
        super(AdminScreen, self).__init__()
        loadUi("admin.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)

        self.insStaff.clicked.connect(self.insertStaffFunction)
        self.insPat.clicked.connect(self.insertPatientFunction)
        self.searchStaff.clicked.connect(self.searchStaffFunction)
        self.searchPatient.clicked.connect(self.searchPatFunction)
        self.regLocation.clicked.connect(self.registerLocationFunction)
        self.regAdmission.clicked.connect(self.registerAdmissionFunction)
        self.logout.clicked.connect(self.logoutFunction)

        self.styleButtons()

    def centerUI(self, screen_width, screen_height):
        title_width = 600
        self.label.setGeometry((screen_width - title_width) // 2, 120, title_width, 61)
        self.label_2.setGeometry((screen_width - title_width) // 2, 200, title_width, 41)
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)

        grid_width = 700
        grid_height = 400
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 260, grid_width, grid_height)

    def styleButtons(self):
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
        for button in [self.insStaff, self.insPat, self.searchStaff, self.searchPatient,
                       self.regLocation, self.regAdmission]:
            button.setStyleSheet(button_style)
            button.setMinimumHeight(60)
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

    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class InsertStaff(QDialog):
    def __init__(self):
        super(InsertStaff, self).__init__()
        loadUi("insertstaff.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)
        self.staffTypeCombo.addItems(["", "Administrator", "Medical Personnel", "Physician", "Volunteer", "Office Staff"])

        self.backTo.clicked.connect(self.goBack)
        self.addStaff.clicked.connect(self.addStaffMember)

        for field in [self.firstNameField, self.lastNameField, self.usernameField, self.passwordField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

        self.staffTypeCombo.setMinimumHeight(35)
        self.staffTypeCombo.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.backTo.setGeometry(50, 70, 120, 40)

        form_width = 600
        form_height = 350
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)

        button_width = 200
        button_height = 50
        self.addStaff.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)

        error_width = 600
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def addStaffMember(self):
        firstName = self.firstNameField.text()
        lastName = self.lastNameField.text()
        username = self.usernameField.text()
        password = self.passwordField.text()
        staffType = self.staffTypeCombo.currentText()

        if not firstName or not lastName or not username or not password or not staffType:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return
        try:
            InsertData.insertStaff(firstName, lastName, username, password, staffType, fixed_salt)
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText(f"Staff member {firstName} {lastName} added successfully!")
            self.firstNameField.clear()
            self.lastNameField.clear()
            self.usernameField.clear()
            self.passwordField.clear()
            self.staffTypeCombo.setCurrentIndex(0)
        except psycopg2.errors.UniqueViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Username already exists.")
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")

    def goBack(self):
        admin = AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class InsertPatient(QDialog):
    def __init__(self):
        super(InsertPatient, self).__init__()
        loadUi("insertpat.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)
        self.populateDoctors()

        self.back.clicked.connect(self.goBack)
        self.addPatient.clicked.connect(self.addPatientData)

        self.firstNameField.setStyleSheet("border: 1px solid red;")
        self.lastNameField.setStyleSheet("border: 1px solid red;")

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.back.setGeometry(50, 70, 120, 40)
        note_width = 400
        self.requiredNote.setGeometry((screen_width - note_width) // 2, 140, note_width, 20)

        grid_width = min(900, screen_width - 100)
        grid_height = min(550, screen_height - 250)
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 170, grid_width, grid_height)

        button_width = 200
        button_height = 50
        button_y = 170 + grid_height + 10
        self.addPatient.setGeometry((screen_width - button_width) // 2, button_y, button_width, button_height)

        error_width = 600
        error_y = button_y + button_height + 10
        self.errorMsg.setGeometry((screen_width - error_width) // 2, error_y, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def populateDoctors(self):
        try:
            doctors = SearchDB.getDoctors(encryption_key)
            self.doctorCombo.addItem("", "")
            if doctors and doctors != "Error":
                for doctor in doctors:
                    display_text = f"{doctor[0]} - {doctor[3]}, {doctor[2]}"
                    self.doctorCombo.addItem(display_text, doctor[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")

    def addPatientData(self):
        if not self.firstNameField.text().strip() or not self.lastNameField.text().strip():
            self.errorMsg.setText("First and last name are required.")
            return
        try:
            firstName = self.firstNameField.text()
            middleInit = self.middleInitField.text()
            lastName = self.lastNameField.text()
            address = self.addressField.text()
            doctorIndex = self.doctorCombo.currentIndex()
            doctorID = self.doctorCombo.itemData(doctorIndex) if doctorIndex > 0 else None
            InsertData.insertPatient(firstName, middleInit, lastName, address, doctorID, fixed_salt)

            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT MAX(patient_id) FROM patient;")
                patientID = cursor.fetchone()[0]

            for kind, field in [("Home", self.homePhoneField), ("Mobile", self.cellPhoneField), ("Work", self.workPhoneField)]:
                phone = field.text()
                if phone:
                    UpdateDB.patientUpdatePhone(patientID, kind, phone)

            if self.contact1NameField.text() and self.contact1PhoneField.text():
                UpdateDB.patientUpdateContact(patientID, self.contact1NameField.text(), self.contact1PhoneField.text(), "1")
            if self.contact2NameField.text() and self.contact2PhoneField.text():
                UpdateDB.patientUpdateContact(patientID, self.contact2NameField.text(), self.contact2PhoneField.text(), "2")

            UpdateDB.patientUpdateInsurance(patientID, self.insuranceField.text(),
                                            self.accountNumberField.text(), self.groupNumberField.text())

            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText(f"Patient {firstName} {lastName} added successfully!")
            self.clearFields()
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")

    def clearFields(self):
        for field in [self.firstNameField, self.middleInitField, self.lastNameField, self.addressField,
                      self.homePhoneField, self.cellPhoneField, self.workPhoneField,
                      self.contact1NameField, self.contact1PhoneField,
                      self.contact2NameField, self.contact2PhoneField,
                      self.insuranceField, self.accountNumberField, self.groupNumberField]:
            field.clear()
        self.doctorCombo.setCurrentIndex(0)

    def goBack(self):
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            widget.addWidget(AdminScreen())
        else:
            widget.addWidget(ApplicationScreen())
        widget.setCurrentIndex(widget.currentIndex() + 1)

class RegisterLocation(QDialog):
    def __init__(self):
        super(RegisterLocation, self).__init__()
        loadUi("registerlocation.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)

        self.backTo.clicked.connect(self.goBack)
        self.addLocation.clicked.connect(self.addLocationFunction)

        self.styleFormFields()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.backTo.setGeometry(50, 70, 120, 40)

        form_width = 600
        form_height = 350
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)

        button_width = 200
        button_height = 50
        self.addLocation.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)

        error_width = 600
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def styleFormFields(self):
        self.facilityField.setMinimumHeight(35)
        self.facilityField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.roomField.setMinimumHeight(35)
        self.roomField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.bedField.setMinimumHeight(35)
        self.bedField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.floorField.setMinimumHeight(35)
        self.floorField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

    def addLocationFunction(self):
        facility = self.facilityField.text()
        floor = self.floorField.value()
        room = self.roomField.text()
        bed = self.bedField.text()

        if not facility or not room or not bed:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return

        try:
            InsertData.insertLocation(facility, floor, room, bed)
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText("Location added successfully!")
            self.facilityField.clear()
            self.floorField.setValue(1)
            self.roomField.clear()
            self.bedField.clear()
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")

    def goBack(self):
        admin = AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class RegisterAdmission(QDialog):
    def __init__(self):
        super(RegisterAdmission, self).__init__()
        loadUi("registeradmission.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)
        self.admissionDateTime.setDateTime(QDateTime.currentDateTime())

        self.populatePatients()
        self.populateLocations()
        self.populateDoctors()

        self.backTo.clicked.connect(self.goBack)
        self.addAdmission.clicked.connect(self.addAdmissionFunction)
        self.styleFormFields()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.backTo.setGeometry(50, 70, 120, 40)
        form_width = 600
        form_height = 350
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)
        button_width = 200
        button_height = 50
        self.addAdmission.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)
        error_width = 600
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def styleFormFields(self):
        for combo in [self.patientCombo, self.locationCombo, self.doctorCombo]:
            combo.setMinimumHeight(35)
            combo.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.admissionDateTime.setMinimumHeight(35)
        self.admissionDateTime.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.reasonField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

    def populatePatients(self):
        try:
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT patient_id, first_name, middle_name, last_name FROM patientsearchview ORDER BY last_name;")
                patients = cursor.fetchall()

            self.patientCombo.addItem("", "")
            for patient in patients:
                pid, fname, mname, lname = patient
                display_text = f"{pid} - {lname}, {fname} {mname or ''}"
                self.patientCombo.addItem(display_text, pid)
        except Exception as e:
            self.errorMsg.setText(f"Error loading patients: {str(e)}")

    def populateLocations(self):
        try:
            locations = SearchDB.getAvailableLocations()
            self.locationCombo.addItem("", "")
            for loc in locations:
                loc_id, facility, floor, room, bed = loc
                display_text = f"{loc_id} - {facility}, Floor {floor}, Room {room}, Bed {bed}"
                self.locationCombo.addItem(display_text, loc_id)
        except Exception as e:
            self.errorMsg.setText(f"Error loading locations: {str(e)}")

    def populateDoctors(self):
        try:
            doctors = SearchDB.getDoctors(encryption_key)
            self.doctorCombo.addItem("", "")
            if doctors and doctors != "Error":
                for doc in doctors:
                    display_text = f"{doc[0]} - {doc[3]}, {doc[2]}"
                    self.doctorCombo.addItem(display_text, doc[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")

    def addAdmissionFunction(self):
        patient_index = self.patientCombo.currentIndex()
        patient_id = self.patientCombo.itemData(patient_index) if patient_index > 0 else None
        location_index = self.locationCombo.currentIndex()
        location_id = self.locationCombo.itemData(location_index) if location_index > 0 else None
        doctor_index = self.doctorCombo.currentIndex()
        doctor_id = self.doctorCombo.itemData(doctor_index) if doctor_index > 0 else None
        admission_date = self.admissionDateTime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        reason = self.reasonField.toPlainText()

        if not patient_id or not location_id or not doctor_id or not reason:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return

        try:
            InsertData.insertAdmission(patient_id, location_id, doctor_id, admission_date, reason)
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText("Admission registered successfully!")
            self.patientCombo.setCurrentIndex(0)
            self.doctorCombo.setCurrentIndex(0)
            self.reasonField.clear()
            self.locationCombo.clear()
            self.populateLocations()
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")

    def goBack(self):
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class SearchStaff(QDialog):
    def __init__(self):
        super(SearchStaff, self).__init__()
        loadUi("stafflookup.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)

        for field in [self.lastField, self.firstField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

        for checkbox in [self.lastBox, self.firstBox]:
            checkbox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")

        self.search.clicked.connect(self.searchFunction)
        self.logout.clicked.connect(self.logoutFunction)
        self.backButton.clicked.connect(self.goBack)
        self.resultsTable.hide()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 200, title_width, 71)
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        self.backButton.setGeometry(50, 70, 120, 50)

        form_width = 600
        form_height = 151
        self.gridLayoutWidget.setGeometry((screen_width - form_width) // 2, 290, form_width, form_height)

        error_width = 300
        self.error.setGeometry((screen_width - error_width) // 2, 450, error_width, 31)

        search_width = 151
        search_height = 40
        self.search.setGeometry((screen_width - search_width) // 2, 490, search_width, search_height)

        table_width = min(screen_width - 100, 700)
        table_height = min(screen_height - 600, 500)
        table_x = (screen_width - table_width) // 2
        self.resultsTable.setGeometry(table_x, 550, table_width, table_height)
        self.resultsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.resultsTable.hide()

    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

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
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class InsertPatient(QDialog):
    def __init__(self):
        super(InsertPatient, self).__init__()
        loadUi("insertpat.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        self.centerUI(screen_width, screen_height)

        self.populateDoctors()
        self.back.clicked.connect(self.goBack)
        self.addPatient.clicked.connect(self.addPatientData)
        self.firstNameField.setStyleSheet("border: 1px solid red;")
        self.lastNameField.setStyleSheet("border: 1px solid red;")

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.back.setGeometry(50, 70, 120, 40)
        note_width = 400
        self.requiredNote.setGeometry((screen_width - note_width) // 2, 140, note_width, 20)

        grid_width = min(900, screen_width - 100)
        grid_height = min(550, screen_height - 250)
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 170, grid_width, grid_height)

        button_width = 200
        button_height = 50
        button_y = 170 + grid_height + 10
        self.addPatient.setGeometry((screen_width - button_width) // 2, button_y, button_width, button_height)

        error_width = 600
        error_y = button_y + button_height + 10
        self.errorMsg.setGeometry((screen_width - error_width) // 2, error_y, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def populateDoctors(self):
        try:
            keys = EncryptionKey.getKeys()
            doctors = SearchDB.getDoctors(keys[0])
            self.doctorCombo.addItem("", "")
            if doctors and doctors != "Error":
                for doctor in doctors:
                    display_text = f"{doctor[0]} - {doctor[3]}, {doctor[2]}"
                    self.doctorCombo.addItem(display_text, doctor[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")

    def validateRequiredFields(self):
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
        if not self.validateRequiredFields():
            return
        keys = EncryptionKey.getKeys()
        fixed_salt = keys[1]
        firstName = self.firstNameField.text()
        middleInit = self.middleInitField.text()
        lastName = self.lastNameField.text()
        address = self.addressField.text()
        doctorIndex = self.doctorCombo.currentIndex()
        doctorID = self.doctorCombo.itemData(doctorIndex) if doctorIndex > 0 else None
        try:
            InsertData.insertPatient(firstName, middleInit, lastName, address, doctorID, fixed_salt)
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT MAX(patient_id) FROM patient;")
                patientID = cursor.fetchone()[0]

            homePhone = self.homePhoneField.text()
            cellPhone = self.cellPhoneField.text()
            workPhone = self.workPhoneField.text()
            if homePhone:
                UpdateDB.patientUpdatePhone(patientID, "Home", homePhone)
            if cellPhone:
                UpdateDB.patientUpdatePhone(patientID, "Mobile", cellPhone)
            if workPhone:
                UpdateDB.patientUpdatePhone(patientID, "Work", workPhone)

            contact1Name = self.contact1NameField.text()
            contact1Phone = self.contact1PhoneField.text()
            contact2Name = self.contact2NameField.text()
            contact2Phone = self.contact2PhoneField.text()
            if contact1Name and contact1Phone:
                UpdateDB.patientUpdateContact(patientID, contact1Name, contact1Phone, "1")
            if contact2Name and contact2Phone:
                UpdateDB.patientUpdateContact(patientID, contact2Name, contact2Phone, "2")

            insurance = self.insuranceField.text()
            accountNumber = self.accountNumberField.text()
            groupNumber = self.groupNumberField.text()
            if insurance or accountNumber or groupNumber:
                UpdateDB.patientUpdateInsurance(patientID, insurance, accountNumber, groupNumber)

            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText(f"Patient {firstName} {lastName} added successfully!")
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
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class InsertPatient(QDialog):
    def __init__(self):
        super(InsertPatient, self).__init__()
        loadUi("insertpat.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        self.centerUI(screen_width, screen_height)

        self.populateDoctors()
        self.back.clicked.connect(self.goBack)
        self.addPatient.clicked.connect(self.addPatientData)
        self.firstNameField.setStyleSheet("border: 1px solid red;")
        self.lastNameField.setStyleSheet("border: 1px solid red;")

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.back.setGeometry(50, 70, 120, 40)
        note_width = 400
        self.requiredNote.setGeometry((screen_width - note_width) // 2, 140, note_width, 20)

        grid_width = min(900, screen_width - 100)
        grid_height = min(550, screen_height - 250)
        self.gridLayoutWidget.setGeometry((screen_width - grid_width) // 2, 170, grid_width, grid_height)

        button_width = 200
        button_height = 50
        button_y = 170 + grid_height + 10
        self.addPatient.setGeometry((screen_width - button_width) // 2, button_y, button_width, button_height)

        error_width = 600
        error_y = button_y + button_height + 10
        self.errorMsg.setGeometry((screen_width - error_width) // 2, error_y, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def populateDoctors(self):
        try:
            keys = EncryptionKey.getKeys()
            doctors = SearchDB.getDoctors(keys[0])
            self.doctorCombo.addItem("", "")
            if doctors and doctors != "Error":
                for doctor in doctors:
                    display_text = f"{doctor[0]} - {doctor[3]}, {doctor[2]}"
                    self.doctorCombo.addItem(display_text, doctor[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")

    def validateRequiredFields(self):
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
        if not self.validateRequiredFields():
            return
        keys = EncryptionKey.getKeys()
        fixed_salt = keys[1]
        firstName = self.firstNameField.text()
        middleInit = self.middleInitField.text()
        lastName = self.lastNameField.text()
        address = self.addressField.text()
        doctorIndex = self.doctorCombo.currentIndex()
        doctorID = self.doctorCombo.itemData(doctorIndex) if doctorIndex > 0 else None
        try:
            InsertData.insertPatient(firstName, middleInit, lastName, address, doctorID, fixed_salt)
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT MAX(patient_id) FROM patient;")
                patientID = cursor.fetchone()[0]

            homePhone = self.homePhoneField.text()
            cellPhone = self.cellPhoneField.text()
            workPhone = self.workPhoneField.text()
            if homePhone:
                UpdateDB.patientUpdatePhone(patientID, "Home", homePhone)
            if cellPhone:
                UpdateDB.patientUpdatePhone(patientID, "Mobile", cellPhone)
            if workPhone:
                UpdateDB.patientUpdatePhone(patientID, "Work", workPhone)

            contact1Name = self.contact1NameField.text()
            contact1Phone = self.contact1PhoneField.text()
            contact2Name = self.contact2NameField.text()
            contact2Phone = self.contact2PhoneField.text()
            if contact1Name and contact1Phone:
                UpdateDB.patientUpdateContact(patientID, contact1Name, contact1Phone, "1")
            if contact2Name and contact2Phone:
                UpdateDB.patientUpdateContact(patientID, contact2Name, contact2Phone, "2")

            insurance = self.insuranceField.text()
            accountNumber = self.accountNumberField.text()
            groupNumber = self.groupNumberField.text()
            if insurance or accountNumber or groupNumber:
                UpdateDB.patientUpdateInsurance(patientID, insurance, accountNumber, groupNumber)

            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText(f"Patient {firstName} {lastName} added successfully!")
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
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class RegisterLocation(QDialog):
    def __init__(self):
        super(RegisterLocation, self).__init__()
        loadUi("registerlocation.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        self.centerUI(screen_width, screen_height)

        self.backTo.clicked.connect(self.goBack)
        self.addLocation.clicked.connect(self.addLocationFunction)
        self.styleFormFields()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.backTo.setGeometry(50, 70, 120, 40)

        form_width = 600
        form_height = 350
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)

        button_width = 200
        button_height = 50
        self.addLocation.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)

        error_width = 600
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def styleFormFields(self):
        self.formLayout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.formLayout.setHorizontalSpacing(20)
        self.formLayout.setVerticalSpacing(20)

        self.facilityField.setMinimumHeight(35)
        self.facilityField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.roomField.setMinimumHeight(35)
        self.roomField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.bedField.setMinimumHeight(35)
        self.bedField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.floorField.setMinimumHeight(35)
        self.floorField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

    def addLocationFunction(self):
        facility = self.facilityField.text()
        floor = self.floorField.value()
        room = self.roomField.text()
        bed = self.bedField.text()

        if not facility or not room or not bed:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return

        try:
            InsertData.insertLocation(facility, floor, room, bed)
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText("Location added successfully!")
            self.facilityField.clear()
            self.floorField.setValue(1)
            self.roomField.clear()
            self.bedField.clear()
        except psycopg2.errors.UniqueViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("This location already exists. Please try a different combination.")
        except psycopg2.errors.NotNullViolation:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Missing required information. Please fill all fields.")
        except psycopg2.OperationalError:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("Connection to database failed. Please try again later.")
        except Exception as e:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText(f"Error: {str(e)}")

    def goBack(self):
        admin = AdminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class RegisterAdmission(QDialog):
    def __init__(self):
        super(RegisterAdmission, self).__init__()
        loadUi("registeradmission.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)
        self.centerUI(screen_width, screen_height)

        self.admissionDateTime.setDateTime(QDateTime.currentDateTime())

        self.populatePatients()
        self.populateLocations()
        self.populateDoctors()

        self.backTo.clicked.connect(self.goBack)
        self.addAdmission.clicked.connect(self.addAdmissionFunction)
        self.styleFormFields()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 70, title_width, 61)
        self.backTo.setGeometry(50, 70, 120, 40)

        form_width = 600
        form_height = 350
        self.formLayoutWidget.setGeometry((screen_width - form_width) // 2, 180, form_width, form_height)

        button_width = 200
        button_height = 50
        self.addAdmission.setGeometry((screen_width - button_width) // 2, 550, button_width, button_height)

        error_width = 600
        self.errorMsg.setGeometry((screen_width - error_width) // 2, 610, error_width, 40)
        self.errorMsg.setWordWrap(True)

    def styleFormFields(self):
        for combo in [self.patientCombo, self.locationCombo, self.doctorCombo]:
            combo.setMinimumHeight(35)
            combo.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

        self.admissionDateTime.setMinimumHeight(35)
        self.admissionDateTime.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        self.reasonField.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

    def populatePatients(self):
        try:
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("SELECT patient_id, first_name, middle_name, last_name FROM patientsearchview ORDER BY last_name;")
                patients = cursor.fetchall()

            self.patientCombo.addItem("", "")
            for patient in patients:
                display_text = f"{patient[0]} - {patient[3]}, {patient[1]} {patient[2] or ''}"
                self.patientCombo.addItem(display_text, patient[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading patients: {str(e)}")

    def populateLocations(self):
        try:
            locations = SearchDB.getAvailableLocations()
            self.locationCombo.addItem("", "")
            for location in locations:
                display_text = f"{location[0]} - {location[1]}, Floor {location[2]}, Room {location[3]}, Bed {location[4]}"
                self.locationCombo.addItem(display_text, location[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading locations: {str(e)}")

    def populateDoctors(self):
        try:
            keys = EncryptionKey.getKeys()
            doctors = SearchDB.getDoctors(keys[0])
            self.doctorCombo.addItem("", "")
            if doctors and doctors != "Error":
                for doctor in doctors:
                    display_text = f"{doctor[0]} - {doctor[3]}, {doctor[2]}"
                    self.doctorCombo.addItem(display_text, doctor[0])
        except Exception as e:
            self.errorMsg.setText(f"Error loading doctors: {str(e)}")

    def addAdmissionFunction(self):
        patient_index = self.patientCombo.currentIndex()
        patient_id = self.patientCombo.itemData(patient_index) if patient_index > 0 else None

        location_index = self.locationCombo.currentIndex()
        location_id = self.locationCombo.itemData(location_index) if location_index > 0 else None

        doctor_index = self.doctorCombo.currentIndex()
        doctor_id = self.doctorCombo.itemData(doctor_index) if doctor_index > 0 else None

        admission_date = self.admissionDateTime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        reason = self.reasonField.toPlainText()

        if not patient_id or not location_id or not doctor_id or not reason:
            self.errorMsg.setStyleSheet("color: red;")
            self.errorMsg.setText("All fields are required.")
            return

        try:
            InsertData.insertAdmission(patient_id, location_id, doctor_id, admission_date, reason)
            self.errorMsg.setStyleSheet("color: green;")
            self.errorMsg.setText("Admission registered successfully!")

            self.patientCombo.setCurrentIndex(0)
            self.doctorCombo.setCurrentIndex(0)
            self.reasonField.clear()
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
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class SearchStaff(QDialog):
    def __init__(self):
        super(SearchStaff, self).__init__()
        loadUi("stafflookup.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)

        for field in [self.lastField, self.firstField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")

        for checkbox in [self.lastBox, self.firstBox]:
            checkbox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")

        self.search.clicked.connect(self.searchFunction)
        self.logout.clicked.connect(self.logoutFunction)
        self.backButton.clicked.connect(self.goBack)
        self.resultsTable.hide()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 200, title_width, 71)
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        self.backButton.setGeometry(50, 70, 120, 50)
        form_width = 600
        form_height = 151
        self.gridLayoutWidget.setGeometry((screen_width - form_width) // 2, 290, form_width, form_height)
        error_width = 300
        self.error.setGeometry((screen_width - error_width) // 2, 450, error_width, 31)
        search_width = 151
        search_height = 40
        self.search.setGeometry((screen_width - search_width) // 2, 490, search_width, search_height)
        table_width = min(screen_width - 100, 700)
        table_height = min(screen_height - 600, 500)
        table_x = (screen_width - table_width) // 2
        self.resultsTable.setGeometry(table_x, 550, table_width, table_height)
        self.resultsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.resultsTable.hide()

    def logoutFunction(self):
        eventFilter.enabled = False
        hospitalDB.userLogout()
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

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
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class StaffDetailsScreen(QDialog):
    def __init__(self, staff_id):
        super(StaffDetailsScreen, self).__init__()
        self.setWindowTitle("Staff Details")
        self.setGeometry(100, 100, 900, 700)
        self.staff_id = staff_id
        self.usertype = hospitalDB.getCurrentUserType()

        layout = QVBoxLayout()

        # Header
        self.header_frame = QWidget()
        self.header_layout = QHBoxLayout()
        self.staff_info_label = QLabel()
        self.staff_info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.header_layout.addWidget(self.staff_info_label)
        self.header_frame.setLayout(self.header_layout)
        layout.addWidget(self.header_frame)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        # Basic info tab
        self.basic_info_tab = QWidget()
        self.setupTabs()
        layout.addWidget(self.tabs)

        # Bottom buttons
        button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.goBack)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.loadStaffData()

    def setupTabs(self):
        self.num_static_tabs = 0
        self.tabs.addTab(self.basic_info_tab, "Basic Info")
        self.num_static_tabs = self.tabs.count()


    def closeTab(self, index):
        if index < self.num_static_tabs:
            QMessageBox.information(self, "Protected Tab", "You cannot close the default staff tabs.")
            return
        self.tabs.removeTab(index)

    def loadStaffData(self):
        try:
            data = SearchDB.searchStaffWithID(self.staff_id, encryption_key)
            name = f"{data[1]} {data[2]}"
            self.staff_info_label.setText(f"Staff Member: {name}")

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
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error loading staff data: {str(e)}")
            print(f"Error: {e}")

    def goBack(self):
        search_staff = SearchStaff()
        widget.addWidget(search_staff)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class SearchScreen(QDialog):
    def __init__(self):
        super(SearchScreen, self).__init__()
        loadUi("patientsearch.ui", self)

        screen_size = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.widget.setGeometry(0, 0, screen_width, screen_height)

        self.centerUI(screen_width, screen_height)

        for field in [self.lastField, self.firstField, self.midField]:
            field.setMinimumHeight(35)
            field.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";")
        for checkbox in [self.lastBox, self.firstBox]:
            checkbox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")

        self.search.clicked.connect(self.searchFunction)
        self.logout.clicked.connect(self.logoutFunction)
        self.backButton.clicked.connect(self.goBack)
        self.resultsTable.hide()

        self.activeAdmissionsBox = QtWidgets.QCheckBox("Only Active Admissions")
        self.activeAdmissionsBox.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
        self.gridLayoutWidget.layout().addWidget(self.activeAdmissionsBox, 3, 2)

        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Volunteer":
            self.activeAdmissionsBox.hide()

    def centerUI(self, screen_width, screen_height):
        title_width = 401
        self.label.setGeometry((screen_width - title_width) // 2, 170, title_width, 61)
        self.logout.setGeometry(screen_width - 150, 70, 120, 50)
        self.backButton.setGeometry(50, 70, 120, 50)
        self.gridLayoutWidget.setGeometry((screen_width - 600) // 2, 270, 600, 200)
        self.error.setGeometry((screen_width - 300) // 2, 470, 300, 31)
        self.search.setGeometry((screen_width - 116) // 2, 510, 116, 40)
        self.resultsTable.setGeometry((screen_width - 700) // 2, 550, 700, 500)
        self.resultsTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.resultsTable.hide()

    def searchFunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        middleName = self.midField.text()
        lastBox = self.lastBox.isChecked()
        firstBox = self.firstBox.isChecked()
        activeAdmissionsOnly = False

        if hasattr(self, 'activeAdmissionsBox') and self.activeAdmissionsBox.isVisible():
            activeAdmissionsOnly = self.activeAdmissionsBox.isChecked()

        partials = set()

        if len(lastName) == 0 and len(firstName) == 0 and len(middleName) == 0:
            self.error.setText("Input at least one field.")
        else:
            if firstBox:
                partials.add('fname')
            if lastBox:
                partials.add('lname')

            df = pd.DataFrame(SearchDB.searchPatientWithName(
                fixed_salt,
                fname=firstName if firstName else None,
                mname=middleName if middleName else None,
                lname=lastName if lastName else None,
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
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goBack(self):
        usertype = hospitalDB.getCurrentUserType()
        if usertype == "Administrator":
            admin = AdminScreen()
            widget.addWidget(admin)
        else:
            application = ApplicationScreen()
            widget.addWidget(application)
        widget.setCurrentIndex(widget.currentIndex() + 1)
from EncryptionKey import getKeys
class PatientDetailsScreen(QDialog):
    def __init__(self, patient_id):
        super(PatientDetailsScreen, self).__init__()
        self.setWindowTitle("Patient Details")
        self.setGeometry(100, 100, 900, 700)
        self.patient_id = patient_id
        self.usertype = hospitalDB.getCurrentUserType()
        keys = getKeys()
        self.encryption_key = keys[0]
        self.basicInfoTab = QWidget()
        self.setupBasicInfoTab()

        layout = QVBoxLayout()

        self.header_frame = QWidget()
        self.header_layout = QHBoxLayout()
        self.patient_info_label = QLabel()
        self.patient_info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.header_layout.addWidget(self.patient_info_label)
        self.header_frame.setLayout(self.header_layout)
        layout.addWidget(self.header_frame)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        self.basicInfoTab = QWidget()
        self.insurance_tab = QWidget()
        self.contacts_tab = QWidget()
        self.notes_tab = QWidget()
        self.medications_tab = QWidget()
        self.procedures_tab = QWidget()
        self.location_tab = QWidget()
        self.visitors_tab = QWidget()
        self.admissions_tab = QWidget()

        self.setupTabs()
        layout.addWidget(self.tabs)

        button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.goBack)
        button_layout.addWidget(self.back_button)
        self.print_button = QPushButton("Print to File")
        self.print_button.clicked.connect(self.printPatientDetails)
        button_layout.addWidget(self.print_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.loadPatientData()

    def setupTabs(self):
        self.num_static_tabs = 0
        if self.usertype == "Volunteer":
            self.tabs.addTab(self.basic_info_tab, "Patient Info")
            self.tabs.addTab(self.location_tab, "Location")
            self.tabs.addTab(self.visitors_tab, "Approved Visitors")
        elif self.usertype == "Office Staff":
            self.tabs.addTab(self.basic_info_tab, "Basic Info")
            self.tabs.addTab(self.insurance_tab, "Insurance")
            self.tabs.addTab(self.contacts_tab, "Contacts")
        elif self.usertype in ["Medical Personnel", "Physician", "Administrator"]:
            self.tabs.addTab(self.basic_info_tab, "Basic Info")
            self.tabs.addTab(self.insurance_tab, "Insurance")
            self.tabs.addTab(self.contacts_tab, "Contacts")
            self.tabs.addTab(self.admissions_tab, "Admissions")
            self.tabs.addTab(self.notes_tab, "Notes")
            self.tabs.addTab(self.medications_tab, "Medications")
            self.tabs.addTab(self.procedures_tab, "Procedures")
        self.num_static_tabs = self.tabs.count()

    def closeTab(self, index):
            # Prevent closing the default tabs (index < num_static_tabs)
            if index < self.num_static_tabs:
                QMessageBox.information(self, "Protected Tab", "You cannot close the default patient tabs.")
                return
            self.tabs.removeTab(index)
    def goBack(self):
        search_screen = SearchScreen()
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def loadPatientData(self):
        try:
            # Get data using the search function
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            print("Keys in patient_data:", patient_data.keys())

            if not patient_data:
                QMessageBox.warning(self, "No Data", "No patient data found.")
                return

            # Process data based on user type
            if self.usertype == "Volunteer":
                self.loadVolunteerData(patient_data)
            elif self.usertype == "Office Staff":
                self.loadOfficeStaffData(patient_data)
            elif self.usertype in ["Medical Personnel", "Physician"]:
                self.loadMedicalData(patient_data)

        except Exception as e:
            traceback.print_exc()  # Add this line for full stack trace in terminal
            QMessageBox.critical(self, "Error", f"Error loading patient data: {str(e)}")
            print(f"Error: {e}")

    def setupBasicInfoTab(self):
        self.basic_info_tab = QWidget()  # <-- Add this here now
        layout = QFormLayout()
        self.firstNameEdit = QLineEdit()
        self.middleNameEdit = QLineEdit()
        self.lastNameEdit = QLineEdit()
        self.addressEdit = QTextEdit()

        self.firstNameEdit.setReadOnly(True)
        self.middleNameEdit.setReadOnly(True)
        self.lastNameEdit.setReadOnly(True)
        self.addressEdit.setReadOnly(True)

        layout.addRow("First Name:", self.firstNameEdit)
        layout.addRow("Middle Name:", self.middleNameEdit)
        layout.addRow("Last Name:", self.lastNameEdit)
        layout.addRow("Mailing Address:", self.addressEdit)

        self.editBasicInfoBtn = QPushButton("Edit")
        self.saveBasicInfoBtn = QPushButton("Save")
        self.saveBasicInfoBtn.setEnabled(False)
        self.editBasicInfoBtn.clicked.connect(self.enableBasicInfoEdit)
        self.saveBasicInfoBtn.clicked.connect(self.saveBasicInfo)

        layout.addRow(self.editBasicInfoBtn, self.saveBasicInfoBtn)
        self.basic_info_tab.setLayout(layout)

        self.loadBasicInfo()


    def enableBasicInfoEdit(self):
        self.firstNameEdit.setReadOnly(False)
        self.middleNameEdit.setReadOnly(False)
        self.lastNameEdit.setReadOnly(False)
        self.addressEdit.setReadOnly(False)
        self.saveBasicInfoBtn.setEnabled(True)

    def loadBasicInfo(self):
        try:
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("""
                    SELECT
                        pgp_sym_decrypt(first_name, %s),
                        pgp_sym_decrypt(middle_name, %s),
                        pgp_sym_decrypt(last_name, %s),
                        pgp_sym_decrypt(mailing_address, %s)
                    FROM patient
                    WHERE patient_id = %s
                """, (self.encryption_key,)*4 + (self.patient_id,))
                row = cursor.fetchone()
                print("DEBUG - patient row:", row)


            if row and len(row) >= 4:
                self.firstNameEdit.setText(row[0])
                self.middleNameEdit.setText(row[1])
                self.lastNameEdit.setText(row[2])
                self.addressEdit.setText(row[3])
            else:
                QMessageBox.warning(self, "Data Issue", "Incomplete patient data retrieved.")
        except Exception as e:
            print("DEBUG - loadBasicInfo error:", e)
            QMessageBox.critical(self, "Error loading patient data", str(e))


    def saveBasicInfo(self):
        first = self.firstNameEdit.text().strip()
        middle = self.middleNameEdit.text().strip()
        last = self.lastNameEdit.text().strip()
        address = self.addressEdit.toPlainText().strip()

        try:
            with hospitalDB.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE patient
                    SET
                        first_name = pgp_sym_encrypt(%s, %s),
                        middle_name = pgp_sym_encrypt(%s, %s),
                        last_name = pgp_sym_encrypt(%s, %s),
                        mailing_address = pgp_sym_encrypt(%s, %s)
                    WHERE patient_id = %s
                """, (first, self.encryption_key,
                      middle, self.encryption_key,
                      last, self.encryption_key,
                      address, self.encryption_key,
                      self.patient_id))
            QMessageBox.information(self, "Success", "Patient info updated.")
            self.firstNameEdit.setReadOnly(True)
            self.middleNameEdit.setReadOnly(True)
            self.lastNameEdit.setReadOnly(True)
            self.addressEdit.setReadOnly(True)
            self.saveBasicInfoBtn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update info: {e}")

    def loadVolunteerData(self, data):
        """Load data for Volunteer view"""
        # Volunteer view has: patient_id, first_name, middle_name, last_name, 
        # facility, floor, room_number, bed_number, visitors
        
        # Set header
        name = f"{data['first_name']} {data.get('middle_name', '')} {data['last_name']}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data.get('first_name', '')))
        basic_layout.addRow("Middle Name:", QLabel(data.get('middle_name', '')))
        basic_layout.addRow("Last Name:", QLabel(data.get('last_name', '')))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Location Tab
        location_layout = QFormLayout()
        location_layout.addRow("Facility:", QLabel(data.get('location', [''])[0]))
        location_layout.addRow("Floor:", QLabel(str(data.get('location', ['', '', '', ''])[1])))
        location_layout.addRow("Room Number:", QLabel(str(data.get('location', ['', '', '', ''])[2])))
        location_layout.addRow("Bed Number:", QLabel(str(data.get('location', ['', '', '', ''])[3])))

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
        name = f"{data['first_name']} {data.get('middle_name', '')} {data['last_name']}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data.get('first_name', '')))
        basic_layout.addRow("Middle Name:", QLabel(data.get('middle_name', '')))
        basic_layout.addRow("Last Name:", QLabel(data.get('last_name', '')))
        basic_layout.addRow("Mailing Address:", QLabel(data.get('mailing_address', '')))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Insurance Tab
        insurance_layout = QFormLayout()
        insurance_layout.addRow("Insurance Carrier:", QLabel(data.get('insurance_carrier', '')))
        insurance_layout.addRow("Account Number:", QLabel(data.get('insurance_account', '')))
        insurance_layout.addRow("Group Number:", QLabel(data.get('insurance_group', '')))
        self.insurance_tab.setLayout(insurance_layout)
        
        # Contacts Tab
        contacts_layout = QVBoxLayout()
        
        # Phone numbers
        phone_group = QGroupBox("Phone Numbers")
        phone_layout = QFormLayout()
        phone_layout.addRow("Home Phone:", QLabel(data.get('home_phone', '')))
        phone_layout.addRow("Work Phone:", QLabel(data.get('work_phone', '')))
        phone_layout.addRow("Mobile Phone:", QLabel(data.get('mobile_phone', '')))
        phone_group.setLayout(phone_layout)
        contacts_layout.addWidget(phone_group)
        
        # Emergency contacts
        ec_group = QGroupBox("Emergency Contacts")
        ec_layout = QFormLayout()
        ec_layout.addRow("Contact 1 Name:", QLabel(data.get('ec1_name', '')))
        ec_layout.addRow("Contact 1 Phone:", QLabel(data.get('ec1_phone', '')))
        ec_layout.addRow("Contact 2 Name:", QLabel(data.get('ec2_name', '')))
        ec_layout.addRow("Contact 2 Phone:", QLabel(data.get('ec2_phone', '')))

        ec_group.setLayout(ec_layout)
        contacts_layout.addWidget(ec_group)
        
        self.contacts_tab.setLayout(contacts_layout)

    def loadMedicalData(self, data):
        """Load data for Medical Personnel and Physician view"""
        # Medical view has: patient_id, first_name, middle_name, last_name, address, insurance, phones, emergency contacts, admissions
        
        # Set header
        name = f"{data['first_name']} {data.get('middle_name', '')} {data['last_name']}"
        self.patient_info_label.setText(f"Patient: {name}")
        
        # Basic Info Tab
        basic_layout = QFormLayout()
        basic_layout.addRow("First Name:", QLabel(data.get('first_name', '')))
        basic_layout.addRow("Middle Name:", QLabel(data.get('middle_name', '')))
        basic_layout.addRow("Last Name:", QLabel(data.get('last_name', '')))
        basic_layout.addRow("Mailing Address:", QLabel(data.get('mailing_address', '')))
        self.basic_info_tab.setLayout(basic_layout)
        
        # Insurance Tab
        insurance_layout = QFormLayout()
        insurance_layout.addRow("Insurance Carrier:", QLabel(data.get('insurance_carrier', '')))
        insurance_layout.addRow("Account Number:", QLabel(data.get('insurance_account', '')))
        insurance_layout.addRow("Group Number:", QLabel(data.get('insurance_group', '')))
        self.insurance_tab.setLayout(insurance_layout)
        
        # Contacts Tab
        contacts_layout = QVBoxLayout()
        
        # Phone numbers
        phone_group = QGroupBox("Phone Numbers")
        phone_layout = QFormLayout()
        phone_layout.addRow("Home Phone:", QLabel(data.get('home_phone', '')))
        phone_layout.addRow("Work Phone:", QLabel(data.get('work_phone', '')))
        phone_layout.addRow("Mobile Phone:", QLabel(data.get('mobile_phone', '')))
        phone_group.setLayout(phone_layout)
        contacts_layout.addWidget(phone_group)
        
        # Emergency contacts
        ec_group = QGroupBox("Emergency Contacts")
        ec_layout = QFormLayout()
        ec_layout.addRow("Contact 1 Name:", QLabel(data.get('ec1_name', '')))
        ec_layout.addRow("Contact 1 Phone:", QLabel(data.get('ec1_phone', '')))
        ec_layout.addRow("Contact 2 Name:", QLabel(data.get('ec2_name', '')))
        ec_layout.addRow("Contact 2 Phone:", QLabel(data.get('ec2_phone', '')))

        ec_group.setLayout(ec_layout)
        contacts_layout.addWidget(ec_group)
        
        self.contacts_tab.setLayout(contacts_layout)
        
        # Process admissions data which is in position 15
        admissions = data.get('admissions', [])
        
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
        
        # Add note entry section
        note_entry_group = QGroupBox("Add Note")
        note_entry_layout = QVBoxLayout()

        note_type_combo = QComboBox()
        note_type_combo.addItems(["Clinical", "Progress", "Discharge", "Other"])

        note_text_edit = QTextEdit()
        note_text_edit.setPlaceholderText("Enter your note here...")

        save_note_button = QPushButton("Save Note")

        from datetime import datetime

        def saveNote():
            note_type = note_type_combo.currentText()
            note_text = note_text_edit.toPlainText().strip()
            author_id = hospitalDB.getCurrentUserID()
            from datetime import datetime
            timestamp = datetime.now()

            if not note_text:
                QMessageBox.warning(self, "Empty Note", "Please enter note content.")
                return

            try:
                InsertData.insertNote(admission_id, note_text)
                QMessageBox.information(self, "Success", "Note added successfully!")
                note_text_edit.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save note: {str(e)}")



        save_note_button.clicked.connect(saveNote)

        note_entry_layout.addWidget(QLabel("Note Type:"))
        note_entry_layout.addWidget(note_type_combo)
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
        for med in admission['details'].get('prescriptions', []):
            meds_layout.addWidget(QLabel(f"{med['medication']} - {med['amount']} ({med['schedule']})"))
        meds_group.setLayout(meds_layout)
        layout.addWidget(meds_group)

        # Procedures
        proc_group = QGroupBox("Procedures")
        proc_layout = QVBoxLayout()
        for proc in admission['details'].get('procedures', []):
            proc_layout.addWidget(QLabel(f"{proc['name']} (Scheduled: {proc['scheduled']})"))
        proc_group.setLayout(proc_layout)
        layout.addWidget(proc_group)

        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        for note in admission['details'].get('notes', []):
            notes_layout.addWidget(QLabel(
                f"{note['datetime']} - {note['type']} by {note['author']}: {note['text']}"
            ))
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Finalize layout and tab
        tab.setLayout(layout)
        new_index = self.tabs.addTab(tab, tab_title)
        self.tabs.setCurrentWidget(tab)

        # --- Add close button only for this dynamic tab ---
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


    def printPatientDetails(self):
        """Print patient details to a file"""
        try:
            # Get the patient data again
            patient_data = SearchDB.searchPatientWithID(self.patient_id)
            
            if not patient_data or len(patient_data) == 0:
                QMessageBox.warning(self, "No Data", "No patient data to print.")
                return
            
            if isinstance(patient_data, dict):
                data = patient_data
            elif isinstance(patient_data, (list, tuple)) and len(patient_data) > 0:
                data = patient_data[0]
            else:
                QMessageBox.warning(self, "No Data", "No patient data to print.")
                return

            lines = []
            lines.append("PATIENT DETAILS REPORT")
            lines.append("=" * 50)
            
            # Format based on user type
            if self.usertype == "Volunteer":
                name = f"{data['first_name']} {data.get('middle_name', '')} {data['last_name']}"
                lines.append(f"Patient: {name}")
                lines.append(f"Location: {data[4]}, Floor {data[5]}, Room {data[6]}, Bed {data[7]}")
                lines.append("\nApproved Visitors:")
                if data[8] and len(data[8]) > 0:
                    for visitor in data[8]:
                        lines.append(f"- {visitor}")
                else:
                    lines.append("No approved visitors")
                    
            elif self.usertype == "Office Staff":
                name = f"{data['first_name']} {data.get('middle_name', '')} {data['last_name']}"
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
                name = f"{data['first_name']} {data.get('middle_name', '')} {data['last_name']}"
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
                
                admissions = data.get('admissions', [])
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
            
            # Write to file
            filename = f"patient_{self.patient_id}_details.txt"
            with open(filename, 'w') as f:
                f.write("\n".join(lines))
            
            QMessageBox.information(self, "Success", f"Patient details saved to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error printing patient data: {str(e)}")
            print(f"Error: {e}")
    
    def goBack(self):
        search_screen = SearchScreen()
        widget.addWidget(search_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class LockScreen(QtWidgets.QDialog):
    def __init__(self, exitAction, widget, eventFilter, currentUser):
        super(LockScreen, self).__init__()
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
    home = MainScreen()
    widget.addWidget(home)
    widget.setCurrentIndex(widget.currentIndex() + 1)

def lockScreen():
    print("here")
    eventFilter.enabled = False
    lock = LockScreen(LogOut, widget, eventFilter, hospitalDB.getCurrentUserID())
    widget.addWidget(lock)
    widget.setCurrentIndex(widget.currentIndex() + 1)

app = QApplication(sys.argv)
app.setStyleSheet("""
    QPushButton {
        outline: none;
    }
    QPushButton:focus {
        outline: none;
    }
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
home = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
#widget.resize(1200, 800)
widget.showMaximized()
eventFilter = InactivityTimer(lockScreen)
app.installEventFilter(eventFilter)
try:
    sys.exit(app.exec())
except:
    print("Exiting")
