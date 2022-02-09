import socket

HOST = ''  # Standard loopback interface address (localhost)
PORT = 30000        # Port to listen on (non-privileged ports are > 1023)

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    conn.send(bytes("Message LMAO\n","UTF-8"))
    except (BrokenPipeError, OSError) as e:
        print("connection lost... retrying")