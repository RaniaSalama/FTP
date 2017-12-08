import os, inspect, stat
from datetime import datetime
import csv
from socket import *
from termcolor import colored

RETR = 'RETR'
STOR = 'STOR'
HOME = 'Home'
UPLOAD_DIR = 'Upload'
SERVER_DATA_PORT = 2227
BUFFER_SIZE = 1024
class Server:
        # Key = username.
        # Value = password.
        users = {}

        def process_get(self, file_path):
                file_size = os.stat(file_path).st_size

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
                                print(colored('Recieved bad sequence of commands.', 'red'))
                                connection_socket.send('503 Bad sequence of commands.')
                        else:
                                print(colored('Invalid command!', 'red'))
                                connection_socket.send('502 Command not implemented.')
                        return False
                if len(command_messgae.split()) != args_no:
                        print(colored('Problem with the command arguments number!', 'red'))
                        connection_socket.send('501 Syntax error in parameters or arguments.')
                        return False
                return True
                
	# Construct and send the ftp response.
	# sentence: the request message.
	# connection_socket: the socket to send the response through.
	def send_ftp_response(self, sentence, connection_socket, client_addr):
                print(colored('Recieved client connection, ready for new user.', 'yellow'))
                connection_socket.send('220 Service ready for new user.')
                # username_message will be like "USER rania" 
                username_message = connection_socket.recv(BUFFER_SIZE).decode()
                # Check for errors.
                if not self.has_no_errors(connection_socket, username_message, 'USER', 2):
                        return
                username = username_message.split()[1]
                print(colored('Recieved username ' + username + '. Waiting for password.', 'yellow'))
                connection_socket.send('331 User name okay, need password.')
                # password_message will be like "PASS XXXX" 
                password_message = connection_socket.recv(BUFFER_SIZE).decode()
                # Check for errors.
                if not self.has_no_errors(connection_socket, password_message, 'PASS', 2):
                        return
                password = password_message.split()[1]
                # Check if username and password is correct.
                if self.check_username_and_password(username, password):
                        print(colored('Recieved correct username and password.', 'green'))
                        connection_socket.send('230 User logged in, proceed.')
                else:
                        print(colored('Recieved wrong username and/or password.', 'red'))
                        connection_socket.send('332 Need account for login.')
                        return
                # Read user file commands.
                command_message = connection_socket.recv(BUFFER_SIZE).decode()
                client_data_port = -1
                while command_message != 'QUIT':
                        # print('Recieved command message = ' + command_message)
                        if command_message.startswith('PORT'):
                                command_split = command_message.split()
                                if len(command_split) != 2:
                                        print(colored('Problem with the command arguments number!', 'red'))
                                        connection_socket.send('501 Syntax error in parameters or arguments.')
                                        return
                                client_data_port = int(command_split[1])
                                print(colored('Changed client data port number to ' + str(client_data_port), 'green'))
                                connection_socket.send('200 Command okay.')
                        elif command_message.startswith('LIST'):
                                data_socket = socket(AF_INET, SOCK_STREAM)
                                connection_socket.send('150 File status okay; about to open data connection.')
                                data_socket.connect((client_addr[0], client_data_port))
                                data_socket.send('HELLO LISTING ...'.encode())
                        elif command_message.startswith(RETR):
                                file_path = os.path.join(HOME, username, command_message.split()[1])
                                if not os.path.isfile(file_path):
                                        connection_socket.send('550 File not Found.')
                                else:
                                        file_size = os.stat(file_path).st_size
                                        connection_socket.send('150 Opening BINARY mode data connection for %s (%d bytes).' %(file_path, file_size))
                                        data_socket = socket(AF_INET, SOCK_STREAM)
                                        data_socket.connect((client_addr[0], client_data_port))
                                        #Sedn file
                                        file = open(file_path)
                                        file_content = file.read(file_size)
                                        data_socket.send(file_content)
                                        data_socket.close()
                        elif command_message.startswith(STOR):
                                ##TODO
                                command_tokens = command_message.split() 
                                file_name = command_tokens[1]
                                file_size = int(command_tokens[2])
                                print 'file_name', file_name, 'file_size', file_size
                                connection_socket.send('150 Opening BINARY mode data connection for %s (%d bytes).' %(file_name, file_size))
                                data_socket = socket(AF_INET, SOCK_STREAM)
                                data_socket.bind(('', SERVER_DATA_PORT))
                                data_socket.listen(1)
                                data_connection_socket, addr = data_socket.accept()
                                cur_file_size = 0
                                uploaded_file = self.cerate_file(file_name, username)
                                while cur_file_size < file_size:
                                        print 'cur_file_size', cur_file_size
                                        content = data_connection_socket.recv(BUFFER_SIZE)
                                        uploaded_file.write(content)
                                        cur_file_size += len(content)
                                uploaded_file.close()
                                data_connection_socket.close()
                                data_socket.close()
                        command_message = connection_socket.recv(BUFFER_SIZE).decode()

        def cerate_file(self, file_name, username, open_mode = 'w'):
                if not os.path.isdir(HOME):
                        os.mkdir(HOME)
                if not os.path.isdir(os.path.join(HOME, username)):
                        os.mkdir(os.path.join(HOME, username))
                if not os.path.isdir(os.path.join(HOME, username, UPLOAD_DIR)):
                        os.mkdir(os.path.join(HOME, username, UPLOAD_DIR))
                file = open(os.path.join(HOME, username, UPLOAD_DIR, file_name), 'w')      
                return file

