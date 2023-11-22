import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 12345

clients = []
clientNames = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

def handle_client(conn, addr):

    connPort = addr[1]

    while True:
        try:
            send_back = {}

            data = conn.recv(1024)
            
            message = data.decode()
            # assumes everything is in json
            cmdDict = json.loads(message)

            # print(type(message))
            command= cmdDict.get('command')

            # ! -- join  --------------------
            if command == 'join':
                clients.append(conn)
                send_back['message'] = 'Connection to the Message Board Server is successful!'

                # means user was registered
                handle = clientNames.get(connPort)
                if handle != None:
                    send_back['message'] = 'You have reconnected'
                    send_back['success'] = True
                    send_back['handle'] = handle
            # ! -- leave -------------------
            if command == 'leave':
                clients.remove(conn)
                # remove name
                del(clientNames[connPort])
                send_back['message'] = 'Connection closed. Thank you!'

            # ! -- register ----------------
            if command == 'register':
                newHandle = cmdDict.get('handle')
                
                if clientNames.get(connPort) != None:
                    send_back['message'] = f'already registered'
                    send_back = json.dumps(send_back)
                    conn.sendall(send_back.encode())
                    continue

                send_back['message'] = f'Welcome {newHandle}!'

                if newHandle in clientNames.values():
                    send_back['message'] = f'Error: Registration failed. Handle or alias already exists.'
                    send_back['success'] = False
                else:
                    clientNames[connPort] = newHandle

                


            # ! ---- send all
            if command == 'all':
                message = cmdDict.get('message')
                sender = clientNames[connPort]
                message = f'{sender} : {message}'


                send_back['message'] = message

                message = {'message': message}
                message = json.dumps(message)
                for client in clients:
                    if client != conn:
                        client.sendall(message.encode())

            # ! -- send to handle        
            if command == 'msg':
                message = cmdDict.get('message')
                handle = cmdDict.get('handle')
                sender = clientNames.get(connPort)

                send_back['message'] = f'[To {handle}] : {message}'
                if handle not in clientNames.values():
                    send_back['message'] = 'Error: Handle or alias not found.'
                
                # ? this is to find port number of client
                handle_port = None
                for port, handlee in clientNames.items():
                    # find port number
                    if handle == handlee:
                        handle_port = port
                # ? find the client that matches the port number
                for client in clients:
                    if handle_port == client.getpeername()[1]:
                        #send here?
                        message = f'[From {sender}] : {message}'
                        message = json.dumps({'message': message})
                        client.sendall(message.encode())
                


            # send back
            send_back = json.dumps(send_back)
            conn.sendall(send_back.encode())


        except socket.error as e:
            print(f"client has left/terminal window has been closed")
            clients.remove(conn)
            del(clientNames[connPort])
            conn.close()
            break

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            break

        except Exception as e:
            print(e)
            break

while True:

    conn, addr = server_socket.accept()

    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
    client_thread.start()
