import json
class UserProfile:
    def __init__(self, username=None, is_instructor=None):
        self.username = username if username is not None else None
        self.is_instructor = is_instructor if is_instructor is not None else None 

    def get_profile_json(self):
        if self.username is None:
            return 
    
        data = {"username": self.username, "is_instructor": self.is_instructor}
        return json.dumps(data)
    
    def init_from_json(self, decoded_json): # Only works if UserProfile was not initialized with any args 
        self.username = decoded_json["username"] if self.username is None else self.username
        self.is_instructor = decoded_json["is_instructor"] if self.username is None else self.is_instructor
        return 