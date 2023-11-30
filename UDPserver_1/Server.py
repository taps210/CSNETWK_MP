#De Leon, Fancis Zaccharie
#Bernardo, Noah
#Yu, Hanz Patrick

import socket
import threading
import os
from datetime import datetime
import pickle

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

            # if not data:
            #     # If data is empty, the client has closed the connection
            #     clients.remove(conn)
            #     del(clientNames[connPort])
            #     conn.close()
            #     break

            # Check the type of command based on the first word

            command, *args = data.split()
            print(data)
            # ! -- join  --------------------
            if command == b'join':
                clients.append(conn)
                send_back['message'] = 'Connection to the File Exchange Server is successful!'
                conn.sendall(send_back['message'].encode())

                # means user was registered
                handle = clientNames.get(connPort)
                if handle != None:
                    send_back['message'] = 'You have reconnected'
                    send_back['success'] = True
                    send_back['handle'] = handle
                    conn.sendall(send_back['message'].encode())
            
            # ! -- leave -------------------
            elif command == b'leave':
                clients.remove(conn)
                # remove name
                #del(clientNames[connPort])
                send_back['message'] = 'Connection closed. Thank you!'
                conn.sendall(send_back['message'].encode())
            
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
                conn.sendall(send_back['message'].encode())

            # ! ---- store
            elif command == b'store':
                filename = args[0].decode()
                print("The filename is " + filename)
                file_path = os.path.join(file_save_folder, filename)

                with open(file_path, 'wb') as f:
                #     while True:
                #         data, addr = conn.recvfrom(8192) # retrieve bytes from the client
                #         if not data:
                #             break
                #         f.write(data)
                #         f.flush()

                # print("done saving file")
                    data, addr = conn.recvfrom(892000) # retrieve bytes from the client
                    print(data)
                    f.write(data)
                    f.close()

                c_datetime = datetime.now()
                f_datetime = c_datetime.strftime('%Y-%m-%d %H:%M:%S')
                send_back['message'] = f'{newHandle}<{f_datetime}>: uploaded {filename}'
                conn.sendall(send_back['message'].encode())

            # ! ---- dir
            elif command == b'dir':
                server_directory = f"./Server"

                if not os.path.exists(server_directory):
                    send_back['message'] = f'Error: Cannot resolve directory target'
                    conn.sendall(send_back['message'].encode())

                try:
                    list_dir = os.listdir(server_directory)
                    serialized_list = pickle.dumps(list_dir)
                    conn.sendall(serialized_list)

                except Exception as e:
                    print(f"Error accessing the directory: {e}")

            # ! ---- get
            elif command == b'get':
                filename = args[0].decode()
                file_path = os.path.join(file_save_folder, filename)
                print(file_path)
                    

                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            data = file.read(892000)
                            #print("Data:" + data.decode())
                            conn.sendall(data)
                        print(f'Sent file: {filename}')
                        print(data)
                        print('--------------------------------------------------')
                        print(data.decode)
                    else:
                        raise FileNotFoundError
                except FileNotFoundError:
                    print(f'Error: File DNE')
                    conn.sendall(f"FileDNE".encode())

                    

            # ! ---- unknown command
            else:
                print(f"Received unknown command: {command}")

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