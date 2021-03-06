if(__name__=='__main__'):
	import os
	import sys
	os.environ['PATH']=r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'+r';C:\Program Files\Side Effects Software\Houdini 16.0.600\houdini\dso;'+os.environ['PATH']
	os.environ['HOUDINI_USER_PREF_DIR']=r'C:\Users\User\Documents\houdini16.0'


	#print sys.path
	from hcollections.QDoubleInputDialog import QDoubleInputDialog


try:
	from PySide2.QtWidgets import *
	from PySide2.QtGui import *
	from PySide2.QtCore import *
except:
	from PySide.QtCore import *
	from PySide.QtGui import *

try:
	import accountsmanager_ui
except ImportError:
	import accountsmanager_ui4 as accountsmanager_ui

from githubauthorizator import GithubAuthorizator


class AccountsManager(object):
	class __AccountsManager(QWidget):
		def __init__(self, parent, flags=0):
			super(AccountsManager.__AccountsManager,self).__init__(parent, flags)

			self.ui=accountsmanager_ui.Ui_MainWindow()
			self.ui.setupUi(self)


			self.__authModel = QStringListModel(self)
			self.ui.authListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
			self.ui.authListView.setModel(self.__authModel)

			self.__publicModel = QStringListModel(self)
			self.ui.publicListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
			self.ui.publicListView.setModel(self.__publicModel)

			#slots-signals
			self.ui.addAuthPushButton.clicked.connect(self.newAuth)
			self.ui.removeAuthPushButton.clicked.connect(self.removeAuth)
			self.ui.addPublicPushButton.clicked.connect(self.newPublic)
			self.ui.removePublicPushButton.clicked.connect(self.removePublic)
			self.ui.reinitPushButton.clicked.connect(self.reinitCallback)

			self.updateAuthList()
			self.updatePublicList()


		def newAuth(self):
			good = False
			try:
				good = GithubAuthorizator.newAuthorization()
			except IOError as e:
				QMessageBox.warning(self,'could not write the account file!','Error: %d : %s'%e.args)
			if(good):
				self.updateAuthList()

		def removeAuth(self):
			index = self.ui.authListView.currentIndex()
			good = False
			try:
				good = GithubAuthorizator.removeAuthorization(index.data())
			except IOError as e:
				QMessageBox.warning(self,'could not write the account file!','Error: %d : %s'%e.args)
			if(good):
				self.updateAuthList()
				msg=QMessageBox(self)
				msg.setWindowTitle('account removed from the list!')
				msg.setTextFormat(Qt.RichText)
				msg.setText("But...<br>The access token should be deleted manually from your account.<br>Please visit <a href='https://github.com/settings/tokens'>https://github.com/settings/tokens</a> and delete access tokens you don't use anymore")
				msg.exec_()


		def newPublic(self):
			good = False
			try:
				good = GithubAuthorizator.newPublicCollection()
			except IOError as e:
				QMessageBox.warning(self,'could not write the account file!','Error: %d : %s'%e.args)
			if (good):
				self.updatePublicList()

		def removePublic(self):
			index = self.ui.publicListView.currentIndex()
			good = False
			try:
				good = GithubAuthorizator.removePublicCollection(index.data())
			except IOError as e:
				QMessageBox.warning(self,'could not write the account file!','Error: %d : %s'%e.args)
			if (good):
				self.updatePublicList()

		def updateAuthList(self):
			try:
				data = GithubAuthorizator.listAuthorizations()
			except IOError as e:
				QMessageBox.warning(self,'could not read the account file!','Error: %d : %s'%e.args)
			self.__authModel.setStringList([x['user'] for x in data])

		def updatePublicList(self):
			try:
				data = GithubAuthorizator.listPublicCollections()
			except IOError as e:
				QMessageBox.warning(self,'could not read the account file!','Error: %d : %s'%e.args)
			self.__publicModel.setStringList([x['user'] for x in data])

		def reinitCallback(self):
			try:
				import hpastecollectionwidget
				hpastecollectionwidget.HPasteCollectionWidget._killInstance()
			except:
				pass

	__instance=None

	def __init__(self,parent):
		if(AccountsManager.__instance is None):
			AccountsManager.__instance=AccountsManager.__AccountsManager(parent,Qt.Window)
		else:
			AccountsManager.__instance.setParent(parent)
			AccountsManager.__instance.updateAuthList()
			AccountsManager.__instance.updatePublicList()

	def __getattr__(self, item):
		return getattr(AccountsManager.__instance,item)

if(__name__=='__main__'):
	import sys
	#testing here
	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp = QApplication(sys.argv)

	wid=AccountsManager(None)
	wid.show()

	qapp.exec_()