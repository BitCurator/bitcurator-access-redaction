#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# BitCurator Access Redaction Tool GUI (bca-redtools GUI)
#
# RedactGUI.py
#
# Implementation of GUI interface in PyQT5 for bca-redtools
#

import os
import sys
import time
import libredact
import threading
import logging
from libredact.redact import Redactor
from libredact import config
from subprocess import Popen, PIPE

from PyQt5 import QtCore, QtGui, QtWidgets
from RedactWindow import Ui_RedactWindow


class RedactGUI(QtWidgets.QMainWindow, Ui_RedactWindow):
    def __init__(self):
        super(RedactGUI, self).__init__()
        self.setupUi(self)

        # ALL CONTROL CODE GOES HERE, IN SUBSEQUENT FUNCTIONS, IN ADDITIONAL MODULES, OR MAIN!
        # *DO NOT* EDIT RedactWindow,py! (USE ONLY QTCREATOR TO UPDATE IT)
        # self.worker = RedactWorker()

        # Override any CLI arguments
        # if args.get('--input'):
        #     cfg['image_file'] = args.get('--input')
        # if args.get('--output'):
        #     cfg['output_file'] = args.get('--output')
        # if args.get('--dfxml'):
        #     cfg['dfxml_file'] = args.get('--dfxml')
        # if args.get('--report'):
        #     cfg['report_file'] = args.get('--report')
        # if args.get('--dry-run'):  # if True then override COMMIT
        #     cfg['commit'] = False
        # cfg['detail'] = args.get('--detail')

        # Custom signal connection to update redaction progress bar
        # RedactWindow.connect(self.thread, SIGNAL("progress(int, int)"), self.updateProgressBar)
        # Handle buttons in main tab - this may be better done elsewhere
        self.CloseButton.clicked.connect(self.buttonClickedClose)
        self.CancelButton.clicked.connect(self.buttonClickedCancel)
        self.CancelButton.clicked.connect(self.buttonClickedRun)

        # Handle button presses in config edit tab - this may be better done elsewhere
        self.LoadButton.clicked.connect(self.buttonClickedLoad)
        self.SaveButton.clicked.connect(self.buttonClickedSave)

    def updateProgressBar(self, offset, total):
        fraction = offset/total
        self.RedactionProgress.setProperty("value", fraction)

    def buttonClickedClose(self):
        # Quit the app, duh
        QtCore.QCoreApplication.instance().quit()

    def buttonClickedCancel(self):
        # Placeholder - fix for actual app
        QtCore.QCoreApplication.instance().quit()

    def buttonClickedRun(self):
        # Placeholder - fix for actual app
        self.worker.redact(self.redactor)

    def buttonClickedLoad(self):
        # Read the redaction configuration file
        config_path = self.SelectConfigEdit.text()
        cfg = config.parse(config_path)
        logging.debug('Combined config & arguments:\n%s' % cfg)
        # validate the config against schema and show any errors
        self.redactor = Redactor(**cfg)

    def buttonClickedSave(self):
        # Placeholder - fix for actual app
        QtCore.QCoreApplication.instance().quit()


def main():

    app = QtWidgets.QApplication(sys.argv)

    # UI setup is performed in the RedactGUI class
    form = RedactGUI()
    form.show()

    sys.exit(app.exec_())
