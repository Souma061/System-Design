import socket

HOST = '0.0.0.0'

PORT = 8080

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
socket.send("Hello from client!".encode('utf-8'))
print(socket.recv(1024))
