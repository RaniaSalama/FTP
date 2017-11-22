from socket import *
from server_class import Server
import sys
import threading

# Connection thread to handle each client response.
# connectionSocket: the socket with the client.
def connection_thread(connectionSocket):
    sentence = connectionSocket.recv(1024).decode()
    server = Server()
    response = server.send_ftp_response(sentence, connectionSocket)
    connectionSocket.close()

# Get the args from the commandline.
serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

print 'The server is ready to receive'

while True:
    connectionSocket, addr = serverSocket.accept()
	# Handle each client request in a seperated thread.
    threading.Thread(target=connection_thread, args=(connectionSocket,)).start()