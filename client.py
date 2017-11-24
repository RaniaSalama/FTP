from socket import *
import sys

def send_request(client_socket, request):
    client_socket.send(request.encode())
    response = client_socket.recv(1024)
    print(response)
    return response

def is_valid_response(response):
    if response.startswith('5'):
        return False
    # Wrong username, password.
    elif response.startswith('332'):
        return False
    return True

server_name = sys.argv[1]
server_port = int(sys.argv[2])
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name,server_port))
request = 'START...'
print('send start request first!')
send_request(client_socket, request)
# Start authentication.
username = raw_input('Enter your username: ')
request = 'USER ' + username
send_request(client_socket, request)
password = raw_input('Enter your password: ')
request = 'PASS ' + password
response = send_request(client_socket, request)
if not is_valid_response(response):
    print('Wrong username and/or password!')
    print('Goodbye!')
    client_socket.close()
    exit(0)

# User is authenticated. Start file commands.
data_socket = 0
while True:
    print('Please enter LIST, PORT, RETE, STOR or QUIT')
    command = raw_input('Enter your command: ')
    if command == 'QUIT':
        print('Goodbye')
        client_socket.close()
        exit(0)
    elif command == 'PORT':
        port_number = raw_input('Enter data port number: ')
        request = 'PORT ' + port_number
        send_request(client_socket, request)
        # list on the data connection.
        data_socket = socket(AF_INET,SOCK_STREAM)
        data_socket.bind(('', int(port_number)))
        data_socket.listen(1)
    elif command == 'LIST':
        request = 'LIST'
        send_request(client_socket, request)
        print('before accept')
        data_connection_socket, server_addr = data_socket.accept()
        print('after accept')
        response = data_connection_socket.recv(1024)
        print(response)
    elif command == 'RETE':
        print('In reterive!')
    elif command == 'STOR':
        print('In store!')
    else:
        print('Invalid command!')

