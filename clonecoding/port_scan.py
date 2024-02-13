# 멀티스레딩을 활용한 포트 스캐닝 기능을 구현한 페이지, 주어진 호스트의 특정 포트 범위를 스캔하여 상태를 확인
import socket  # 네트워크 연결을 위한 소켓 프로그래밍에 필요한 모듈
import threading  # 스레드를 사용하기 위한 모듈
import sys  # 시스템 관련 파라미터와 함수를 다루기 위한 모듈
import concurrent.futures  # 멀티스레딩을 위한 고수준 인터페이스 제공 모듈
from tqdm import tqdm  # 진행 상황(progress bar)을 표시하기 위한 라이브러리
import random  # 리스트를 무작위로 섞기 위한 모듈

from print_message import port_result_printing  # 포트 스캔 결과를 출력하는 함수가 정의된 모듈

# 포트 스캔을 위한 멀티스레딩 함수
def port_scan_multi_threading(num_threads, thread_ids, target_host, ports, scan):
    
    random.shuffle(ports)  # 스캔할 포트 목록을 무작위로 섞어서 스캔 패턴을 예측하기 어렵게 합니다.
    #굳이 스캔 패턴을 섞는 이유는 아마도 보안 시스템이나 네트워크 장비에서 스캔을 비정상적인 활동으로 간주하고 차단하는 것을 피하기 위함일듯

    # 열려있는 포트, 닫혀있는 포트, 필터링된 포트 목록을 초기화합니다.
    open_ports = []
    closed_ports = []
    filtered_ports = []
    
    # 지정된 최대 스레드 수를 사용하여 ThreadPoolExecutor를 생성합니다.
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor: #ThreadPoolExecutor는 Python의 concurrent.futures 모듈에 있는 클래스, 멀티스레딩을 위한 고수준 인터페이스를 제공. 이 클래스를 사용하면 스레드 풀을 생성하고, 여러 작업(task)을 스레드 풀에 제출(submit)하여 병렬로 실행가능. 이를 통해 I/O 바운드(I/O-bound) 작업이나 네트워크 요청과 같이 멀티스레딩으로 성능 개선이 가능한 작업을 효율적으로 처리
        # 모든 포트에 대해 스캔 함수를 병렬 실행하기 위한 future 객체 리스트를 생성합니다.
        futures = [executor.submit(scan, target_host, port, thread_ids) for port in ports]
        total_ports = len(ports)  # 스캔할 총 포트 수
        # tqdm을 사용하여 스캔 진행 상황을 표시하는 프로그레스 바를 생성합니다.
        with tqdm(total=total_ports, desc="Scanning Ports", unit="port") as pbar:
            # 모든 future 객체의 완료를 기다리고, 각각의 결과를 처리합니다.
            for future in concurrent.futures.as_completed(futures):
                pbar.update(1)  # 프로그레스 바를 업데이트합니다.
                thread_id, port, is_open, sock, result = future.result()  # future의 결과를 얻습니다.
                if is_open or sock is not None:
                    open_ports.append(port)  # 열려있는 포트를 목록에 추가합니다.
                elif result == 61:
                   filtered_ports.append(port)  # 필터링된(차단된) 포트를 목록에 추가합니다.
                else:
                    closed_ports.append(port)  # 닫혀있는 포트를 목록에 추가합니다.

    # 포트 스캔 결과를 출력합니다.
    port_result_printing(thread_ids, filtered_ports, closed_ports, open_ports)
    

    return open_ports  # 열려있는 포트 목록을 반환합니다.

# TCP 포트 스캔을 수행하는 함수
def tcp_scan(host, port, thread_ids):

    scan = tcp_scan  # 현재 함수를 다시 참조하는 변수, 여기서는 사용되지 않는 것으로 보입니다.

    lock = threading.Lock()  # 스레드 간의 동기화를 위한 Lock 객체 생성
    
    # Lock을 사용하여 스레드 안전한 영역을 생성합니다.
    with lock:
        thread_id = threading.get_ident()  # 현재 스레드의 식별자를 얻습니다.
        thread_ids.add(thread_id)  # 스레드 ID를 전달된 집합에 추가합니다.

    # 소켓을 생성하여 TCP 연결을 시도합니다.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성
        sock.settimeout(1)  # 소켓 연결 시도의 타임아웃을 1초로 설정합니다.
        result = sock.connect_ex((host, port))  # 소켓을 통해 해당 호스트와 포트에 연결 시도
        if result == 0:
            return thread_id, port, True, sock, result  # 연결 성공 시 정보 반환
        elif result == 61:
            # 특정 에러(61)인 경우, 필터링된 포트로 간주하고 정보 반환
            sock.close()
            sock = None
            return thread_id, port, False, sock, result
        else:
            # 그 외의 경우, 연결 실패로 간주하고 정보 반환
            sock.close()
            sock = None
            return thread_id, port, False, sock, result
    except KeyboardInterrupt:
        # 사용자가 프로그램 실행 중 Ctrl+C를 누른 경우, 프로그램 종료 메시지 출력 후 종료
        print("\nExiting program.")
        sys.exit()
    except socket.gaierror:
        # 호스트 이름 해석 실패 시 에러 메시지 출력 후 종료
        print("Hostname could not be resolved.")
        sys.exit()
    except socket.error:
        # 소켓 에러 발생 시 에러 메시지 출력 후 종료
        print("Couldn't connect to server.")
        sys.exit()
    finally:
        # 마지막에 항상 소켓이 열려있는 경우 닫습니다.
        if sock:
            sock.close()