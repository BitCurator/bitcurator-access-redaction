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
import logging
from libredact import redact, config

from PyQt5 import QtCore, QtWidgets
from RedactWindow import Ui_RedactWindow


class RedactGUI(QtWidgets.QMainWindow, Ui_RedactWindow):
    def __init__(self):
        super(RedactGUI, self).__init__()
        self.setupUi(self)
        self.fname = None

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
        self.CancelButton.clicked.connect(self.buttonClickedCancel)
        self.RunButton.clicked.connect(self.buttonClickedRun)

        self.SelectConfigTool.clicked.connect(self.buttonClickedSelectConfig)
        self.OpenConfigEditorButton.clicked.connect(self.buttonClickedOpenConfigEditorButton)

        # Handle button presses in config edit tab - this may be better done elsewhere

    class CallbackHandler(object):
        def __init__(self, progress_widget):
            self.progress_widget = progress_widget

        def updateProgressBar(self, offset, total):
            fraction = offset/total
            self.progress_widget.setProperty("value", fraction)

    def buttonClickedClose(self):
        # Quit the app, duh
        QtCore.QCoreApplication.instance().quit()

    def buttonClickedCancel(self):
        # Placeholder - fix for actual app
        QtCore.QCoreApplication.instance().quit()

    def buttonClickedRun(self):
        # Run through API
        # Read the redaction configuration file
        if self.fname is None:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Invalid Configuration")
            msg.setInformativeText("You must select a configuration file.")
            msg.setWindowTitle("Error")
            # msg.setDetailedText("The details are as follows:")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        cfg = config.parse(self.fname)
        logging.debug('Combined config & arguments:\n%s' % cfg)
        # validate the config against schema and show any errors
        redactor = redact.Redactor(**cfg)
        cbh = self.CallbackHandler(self.RedactionProgress)
        redactor.setProgressCallback(cbh)
        redactor.execute()

        # Run as shell process
        # self.process = QtWidgets.QProcess()
        # self.connect(self.process, QtCore.SIGNAL("readyReadStdout()"), self.readOutput)
        # self.connect(self.process, QtCore.SIGNAL("readyReadStderr()"), self.readErrors)
        # command = "redact-cli --config=%s" % self.fname
        # self.process.setArguments(QtWidgets.QStringList.split(" ", command))
        # self.process.start()

    def readOutput(self):
        self.textEdit.append(QtCore.QString(self.process.readStdout()))
        if self.process.isRunning() is False:
            self.textEdit.append("\n Redaction completed, see above for any errors.")

    def readErrors(self):
        self.textEdit.append("error: " + QtCore.QString(self.process.readLineStderr()))

    def buttonClickedSelectConfig(self):
        self.fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file',
            '', "configuration text files (*.*)")[0]
        self.SelectConfigEdit.setText(self.fname)

    def buttonClickedOpenConfigEditorButton(self):
        os.system("gnome-text-editor %s" % self.fname)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Save Editor Changes")
        msg.setInformativeText("You opened the configuration file in an editor."
                               "\nYou must save any changes before they will take effect.")
        msg.setWindowTitle("Reminder")
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


class QTextEditLogger(logging.Handler):
    def __init__(self, textEdit):
        super(QTextEditLogger, self).__init__()
        self.widget = textEdit

    def emit(self, record):
        msg = self.format(record)
        self.widget.textCursor().appendPlainText(msg)

    def write(self, m):
        pass


def main():

    app = QtWidgets.QApplication(sys.argv)

    # UI setup is performed in the RedactGUI class
    form = RedactGUI()

    # Connect redactor logging to text box
    log_handler = QTextEditLogger(form.textEdit)
    logging.getLogger().addHandler(log_handler)
    form.show()

    sys.exit(app.exec_())
