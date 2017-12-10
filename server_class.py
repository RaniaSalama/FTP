import os, inspect, stat
from datetime import datetime
import csv
from socket import *
from stat import S_ISREG, ST_CTIME, ST_MODE, ST_SIZE, S_ISDIR
import time
from termcolor import colored
RETR = 'RETR'
STOR = 'STOR'
HOME = 'Home'
SERVER_DATA_PORT = 2300
BUFFER_SIZE = 2**15
# Get the base directory of the source code, as the upload folder will be next to it.
base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

DIR = 2
FILE = 1
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

        def list_files(self, dirpath):
                # get all entries in the directory w/ stats
                entries = (os.path.join(base_dir, HOME, dirpath, fn) for fn in os.listdir(os.path.join(base_dir, HOME, dirpath)))
                entries = ((os.stat(path), path) for path in entries)
                # leave only regular files and directories, insert creation date
                entries = list((FILE if S_ISREG(stat[ST_MODE]) else DIR, stat[ST_SIZE], stat[ST_CTIME], path)
                           for stat, path in entries if (S_ISREG(stat[ST_MODE]) or S_ISDIR(stat[ST_MODE])))
                #format output
                size_max_size = 0
                date_max_size = 0
                size_max_size = max([len(str(tup[1])) for tup in entries])
                date_max_size = max([len(time.ctime(tup[2])) for tup in entries])
                output = ''
                for f_type, size, cdate, path in entries:
                        output += ('File     ' if f_type == FILE else 'Directory') + '\t' + str(size) + ' ' * (size_max_size- len(str(size))) +'\t' + time.ctime(cdate) + ' ' * (date_max_size - len(time.ctime(cdate))) + '\t' + os.path.basename(path) + '\n'
                return output.strip()
                
        def send_file(self, sock, file_content):
                file_len = len(file_content)
                sent_len = 0
                while sent_len < len(file_content):
                        to_be_sent_len = min(BUFFER_SIZE, file_len - sent_len)
                        sock.send(file_content[sent_len: sent_len + to_be_sent_len])
                        sent_len += to_be_sent_len
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
                                data_socket.send(self.list_files(username).encode())
                        elif command_message.startswith(RETR):
                                file_path = os.path.join(base_dir, HOME, username, command_message.split()[1])
                                if not os.path.isfile(file_path):
                                        connection_socket.send('550 File not Found.')
                                        print('File not found')
                                else:
                                        file_size = os.stat(file_path).st_size
                                        connection_socket.send('150 Opening BINARY mode data connection for %s (%d bytes).' %(file_path, file_size))
                                        data_socket = socket(AF_INET, SOCK_STREAM)
                                        data_socket.connect((client_addr[0], client_data_port))
                                        #Sedn file
                                        file_pointer = open(file_path, 'rb')
                                        file_content = file_pointer.read(file_size)
                                        self.send_file(data_socket, file_content)
                                        data_socket.close()
                                        file_pointer.close()
                                        print('Finished downloading the file.')
                        elif command_message.startswith(STOR):
                                command_tokens = command_message.split() 
                                file_name = command_tokens[1]
                                file_size = int(command_tokens[2])
                                print 'file_name', file_name, 'file_size', file_size
                                connection_socket.send('150 Opening BINARY mode data connection for %s (%d bytes).' %(file_name, file_size))
                                data_socket = socket(AF_INET, SOCK_STREAM)
                                data_socket.connect((client_addr[0], client_data_port))
                                cur_file_size = 0
                                uploaded_file = self.cerate_file(file_name, username)
                                while cur_file_size < file_size:
                                        content = data_socket.recv(BUFFER_SIZE)
                                        uploaded_file.write(content)
                                        cur_file_size += len(content)
                                uploaded_file.close()
                                # data_connection_socket.close()
                                data_socket.close()
                                print('Finished uploading the file.')
                        command_message = connection_socket.recv(BUFFER_SIZE).decode()

        def cerate_file(self, file_name, username, open_mode = 'w'):
                if not os.path.isdir(os.path.join(base_dir, HOME)):
                        os.mkdir(os.path.join(base_dir, HOME))
                if not os.path.isdir(os.path.join(base_dir, HOME, username)):
                        os.mkdir(os.path.join(base_dir, HOME, username))
                file_pointer = open(os.path.join(base_dir, HOME, username, file_name), 'wb')      
                return file_pointer

