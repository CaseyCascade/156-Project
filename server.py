import socket
import json 
from user_profile import UserProfile

class Room:
  def __init__(self):
    self.max_students = 8
    self.students = []
    self.instructor: UserProfile = None

  def get_all_users(self):
    all_users = self.students 
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
    
  
  def broadcast_message(self, message_json):
    for user in self.get_all_users():
      if not user.has_socket():
        continue 

    pass
def run_server():
  multicast = Room()

  serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serv.bind(('localhost', 8080))
  serv.listen(5)
  while True:
    conn, addr = serv.accept()
    from_client = ''
    while True:
      data = conn.recv(4096)
      if not data: break
      from_client += data.decode('utf8')

      # Deserialize json data # Chat GPT
      decoded_json = json.loads(from_client)

      # Create new user from JSON and add to the multicast 
      new_user = UserProfile()
      new_user.init_from_json(decoded_json)
      add_response = multicast.add_user(new_user)
      
      # If user is successfully added, add their socket to their User Profile 
      if add_response[0] == True:
        multicast[-1].set_socket(conn)
        
    conn.close()
  print ('client disconnected and shutdown')

run_server()