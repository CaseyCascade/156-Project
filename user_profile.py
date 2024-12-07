import json
class UserProfile:
    def __init__(self, username=None, is_instructor=None, socket=None):
        self.username = username if username is not None else None
        self.is_instructor = is_instructor if is_instructor is not None else None 
        self.socket = None 

    def init_from_json(self, decoded_json): # Only works if UserProfile was not initialized with any args 
        self.username = decoded_json["username"] if self.username is None else self.username
        self.is_instructor = decoded_json["is_instructor"] if self.is_instructor is None else self.is_instructor
        return 
    
    def get_is_instructor(self):
        return self.is_instructor
    
    def set_socket(self, socket):
        self.socket = socket 

    def has_socket(self):
        if self.socket is None:
            return False
        else:
            return True 
        
    def get_profile_json(self)->dict:
        data = {"username": self.username, "is_instructor": self.is_instructor}
        return data
    
    def get_full_request(self, request: str, data_json: dict = None)->str:
        if self.username is None:
            return
        request_json = {"request": request, "username": self.username, "is_instructor": self.is_instructor}
        if data_json is None:
            return json.dumps(request_json)
        else:
            combined_json = {**request_json, **data_json}
            return json.dumps(combined_json)
    
    def parse_raw_request(self, raw_string)->str:
        arguments = raw_string.split('|')
        request_type = arguments[0]
        
        # Remove the first element using slicing
        arguments = arguments[1:]

        if not arguments:
            return self.get_full_request(request_type)
        elif request_type == "broadcast":
            return self.get_full_request(request_type, {"message":','.join(arguments)})
        elif request_type == "request_breakout":
            return self.get_full_request(request_type, {"users": arguments})
        
    def send_message(self, message: str) -> bool: 
        if not self.socket:
            print(f"User {self.username} does not have an active socket.")
            return False

        try:
            self.socket.send(message.encode('utf8'))  # Send the message as UTF-8 encoded string
            return True
        except Exception as e:
            print(f"Error sending message to {self.username}: {e}")
            return False

    def print(self):
        print("Username:", self.username)
        print("Instructor:", self.is_instructor)