import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 12345

clients = []
clientNames = {}

script_dir = os.path.dirname(os.path.abspath(__file__))
file_save_folder = os.path.join(script_dir, "Server")
os.makedirs(file_save_folder, exist_ok=True)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

def handle_client(conn, addr):
    connPort = addr[1]

    while True:
        try:
            send_back = {}

            data = conn.recv(89200)

            if not data:
                # If data is empty, the client has closed the connection
                clients.remove(conn)
                del(clientNames[connPort])
                conn.close()
                break

            # Check the type of command based on the first word

            command, *args = data.split()
            print(data)
            # ! -- join  --------------------
            if command == b'join':
                clients.append(conn)
                send_back['message'] = 'Connection to the File Exchange Server is successful!'

                # means user was registered
                handle = clientNames.get(connPort)
                if handle != None:
                    send_back['message'] = 'You have reconnected'
                    send_back['success'] = True
                    send_back['handle'] = handle
            # ! -- leave -------------------
            elif command == b'leave':
                clients.remove(conn)
                # remove name
                del(clientNames[connPort])
                send_back['message'] = 'Connection closed. Thank you!'
            # ! -- register ----------------
            elif command == b'register':
                newHandle = args[0].decode()

                if clientNames.get(connPort) != None:
                    send_back['message'] = f'already registered'
                    conn.sendall(send_back['message'].encode())
                    continue

                send_back['message'] = f'Welcome {newHandle}!'

                if newHandle in clientNames.values():
                    send_back['message'] = f'Error: Registration failed. Handle or alias already exists.'
                    send_back['success'] = False
                else:
                    clientNames[connPort] = newHandle

            # ! ---- store
            elif command == b'store':
                filename = args[0].decode()
                print("The filename is " + filename)
                file_path = os.path.join(file_save_folder, filename)

                with open(file_path, 'wb') as f:
                    data, addr = conn.recvfrom(892000) # retrieve bytes from the client
                    print(data)
                    f.write(data)
                f.close()

                send_back['message'] = f'File {filename} stored successfully.'

            elif command == b'get':
                filename = args[0].decode()
                file_path = os.path.join(file_save_folder, filename)

                try:
                    with open(file_path, 'rb') as file:
                        while True:
                            data = file.read(1024)
                            if not data:
                                break
                            conn.sendall(data)
                    print(f'Sent file: {filename}')
                except FileNotFoundError:
                    print(f'Error: File {filename} not found.')
                    conn.sendall(f'Error: File {filename} not found.'.encode())


            else:
                # Handle other types of messages if needed
                print(f"Received unknown command: {command}")
            # Send back responses
            conn.sendall(send_back['message'].encode())

        except socket.error as e:
            print(f"client has left/terminal window has been closed")
            clients.remove(conn)
            del(clientNames[connPort])
            conn.close()
            break

while True:
    conn, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
    client_thread.start()