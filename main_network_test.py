import os
import socket
import ssl
import time
import multiprocessing
import pandas as pd
import matplotlib.pyplot as plt
from encryption.aes_encryption import aes_encrypt, aes_decrypt
from encryption.chacha20_encryption import chacha20_encrypt, chacha20_decrypt

# 서버 함수
def server(encryption, result_queue, cert_file=None, key_file=None, port=8081):
    try:
        # TLS 설정
        if encryption == "TLS":
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if encryption == "TLS":
            server_socket = context.wrap_socket(server_socket, server_side=True)

        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(5)
        print(f"[SERVER] {encryption} Server is listening on port {port}...")

        conn, addr = server_socket.accept()
        print(f"[SERVER] Connection established from {addr}")

        # 데이터 수신
        data = b""
        start_time = time.time()
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        end_time = time.time()

        elapsed_time = end_time - start_time
        print(f"[SERVER] {encryption} received {len(data)} bytes in {elapsed_time:.4f} seconds.")
        result_queue.put(elapsed_time)

    except Exception as e:
        print(f"[SERVER] Error: {str(e)}")
        result_queue.put(0.0)
    finally:
        if 'conn' in locals():
            conn.close()
        server_socket.close()

# 클라이언트 함수
def client(data_path, host, port, encryption, first_run=False, cert_file=None):
    with open(data_path, "rb") as f:
        data = f.read()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if encryption == "TLS":
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.load_verify_locations(cert_file)
        client_socket = context.wrap_socket(client_socket, server_hostname=host)

    start_time = time.time()
    client_socket.connect((host, port))
    print(f"[CLIENT] {encryption} connection established.")

    client_socket.sendall(data)  # 데이터 전송
    client_socket.shutdown(socket.SHUT_WR)  # 전송 완료 후 연결 종료 신호
    client_socket.close()
    end_time = time.time()

    transfer_time = end_time - start_time
    print(f"[CLIENT] {encryption} transmission completed in {transfer_time:.4f} seconds.")
    return transfer_time

# 테스트 실행 함수
def run_test(encryption, data_path, result_queue, host="localhost", port=8081, cert_file="cert/cert.pem", key_file="cert/key.pem"):
    print(f"\n[TEST] Starting test for {encryption}...")
    server_process = multiprocessing.Process(target=server, args=(encryption, result_queue, cert_file, key_file, port))
    server_process.start()
    time.sleep(1)

    transfer_time = client(data_path, host, port, encryption, cert_file=cert_file)
    server_time = result_queue.get()

    total_time = transfer_time + server_time
    print(f"[TEST] {encryption} total time: {total_time:.4f} seconds.")
    result_queue.put(total_time)
    server_process.join()

if __name__ == "__main__":
    # 데이터 파일 경로 설정
    data_path = "data/lidar_data_32ch.json"
    os.makedirs("results", exist_ok=True)

    # 사용자 입력: 테스트 반복 횟수
    while True:
        try:
            num_runs = int(input("Enter the number of test runs (e.g., 5, 10): "))
            if num_runs <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive integer for the number of runs.")

    # 결과 저장용 큐와 딕셔너리 초기화
    result_queue = multiprocessing.Queue()
    results_total = {"AES": [], "ChaCha20": [], "TLS": []}

    # 테스트 반복 실행
    for i in range(num_runs):
        print(f"\n[RUN {i+1}] Repeating tests...")
        for encryption in ["AES", "ChaCha20", "TLS"]:
            run_test(encryption, data_path, result_queue)
            total_time = result_queue.get()
            results_total[encryption].append(total_time)

    # 결과 저장
    df_total = pd.DataFrame(results_total)
    df_total.to_csv("results/total_times.csv", index=False)
    print("\n[+] Results saved to results/total_times.csv")

    # 그래프 시각화
    plt.figure(figsize=(10, 6))
    for enc, times in results_total.items():
        plt.plot(range(1, len(times) + 1), times, marker='o', label=f"{enc}")

    plt.title(f"Encryption Method vs Total Time Over {num_runs} Runs")
    plt.xlabel("Test Run")
    plt.ylabel("Total Time (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig("results/total_times_plot.png")
    print("[+] Total time plot saved to results/total_times_plot.png")

    print(f"[DEBUG] Final total results: {results_total}")
