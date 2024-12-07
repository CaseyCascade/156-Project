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
        
    def get_profile_json(self):
        data = {"username": self.username, "is_instructor": self.is_instructor}
        return data
    
    def get_request_json(self, request):
        if self.username is None:
            return
        data = {"request": request, "username": self.username, "is_instructor": self.is_instructor}
        return json.dumps(data)

    
    
    def print(self):
        print("Username:", self.username)
        print("Instructor:", self.is_instructor)