#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BitCurator Access Redaction Tool GUI (bca-redtools GUI)
#
# RedactGUI.py
#
# Implementation of GUI interface in PyQT5 for bca-redtools
#

import os
import sys, time
from subprocess import Popen, PIPE


from PyQt5 import QtCore, QtGui, QtWidgets
from RedactWindow import Ui_RedactWindow


class RedactGUI(QtWidgets.QMainWindow, Ui_RedactWindow):
	def __init__(self):
		super(RedactGUI, self).__init__()
		self.setupUi(self)

		# ALL CONTROL CODE GOES HERE, IN SUBSEQUENT FUNCTIONS, IN ADDITIONAL MODULES, OR MAIN! 
		# *DO NOT* EDIT RedactWindow,py! (USE ONLY QTCREATOR TO UPDATE IT)

		# Signal application exit request
		self.CloseButton.clicked.connect(self.buttonClickedClose)

	# Handle application exit
	def buttonClickedClose(self):
		QtCore.QCoreApplication.instance().quit()

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
