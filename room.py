from user_profile import UserProfile
from typing import List 

class Room:
  def __init__(self):
    self.max_students = 8
    self.students: List[UserProfile] = []
    self.instructor: UserProfile = None

  def get_all_users(self):
    all_users = self.students[:]  # Create a shallow copy of the students list
    if self.instructor:  # Only add the instructor if it's not None
        all_users.append(self.instructor)
    return all_users


  def add_user(self, user: UserProfile):
    if user.is_instructor:
      if self.instructor is None:
        self.instructor = user
        return [True, "Instructor " + user.username + " Added"]
      else:
        return [False, "Cannot add " + user.username + "as Instructor. The current Instructor is: " + self.instructor.username]
    if len(self.students) < self.max_students:
      self.students.append(user)
      return [True, "Student " + user.username + " Added"]
    else:
      return [False, "Cannot add " + user.username + " as Student. The maximum # of Students has been reached"]
    
  def find_user(self, name):
    print(f"Searching for user: {name}")
    for user in self.get_all_users():
        if user and user.username == name:  # Check for None
            print(f"User found: {user.username}")
            return user
    print(f"User '{name}' not found.")
    return None

    
  def broadcast_message(self, message_json):
    for user in self.get_all_users():
      if not user.has_socket():
        continue 