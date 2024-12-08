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