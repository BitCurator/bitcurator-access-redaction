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
import threading
from subprocess import Popen, PIPE


from PyQt5 import QtCore, QtGui, QtWidgets
from RedactWindow import Ui_RedactWindow


class RedactGUI(QtWidgets.QMainWindow, Ui_RedactWindow):
	def __init__(self):
		super(RedactGUI, self).__init__()
		self.setupUi(self)

		# ALL CONTROL CODE GOES HERE, IN SUBSEQUENT FUNCTIONS, IN ADDITIONAL MODULES, OR MAIN! 
		# *DO NOT* EDIT RedactWindow,py! (USE ONLY QTCREATOR TO UPDATE IT)

		# Connect "add" button with a custom function (addInputTextToListbox)
		# self.addBtn.clicked.connect(self.addInputTextToListbox)

		# Application exit request from "Close" button
		self.CloseButton.clicked.connect(self.buttonClickedClose)

		# Cancel of current run from "Cancel" button
		self.CancelButton.clicked.connect(self.buttonClickedCancel)

		# Start of current run from "Run" button
		self.CancelButton.clicked.connect(self.buttonClickedRun)

	# Handle application exit from "Close" button
	def buttonClickedClose(self):
		QtCore.QCoreApplication.instance().quit()

	def buttonClickedCancel(self):
		# Fix for actual app
		QtCore.QCoreApplication.instance().quit()
	
	def buttonClickedRun(self):
		# Fix for actual app
		QtCore.QCoreApplication.instance().quit()

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
