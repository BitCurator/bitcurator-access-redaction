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
        self.callback_handler = self.CallbackHandler()

        # ALL CONTROL CODE GOES HERE, IN SUBSEQUENT FUNCTIONS, IN ADDITIONAL MODULES, OR MAIN!
        # *DO NOT* EDIT RedactWindow,py! (USE ONLY QTCREATOR TO UPDATE IT)
        # self.worker = RedactWorker()

        self.RunButton.clicked.connect(self.buttonClickedRun)
        self.SelectConfigTool.clicked.connect(self.buttonClickedSelectConfig)
        self.OpenConfigEditorButton.clicked.connect(self.buttonClickedOpenConfigEditorButton)
        XStream.stdout().messageWritten.connect(self.textEdit.insertPlainText)
        XStream.stderr().messageWritten.connect(self.textEdit.insertPlainText)
        self.callback_handler.valueUpdated.connect(self.handleProgressBarUpdated)

    class CallbackHandler(QtCore.QObject):
        valueUpdated = QtCore.pyqtSignal(int)

        def updateProgressBar(self, percent):
            self.valueUpdated.emit(percent)

    def handleProgressBarUpdated(self, value):
        self.RedactionProgress.setValue(value)
        QtWidgets.QApplication.processEvents()

    def buttonClickedClose(self):
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

        output_file = self.redact_config['output_file']
        if os.path.exists(output_file):
            msg = "Output image file exists. Want to overwrite this file?\n%s" % output_file
            reply = QtWidgets.QMessageBox.question(
                self, 'Confirm', msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply != QtWidgets.QMessageBox.Yes:
                return

        self.redact_thread = RedactorThread(self.redact_config, self.callback_handler)

        # Connect any signals..
        self.redact_thread.finished.connect(self.done)

        self.redact_thread.start()

        self.CancelButton.setEnabled(True)
        self.CancelButton.clicked.connect(self.redact_thread.terminate)
        self.RunButton.setEnabled(False)

    def done(self):
        self.handleProgressBarUpdated(100)
        self.CancelButton.setEnabled(False)
        self.RunButton.setEnabled(True)

    def buttonClickedSelectConfig(self):
        # TODO implement GUI controls for config overrides
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
        filenames = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file',
            '', "Configuration text files (*.*)")
        if filenames[0]:
            self.fname = filenames[0]
            self.SelectConfigEdit.setText(self.fname)
            try:
                self.redact_config = config.parse(self.fname)
                logging.debug('Combined config & arguments:\n%s' % self.redact_config)
            except Exception as e:
                logging.error(e)

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


class XStreamLogger(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record:
            XStream.stdout().write('%s\n' % record)


class XStream(QtCore.QObject):
    _stdout = None
    _stderr = None
    messageWritten = QtCore.pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if (not self.signalsBlocked()):
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if (not XStream._stdout):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if (not XStream._stderr):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class RedactorThread(QtCore.QThread):
    def __init__(self, config, cbh=None):
        """
        Make a new thread instance with the specified
        Redactor config as the first argument.
        :param subreddits: A list of subreddit names
        :type subreddits: list
        """
        QtCore.QThread.__init__(self)
        self.redactor = redact.Redactor(**config)
        self.redactor.setProgressCallback(cbh)

    def __del__(self):
        self.wait()

    def run(self):
        self.redactor.execute()


def main():
    app = QtWidgets.QApplication(sys.argv)

    # UI setup is performed in the RedactGUI class
    form = RedactGUI()

    # Connect redactor logging to text box
    logging.basicConfig(level=logging.INFO)
    log_handler = XStreamLogger()
    logging.getLogger().addHandler(log_handler)

    form.show()
    sys.exit(app.exec_())
