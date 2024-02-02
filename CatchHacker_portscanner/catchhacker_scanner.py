#스캐너의 메인
import socket  # 네트워크 연결을 위한 소켓 모듈을 임포트합니다.
import random  # 난수 생성을 위한 랜덤 모듈을 임포트합니다.

# 필요한 기능별로 모듈화된 스크립트를 임포트합니다.
from print_message import print_welcome_message  # 시작 메시지를 출력하는 함수를 임포트합니다.
from option import option_set  # 사용자 입력 옵션을 처리하는 함수를 임포트합니다.
from port_scan import port_scan_multi_threading, tcp_scan  # 포트 스캐닝을 위한 함수를 임포트합니다.
from service_scan import service_scan_service_banner  # 서비스 스캐닝을 위한 함수를 임포트합니다.

# 메인 함수 정의, 프로그램의 시작점입니다.
def main():
    # 시작시 환영 메시지를 출력합니다.
    print_welcome_message()

    # 사용자로부터 입력받은 옵션값들을 처리하여 가져옵니다.
    args = option_set() #args는 일반적으로 "arguments"의 약자로 사용. 프로그래밍에서 "arguments"는 함수나 프로그램에 전달되는 입력값을 의미

    # 대상 호스트의 IP 주소를 반드시 입력받아야 합니다.
    target_host = args.target_host

    # 사용할 스레드의 개수를 지정합니다.
    num_threads = args.threads
    thread_ids = set()  # 스레드 ID를 저장할 집합입니다.

    # 스캔할 포트의 범위를 지정합니다. 시작 포트와 종료 포트를 지정합니다.
    start_num = args.ports[0]
    end_num = args.ports[-1]
    ports = list(args.ports)  # 스캔할 포트 목록입니다.

    # TCP 스캔 옵션이 선택되었는지 확인합니다.
    if args.tcp:
        scan = tcp_scan  # TCP 스캔 함수를 사용합니다.
    
    # 멀티스레딩을 사용하여 포트 스캔을 실행합니다.
    open_ports = port_scan_multi_threading(num_threads, thread_ids, target_host, ports, scan)

    # 스캔 결과를 출력합니다.
    print(f"\nProtocol : TCP \nDetected Ports : {start_num}~{end_num} \nTarget Host :({target_host})\n")

    # 열린 포트를 대상으로 서비스 스캔을 수행합니다.
    service_scan_service_banner(target_host, open_ports, username="username", password="password")

# 이 스크립트가 직접 실행될 때만 main() 함수를 호출합니다.
if __name__ == "__main__":
    main()