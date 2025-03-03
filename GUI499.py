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
import string
import EncryptionKey
import SearchDB
# import sql thing


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
        
    def searchfunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        
        if len(lastName)==0 and len(firstName)==0:
            self.error.setText("Input at least one field.")
        
        if len(lastName) > 0 and len(firstName) > 0:
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
                self.firstQuery(firstName)
                
    
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
               ''' This will connect to the certain SQL db '''
           else:    
                conn = psycopg2.connect(
                database="huntsvillehospital",
                user='postgres',
                password='49910',
                host='localhost',
                port= '5432'
                )
                cur = conn.cursor()
                # Password is encrytped so crypt() comapares the decrytped password
                # The result of the query is a boolean that is true if there is a match and false when there is not a match
                query = "SELECT (password = crypt('{}', password)) AS password_match FROM Users WHERE username = '{}' ;" .format(password, user)
                cur.execute(query)
                result_pass = cur.fetchone()[0]
                if result_pass:
                    print("Successfully logged in.")
                    #self.connect(self.gotosearch)
                    self.errorMsg.setText("")
                else:
                    self.errorMsg.setText("Invalid username or password")
        
                  
               
        
        
   # def gototsearch(self):
     #  search.SearchScreen()
     #  widget.addWidget(search)
     #  widget.setCurrentIndex(widget.currentIndex()+1)
        
class SearchScreen(QDialog):
    def __innit__(self):
        super(SearchScreen, self).__init__()
        loadUi("searchscreen.ui", self)



# main
app = QApplication(sys.argv)
login = LoginScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(login)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")