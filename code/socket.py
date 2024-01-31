import socket

def start_server(host, port):
    # 소켓 객체 생성
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 소켓을 주소와 포트에 바인드
        s.bind((host, port))
        print(f"Server is listening on {host}:{port}")

        # 소켓을 리스닝 상태로 전환, 1개의 연결 요청 대기
        s.listen(1)

        # 연결 요청을 수락
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            # 클라이언트로부터 데이터를 받을 때까지 대기
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # 데이터 수신 후 클라이언트에게 응답
                conn.sendall(b'Hello, client')

if __name__ == "__main__":
    HOST = '127.0.0.1'  # 로컬호스트
    PORT = 65432        # 리스닝할 포트 번호

    start_server(HOST, PORT)