# STUDENT NAME: Nina Rubanovich
# PAWPRINT: NRFGH
# ID: 14364557
# DATE: 10/9/2023
# DESCRIPTION: Server side of client-server socker api. Listens for client connections and implements
#               functionality for the following commands: login, newuser, send, and logout.
#               Maintains a list of active client sockets and login states.
#               Reads and writes user info in a "users.txt" file.

import os
import socket

# Constants
SERVER_IP = "127.0.0.1"
SERVER_PORT = 14557
USERS_FILE = "users.txt"

# Create a Socket and bind it
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)

# Print the server version message
print("My chat room server. Version One.\n")

# Initialize the list to keep track of active client sockets
active_clients = []

# Initialize a dictionary to track the login state of clients
login_state = {}


# Function to load user accounts from users.txt into user account list
def load_user_accounts():
    user_accounts = {}
    try:
        with open(USERS_FILE, "r") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    user, password = parts
                    user_accounts[user] = password
                else:
                    # Handle malformed lines or empty lines in the file
                    print("Skipping malformed line: {}".format(line))
    except FileNotFoundError:
        pass  # Handle the case when the file does not exist

    return user_accounts


# Function to handle login
def handle_login(client_socket, user_accounts, user_input):
    # Check if any user is already logged in
    if any(login_state.values()):
        response = "Denied. Another user is already logged in. You can't login until they log out."
        user_id = None  # Since login is denied, user_id remains None
    else:
        # Initialize user_id with None
        user_id = None

        # Check if input has three parts (correct usage of command is three parts)
        input_parts = user_input.split()
        if len(input_parts) != 3:
            response = "Denied. Must provide both username and password"
        else:
            # Split the user input into command, UserID, and Password
            command, UserID, Password = user_input.split()

            if (user_accounts.get(UserID) != Password) or (UserID not in user_accounts):
                response = "Denied. Username or password incorrect"
            else:
                # Set the login state for the client to True
                login_state[client_socket] = True
                active_clients.append(client_socket)
                response = "Login confirmed"
                user_id = UserID  # Set the user_id when login is confirmed
                print(UserID + " login.")

    # Send the response to the client
    client_socket.send(response.encode())

    return user_id  # Return user_id


# Function to handle logout command
def handle_logout(client_socket, user_id):
    if login_state.get(client_socket, False):
        try:
            active_clients.remove(client_socket)  # Remove the client from the list of active clients
            login_state[client_socket] = False  # Set the login state to False
            response = "{} left".format(user_id)
            print("{} logout.".format(user_id))
            client_socket.send(response.encode())

            # Close the connection between the client and the server
            client_socket.close()

        except Exception as e:
            print("Error handling logout:", e)
    else:
        response = "Denied. You can only log out if you are logged in."
        client_socket.send(response.encode())

        # Close the connection between the client and the server
        client_socket.close()


# Function to handle newuser command
def handle_newuser(client_socket, user_accounts, user_input):
    # Make sure user is not logged in
    if any(login_state.values()):
        response = "Denied. New user accounts can only be created when no user is logged in."
    else:
        # Check if input has three parts
        input_parts = user_input.split()
        if len(input_parts) != 3:
            response = "Denied. Must provide both username and password"
        else:
            # Split the user input into command, UserID, and Password
            command, UserID, Password = user_input.split()

            # Check if user already exists
            if user_accounts.get(UserID):
                response = "Denied. User account already exists."
            # Check lengths
            elif len(UserID) < 3 or len(UserID) > 32:
                response = "Denied. UserID length should be between 3 and 32 characters."
            elif len(Password) < 4 or len(Password) > 8:
                response = "Denied. Password length should be between 4 and 8 characters."
            elif user_accounts.get(UserID):
                response = "Denied. User account already exists."
            else:
                # Create the users.txt file if it doesn't exist
                if not os.path.exists(USERS_FILE):
                    open(USERS_FILE, 'w').close()

                # Save the new user account to users.txt
                with open(USERS_FILE, "a") as file:
                    file.write("{} {}\n".format(UserID, Password))
                response = "New user account created. Please login."
                print("New user account created.")

                # Update the user_accounts dictionary with the new user
                user_accounts[UserID] = Password

    # Send the response to the client
    client_socket.send(response.encode())


# Function to handle send command
def handle_send(client_socket, user_input, user_id):
    if login_state.get(client_socket, False):  # Check if the client is logged in
        if not user_input.startswith("send "):
            response = "Denied. Invalid command. Usage: send message"
        else:
            message = user_input[len("send "):]  # Extract the message part

            # Check message lengths
            if not message:
                response = "Denied. Please provide a message to send."
            elif len(message) > 256:
                response = "Denied. Message size should be 256 characters or less."
            else:
                # Prepend the message with the UserID
                message_with_user = "{}: {}".format(user_id, message)

                # Broadcast the message to connected client
                for client in active_clients:
                    if client != client_socket:
                        client.send(message_with_user.encode())

                response = message_with_user
                print(message_with_user)
    else:
        response = "Denied. Please login first."

    # Send the response to the client
    client_socket.send(response.encode())


# Handle client connections
while True:
    client_socket, client_address = server_socket.accept()

    # Initialize the user accounts dictionary
    user_accounts = load_user_accounts()

    # Define user_id within the loop scope
    user_id = None  # Initialize user_id

    # Handle client commands here
    while True:
        try:
            user_input = client_socket.recv(1024).decode()
            if not user_input:
                break  # Client disconnected

            if user_input.startswith("newuser"):
                handle_newuser(client_socket, user_accounts, user_input)
            elif user_input.startswith("login"):
                user_id = handle_login(client_socket, user_accounts, user_input)
            elif user_input.startswith("send"):
                handle_send(client_socket, user_input, user_id)
            elif user_input == "logout":
                handle_logout(client_socket, user_id)
                break  # Exit the loop when a user logs out
            elif user_input is None:
                print()
            else:
                response = "Invalid command"
                client_socket.send(response.encode())
        except OSError as e:
            # Handle exceptions when the client socket is closed or no longer valid
            print("Error handling client:", e)
            break  # Exit the loop on error

    client_socket.close()  # Ensure the client socket is closed
