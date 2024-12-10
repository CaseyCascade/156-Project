import json
from typing import List 
class UserProfile:
    def __init__(self, username=None, is_instructor=None, socket=None):
        self.username = username if username is not None else None
        self.is_instructor = is_instructor if is_instructor is not None else None 
        self.breakout_requests: List[dict] = []
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
        
    def add_breakout_request(self, request):
        print(request)
        self.breakout_requests.append(request)

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
    
    def parse_raw_request(self, raw_request):
        try:
            parts = raw_request.split("|")
            request_type = parts[0]
            data = parts[1:]  # Remaining parts are additional data
            
            # Formulate a JSON object based on the request
            request_dict = {
                "request": request_type,
                "username": self.username,
                "is_instructor": self.is_instructor,
                "data": data
            }
            return json.dumps(request_dict)  # Return JSON as a string
        except Exception as e:
            print(f"Error parsing raw request: {e}")
            return None

        
    def display_requests(self):
        message_to_instructor = "Requests:\n"
        for i, item in enumerate(self.breakout_requests):
            message_to_instructor += f"{i + 1}. {item['data']}\n"
        print("Displaying Requests for Instructor on client side")
        return message_to_instructor

    def get_request(self, request_index):
        request = self.breakout_requests[request_index]
        del self.breakout_requests[request_index]
        return request

    def print(self):
        print("Username:", self.username)
        print("Instructor:", self.is_instructor)