import ssl
import socket

def tls_server(cert_file, key_file, port=8081):
    import ssl
    import socket

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket = context.wrap_socket(server_socket, server_side=True)
        server_socket.bind(('localhost', port))
        server_socket.listen(5)
        print(f"[*] TLS Server is listening on port {port}...")

        conn, addr = server_socket.accept()
        print(f"[+] Connection established from {addr}")

        # 반복적으로 데이터 수신
        total_data = b""
        while True:
            chunk = conn.recv(4096)  # 4KB씩 수신
            if not chunk:
                break  # 더 이상 데이터가 없으면 종료
            total_data += chunk
        print(f"[+] Received {len(total_data)} bytes")
        conn.close()


def tls_client(cert_file, port=8081):
    import ssl
    import socket

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cert_file)
    context.check_hostname = False  # 테스트용

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket = context.wrap_socket(client_socket, server_hostname='localhost')
        print(f"[*] Connecting to TLS server on port {port}...")
        client_socket.connect(('localhost', port))
        print("[+] Connection successful")

        with open("data/lidar_data_32ch.json", "rb") as f:
            data = f.read()
        client_socket.sendall(data)  # 데이터 전송
        print(f"[+] Sent {len(data)} bytes")

        client_socket.close()  # 연결 정상 종료
