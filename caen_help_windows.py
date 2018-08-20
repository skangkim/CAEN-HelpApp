# CAEN HELP APP
# Python 3 and PyQT5
# Windows version written by Sukang Kim
import sys
from PyQt5.QtWidgets import QMessageBox, QPlainTextEdit, QGridLayout, QFileDialog, QComboBox, QGroupBox, QPushButton, QWidget, QTextEdit, QApplication, QMainWindow, QLabel, QHBoxLayout, QSplitter, QStyleFactory
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QScreen
import socket, webbrowser
import subprocess
import os
# email 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import email.encoders
# get uniqname
import getpass
# time
import time
# log
import logging

# global variables 
files_arr = [] # array of attached files and screenshots
sc_count = 0 # number of screenshots taken 
saved = -1 # number of screenshots saved


# Main Window
class MainWindow(QWidget):
	def __init__ (self):
		super(MainWindow, self).__init__()
		# make splitter
		self.initUI()

	def getSysInfo(self):
		self.hostname = socket.gethostname()
		self.ip = socket.gethostbyname(self.hostname)

	def initUI(self):

		hbox = QHBoxLayout(self)

		splitter1 = QSplitter(Qt.Vertical) # for buttons
		user_info = QSplitter(Qt.Vertical) # for contact and system information
		
                # contact information 
		contact_box = QGroupBox('Contact')
		contact_layout = QHBoxLayout()
		contact_label = QLabel("(734) 764 2236\ncaen@umich.edu", self)
		contact_label.setAlignment(Qt.AlignCenter)
		contact_layout.addWidget(contact_label)
		contact_box.setLayout(contact_layout)

                # system information 
		sys_info_box = QGroupBox('System Info')
		sys_info_layout = QHBoxLayout()
		self.getSysInfo()
		sys_info = "{hostname}\n{ip}".format(hostname=self.hostname, ip = self.ip)
		sys_info_label = QLabel(sys_info)
		sys_info_label.setAlignment(Qt.AlignCenter)
		sys_info_layout.addWidget(sys_info_label)
		sys_info_box.setLayout(sys_info_layout)

                # add contact & system info to user_info splitter 
		user_info.addWidget(contact_box)
		user_info.addWidget(sys_info_box)

                # button
		button_report = QPushButton('Report a Problem', self)
		button_report.clicked.connect(self.show_sub_window)
		self.w = None
		button_FAQ = QPushButton('Visit the FAQ', self)
		button_FAQ.clicked.connect(self.visitFAQ)
		splitter_button = QSplitter(Qt.Vertical)
		splitter_button.addWidget(button_report)
		splitter_button.addWidget(button_FAQ)

		# add buttons to splitter 
		splitter1.addWidget(user_info)
		splitter1.addWidget(splitter_button)

                # main splitter
		splitter2 = QSplitter(Qt.Horizontal)

		# open the caen logo
		logo = QLabel(self)
		logo_pixmap = QPixmap('caen.png')
		logo.setPixmap(logo_pixmap)

		splitter2.addWidget(logo)
		splitter2.addWidget(splitter1)
		hbox.addWidget(splitter2)
		self.setLayout(hbox)
		QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

		self.setGeometry(300,300,300,200)
		self.setWindowTitle('CAEN Help')
		self.show()

	# open the web browser
	def visitFAQ(self):
		webbrowser.open('http://caenfaq.engin.umich.edu/')

	def show_sub_window(self):
		self.w = SubWindow()
		self.w.show()


# Questionnaries window
class SubWindow(QWidget):
	def __init__(self):
		global saved
		super(SubWindow, self).__init__()
		self.openWindow()

	def openWindow(self):
		sub_box = QHBoxLayout(self)

		# Q1
		splitter1 = QSplitter(Qt.Horizontal)
		Q1 = QLabel("Is the problem with this computer?")
		self.A1 = QComboBox(self)
		self.A1.addItem("Yes")
		self.A1.addItem("No")
		Q1.resize(self.width()/2, 50)
		self.A1.resize(self.width()/2, 50)
		splitter1.addWidget(Q1)
		splitter1.addWidget(self.A1)
		splitter1.resize(self.width(), 50)

		# Q2
		splitter2 = QSplitter(Qt.Horizontal)
		Q2 = QLabel("Please describe this issue:")
		Q2.resize(self.width()/2,200)
		self.A2 = QPlainTextEdit(self)
		self.A2.resize(self.width()/2,200)
		splitter2.addWidget(Q2)
		splitter2.addWidget(self.A2)
		splitter2.resize(self.width(),200)
		
		# Q3
		splitter3 = QSplitter(Qt.Horizontal)
		Q3 = QLabel("Attach any useful information:\n(Files have to be under 10MB \nincluding the screenshots)")
		A3 = QPushButton("Select files")
		A3.clicked.connect(self.getfile)
		Q3.resize(self.width()/2, 50)
		A3.resize(self.width()/2, 50)
		splitter3.addWidget(Q3)
		splitter3.addWidget(A3)
		splitter3.resize(self.width(), 50)

		# Q4
		splitter4 = QSplitter(Qt.Horizontal)
		Q4 = QLabel("Press this button to take a screenshot \nof the entire screen.\nOnly the two screenshots are sent.")
		A4 = QPushButton("Take a screenshot")
		A4.clicked.connect(self.showScreenshotWindow)
		Q4.resize(self.width()/2, 50)
		A4.resize(self.width()/2, 50)
		splitter4.addWidget(Q4)
		splitter4.addWidget(A4)
		splitter4.resize(self.width(), 50)

		# Submit
		splitter5 = QSplitter(Qt.Horizontal)
		submit = QPushButton("Submit Report")
		submit.clicked.connect(self.submitReport)
		splitter5.addWidget(submit)
		splitter5.resize(self.width(), 50)

		splitter = QSplitter(Qt.Vertical)  
		splitter.addWidget(splitter1) 
		splitter.addWidget(splitter2) 
		splitter.addWidget(splitter3) 
		splitter.addWidget(splitter4) 
		splitter.addWidget(splitter5) 

		sub_box.addWidget(splitter)
		self.setGeometry(300,300,600,400)
		self.setWindowTitle("Report Window")
	
        # save attached files to files_arr
	def getfile(self):
		self.files_list, _ = QFileDialog.getOpenFileNames(self, directory="C:\TEMP") 
		global files_arr
		for i in self.files_list:
			files_arr.append(i)

        # open screenshot window
	def showScreenshotWindow(self):
		if(saved < 1):
			self.w = ScreenShotClass()
			self.w.show()
		else:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setText("You already attached 2 screenshots!")
			msg.exec_()
        # email window 
	def sendEmail(self):
		global files_arr
		global saved

                # set up email 
		SERVER = "mx1.a.mail.umich.edu"
		send_email = MIMEMultipart()
		UserName = getpass.getuser()
		send_email['From'] = "{username}@umich.edu".format(username=UserName)
		send_email['To'] = "sukang@umich.edu" # TODO: edit this email address 
		send_email['Subject'] = "Issue Report"
		message = "Issue Report from {username}\nDescription of the issue: \n{description}".format(username = UserName, description=self.A2.toPlainText())
		send_email.attach(MIMEText(message, 'plain'))

		# open attached files & screenshot
		for f in files_arr:
			part = MIMEBase('application', "octet-stream")
			part.set_payload(open(f, "rb").read())
			email.encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename={filename}'.format(filename = f))
			send_email.attach(part)

		# get necessary information the computer is the issue
		if str(self.A1.currentText()) == "Yes":
                        # powershell script running .. 
			proc = subprocess.Popen(["powershell.exe",'-executionpolicy', 'bypass' , '-noninteractive', '-nologo', '-file', "\\\\adsroot.itcs.umich.edu\\sysvol\\adsroot.itcs.umich.edu\\scripts\\engin\\helpdeskapp\\caeninfo.ps1"], stdout = sys.stdout)
			proc.wait()
			filename = "info.txt"
			self.setWindowTitle("Report Window [Sending your report ...]")
			try: 
				f = open(filename)
				attachment = MIMEText(f.read())
				attachment.add_header('Content-Disposition', 'attachment', filename=filename)
				send_email.attach(attachment)
			except Exception as e:
				send_email.attach(MIMEText('\nUnable to attach info.txt because of this error:\n{error}'.format(error=e), 'plain'))

                # send email 
		server = smtplib.SMTP(SERVER)
		server.starttls()
		server.sendmail(send_email['From'], send_email['To'], send_email.as_string())
		server.quit()		

	def submitReport(self):
		global files_arr
		global saved
		global sc_count
		self.setWindowTitle("Report Window [Gathering Information...]")
		
		#check if log exists
		log_file = "C:\\temp\\caenHelpAppLog.log"
		if(os.path.isfile(log_file) == True): 
			time_diff = time.time() - os.path.getmtime(log_file) # in seconds

                # check if the user submitted more than 5 minutes ago 
		if(os.path.isfile(log_file) != True) or (os.path.isfile(log_file) == True and ( time_diff > 60*5)):

			# check the size (in Bytes) of files_arr
			file_size = 0
			for f in files_arr:
				file_size += os.path.getsize(f)
                        # <= 10MB 
			if file_size/1000000 <= 10:
				self.sendEmail()
				# logging
				logging.basicConfig(filename = "C:\\temp\\caenHelpAppLog.log", level = logging.INFO)
				logger = logging.getLogger("caen-Help-App")
				logger.info("Sent email @ {time}".format(time = time.ctime(time.time())))
				self.setWindowTitle("Report Window [Sent!]")

				# remove files in TEMP
				for i in range(0,sc_count):
					if(os.path.isfile("sc_{count}.png".format(count=i))):
						os.remove("sc_{count}.png".format(count=i))
				if os.path.isfile("info.txt"):
					os.remove("info.txt")

                                # sent pop-up 
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Information)
				msg.setStandardButtons(QMessageBox.Ok)
				msg.setText("Your report has been sent. Thank you!")
				result = msg.exec_()
				if result == QMessageBox.Ok:
					msg.setEscapeButton(QMessageBox.Close)

				# close the questionarrie window
				self.close()
			# > 10MB		
			else:

				# delete files
				for i in range(0,saved):
					os.remove("sc_{count}.png".format(count=saved))
				files_arr = []

				# error message pop-up
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Information)
				msg.setStandardButtons(QMessageBox.Ok)
				msg.setText("Attached files exceeded 10MB.\n Your files and screenshots have been deleted.")
				
				saved = -1
				sc_count = 0
				msg.exec_()

				# remove info.txt 
				if os.path.isfile("info.txt"):
					os.remove("info.txt")
				return

		else:
                        # submitted <= 5 minutes ago 
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setText("You already submitted the report {minutes} minute(s) ago.".format(minutes = int(round(time_diff/60))))
			msg.setDetailedText("You can only send report every 5 minutes. \n Please try again later.")
			result = msg.exec_()
			if result == QMessageBox.Ok:
				msg.setEscapeButton(QMessageBox.Close)

		self.setWindowTitle("Report Window")


# Screenshot window 
class ScreenShotClass(QWidget):

	def __init__(self, parent=None): # Initialize screenshot window
		super(ScreenShotClass, self).__init__()
		self.preview_screen = QApplication.primaryScreen().grabWindow(0)
		self.settings()
		self.create_widgets()
		self.set_layout()

	def settings(self):
		self.resize(500, 500)
		self.setWindowTitle("Screenshoter")

	def create_widgets(self): 
		global sc_count
		self.img_preview = QLabel()
		self.img_preview.setPixmap(self.preview_screen.scaled(350,350,
								 Qt.KeepAspectRatio, Qt.SmoothTransformation))
		self.btn_save_screenshot = QPushButton("Save screenshot")
		self.btn_new_screenshot = QPushButton("New screenshot")

		# signals connections
		self.btn_save_screenshot.clicked.connect(self.save_screenshot)
		self.btn_new_screenshot.clicked.connect(self.new_screenshot)

	def set_layout(self):
		self.layout = QGridLayout(self)
		self.layout.addWidget(self.img_preview, 0, 0, alignment=Qt.AlignCenter)
		self.layout.addWidget(self.btn_save_screenshot, 2,0, alignment=Qt.AlignLeft)
		self.layout.addWidget(self.btn_new_screenshot, 2, 0, alignment=Qt.AlignRight)
		self.setLayout(self.layout)

	def save_screenshot(self):
		global sc_count
		global files_arr
		global saved
		filename = "sc_{num}.png".format(num = saved+1) 
		if saved > 0: # if saved more than 2 screenshots 
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setText("You already saved 2 screenshots!\nClosing the screenshot window.")
			msg.setDetailedText("To attach more screenshot, add it to attachments.")
			result = msg.exec_()
			if result == QMessageBox.Ok:
				self.close()
			msg.setEscapeButton(QMessageBox.Close)

		elif (saved == -1 or saved != (sc_count - 1)) : # prevent saving the same file 
			self.preview_screen.save(filename, "png")
			files_arr.append(filename)
			sc_count += 1 
			saved += 1
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setText("Screenshot was saved! You can take {no_sc} more screenshot(s)".format(no_sc = 1 - saved))
			result = msg.exec_()
			msg.setEscapeButton(QMessageBox.Close)

		else: 
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setText("This screenshot has already been saved. \nClick \"New Screenshot\" to take {no_sc} more screenshot(s)".format(no_sc = 1 - saved))
			result = msg.exec_()
			msg.setEscapeButton(QMessageBox.Close)

	def new_screenshot(self):
		global sc_count
		global saved
		if saved > 1: # prevent taking more than two screenshots
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setText("You already saved 2 screenshots!\nClosing the screenshot window.")
			msg.setDetailedText("To attach more screenshot, add it to attachments.")
			result = msg.exec_()
			if result == QMessageBox.Ok:
				self.close()
			msg.setEscapeButton(QMessageBox.Close)
		else:
			if(sc_count > saved + 1): sc_count = saved +1
			sc_count += 1
			QTimer.singleShot(1000, self.take_screenshot)

	def take_screenshot(self):
		self.preview_screen = QApplication.primaryScreen().grabWindow(0)
		self.img_preview.setPixmap(self.preview_screen.scaled(350,350,
							 Qt.KeepAspectRatio, Qt.SmoothTransformation))
		self.show()



# you need one QApplication instance per application
# pass in sys.argv to allow cmd arguments for your app
# if you don't need cmd arguments then app = QApplication() is fine
app = QApplication(sys.argv)

# create window
window = MainWindow() # can only hold a single widget
window.show() # windows are hidden by default

# start the event loop
app.exec_()

# remove files in TEMP
for i in range(0,sc_count):
	if(os.path.isfile("sc_{count}.png".format(count=i))):
		os.remove("sc_{count}.png".format(count=i))

	if os.path.isfile("info.txt"):
		os.remove("info.txt")
		
#app wont reach here until you exit and the event loop has stopped
