
import psycopg2
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
import string

class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("mainscreen.ui", self)
        self.enterApplication.clicked.connect(self.openLogin)

    def openLogin(self):
        login=LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login1.ui", self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
       
    def loginfunction(self):
           user = self.userField.text()
           password = self.passwordField.text()
           
           if len(user)==0 or len(password)==0:
               self.errorMsg.setText("Missing field.")
              
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
                    self.errorMsg.setText("")
                    #store user type here maybe?
                    if userType == "admin":
                        self.gotoadmin()
                    else:
                        self.gotosearch()
                else:
                    self.errorMsg.setText("Invalid username or password")
    def gotosearch(self):
        search=SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex()+1)

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
        '''
        for i in range(0,5):
            firstName=self.tableWidget.item(i, 1)
            lastName=self.tableWidget.item(i,1)
            username = self.tableWidget.item(i,1)
            password = self.tableWidget.item(i,1)
            staffType = self.tableWidget.item(i,1)
            '''
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

    def logoutfxn(self):
        login=LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def searchfunction(self):
        lastName = self.lastField.text()
        firstName = self.firstField.text()
        
        if len(lastName)==0 and len(firstName)==0:
            self.error.setText("Input at least one field.")
#do something here with sql
        self.gotolist()
    def gotolist(self):
        plist=ListScreen()
        widget.addWidget(plist)
        widget.setCurrentIndex(widget.currentIndex()+1)
class SearchScreen(QDialog):
    def __init__(self):
        super(SearchScreen, self).__init__()
        loadUi("patientsearch.ui", self)
        self.search.clicked.connect(self.searchfunction)
        self.logout.clicked.connect(self.logoutfxn)
        
    def logoutfxn(self):
        login=LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
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
    
    # theres probably a better way to implement this, but I couldnt wrap my head around it    
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
        self.tableWidget.itemSelectionChanged.connect(self.row_selected)
        self.tableWidget.setColumnWidth(0,150)
        self.tableWidget.setColumnWidth(1,150)
        self.tableWidget.setColumnWidth(2,150)
        self.tableWidget.setHorizontalHeaderLabels(["Last Name", "First Name", "MI"])
        self.loadData()
        self.nextButton.clicked.connect(self.selectedfunction)
        self.logoutButton.clicked.connect(self.lgout)
        self.backSearchButton.clicked.connect(self.back)
        #self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        
    def back(self):
        search=SearchScreen()
        widget.addWidget(search)
        widget.setCurrentIndex(widget.currentIndex()+1)
    def lgout(self):
        login=LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    def row_selected(self):
        selected_items = self.tableWidget.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            col_count = self.tableWidget.columnCount()
            row_data = [self.tableWidget.item(row, col).text() for col in range(col_count)]
            selectedLName, selectedFName, selectedMI = row_data

        
    def loadData(self):
        # another query is needed here, or if we can use the one from the search here
        self.tableWidget.setRowCount(50)
        # or self.tableWidget.setRowCount(len(sqlquery))
        tableRow = 0
        # you can change the placeholder var name sqlquery to whatever you like
        for row in cur.execute(sqlquery):
            self.tableWidget.setItem(tableRow, 0, QtWidgets.QTableWidgetItem(row[0]))
            self.tableWidget.setItem(tableRow, 1, QtWidgets.QTableWidgetItem(row[1]))
            self.tableWidget.setItem(tableRow, 2, QtWidgets.QTableWidgetItem(row[2]))
            tableRow+=1
            
    def selectedfunction(self):
        #do something here with the variables selected:LName/FName/MI from row_selected fxn
        #another query to pull up all patient data to display on the next screen
        self.gotodata()
    
    def gotodata(self):
        data=DataScreen()
        widget.addWidget(data)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
class DataScreen(QDialog):
    def __init__(self):
        super(DataScreen, self).__init__()
        loadUi("data2.ui", self)
        
    def checkCreds(self):
        #somehow test credentials of staff probably with query, put their position in a variable, test variable against different staff types
        if staffType == "Office Staff":
            patInfo = QtWidgets.QWidget()
            tableView = QtWidgets.QTableView(patInfo)
            layout = QtWidgets.QVBoxLayout(patInfo)
            layout.addWidget(tableView)
            patInfo.setLayout(layout)
            self.tabWidget.addTab(patInfo, "Patient Information")
            insuranceTab = QtWidgets.QWidget()
            tableInsurance = QtWidgets.QTableView(insuranceTab)
            layoutIns = QtWidgets.QVBoxLayout(insuranceTab)
            layout.addWidget(tableInsurance)
            insuranceTab.setLayout(layoutIns)
            self.tabWidget.addTab(insuranceTab, "Insurance")

        #elif staffType == "Medical Personnel":
            #


            
    


# main
app = QApplication(sys.argv)
mainscreen = MainScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainscreen)
widget.setFixedHeight(881)
widget.setFixedWidth(801)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Exiting")