# STUDENT NAME: Nina Rubanovich
# PAWPRINT: NRFGH
# ID: 14364557
# DATE: 10/9/2023
# DESCRIPTION: Client side of client-server socker api.
#               Connects to server and allows users to interact withs server via command line interface.
#               Client remains running until user chooses to exit.

import socket
import sys

# Constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 14557

# Create a socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
print("My chat room client. Version One.\n")

while True:
    user_input = input("> ").strip()

    # Send user input to the server
    client_socket.send(user_input.encode())

    # Receive and display the server's response
    server_response = client_socket.recv(1024).decode()
    print(server_response)

    # Check if the users logs out, and exit program if user logs out
    if "left" in server_response.lower():
        client_socket.close()  # Close the client socket
        sys.exit()  # Exit the client