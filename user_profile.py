import json
class UserProfile:
    def __init__(self, username, is_instructor):
        self.username = username
        self.is_instructor = is_instructor

    def get_profile_json(self):
        data = {"username": self.username, "is_instructor": self.is_instructor}
        return json.dumps(data)
