# user_profile.py
Class to hold information for each user, including username, socket, whether they are an instructor, etc. 
JSON Objects representing client requests are created here as each request contains info found in the User Profile. 

# room.py 
Class to hold a list of all users within a multicast and handle connections between students and the instructor. 
"Breakout Rooms" are simply a list of additional rooms held within the main room (multicast)
The intention is for the multicast to hold any number of smaller rooms, but none of the breakout rooms will be allowed to have sub-rooms of their own. 

# client.py
Holds functions to create a User Profile and client side loops to send and compose requests 

# server.py
Handles requests sent by the client and holds logic for each request that is sent in 


# Command List
## Instructor Only
### create_room
Currently, this takes all students in the waiting list and puts them into the multicast. We likely should do this differently, but only if we have time 
### show_requests
Shows all requests made for breakout rooms and their indexes
### accept|Index
Creates a broadcast room at the index given at Index. The indexes correspond to those that display when using show_requests


## Instructor & Student
### request|User1|User2...
Sends a request to the instructor to create a breakout room with the following usernames given as arguments. 
The resulting room will contain the instructor, the sender of the request, 
and all the users they passed in. 
### show
Shows a record of which users are in the waitlist, the multicast, and all open breakout rooms
### message
Not implemented yet. An idea would be to have the message have two args, user|message
### broadcast|message
Not implemented yet. Should send message to everyone in room 
### add_user
This shouldn't need to be implemented any further, 
and is only used in our registration to get users into the waiting list or put the instructor in the multicast