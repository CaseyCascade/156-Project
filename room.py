from user_profile import UserProfile
from typing import List 

class Room:
  def __init__(self):
    self.max_students = 8
    self.students: List[UserProfile] = []
    self.instructor: UserProfile = None
    self.breakout_rooms: List[Room] = []
    self.is_breakout = False

  def get_all_users(self):
    all_users = self.students[:]  # Create a shallow copy of the students list
    if self.instructor:  # Only add the instructor if it's not None
        all_users.append(self.instructor)
    return all_users
  
  def get_instructor(self):
    return self.instructor

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
    for user in self.get_all_users():
        if user and user.username == name: 
            return user
    return None
  
  def remove_user(self, user:UserProfile):
    for i in self.get_all_users():
      if user == i and not user.is_instructor:
        self.students.remove(i)
        break 
      
  
  def create_breakout(self, students:List[UserProfile]): 
    if self.is_breakout: #Only the multicast can have sub-rooms
      return 
    
    # Initialize our Breakout Room 
    new_breakout = Room()
    new_breakout.add_user(self.instructor)
    new_breakout.is_breakout = True

    # Add all students in our list to the new breakout and remove them from multicast
    for student in students:
      print(new_breakout.add_user(student)[1])
      self.remove_user(student)
    
    
    # Add breakout room to our list 
    self.breakout_rooms.append(new_breakout)
    
  def delete_breakout(self, index):
    if len(self.breakout_rooms) == 0:
      return 
    breakout = self.breakout_rooms[index]
    for student in breakout.students:
      self.add_user(student)
    self.breakout_rooms.remove(breakout)

  def get_room_of_user(self, username):
     if self.find_user(username):
        return self
     else:
        for breakout in self.breakout_rooms:
          if breakout.find_user(username):
            return breakout
        print("User not found in any Rooms")

  def send_message(self, sender_username, recipient_username, message):
    recipient_username = recipient_username.strip().lower()

    # Look up recipient
    recipient_profile = self.find_user(recipient_username)
    if recipient_profile is None:
        print(f"Client {recipient_username} not found.")
        return

    # Ensure recipient has a valid socket
    if not recipient_profile.has_socket():
        print(f"Recipient {recipient_username} does not have a valid socket.")
        return

    try:
        # Send message
        recipient_socket = recipient_profile.get_socket()
        recipient_socket.send(f"Message from {sender_username}: {message}".encode('utf-8'))
        print(f"Message sent to {recipient_username}: {message}")
    except Exception as e:
        print(f"Error sending message to {recipient_username}: {e}")
