import socket
import threading
import os

HOST = ''
PORT = 0

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
userhandle = None

# ! ----------------WRAPPERS----------------------------

#Checks if correct ip and port combination
def connection_req(func):
    def wrapper(*args, **kwargs):
        if client_socket.getsockname() == ('0.0.0.0', 0):
            print('Error: Connection to the Server has failed! Please check IP Address and Port Number.')
            return
        return func(*args, **kwargs)
    return wrapper

#Checks if correct users
def register_req(func):
    def wrapper(*args, **kwargs):
        # Check the condition here
        if userhandle == None:
            print('Error: Unregistered user.')
        else:
            return func(*args, **kwargs)
    return wrapper

#Checks if incorrect parameters
def check_args(n):
    def length_decorator(func):
        def wrapper(userInput):
            if len(userInput) != n:
                print('Error: Command parameters do not match or is not allowed.')
            else:
                return func(userInput)
        return wrapper
    return length_decorator
# ! ----------------WRAPPERS----------------------------

@check_args(3)
def join(inp):
    global HOST, PORT
    HOST, PORT = inp[1], int(inp[2])
    try:
        client_socket.connect((HOST, PORT))
        receive_thread.start()
    except:
        print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
        return None
    return b"join"

@check_args(1)
@connection_req
def leave(inp):
    return b"leave"

@check_args(2)
@connection_req
def register(inp):
    newHandle = inp[1]
    global userhandle
    userhandle = newHandle
    return f"register {newHandle}".encode()

@check_args(2)
@connection_req
@register_req
def store(inp):
    filename = inp[1]
    try:
        with open(filename, 'rb') as file:
            file_content = file.read()

        send_to_server = f"store {filename}\n".encode() + file_content
        client_socket.sendall(send_to_server)

    except FileNotFoundError:
        print(f'Error: File {filename} not found.')


def instructions():
    print(
'''
    List of commands

    /join <server_ip_add> <port>
    - Connect to the server application
    
    /leave
    - Disconnect to the server application
    
    /register <handle> 
    - Register a unique handle or alias

    /store <filename>
    - Send file to server

    /dir
    - Request directory file list from a server

    /get <filename>
    - Fetch a file from a server

    /?
    - Request command help to output all input syntax commands for references
''')



def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                print("Server closed the connection.")
                client_socket.close()
                break

            print(data.decode())

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            break

receive_thread = threading.Thread(target=receive_messages)

while True:
    # Read a message from the user and send it to the server
    message = input()

    newinp = message.split()

    command = newinp[0]

    if command[0] != '/':
        print('Error: Command not found.')
        continue

    if command == '/join':
        send_to_server = join(newinp)
    elif command == '/leave':
        send_to_server = leave(newinp)
    elif command == '/register':
        send_to_server = register(newinp)
    elif command == '/store':
        store(newinp)
    elif command == '/dir':
        pass
    elif command == '/get':
        pass
    elif command == '/?':
        instructions()
    else:
        print('Error: Command not found.')

    if send_to_server is None:
        continue
    client_socket.sendall(send_to_server)



