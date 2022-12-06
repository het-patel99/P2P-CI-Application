import socket
from multiprocessing import Lock
from threading import Thread


rfc = {}
clients = []
rfc_lock = Lock()
client_lock = Lock()

supported_version = "P2P-CI-v1.0.0"
server_port = 7734
server_ip = socket.gethostbyname(socket.gethostname())

status_codes = {
    200 : "OK",
    400 : "Bad Request",
    404 : "Not Found",
    505 : "P2P-CI Version Not Supported"
}

def handle_client(connection, client_address):

    try:
        while True:
            client_request = connection.recv(65000)
            client_message = client_request.decode("utf-8")
            client_message = client_message.split("\n")
            client_message_header = client_message[0].split(" ")
            method = client_message_header[0]
            client_host_name = client_message[1].split(" ")[-1]
            client_port_number = client_message[2].split(" ")[-1]

            if method == "ADD":              
                rfc_number = client_message_header[2]
                client_version = client_message_header[3]
                rfc_title = client_message[3][7:]

                status_code = 200
                status_message = status_codes[status_code]
                if client_version != supported_version:
                    status_code = 505
                    status_message = status_codes[status_code]
                else:
                    client_lock.acquire()
                    if (client_host_name,client_port_number) not in clients:
                        clients.insert(0,(client_host_name,client_port_number))
                    
                    client_lock.release()

                    rfc_lock.acquire()
                    if (rfc_number,rfc_title) not in rfc.keys():
                        rfc[(rfc_number,rfc_title)] = []
                        rfc[(rfc_number,rfc_title)].insert(0,(client_host_name,client_port_number)) 
                    else:
                        if (client_host_name,client_port_number) not in rfc[(rfc_number,rfc_title)]:
                            rfc[(rfc_number,rfc_title)].insert(0,(client_host_name,client_port_number))

                    rfc_lock.release()
                
                response_message = client_version + " " + str(status_code) + " " + status_message + "\n"
                response_message = response_message + "RFC " + str(rfc_number) + " " + rfc_title + " " + client_host_name + " " + str(client_port_number) + "\n"
                connection.send(response_message.encode("utf-8"))

            elif method == "LOOKUP":
                rfc_number = client_message_header[2]
                client_version = client_message_header[3]
                rfc_title = client_message[3][7:]

                status_code = 200
                status_message = status_codes[status_code]
                client_details = ""

                if client_version != supported_version:
                    status_code = 505
                    status_message = status_codes[status_code]
                else:

                    rfc_lock.acquire()
                    if (rfc_number,rfc_title) not in rfc:
                        status_code = 404
                        status_message = status_codes[status_code]
                    else:
                        for client in rfc[(rfc_number,rfc_title)]:
                            client_details = client_details + "RFC " + str(rfc_number) + " " + rfc_title + " " + str(client[0]) + " " + str(client[1]) + "\n"

                    rfc_lock.release()

                response_message = client_version + " " + str(status_code) + " " + status_message + "\n"
                response_message = response_message + client_details

                connection.send(response_message.encode("utf-8"))

            elif method == "LIST":
                client_version = client_message_header[2]
                status_code = 200
                status_message = status_codes[status_code]
                client_details = ""

                if client_version != supported_version:
                    status_code = 505
                    status_message = status_codes[status_code]
                else:
                    
                    rfc_lock.acquire()
                    for rfc_key in rfc.keys():
                        for client in rfc[rfc_key]:
                            client_details = client_details + "RFC " + str(rfc_key[0]) + " " + str(rfc_key[1]) + " " + str(client[0]) + " " + str(client[1]) + "\n"

                    rfc_lock.release()

                response_message = client_version + " " + str(status_code) + " " + status_message + "\n"
                response_message = response_message + client_details

                connection.send(response_message.encode("utf-8"))
    except:
        status_code = 400
        status_message = status_codes[status_code]
        response_message = client_version + " " + status_code + " " + status_message + "\n"
        connection.send(response_message.encode("utf-8"))

    finally:

        client_lock.acquire()
        if client_address in clients:
            clients.remove(client_address)
        client_lock.release()

        rfc_lock.acquire()
        for rfc_key in rfc.keys():
            if client_address in rfc[rfc_key]:
                rfc[rfc_key].remove(client_address)
                if len(rfc[rfc_key]) == 0:
                    rfc.pop(rfc_key)
        rfc_lock.release()

        connection.close()
        exit(0)

if __name__ == '__main__':
    print("Waiting for Client......\n")
    threads = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((server_ip,server_port))
    sock.listen()

    while True:
        connection, client_address = sock.accept()
        process = Thread(target = handle_client, args = (connection,client_address))
        threads.append(process)
        process.start()
        print("Client Connected: ",client_address)