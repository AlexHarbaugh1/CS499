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