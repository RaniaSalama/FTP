from socket import *
from server_class import Server
import sys
import threading

if __name__ == '__main__':
	# Connection thread to handle each client response.
	# connectionSocket: the socket with the client.
	def connection_thread(connection_socket, server, client_addr):
	    sentence = connection_socket.recv(1024).decode()
	    response = server.send_ftp_response(sentence, connection_socket, client_addr)
	    connection_socket.close()

	# Get the args from the commandline.
	server_port = int(sys.argv[1])
	server_socket = socket(AF_INET,SOCK_STREAM)
	server_socket.bind(('', server_port))
	server_socket.listen(1)

	print 'The server is ready to receive'

	server = Server()
	server.load_users()

	while True:
	    connection_socket, client_addr = server_socket.accept()
	    # Handle each client request in a seperated thread.
	    threading.Thread(target=connection_thread, args=(connection_socket,
	                                                     server, client_addr, )).start()
