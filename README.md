# How To Use
To get started on multiple machines, make sure to uncomment/comment the lines in client.py and server.py that bind IP addresses. 
- In order to get a room set up: Input the server to connect to on the client programs (if not using localhost)
- Have the instructor run the command create_room to allow all students in the waiting list into the multicast (Any new students joining need to be let in again)
- Students can message other users in the same room through the broadcast and message commands 
- Students can request a breakout room via the commands below, and the request must be accepted by the instructor for it to be created 

## Commands
### Instructor Only
#### create_room
Currently, this takes all students in the waiting list and puts them into the multicast. We likely should do this differently, but only if we have time 
#### show_requests
Shows all requests made for breakout rooms and their indexes
#### accept|Index
Creates a broadcast room at the index given at Index. The indexes correspond to those that display when using show_requests


### Instructor & Student
#### request|User1|User2...
Sends a request to the instructor to create a breakout room with the following usernames given as arguments. 
The resulting room will contain the instructor, the sender of the request, 
and all the users they passed in. 
#### show
Shows a record of which users are in the waitlist, the multicast, and all open breakout rooms
#### message|user|message
Sends a message to a single user in the same room (Instructor can send to any student in any room)
#### broadcast|message
Sends a message to every user in the same room (Instructor messages are sent to everyone)
#### add_user
This shouldn't need to be implemented any further, 
and is only used in our registration to get users into the waiting list or put the instructor in the multicast

# File Descriptions
### user_profile.py
Class to hold information for each user, including username, socket, whether they are an instructor, etc. 
JSON Objects representing client requests are created here as each request contains info found in the User Profile. 

### room.py 
Class to hold a list of all users within a multicast and handle connections between students and the instructor. 
"Breakout Rooms" are simply a list of additional rooms held within the main room (multicast)
The intention is for the multicast to hold any number of smaller rooms, but none of the breakout rooms will be allowed to have sub-rooms of their own. 

### client.py
Holds functions to create a User Profile and client side loops to send and compose requests 

### server.py
Handles requests sent by the client and holds logic for each request that is sent in 
