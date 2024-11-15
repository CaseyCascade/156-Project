import socket
import json 
from user_profile import UserProfile

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user_profile: UserProfile

def register_user():
    global user_profile
    username = "Default Name"
    is_instructor = False

    # Ask for Username 
    user_input = input("Enter a Username: ")
    username = user_input

    # Determine Instructor 
    user_input = input("Are you an Instructor?: ")

    # Convert to boolean
    boolean_value = user_input.lower() in ["true", "1", "yes", "y"]  # Chat GPT Code 
    is_instructor = boolean_value

    if (is_instructor):
        print("Welcome Instructor", username + "!")
    else:
        print("Welcome Student", username + "!")

    user_profile = UserProfile(username, is_instructor)

def compose_request():
    message = input("[>]: ")
    return user_profile.get_request_json(message)


def run_client():
    # The following basic try/catch for connection logic written by ChatGPT, modified and built on by MC 
    # Ask for Username & Instructor 
    register_user()

    try:
        # Connect to Server
        client.connect(('localhost', 8080))
        print("Connected to Server!")

        # Send our User Profile to Server
        client.send(user_profile.get_profile_json().encode())
        from_server = client.recv(4096).decode()
        print("Server Response:", from_server)

        # Enter a loop to get requests and send responses 
        while True:
            message = compose_request() #TODO This functionality is still being built and doesn't do anything on the server side 
            client.send(message.encode())

            from_server = client.recv(4096).decode()
            print("Server Response:", from_server)

    except Exception as e:
        print("An Error Occured:", e)

    finally:
        client.close()
        print("Connection Closed")

run_client()