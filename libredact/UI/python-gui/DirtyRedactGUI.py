import os, sys

from PyQt5 import QtCore, QtGui, QtWidgets
from RedactWindow import Ui_RedactWindow


class RedactGUI(QtWidgets.QMainWindow, Ui_RedactWindow):
	def __init__(self):
		super(MyRedactWindow, self).__init__()
		self.setupUi(self)

	#def __init__(self, parent=None):
	#	QMainWindow.__init__(self,parent)
	#	self.setupUi(self)
 
#class RedactGUI(Ui_RedactWindow):
#	def __init__(self, dialog):
#		Ui_RedactWindow.__init__(self)
#		self.setupUi(dialog)

		# Connect "add" button with a custom function (addInputTextToListbox)
		# self.addBtn.clicked.connect(self.addInputTextToListbox)

	#def addInputTextToListbox(self):
		#txt = self.myTextInput.text()
		#self.listWidget.addItem(txt)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	ui = MyRedactWindow()
	ui.show()
	sys.exit(app.exec_())


	#app = QtWidgets.QApplication(sys.argv)
	#dialog = QtWidgets.QDialog()

	#prog = RedactGUI(dialog)

	#dialog.show()
	#sys.exit(app.exec_())