import socket
import json 
import threading
from user_profile import UserProfile
from room import Room 
from typing import List 

def validate_instructor(multicast:Room, decoded_json:dict):
    username = decoded_json.get("username")
    instructor = multicast.find_user(username)

    if not instructor:
        response = [False, f"User '{username}' not found."]
        return False

    if not instructor.is_instructor:
        response = [False, f"User '{username}' is not an instructor."]
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
            # Add student to the temporary list
            temporary_students.append(new_user)
            response = [True, f"Student {new_user.username} added to the waiting list"]
            conn.send(json.dumps(response).encode('utf8'))
            print(f"Response to add_user (student): {response}")

    elif request_type == "create_room":
        if not instructor:
            return

        for student in temporary_students:
          multicast.add_user(student)
        temporary_students.clear()
        response = [True, "Multicast room created successfully."]
        conn.send(json.dumps(response).encode('utf8'))
        print("Multicast room created successfully.")

    elif request_type == "message": #TODO
        pass 

    elif request_type == "broadcast": #TODO message all users in the room. This can use the same code as the message request above 
        pass 

    elif request_type == "request_breakout":
        multicast.get_instructor().add_breakout_request(decoded_json)
    
    elif request_type == "show_requests":
        if not instructor:
            return
        conn.send(instructor.display_requests().encode('utf8'))

    elif request_type == "execute_request":
        instructor = validate_instructor(multicast, decoded_json)
        if not instructor:
            return
        flattened_string:str = ''.join(decoded_json.get("data"))
        index = int(flattened_string)
        request = instructor.get_request(index-1)
        conn.send(json.dumps(request).encode('utf8'))
        
        
    elif request_type == "participants": # Prints a list of all users in the multicast
      all_user_json = []  
      for user in multicast.get_all_users():
        if user:      
          all_user_json.append(user.get_profile_json())

      # Send the entire list of user JSON data as a single JSON message
      conn.send(json.dumps(all_user_json).encode('utf8'))

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
    serv.bind(('localhost', 8080))
    serv.listen(5)
    print("Server started, listening on port 8080...")

    while True:
        conn, addr = serv.accept()
        print(f"Connection established with {addr}")

        # Create a new thread for each client
        client_thread = threading.Thread(
            target=client_handler,
            args=(conn, addr, multicast, temporary_students)
        )
        client_thread.start()


run_server()