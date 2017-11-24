import os, inspect, stat
from datetime import datetime
import csv
from socket import *

class Server:
        # Key = username.
        # Value = password.
        users = {}

        # Load users names and passwords.
        def load_users(self):
                USERS_FILE = 'users.csv'
                dir_path = os.path.dirname(os.path.realpath(__file__)) 
                csvfile = open(os.path.join(dir_path, USERS_FILE),'rb')
                lines = csv.reader(csvfile, delimiter = ',')
                for line in lines:
                        self.users[line[0]] = line[1]

        def check_username_and_password(self, username, password):
                if username not in self.users:
                        return False
                if password == self.users[username]:
                        return True
                else:
                        return False

        valid_commands = {'USER', 'PASS', 'PORT', 'LIST', 'RETR', 'STOR', 'QUIT'}
        def is_command_vaid(self, command_message):
                command = command_message.split()[0]
                if command in valid_commands:
                        return True
                else:
                        return False

        def has_no_errors(self, connection_socket, command_messgae, expected, args_no):
                if not command_messgae.startswith(expected):
                        if is_command_vaid(command_messgae):
                                print('Recieved bad sequence of commands.')
                                connection_socket.send('503 Bad sequence of commands.')
                        else:
                                print('Invalid command!')
                                connection_socket.send('502 Command not implemented.')
                        return False
                if len(command_messgae.split()) != args_no:
                        print('Problem with the command arguments number!')
                        connection_socket.send('501 Syntax error in parameters or arguments.')
                        return False
                return True
                
	# Construct and send the ftp response.
	# sentence: the request message.
	# connection_socket: the socket to send the response through.
	def send_ftp_response(self, sentence, connection_socket, client_addr):
                print('Recieved client connection, ready for new user.')
                connection_socket.send('220 Service ready for new user.')
                # username_message will be like "USER rania" 
                username_message = connection_socket.recv(1024).decode()
                # Check for errors.
                if not self.has_no_errors(connection_socket, username_message, 'USER', 2):
                        return
                username = username_message.split()[1]
                print('Recieved username ' + username + '. Waiting for password.')
                connection_socket.send('331 User name okay, need password.')
                # password_message will be like "PASS XXXX" 
                password_message = connection_socket.recv(1024).decode()
                # Check for errors.
                if not self.has_no_errors(connection_socket, password_message, 'PASS', 2):
                        return
                password = password_message.split()[1]
                # Check if username and password is correct.
                if self.check_username_and_password(username, password):
                        print('Recieved correct username and password.')
                        connection_socket.send('230 User logged in, proceed.')
                else:
                        print('Recieved wrong username and/or password.')
                        connection_socket.send('332 Need account for login.')
                        return
                # Read user file commands.
                command_message = connection_socket.recv(1024).decode()
                client_data_port = -1
                while command_message != 'QUIT':
                        print('Recieved command message = ' + command_message)
                        if command_message.startswith('PORT'):
                                command_split = command_message.split()
                                if len(command_split) != 2:
                                        print('Problem with the command arguments number!')
                                        connection_socket.send('501 Syntax error in parameters or arguments.')
                                        return
                                client_data_port = int(command_split[1])
                                print('Changed client data port number to ' + str(client_data_port))
                                connection_socket.send('200 Command okay.')
                        elif command_message.startswith('LIST'):
                                data_socket = socket(AF_INET, SOCK_STREAM)
                                print(client_addr[0])
                                connection_socket.send('150 File status okay; about to open data connection.')
                                data_socket.connect((client_addr[0], client_data_port))
                                data_socket.send('HELLO LISTING ...'.encode())

                        command_message = connection_socket.recv(1024).decode()

