import socket
import json 
import threading
from user_profile import UserProfile
from room import Room 
from typing import List 

def broadcast_to_room(room:Room, conn, username:str, is_instructor:bool, message:str): # Takes a room as an argument and sends message to all users in that room 
    for user in room.get_all_users():
        if user.get_username() == username: # Don't send message to ourselves
            continue 
        new_json = {
            "username": username,
            "is_instructor": is_instructor,
            "request": "message",
            "data": [user.get_username(), message]
        }
        handle_client_request(conn, room, new_json)

def validate_instructor(multicast:Room, decoded_json:dict):
    username = decoded_json.get("username")
    instructor = multicast.find_user(username)
    if not instructor:
        return False
    if not instructor.is_instructor:
        return False
    return instructor

def handle_client_request(conn, multicast:Room, decoded_json:dict, temporary_students=None):
    request_type = decoded_json.get("request", "unknown")  # "request" specifies the type
    username = decoded_json.get("username")
    is_instructor = decoded_json.get("is_instructor", False)  # Default to False if not provided

    instructor = validate_instructor(multicast, decoded_json)

    if not username:
        conn.send(json.dumps([False, "Missing 'username' field"]).encode('utf8'))
        print("Missing 'username' field in request")
        return

    if request_type == "add_user": # Logic for this was first built by Chat GPT, and heavily modified as our needs changed 
        # Create a new user
        new_user = UserProfile()
        new_user.username = username
        new_user.is_instructor = is_instructor
        
        if new_user.is_instructor:
            # Add instructor directly to the multicast
            add_response = multicast.add_user(new_user)
            if add_response[0]:
                new_user.set_socket(conn)
            conn.send(json.dumps(add_response).encode('utf8'))
            print(f"Response to add_user (instructor): {add_response}")
        else:
            new_user.set_socket(conn)
            # Add student to the temporary list
            temporary_students.append(new_user)
            response = [True, f"Student {new_user.username} added to the waiting list"]
            conn.send(json.dumps(response).encode('utf8'))
            print(f"Response to add_user (student): {response}")

    elif request_type == "create_room": # Adds all students in waiting list to the multicast
        if not instructor:
            return
        for student in temporary_students:
          multicast.add_user(student)

        temporary_students.clear()
        response = [True, "Multicast room created successfully."]
        conn.send(json.dumps(response).encode('utf8'))
        print("Multicast room created successfully.")

    elif request_type == "message": 
        recipient_username = decoded_json["data"][0]
        message = decoded_json["data"][1]
        sender_room = multicast.get_room_of_user(username)
        recipient_room = multicast.get_room_of_user(recipient_username)
    
        if instructor: # If the sender is the instructor, find the recipient regardless of what room they're in 
            recipient_room.send_message(username, recipient_username, message)
        else: # If the sender is a student, send a message only to someone in the same room 
            sender_room.send_message(username, recipient_username, message)
            

    elif request_type == "broadcast": # Message all users in the current room 
        sender_room = multicast.get_room_of_user(username)
        message = decoded_json["data"][0]
        all_rooms = multicast.breakout_rooms + [multicast]
        
        if instructor: # If sender is instructor, send message to all users in all rooms 
            for room in all_rooms:
                broadcast_to_room(room, conn, username, instructor, message)
        else: # Otherwise, send message to all users in sender's room 
            broadcast_to_room(sender_room, conn, username, is_instructor, message)


    elif request_type == "request": # Request a breakout room ARGS: username of each other student
        multicast.get_instructor().add_breakout_request(decoded_json)
        response = [True, f"Request for breakout room sent."]
        conn.send(json.dumps(response).encode('utf8'))  # Send success response
    
    elif request_type == "show_requests":
        if not instructor:
            return
        conn.send(instructor.display_requests().encode('utf8'))

    elif request_type == "accept": # Accept a breakout room ARGS: index of request in list 
        if not instructor:
            return
        flattened_string:str = ''.join(decoded_json.get("data"))
        index = int(flattened_string)
        request = instructor.get_request(index-1)

        # Add students to a list for breakout room 
        breakout_students = []
        breakout_students.append(multicast.find_user(request["username"]))
        for user in request["data"]:
            breakout_students.append(multicast.find_user(user))

        multicast.create_breakout(breakout_students)

        message = "The Following Students were added to a breakout room: "
        for student in breakout_students:
            message += student.username + ", "
        conn.send(message.encode('utf8'))
    
    elif request_type == "close": # Close a breakout room ARGS: index of active breakout rooms in "show"
        flattened_string:str = ''.join(decoded_json.get("data"))
        index = int(flattened_string)
        multicast.delete_breakout(index-1) 
        response = [True, f"Breakout room {index} closed successfully."]
        conn.send(json.dumps(response).encode('utf8'))  # Send success response
        
    elif request_type == "show": # Prints a list of all users in all rooms
        waiting_message = "\nWaiting List:\n"
        for user in temporary_students:
            waiting_message += json.dumps(user.get_profile_json()) + "\n"
          
        multicast_message = "\nMulticast Room:\n"
        for user in multicast.get_all_users():      
            multicast_message += json.dumps(user.get_username()) + "\n"
            breakout_message = ""
            for index, breakout in enumerate(multicast.breakout_rooms):
                breakout_message += f"Breakout {index+1}:\n"
                for user in breakout.get_all_users():
                    breakout_message += user.username + "\n"
        combined_message = waiting_message + multicast_message + breakout_message
        conn.send(combined_message.encode('utf8'))
    elif request_type == "help": #SHOULD print the list of all possible commands
        #help_command = ''.join(decoded_json.get("data")) #in help|message, this is message
        
        help_command = decoded_json.get("data", [None])[0] if "data" in decoded_json and isinstance(decoded_json["data"], list) else None #THIS LINE was GPT'd #in help|message, this is message
        if not help_command: response = [True, f"Sent all commands."] #was 'help' passed as is? do nothing then.
        elif(help_command == "create_room"): response = [True, f"\033[31mcreate_room\033[0m is an instructor command that lets the instructor create the multicast group. Run as is."]
        elif(help_command == "message"): response = [True, f"message is a command that lets any user send direct messages to a specific user.       Example: message|<recipient name>|Hello World"]
        elif(help_command == "broadcast"): response = [True, f"broadcast is a command that lets any user send a message that is viewable by everyone in the same room.       Example: broadcast|what the sigma?"]
        elif(help_command == "request"): response = [True, f"request is a student command that lets any student user request to be in a breakout room with any other user. Maximum of 8 users allowed.       Example: request|user1|user2|user3..."]
        elif(help_command == "show_requests"): response = [True, f"show_requests is an instructor command that shows the user all student breakout room requests. Run as is."]
        elif(help_command == "accept"): response = [True, f"accept is an instructor command that allows a student breakout room to be granted, based on the show_requests index. See: help|show_requests.       Example: accept|1"]
        elif(help_command == "close"): response = [True, f"close is a command that closes the current room the user is in. This automatically puts them back in the main group. Run as is."]
        elif(help_command == "show"): response = [True, f"show is a command that shows all connected users in the server. Can see users in the waiting room, main room, and other breakout rooms. Run as is."]
        else: response = [False, f"Command not recognized: {help_command}."]
        conn.send(json.dumps(response).encode('utf8')) #because of JSON parsing, had to be a multiline
    else:
        # Handle unknown request types
        response = [False, "Unknown request type"]
        conn.send(json.dumps(response).encode('utf8'))
        print(f"Unknown request type received: {request_type}")    
    
    


def client_handler(conn, addr, multicast, temporary_students): # Handles a separate thread for each client and takes requests using handle_client_requests()
    print(f"Handling connection from {addr}")
    from_client = ''
    
    # This try/catch block was built by Chat GPT as an easy way to get the structure needed to house our handle_client_request function 
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break  # Break if the client closes the connection
        
            from_client += data.decode('utf8')
            try:
                decoded_json = json.loads(from_client)
                from_client = ''  # Clear the buffer after processing the request
            except json.JSONDecodeError:
                conn.send(json.dumps([False, "Invalid JSON format"]).encode('utf8'))
                print("Invalid JSON received")
                continue

            # Handle the client request
            handle_client_request(conn, multicast, decoded_json, temporary_students)

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection from {addr} closed")


def run_server():
    multicast = Room()
    temporary_students: List[UserProfile] = []  # Temporary list for collecting students
    
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname() #ADDED
    ip_address = socket.gethostbyname(hostname)

    # Swap these two lines to do cross-machine instead of local host
    #serv.bind(('localhost', 8080)) 
    serv.bind((ip_address, 8080))

    serv.listen(5)
    print(f"Server started on IP: \033[33m{ip_address}!\033[0m, listening on port 8080...")

    while True:
        conn, addr = serv.accept()
        print(f"Connection established with {addr}")

        # Create a new thread for each client # Chat GPT helped with showing how to do the threading 
        client_thread = threading.Thread( 
            target=client_handler,
            args=(conn, addr, multicast, temporary_students)
        )
        client_thread.start()


run_server()