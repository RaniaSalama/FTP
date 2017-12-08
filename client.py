from socket import *
import sys
from termcolor import colored
import os
import socket as sck
CLIENT_DIR = "Client"
BUFFER_SIZE = 2048
RETR = 'RETR'
STOR = 'STOR'
DEFAULT_PORT = 3422
CIENT_DIR = 'Client'
FILE_NOT_FOUND = 550
SERVER_DATA_PORT = 2227
def send_request(client_socket, request):
    client_socket.send(request.encode())
    response = client_socket.recv(1024)
    response = response.strip()
    if response.strip() != '':
        response_code = get_status_code(response)
        if response_code >= 500:
            print colored('>>Server response: %s' % (response), 'red')
        else:
            print colored('>>Server response: %s' %(response), 'green')
    return response

def is_valid_response(response):
    if response.startswith('5'):
        return False
    # Wrong username, password.
    elif response.startswith('332'):
        return False
    return True
def create_data_connection(client_socket, port_number):
    request = 'PORT ' + str(port_number)
    send_request(client_socket, request)
    # list on the data connection.
    data_socket = socket(AF_INET,SOCK_STREAM)
    data_socket.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)

    data_socket.bind(('', port_number))
    data_socket.listen(1)
    return data_socket
get_status_code  = lambda x : int(x.split()[0])
def cerate_file(file_name, open_mode = 'w'):
    if not os.path.isdir(CLIENT_DIR):
        os.mkdir(CLIENT_DIR)
    if not os.path.isdir(os.path.join(CLIENT_DIR, username)):
        os.mkdir(os.path.join(CLIENT_DIR, username))
    file = open(os.path.join(CLIENT_DIR, username, file_name), 'w')      
    return file


if __name__ == '__main__':
    server_name = sys.argv[1]
    server_port = int(sys.argv[2])
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name,server_port))
    request = 'START...'
    print colored('send start request first!', 'yellow')
    send_request(client_socket, request)
    # Start authentication.
    username = raw_input(colored('Enter your username: ', 'yellow'))
    request = 'USER ' + username
    send_request(client_socket, request)
    password = raw_input(colored('Enter your password: ', 'yellow'))
    request = 'PASS ' + password
    response = send_request(client_socket, request)
    if not is_valid_response(response):
        print(colored('Wrong username and/or password!', 'red'))
        print(colored('Goodbye!', 'red'))
        client_socket.close()
        exit(0)

    # User is authenticated. Start file commands.
    data_socket = 0
    port_number = -1
    while True:
        print 'Please enter LIST, PORT, GET, STOR or QUIT'
        input_str = raw_input('Enter your command: ').split()
        command = input_str[0].lower()
        if command == 'quit':
            print('Goodbye')
            send_request(client_socket, 'QUIT')
            client_socket.close()
            if data_socket:
                data_socket.close()
            exit(0)
        elif command == 'port':
            if len(input_str) < 2:
                print colored('Error please enter port <port number>', 'red')
                continue
            try:
                port_number = int(input_str[1])
                DEFAULT_PORT = port_number
            except ValueError:
                print colored('Error please enter port <port number>', 'red')
                continue
            data_socket = create_data_connection(client_socket, port_number)
        elif command == 'list':
            request = 'LIST'
            send_request(client_socket, request)
            data_connection_socket, server_addr = data_socket.accept()
            response = data_connection_socket.recv(1024)
            print(response)
        elif command == 'get':
            if len(input_str) < 2:
                print colored('Error please enter get <file name>', 'red')
                continue
            if port_number == -1:
                port_number = DEFAULT_PORT
                data_socket = create_data_connection(client_socket, DEFAULT_PORT)
            file_name = input_str[1]    
            request = '%s %s' %(RETR, file_name)
            response = send_request(client_socket, request)
            status_code = get_status_code(response)
            if status_code == FILE_NOT_FOUND:
                print colored('File \'%s\' not found' %(file_name), 'red')
                continue
            file_size = int(response[response.index('(')+1 : response.index(')')].split()[0])
            downloaded_file = cerate_file(file_name)
            cur_file_size = 0
            data_connection_socket, addr = data_socket.accept()
            while cur_file_size < file_size:
                content = data_connection_socket.recv(BUFFER_SIZE)
                downloaded_file.write(content)
                cur_file_size += len(content)
            downloaded_file.close()
            data_connection_socket.close()
            data_socket.close()
            port_number = -1
        elif command == 'stor':
            if len(input_str) < 2:
                print colored('Error please enter get <file name>', 'red')
                continue
            if port_number == -1:
                port_number = DEFAULT_PORT
                data_socket = create_data_connection(client_socket, DEFAULT_PORT)
            file_name = input_str[1]
            if os.path.isfile(file_name):
                file_size = os.stat(file_name).st_size
                request = '%s %s %d' %(STOR, file_name, file_size)
                response = send_request(client_socket, request)
                status_code = get_status_code(response)
                file = open(file_name, 'r')
                file_content = file.read(file_size)

                data_connection_socket, addr = data_socket.accept()

                # data_socket = socket(AF_INET, SOCK_STREAM)
                # data_socket.connect((server_name, SERVER_DATA_PORT))
                # data_socket.send(file_content)
                data_connection_socket.send(file_content)
                data_socket.close()
                data_connection_socket.close()
                file.close()
                port_number = -1
            else:
                print 'File \'%s\' not found'
        else:
            print colored('Invalid command!', 'red')

