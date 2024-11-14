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

    #TODO Here we can assign a Student or Instructor class that gives different permissions 
    if (is_instructor):
        print("Welcome Instructor", username + "!")
    else:
        print("Welcome Student", username + "!")

    user_profile = UserProfile(username, is_instructor)


register_user()
client.connect(('localhost', 8080))
client.send(user_profile.get_profile_json().encode())
from_server = client.recv(4096)
client.close()
print (from_server.decode())