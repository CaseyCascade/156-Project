import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

print(f"Your IP address is: {ip_address}")