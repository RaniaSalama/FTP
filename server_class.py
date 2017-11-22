import os, inspect, stat
from datetime import datetime
import csv

class Server:
	users = {}
	
	# Load users names and passwords.
	def load_users(self, filename):
		csvfile = open(filename,'rb')
		lines = csv.reader(csvfile, delimiter = ',')
		for line in lines:
			users[line[0]] = line[1]
	

	# Construct and send the ftp response.
	# sentence: the request message.
	# connectionSocket: the socket to send the response through.
	def send_ftp_response(self, sentence, connectionSocket):
		print('here')
		
