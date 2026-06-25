import socket
import json
import threading

HOST = "0.0.0.0"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(
    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
)  # it allows the socket to be bound to an address that is already in use. This is useful when you want to restart a server quickly without waiting for the OS to release the port.
server.bind((HOST, PORT))
server.listen(5)

print(f"Server listening on {HOST}:{PORT}")


def handle_request(method, path):
    if path == "/":
        body = f"<h1>Hello from server! You requested {path}</h1>"
        status = "200 OK"
        content_type = "text/html"
    elif path == "/about":
        body = f"<h1>About page</h1>"
        status = "200 OK"
        content_type = "text/html"
    elif path == "/users":
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
        body = json.dumps(data)
        status = "200 OK"
        content_type = "application/json"
    elif path == "/contact":
        body = f"<h1>Contact page</h1>"
        status = "200 OK"
        content_type = "text/html"
    else:
        body = f"<h1>404 Not Found</h1>"
        status = "404 Not Found"
        content_type = "text/html"

    return f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {len(body.encode('utf-8'))}\r\n\r\n{body}"


def handle_client(conn, addr):
    print(f"Connection from {addr} has been established!")
    request = conn.recv(1024).decode("utf-8")
    first_line = request.split("\r\n")[0]
    method, path, version = first_line.split(" ")

    response = handle_request(method, path)
    conn.sendall(response.encode("utf-8"))
    conn.close()


while True:
    conn, addr = server.accept()

    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()


# SOCK_STREAM is used for TCP connections.Let's assume a connection A and connection B. When A sends data to B, it is guaranteed that the data will arrive in the same order it was sent. This is because TCP is a connection-oriented protocol that ensures reliable delivery of data.

# SOCK_DGRAM is used for UDP connections. In this case, when A sends data to B, there is no guarantee that the data will arrive in the same order it was sent. This is because UDP is a connectionless protocol that does not provide reliability or ordering guarantees.

# while True:
#     communication_socket, address = server.accept() # If no client is trying to connect, the server will block and wait for a connection. Once a client connects, it returns a new socket object (communication_socket) that can be used to communicate with the client, and the address of the client.
#     print(f'Connection from {address} has been established!')
#     message = communication_socket.recv(1024).decode('utf-8') # The recv() method is used to receive data from the client. It takes a buffer size as an argument, which specifies the maximum amount of data to be received at once. In this case, it is set to 1024 bytes. The received data is then decoded from bytes to a string using UTF-8 encoding.
#     print(f'Message from client: {message}')
#     communication_socket.send(bytes(f'Hello from server! You said: {message}', 'utf-8')) # The send() method is used to send data to the client. It takes a bytes-like object as an argument, which is the data to be sent. In this case, it sends a greeting message along with the message received from the client. The string is encoded to bytes using UTF-8 encoding before sending.
#     communication_socket.close() # The close() method is used to close the communication socket after the message has been sent. This is important to free up system resources and avoid potential memory leaks. After closing the socket, the server goes back to listening for new connections.
#     print(f'Connection from {address} has been closed.')
