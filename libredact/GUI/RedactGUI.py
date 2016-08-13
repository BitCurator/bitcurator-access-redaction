import os, sys

from PyQt5 import QtCore, QtGui, QtWidgets
from RedactWindow import Ui_RedactWindow


class RedactGUI(QtWidgets.QMainWindow, Ui_RedactWindow):
	def __init__(self):
		super(RedactGUI, self).__init__()
		self.setupUi(self)

	# ALL CONTROL CODE GOES HERE, ADDITIONAL MODULES, OR MAIN! 
	# *DO NOT* EDIT RedactWindow,py! (USE ONLY QTCREATOR TO UPDATE IT)

		# Connect "add" button with a custom function (addInputTextToListbox)
		# self.addBtn.clicked.connect(self.addInputTextToListbox)

	#def addInputTextToListbox(self):
		#txt = self.myTextInput.text()
		#self.listWidget.addItem(txt)

if __name__ == '__main__':

	import sys

	app = QtWidgets.QApplication(sys.argv)

	# UI setup is performed in the RedactGUI class
	form = RedactGUI()
	form.show()

	sys.exit(app.exec_())
