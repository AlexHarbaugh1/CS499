#   Inactivity timeout using event filter to reset timer when certian events are triggered. 
#   Set time delay by changing inactivityTime (initially set to 600000 ms or 10 mins).
#   Connect to window or app with .installEventFilter(InactivityTimer(*action*)) where *action* is the function that occurs when timer ends.

from PyQt5.QtCore import QTimer, QObject, QEvent

class InactivityTimer(QObject):
    def __init__(self, action):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.inactivityAction)
        self.action = action
        self.inactivityTime = 600000

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.KeyPress, QEvent.MouseButtonPress, QEvent.MouseButtonDblClick, QEvent.Wheel, QEvent.Move, QEvent.MouseMove]:
            self.resetTimer()                           # Reset the timer on user activity
            return False                                # Pass the event on
        return super().eventFilter(obj, event)
    
    def resetTimer(self):
        self.timer.stop()
        self.timer.start(self.inactivityTime)

    def inactivityAction(self):
        self.timer.stop()
        # print("Logged out due to inactivity.")        # debug statement
        self.action()



    