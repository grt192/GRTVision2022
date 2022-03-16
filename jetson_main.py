import main
import socket

HOST = ''  # Empty string to accept connections on all available IPv4 interfaces
PORT = 5800  # Port to listen on (non-privileged ports are > 1023)

# Connect to socket
while True:
    try:
        print('Attempting to connect')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                main.run(ip_address='10.1.92.94', ports=(5801, 5802), conn_param=conn)
                # Terminate program if main completes
                break

    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print('Connection lost... retrying')
    except KeyboardInterrupt as e:
        break

