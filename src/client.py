import socket
from multiprocessing import Lock
import platform
from threading import Thread
import time
import os
from time import strftime, gmtime

client_version = "P2P-CI/1.0"
server_port = 7734
server_ip = "10.2.1.223"
client_ip = "10.2.1.223"
client_port = 8080
host_os = platform.platform()

my_rfc = {}
rfc_path = "./rfcs/"
my_rfc_lock = Lock()

status_codes = {
    200 : "OK",
    400 : "Bad Request",
    404 : "Not Found",
    505 : "P2P-CI Version Not Supported"
}

def handle_peers(peer_socket):
    peer_socket.listen()
    while True:
        connection, peer_address = peer_socket.accept()
        peer_requested_message = connection.recv(4096).decode()
        status_code = 200
        status_message = status_codes[status_code]
        peer_requested_rfc = peer_requested_message.split("\n")[0].split(" ")[2]
        peer_requested_version = peer_requested_message.split("\n")[0].split(" ")[-1]
        rfc_file_details = ""
        my_rfc_lock.acquire()
        if client_version != peer_requested_version:
            status_code = 505
            status_message = status_codes[status_code]
        elif peer_requested_rfc not in my_rfc.keys():
            status_code = 404
            status_message = status_codes[status_code]
            my_rfc_lock.release()
        else:
            rfc_file_path = rfc_path + peer_requested_rfc
            client_current_date = strftime("%a, %d %b %Y %X GMT", gmtime())
            rfc_modified_date = strftime("%a, %d %b %Y %X GMT", time.localtime(os.path.getmtime(rfc_file_path)))
            client_os = host_os
            rfc_file_data = ""
            with open(rfc_file_path, 'r') as file_pointer:
                rfc_file_data = file_pointer.read()

            rfc_file_length = str(len(rfc_file_data))
            rfc_file_content_type = "text/text"
            
            rfc_file_details += "Date: " + client_current_date +"\n"
            rfc_file_details += "OS: " + client_os + "\n"
            rfc_file_details += "Last-Modified: " + rfc_modified_date +"\n"
            rfc_file_details += "Content-Length: " + rfc_file_length + "\n"
            rfc_file_details += "Content-Type: " + rfc_file_content_type + "\n"
            rfc_file_details += rfc_file_data + "\n"
            
        my_responded_message = peer_requested_version + " " + status_code + " " + status_message + "\n" + rfc_file_details
        connection.sendall(my_responded_message.encode())
        connection.close()

my_requested_rfc_details = {}
my_requested_rfc_details_lock = Lock()

if __name__ == '__main__':
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind((client_ip,client_port))
    process = Thread(target = handle_peers, args = (peer_socket))
    process.daemon = True
    process.start()
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((server_ip,server_port))
    print("Connected to Server successfully.\n\n")
    while True:
        print("Enter number from below Option.")
        print("1. Add RFC")
        print("2. LookUp RFC")
        print("3. List all availableRFC")
        print("4. Request RFC from peers (Download)")
        print("5. Exit Connection\n")
        option = int(input())
        if option == 1:
            rfc_number_input = int(input("Enter RFC number to be added:\n"))
            rfc_title_input = input("Enter RFC Title associated with entered RFC number:\n")
            request_message = "ADD RFC " + str(rfc_number_input) + " " + str(client_version) + "\nHost: " + socket.gethostbyaddr(client_ip)[0] + "\nPort: " + str(client_port) + "\nTitle: " + rfc_title_input
            server_sock.sendall(request_message.encode())
            my_rfc_lock.acquire()
            my_rfc[rfc_number_input] = rfc_title_input
            my_rfc_lock.release()
            server_response = server_sock.recv(4096).decode()
            print(server_response)
        elif option == 2:
            rfc_number_input = int(input("Enter RFC number for Lookup:\n"))
            rfc_title_input = input("Enter RFC Title associated with entered RFC number:\n")
            request_message = "LOOKUP RFC " + str(rfc_number_input) + " " + str(client_version) + "\nHost: " + socket.gethostbyaddr(client_ip)[0] + "\nPort: " + str(client_port) + "\nTitle: " + rfc_title_input
            server_sock.sendall(request_message.encode())
            server_response = server_sock.recv(4096).decode()
            print(server_response)
            if len(server_response.split("\n")) < 2:
                print("RFC not found with any other peers. Try again Later.")
                continue
            message_by_lines = server_response.split("\n")
            peer_version = message_by_lines[0].split(" ")[0]
            my_requested_rfc_details_lock.acquire()
            my_requested_rfc_details[rfc_number_input] = []
            for peer in range(1,len(message_by_lines)):
                if (peer_version,message_by_lines[peer].split(" ")[-2],message_by_lines[peer].split(" ")[-1],rfc_title_input) not in my_requested_rfc_details[rfc_number_input]:
                    my_requested_rfc_details[rfc_number_input].append((peer_version,message_by_lines[peer].split(" ")[-2],message_by_lines[peer].split(" ")[-1],rfc_title_input))
            my_requested_rfc_details_lock.release()
        elif option == 3:
            request_message = "LIST ALL " + str(client_version) + "\nHost: " + socket.gethostbyaddr(client_ip)[0] + "\nPort: " + str(client_port)
            server_sock.sendall(request_message.encode())
            server_response = server_sock.recv(4096).decode()
            print(server_response)
        elif option == 4:
            rfc_number_input = int(input("Enter RFC number for Lookup:\n"))
            print("Select client index of RFC to be downloaded.")
            count = 1
            my_requested_rfc_details_lock.acquire()
            for peer in my_requested_rfc_details[rfc_number_input]:
                print(str(count) + ". Host Name: " + peer[1] + ", Host Port: " + peer[2])
                count+=1
            client_index_input = int(input())
            peer_request_version = socket.gethostbyname(my_requested_rfc_details[rfc_number_input][client_index_input-1][0])
            peer_request_ip = socket.gethostbyname(my_requested_rfc_details[rfc_number_input][client_index_input-1][1])
            peer_request_port = socket.gethostbyname(my_requested_rfc_details[rfc_number_input][client_index_input-1][2])
            peer_request_title = socket.gethostbyname(my_requested_rfc_details[rfc_number_input][client_index_input-1][3])
            peer_request_message = "GET RFC " + rfc_number_input + " " + my_requested_rfc_details[rfc_number_input][client_index_input-1][0] + "\nHost: " + peer_request_ip + "\nOS: " + str(host_os)
            my_requested_rfc_details_lock.release()

            peer_request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_request_socket.connect((peer_request_ip , peer_request_port))
            peer_request_socket.sendall(request_message.encode())
            
            peer_response_message = ""
            while True:
                current_peer_response_message = peer_request_socket.recv(4096).decode()
                if not current_peer_response_message:
                    break
                peer_request_message += current_peer_response_message

            print(peer_response_message)
            peer_request_socket.close()

            peer_response_message_by_lines = peer_response_message.split("\n")
            if peer_response_message_by_lines[0].split(" ")[1] == "200":
                downloaded_rfc_file = open(rfc_path + rfc_number_input + ".txt", 'w')
                for index in range(6,len(peer_response_message_by_lines)):
                    downloaded_rfc_file.write(peer_response_message_by_lines[index] + "\n")
                downloaded_rfc_file.close()

            my_rfc_lock.acquire()
            my_rfc[rfc_number_input] = peer_request_title
            my_rfc_lock.release()
            request_message = "ADD RFC " + str(rfc_number_input) + " " + str(peer_request_version) + "\nHost: " + socket.gethostbyaddr(client_ip)[0] + "\nPort: " + str(client_port) + "\nTitle: " + peer_request_title
            server_sock.sendall(request_message.encode())
            my_rfc_lock.acquire()
            my_rfc[rfc_number_input] = rfc_title_input
            my_rfc_lock.release()
            server_response = server_sock.recv(4096).decode()

            print(server_response)

        elif option == 5:
            server_sock.close()
            peer_socket.close()
            exit(0)