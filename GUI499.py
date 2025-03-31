# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 09:18:06 2025

@author: laure
"""

import psycopg2
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtCore import QTimer, QEvent, QObject
import string
import EncryptionKey
import SearchDB
# import sql thing

class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("MainScreen.ui", self)
        #self.enterApplication = QPushButton("Enter Application", self)
        self.enterApplication.clicked.connect(self.openLogin)
       
    def openLogin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login1.ui", self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

        # may need to move this to the loginfunction
       # self.login.clicked.connect(self.gotosearch)
       
    def loginfunction(self):
           user = self.userField.text()
           password = self.passwordField.text()
           
           if len(user)==0 or len(password)==0:
               self.errorMsg.setText("Missing field.")
           else:
                keys = EncryptionKey.getKeys() 
                encryption_key = keys[0]
                fixed_salt = keys[1]   
                result_pass = SearchDB.passwordMatch(user, password, fixed_salt)
                if result_pass:
                    print("Successfully logged in.")
                    self.errorMsg.setText("")
                    self.gotosearch()
                else:
                    self.errorMsg.setText("Invalid username or password")
    def gotosearch(self):
        search=SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex()+1)

class SearchScreen(QDialog):
    def __init__(self):
        super(SearchScreen, self).__init__()
        loadUi("patientsearch.ui", self)
        self.search.clicked.connect(self.searchfunction)
        self.logout.clicked.connect(LogOut)
#        monitor = InactivityMonitor(timeout = 5000, callback = LogOut)
#        self.installEventFilter(monitor)
        
    def searchfunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        
        if len(lastName)==0 and len(firstName)==0:
            self.error.setText("Input at least one field.")
        else:
            keys = EncryptionKey.getKeys() 
            encryption_key = keys[0]
            fixed_salt = keys[1]   
            if(firstName[len(firstName) - 1] == "*"):
                print(SearchDB.searchPatientWithName(firstName[0: len(firstName) - 1], None, lastName, encryption_key, fixed_salt, True))
            else:
                print(SearchDB.searchPatientWithName(firstName, None, lastName, encryption_key, fixed_salt))
        """if len(lastName) > 0 and len(firstName) > 0:
            if self.contains_special_char(lastName):
                lastName = lastName[:-1]
                self.lastSpecChar(lastName)
            else:
                self.lastQuery(lastName)
                
            if self.contains_special_char(firstName):
                firstName = firstName[:-1]
                self.firstSpecChar(firstName)
            else:
                self.firstQuery(firstName)
            
            self.combineQuery(lastName,firstName)
                
        if len(lastName) > 0:
            if self.contains_special_char(lastName):
                lastName = lastName[:-1]
                self.lastSpecChar(lastName)
            else:
                self.lastQuery(lastName)
                
        if len(firstName) > 0:
            if self.contains_special_char(firstName):
                firstName = firstName[:-1]
                self.firstSpecChar(firstName)
            else:
                self.firstQuery(firstName)"""
                
    
    def contains_special_char(input_string):
        for char in input_string:
            if char in string.punctuation:
                return True
            return False
        
    def lastSpecChar(input_string):
        '''
        I don't know the specific SQL syntax for a partial search, nor do I know if we
        need to reconnect to the database.
        conn = sql.connect("database name")
        cur = conn.cursor()
        lastquery = 'SELECT lastname FROM patientNames WHERE lastName LIKE =
        
            '''
        
    def firstSpecChar(input_string):
        '''
        conn = sql.connect("database name")
        cur = conn.cursor()
        firstquery = 'SELECT lastname FROM patientNames WHERE lastName LIKE =
            '''
        
    def lastQuery(input_string):
        '''
        conn = sql.connect("database name")
        cur = conn.cursor()
        lastquery = 'SELECT lastname FROM patientNames WHERE lastName LIKE =
            '''
    def firstQuery(input_string):
        '''
        conn = sql.connect("database name")
        cur = conn.cursor()
        firstquery = 'SELECT lastname FROM patientNames WHERE lastName LIKE =
            '''
    def combineQuery(input_string1, input_string2):
        '''
        conn = sql.connect("database name")
        cur = conn.cursor()
        combineQuery = 'SELECT '
        '''
        
    def gotolist(self):
        plist=ListScreen()
        widget.addWidget(plist)
        widget.setCurrentIndex(widget.currentIndex()+1)

class ListScreen(QDialog):
    def __init__(self):
        super(ListScreen, self).__init__()
        loadUi("list.ui", self)       
        
   # def gototsearch(self):
     #  search.SearchScreen()
     #  widget.addWidget(search)
     #  widget.setCurrentIndex(widget.currentIndex()+1)

# class InactivityMonitor(QObject):
#     def __init__(self, timeout = 300000, callback = None, parent = None):
#         super().__init__(parent)
#         print("Inactivity monitor created")
#         print("Timeout = ", timeout)
#         self.callback = callback
#         self.timer = QTimer(self)
#         self.timer.singleShot(timeout, self.callback)
#         print("Timer has started")

#     def handleTimeout(self):
#         print("Handle Timeout")
#         if self.callback:
#             self.callback()

#     def eventFilter(self, obj, event):
#         if event.type() in (QEvent.MouseMove, QEvent.KeyPress, QEvent.MouseButtonPress, QEvent.Wheel):
#             self.timer.start()
#             print("Button pressed")
#         return super().eventFilter(obj, event)
    
def LogOut():
    home = MainScreen()
    widget.addWidget(home)
    widget.setCurrentIndex(widget.currentIndex()+1)
    print("Logging out...")  
        
# main
app = QApplication(sys.argv)
login = LoginScreen()
home = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")