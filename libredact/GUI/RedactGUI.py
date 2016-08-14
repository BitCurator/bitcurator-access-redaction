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

		# Handle buttons in main tab - this may be better done elsewhere
		self.CloseButton.clicked.connect(self.buttonClickedClose)
		self.CancelButton.clicked.connect(self.buttonClickedCancel)
		self.CancelButton.clicked.connect(self.buttonClickedRun)

		# Handle button presses in config edit tab - this may be better done elsewhere
		self.LoadButton.clicked.connect(self.buttonClickedLoad)
		self.SaveButton.clicked.connect(self.buttonClickedSave)

	def buttonClickedClose(self):
		# Quit the app, duh
		QtCore.QCoreApplication.instance().quit()

	def buttonClickedCancel(self):
		# Placeholder - fix for actual app
		QtCore.QCoreApplication.instance().quit()
	
	def buttonClickedRun(self):
		# Placeholder - fix for actual app
		QtCore.QCoreApplication.instance().quit()
	
	def buttonClickedLoad(self):
		# Placeholder - fix for actual app
		QtCore.QCoreApplication.instance().quit()

	def buttonClickedSave(self):
		# Placeholder - fix for actual app
		QtCore.QCoreApplication.instance().quit()



if __name__ == '__main__':

	import sys

	app = QtWidgets.QApplication(sys.argv)

	# UI setup is performed in the RedactGUI class
	form = RedactGUI()
	form.show()

	sys.exit(app.exec_())
