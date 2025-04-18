from PyQt5 import QtWidgets, uic, QtCore

import SearchDB


class LockScreen(QtWidgets.QDialog):
    def __init__(self, exitAction, keys, widget, eventFilter, currentUser):
        super(LockScreen, self).__init__()
        uic.loadUi("lockScreen.ui", self)
        self.exitAction = exitAction
        self.keys = keys
        self.widget = widget
        self.eventFilter = eventFilter
        self.usernameField.setText(currentUser)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.resumeButton.clicked.connect(self.resumePressed)
        self.exitButton.clicked.connect(self.exitPressed)
        self.setWindowFlag(True)
        self.setWindowModality(True)
        # self.setFixedSize(400, 150)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

    def resumePressed(self):
        user = self.usernameField.text()
        password = self.passwordField.text()
        result_pass = SearchDB.passwordMatch(user, password, self.keys[1])
        if result_pass:
            self.errorMsg.setText("")
            self.eventFilter.enabled = True
            self.widget.removeWidget(self)
            self.deleteLater()
        else:
            self.errorMsg.setText("Invalid username or password")
        
    def exitPressed(self):
        self.exitAction()