import socket
import threading
import json
HOST = ''
PORT = 0

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
userhandle = None
# ! ----------------WRAPPERS----------------------------
def connection_req(func):
    def wrapper(*args, **kwargs):
        if client_socket.getsockname() == ('0.0.0.0', 0):
            print('Error: Please connect to the server first.')
            return
        return func(*args, **kwargs)
    return wrapper

def register_req(func):
    def wrapper(*args, **kwargs):
        # Check the condition here
        if userhandle == None:
            print('Error: Please register before sending a message.')
        else:
            return func(*args, **kwargs)
    return wrapper

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
    return json.dumps({"command":"join"})

@check_args(1)
@connection_req
def leave(inp):
    return json.dumps({"command":"leave"})

@check_args(2)
@connection_req
def register(inp):
    newHandle = inp[1]
    global userhandle
    userhandle = newHandle
    return json.dumps({"command":"register", "handle": newHandle})

@check_args(3)
@connection_req
@register_req
def msg(inp):
    handle, message = inp[1], inp[2]
    return json.dumps({"command":"msg", "handle":handle, "message":message} )


@check_args(2)
@connection_req
@register_req
def msgAll(inp):
    message = inp[1]
    return json.dumps({"command":"all", "message": message})

def send_help():
    print(
'''
    List of commands
    ~ to connect to the server app
        /join <server_ip_add> <port>
    ~ to disconnect from the server app
        /leave
    ~ register a unique handle
        /register <handle> 
    ~ send message to all
        /all <message>
    ~ send a direct message
        /msg <handle> <message>
    ~ get list of commands
        /?
''')



def receive_messages():
    while True:
        try:

            data = client_socket.recv(1024)

            data = data.decode()
            data = json.loads(data)

            if data.get('success') != None:
                global userhandle
                if data.get('success'):
                    userhandle = data.get('handle')
                else:
                    userhandle = None
            
            print(data.get('message'))


        except:

            client_socket.close()
            break

receive_thread = threading.Thread(target=receive_messages)

while True:
    # Read a message from the user and send it to the server
    message = input()

    newinp = message.split()

    command = newinp[0]
    if command[0] != '/':
        print('Error: Invalid command.')
        continue
    send_to_sever = ''
    if command == '/join':
        send_to_sever = join(newinp)
        
    elif command == '/leave':
        send_to_sever = leave(newinp)
        
    elif command == '/register':
        send_to_sever = register(newinp)
        
    elif command == '/all':

        newList = [newinp[0]]
        temp = ' '.join(newinp[1:])
        newList.append(temp)
        send_to_sever = msgAll(newList)

        
    elif command == '/msg':

        newList = [newinp[0], newinp[1]]
        temp = ' '.join(newinp[2:])
        newList.append(temp)
        send_to_sever = msg(newList)

    elif command == '/?':
        send_help()
        
    else:
        print('Error: No command was found.')

    if send_to_sever == None:
        continue
    client_socket.sendall(send_to_sever.encode())





