import socket
import json 
import threading
from user_profile import UserProfile
from room import Room 
from typing import List 

def broadcast_to_room(room:Room, conn, username:str, is_instructor:bool, message:str):
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
        #response = [False, f"User '{username}' not found."]
        return False

    if not instructor.is_instructor:
        #response = [False, f"User '{username}' is not an instructor."]
        return False
    
    return instructor

def handle_client_request(conn, multicast:Room, decoded_json:dict, temporary_students=None):
    request_type = decoded_json.get("request", "unknown")  # "request" specifies the type
    username = decoded_json.get("username")
    is_instructor = decoded_json.get("is_instructor", False)  # Default to False if not provide

    instructor = validate_instructor(multicast, decoded_json)

    if not username:
        conn.send(json.dumps([False, "Missing 'username' field"]).encode('utf8'))
        print("Missing 'username' field in request")
        return

    if request_type == "add_user":
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
            multicast_message += json.dumps(user.get_profile_json()) + "\n"
            breakout_message = ""
            for index, breakout in enumerate(multicast.breakout_rooms):
                breakout_message += f"Breakout {index+1}:\n"
                for user in breakout.get_all_users():
                    breakout_message += user.username + "\n"
        combined_message = waiting_message + multicast_message + breakout_message
        conn.send(combined_message.encode('utf8'))

    else:
        # Handle unknown request types
        response = [False, "Unknown request type"]
        conn.send(json.dumps(response).encode('utf8'))
        print(f"Unknown request type received: {request_type}")


def client_handler(conn, addr, multicast, temporary_students):
    print(f"Handling connection from {addr}")
    from_client = ''
    
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break  # Break if the client closes the connection
        
            from_client += data.decode('utf8')
            # Deserialize the JSON data
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
    serv.bind(('localhost', 8080)) 
    #serv.bind((ip_address, 8080))

    serv.listen(5)
    print(f"Server started on IP: {ip_address}, listening on port 8080...")

    while True:
        conn, addr = serv.accept()
        print(f"Connection established with {addr}")

        # Create a new thread for each client # Chat GPT helped with these lines 
        client_thread = threading.Thread( 
            target=client_handler,
            args=(conn, addr, multicast, temporary_students)
        )
        client_thread.start()


run_server()