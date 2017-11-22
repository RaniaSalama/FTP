import os, inspect, stat
from datetime import datetime

class Server:
	# Construct and send the ftp response.
	# sentence: the request message.
	# connectionSocket: the socket to send the response through.
    def send_ftp_response(self, sentence, connectionSocket):