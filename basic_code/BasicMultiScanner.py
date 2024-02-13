import socket
from concurrent.futures import ThreadPoolExecutor

# 로컬 호스트 주소
host = '127.0.0.1'

# 포트 검사 함수
def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)  # 타임아웃 설정
        result = s.connect_ex((host, port))
        if result == 0:
            return f"Port {port}: Open"
        else:
            return f"Port {port}: Closed"

# 멀티스레딩을 사용하여 포트 검사
with ThreadPoolExecutor(max_workers=100) as executor:
    # 모든 작업을 futures에 저장
    futures = {executor.submit(check_port, port): port for port in range(1, 201)}
    # 결과를 포트 번호 순서대로 정렬하여 출력
    for future in sorted(futures, key=futures.get):
        print(future.result())
