from socket import *
from server_class import Server
import sys
import threading

USERS_FILE = 'users.csv'

# Key = username.
# Value = password.
users = {}

# Key = client_IP:client_port.
# Value = state number.
# State 0 --> need authorization.
# State 1 --> provided username and still need to provide password.
# State 2 --> authorized.
current_users_states = {}

# Key =  client_IP:client_port.
# Value = provided username if any.
current_users_username = {}

	
# Load users names and passwords.
def load_users(filename):
    csvfile = open(filename,'rb')
    lines = csv.reader(csvfile, delimiter = ',')
    for line in lines:
        users[line[0]] = line[1]

# Connection thread to handle each client response.
# connectionSocket: the socket with the client.
def connection_thread(connectionSocket):
    sentence = connectionSocket.recv(1024).decode()
    # Authorize here
    # ..............................
    
    # Call server for list, store and reterive operations.
    server = Server()
    response = server.send_ftp_response(sentence, connectionSocket)
    connectionSocket.close()

# Get the args from the commandline.
serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

# Load users in the system.
load_users(USERS_FILE)

print 'The server is ready to receive'

while True:
    connectionSocket, addr = serverSocket.accept()
    # Handle each client request in a seperated thread.
    threading.Thread(target=connection_thread, args=(connectionSocket,)).start()
