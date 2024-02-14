#포트 오픈 여부 확인하는 nmap식. 배너도 귀납적으로 하지말고 연역적으로하는 방향으로.
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def get_service_name(port, proto):
    try:
        name = socket.getservbyport(port, proto)
    except:
        name = "알 수 없는 서비스"
    return name

def scan_tcp_port(ip, port, timeout=1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        return port, "TCP", result == 0 

def scan_udp_port(ip, port, timeout=1):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.sendto(b'Hello', (ip, port)) 
            sock.recvfrom(1024)  
            return port, "UDP", True
        except socket.timeout:
            return port, "UDP", False
        except Exception as e:
            return port, "UDP", False

def total_scan(ip, start_port=1, end_port=1024, threads=100):
    print(f"{ip}의 {start_port}부터 {end_port}까지 포트 스캔 중...")
    scan_results = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(scan_tcp_port, ip, port) for port in range(start_port, end_port + 1)]
        futures += [executor.submit(scan_udp_port, ip, port) for port in range(start_port, end_port + 1)]
        for future in tqdm(as_completed(futures), total=len(futures), desc="스캔 중", unit="포트"):
            port, proto, is_open = future.result()
            if is_open:
                scan_results.append((port, proto, get_service_name(port, 'tcp' if proto == 'TCP' else 'udp')))

   
    scan_results.sort(key=lambda x: (x[1], x[0])) 

    for port, proto, service_name in scan_results:
        print(f"포트 {port}/{proto} 열림 ({service_name})")

if __name__ == "__main__":
    target_ip = input("대상 IP(Host)를 입력하세요: ") #127.0.0.1 #211.229.25.137
    start_port = int(input("시작 포트를 입력하세요: "))
    end_port = int(input("마지막 포트를 입력하세요 (최대 65535): "))

    if end_port > 65535 or end_port < start_port:
        print("잘못된 포트 범위입니다. 시작 포트가 마지막 포트보다 작고 마지막 포트가 65535 이하인지 확인하세요.")
    else:
        total_scan(target_ip, start_port, end_port, threads=100)  
