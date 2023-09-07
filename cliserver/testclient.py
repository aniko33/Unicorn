"""
import socket



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(('127.0.0.1', 9035))

# Send data to the server
message = "unity".encode()
client_socket.send(message)

# Receive data from the server
data = client_socket.recv(1024)
print(f"Received from server: {data.decode()}")

client_socket.close()
"""

from bm import BMKey

x = BMKey.new()
print(x)
y = BMKey.retrieve(x)
print("\n"+str(y))