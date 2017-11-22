from socket import *

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

request = ''

# Parse the response message.
# response: response message.
# filename: name of the file sent.
# command: either ....................................
def parse_response(response, filename, command):


clientSocket.send(request.encode())
response = clientSocket.recv(1024)
# Parse server response and save the file.
parse_response(response, filename, command)
clientSocket.close()