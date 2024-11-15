import socket
import json 
from user_profile import UserProfile

class Room:
  def __init__(self):
    self.max_students = 8
    self.students = []
    self.instructor: UserProfile = None
  
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
      multicast.add_user(new_user.init_from_json(decoded_json)) #TODO Test this 

      conn.send("I am SERVER\n".encode())
    conn.close()
  print ('client disconnected and shutdown')

run_server()