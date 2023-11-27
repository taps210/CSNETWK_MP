import socket
import threading
import os
import time
import math

HOST = ''
PORT = 0
is_connected = False

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
    global HOST, PORT, is_connected
    HOST, PORT = inp[1], int(inp[2])
    try:
        client_socket.connect((HOST, PORT))
        is_connected = True
        client_socket.sendall(b'join')
        return True
    except:
        print("Error: Connection to the File Exchange Server has failed! Please check IP Address and Port Number.")
        return False
        #return None
    
    

@check_args(1)
@connection_req
def leave(inp):
    client_socket.sendall(b'leave')

@check_args(2)
@connection_req
def register(inp):
    newHandle = inp[1]
    global userhandle
    userhandle = newHandle
    client_socket.sendall(f"register {newHandle}".encode())
    return True
    

@check_args(2)
@connection_req
@register_req
def store(inp):
    filename = inp[1]
    
    if not os.path.exists(filename):
        print(f'Error: File {filename} not found.')
        return False

    try:
        client_socket.sendall(f'store {filename}\n'.encode())

        time.sleep(0.01)

        with open(filename, 'rb') as f:
            data = f.read(892000)
            client_socket.sendto(data, (HOST, PORT)) # send as bytes
            f.close()
        return True

    #kind of redundant but ig this is just to be safe
    except FileNotFoundError:
        print(f'Error: File {filename} not found.')
        return False

@connection_req
@register_req
def dir():
        server_directory = f"./Server"

        if not os.path.exists(server_directory):
            print(f"Directory '{server_directory}' does not exist.")

        try:
            with os.scandir(server_directory) as entries:
                print(f"Files and Directories in '{server_directory}':")
                for entry in entries:
                    print(entry.name)
        except Exception as e:
            print(f"Error accessing the directory: {e}")

@connection_req
@register_req
def get(newinp):
    filename = newinp[1]
    client_socket.sendall(f'get {filename}\n'.encode())

    try:
        with open(filename, 'wb') as file:
            data = client_socket.recv(892000)
            file.write(data)
            file.flush()
    
        print(f'File received from Server: {filename}')
    except Exception as e:
        print(f'Error receiving file: {e}')

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
    - Request directory file list from the server

    /get <filename>
    - Fetch a file from a server

    /?
    - Request command help to output all input syntax commands for references
''')

# def receive_messages():
#     while True:
#         try:
#             data = client_socket.recv(1024)

#             if not data:
#                 print("Server closed the connection.")
#                 break

#             print(data.decode())
#             return data

#         except Exception as e:
#             print(f"Error: {e}")
#             break
#     client_socket.close()


def receive_messages():
    # How to use
    # This collects the message from the server sent through the sendall() method
    # the recv method collects that data.
    # MAKE SURE that every method will send some kind of message. If a method does not send a message
    # spaghettification will ensue
    try:
            data = client_socket.recv(1024)
            print(data.decode())

    except Exception as e:
        #print(f"Error: {e}")
        pass

while True:
    # Read a message from the user and send it to the server
    message = input()

    newinp = message.split()

    command = newinp[0]

    if command[0] != '/':
        print('Error: Command not found.')
        continue

    if command == '/join':
        shouldReceive = join(newinp)
        if shouldReceive == True:
            receive_messages()
    elif command == '/leave':
        if is_connected == False:
            print('Error: Disconnection failed. Please connect to the server first.')
        else:
            leave(newinp)
            is_connected = False
            receive_messages()
    elif command == '/register':
        if is_connected == False:
            print('Error: Register failed. Please connect to the server first.')
        else:   
            shouldReceive = register(newinp)
            if shouldReceive == True:
                receive_messages()
    elif command == '/store':
        shouldReceive = store(newinp)
        if shouldReceive == True:
            receive_messages()
    elif command == '/dir':
        dir()
        # receive_messages()
    elif command == '/get':
        get(newinp)
        receive_messages()
    elif command == '/?':
        instructions()
    else:
        print('Error: Command not found.')


