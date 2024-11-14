import socket
import json 
from user_profile import UserProfile

class Server:
  def __init__(self):
    self.max_students = 8
    self.student_count = 0
    self.users = []
  
  def update_student_count(self):
    if all(isinstance(item, UserProfile) for item in self.users):
      pass
     
        

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
    print("Received dictionary:", decoded_json)

    conn.send("I am SERVER\n".encode())
  conn.close()
print ('client disconnected and shutdown')