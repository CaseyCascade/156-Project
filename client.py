import socket
import json
from user_profile import UserProfile

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user_profile: UserProfile


def register_user():
    """
    Registers a user by asking for username and instructor status.
    """
    global user_profile
    print("Welcome to the registration system!")

    # Ask for Username
    while True:
        username = input("Enter a Username: ").strip()
        if username:
            break
        print("Username cannot be empty. Please try again.")

    # Determine if the user is an Instructor
    while True:
        is_instructor_input = input("Are you an Instructor? (yes/no): ").strip().lower()
        if is_instructor_input in ["yes", "y", "true", "1"]:
            is_instructor = True
            break
        elif is_instructor_input in ["no", "n", "false", "0"]:
            is_instructor = False
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    # Confirm and Create Profile
    if is_instructor:
        print(f"Welcome Instructor {username}!")
    else:
        print(f"Welcome Student {username}!")
    user_profile = UserProfile(username, is_instructor)


def compose_request():
    while True:
        request = input("[>] Enter request type (e.g., 'create_room', 'exit'): ").strip()
        if request:
            return request
        print("Request cannot be empty. Please try again.")


def run_client():

    register_user()

    try:
        # Connect to Server
        client.connect(('localhost', 8080))
        print("Connected to Server!")

        # Send initial User Profile to Server
        initial_request = user_profile.get_full_request("add_user")
        client.send(initial_request.encode())
        from_server = client.recv(4096).decode()
        print("Server Response:", from_server)

        # Enter a loop to send and receive requests
        while True:
            # Get the request from the user
            request = compose_request()

            # Handle exit request
            if request.lower() == "exit":
                print("Exiting client...")
                break

            # Send the request to the server
            try:
                client.send(user_profile.parse_raw_request(request).encode())
                from_server = client.recv(4096).decode()
                print("Server Response:", from_server)
            except Exception as e:
                print("Error during communication:", e)
                break

    except Exception as e:
        print("An error occurred:", e)

    finally:
        client.close()
        print("Connection Closed")


if __name__ == "__main__":
    run_client()
