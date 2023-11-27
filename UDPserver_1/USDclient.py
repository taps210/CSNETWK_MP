import socket
import threading
import os
import time
import math
import re
import pickle

HOST = ''
PORT = 0
is_connected = False

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
userhandle = None
# ! ----------------WRAPPERS----------------------------

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
    global HOST, PORT, is_connected, client_socket
    HOST, PORT = inp[1], int(inp[2])

    try:
        client_socket.settimeout(5)
        client_socket.connect((HOST, PORT))
        print('has connected')
        is_connected = True
        client_socket.sendall(b'join')
        return True
    except Exception as e:
        print("Error: Connection to the File Exchange Server has failed! Please check IP Address and Port Number.")
        print(e)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return False
    
def leave():
    client_socket.sendall(b'leave')

@check_args(2)
def register(inp):
    newHandle = inp[1]
    global userhandle
    userhandle = newHandle
    client_socket.sendall(f"register {newHandle}".encode())
    return True
    

@check_args(2)
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
    
    except FileNotFoundError:
        print(f'Error: File {filename} not found.')
        return False

@register_req
def dir():

        client_socket.sendall('dir\n'.encode())

        try:
            #get data
            data = client_socket.recv(892000)
            if data.decode != '':
                # code for deserializing data
                print(f"Files in the server:")
                received_list = pickle.loads(data)
                for file_name in received_list:
                    print(file_name)

        except Exception as e:
            print(e)
            print(f'Error: Cannot retrieve list of server files.')

@register_req
def get(newinp):
    filename = newinp[1]

    #request
    client_socket.sendall(f'get {filename}\n'.encode())

    try:
        #get data
        data = client_socket.recv(892000)
        if data.decode() != "FileDNE2457093745443":
            if os.path.exists(filename):
                match = re.search('\\((\\d+)\\)', filename)
                count = int(match.group(1)) if match else 0
                count += 1
                base, extension = os.path.splitext(filename)
                new_filename = f"{base}({count}){extension}"

                while os.path.exists(new_filename):
                    count += 1
                    new_filename = f"{base}({count}){extension}"

                with open(new_filename, 'wb') as file:
                    file.write(data)
                    file.flush()
                print(f'File received from Server: {new_filename}')
            else:
                with open(filename, 'wb') as file:
                    file.write(data)
                    file.flush()
                print(f'File received from Server: {filename}')
        else:
            raise FileNotFoundError
    except Exception as e:
        print(f'Error receiving file: File not found in the server.')

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
            leave()
            is_connected = False
            receive_messages()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif command == '/register':
        if is_connected == False:
            print('Error: Register failed. Please connect to the server first.')
        else:   
            shouldReceive = register(newinp)
            if shouldReceive == True:
                receive_messages()
    elif command == '/store':
        if is_connected == False:
            print('Error: Store failed. Please connect to the server first.')
        else:
            shouldReceive = store(newinp)
            if shouldReceive == True:
                receive_messages()
    elif command == '/dir':
        if is_connected == False:
            print('Error: Directory request failed. Please connect to the server first.')
        else:
            dir()
    elif command == '/get':
        if is_connected == False:
            print('Error: Get failed. Please connect to the server first.')
        else:
            get(newinp)
            receive_messages()
    elif command == '/?':
        instructions()
    else:
        print('Error: Command not found.')


