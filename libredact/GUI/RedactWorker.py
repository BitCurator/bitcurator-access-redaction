from PyQt4.QtCore import QThread
from libredact import Redactor


class RedactWorker(QThread):

    def __init__(self, parent=None):

        QThread.__init__(self, parent)
        self.exiting = False

    def redact(self, Redactor):

        self.size = size
        self.stars = stars
        self.start()

    def run(self):
        Redactor.execute()

    def updateProgress(offset, total):
        self.emit(SIGNAL("progress(int, int)"), offset, total)

    def __del__(self):

        self.exiting = True
        self.wait()
