#특정 포트별 서비스 스캔을 수행하는 함수들의 집합. 각 함수는 특정 포트에서 실행 중인 네트워크 서비스를 확인하고, 해당 서비스의 상태나 정보를 반환

import socket  # 소켓 프로그래밍을 위한 모듈
import threading  # 스레드를 사용하기 위한 모듈
import concurrent.futures  # 병렬 실행을 위한 모듈
from print_message import service_result_printing  # 서비스 스캔 결과를 출력하는 함수
from tqdm import tqdm  # 진행률 표시 바를 위한 모듈

lock = threading.Lock()  # 스레드 간 동기화를 위한 락 객체

# 대상 호스트의 특정 포트로 간단한 HTTP 요청을 보내고 받은 응답에서 서비스 배너를 추출하는 함수
#배너 그래빙(Banner Grabbing)은 네트워크 서비스의 정보를 수집하는 기술, 서비스에 연결하여 해당 서비스가 전송하는 초기 정보(배너)를 캡처하는 과정. 서비스의 이름, 버전, 운영 체제 등
def banner_grabbing(target_host, target_port, sock):
    try:
        sock.send(b'POST / HTTP/1.1\r\nHost: ' + target_host.encode() + b'\r\n\r\n')  # HTTP 요청 전송
        banner = sock.recv(4096).decode().strip()  # 응답 수신 및 디코딩
        banner_lines = banner.split('\n')  # 응답을 줄 단위로 분할
        banner = banner_lines[:3]  # 처음 세 줄만 추출
        return banner  # 추출된 배너 반환
    except Exception as e:
        pass  # 예외 발생 시 처리하지 않고 넘어감
    finally:
        sock.close()  # 소켓 종료

# FTP 서비스 접속 시도 함수
# FTP_conn등 TCP스캔으로 포트가 열려있는지 닫혀있는지만 확인하면 되는데 굳이 username이나 password로 로그인까지 구현한 이유는 뭘까? 성공적으로 로그인 할 수 있는지까지 검증?
def FTP_conn(target_host, port, username, password):
    import ftplib  # FTP 프로토콜을 위한 모듈
    service_name = "FTP"
    try:
        ftp = ftplib.FTP(target_host)  # FTP 객체 생성 및 서버에 연결
        ftp.login(user=username, passwd=password)  # 로그인 시도
        ftp.quit()  # 연결 종료
        return (True, service_name)  # 성공적으로 연결되면 True 반환
    except ftplib.error_perm as e:
        return ("Closed", service_name)  # 권한 오류 발생 시 "Closed" 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# SSH 서비스 접속 시도 함수
def SSH_conn(target_host, port, username, password):
    import paramiko  # SSH 프로토콜을 위한 모듈
    service_name = "SSH"
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 호스트 키 정책 설정
        ssh_client.connect(target_host, port=port, username=username, password=password, timeout=10)  # SSH 서버에 연결 시도
        ssh_client.close()  # 연결 종료
        return (True, service_name)  # 성공적으로 연결되면 True 반환
    except paramiko.AuthenticationException as e:
        return (True, service_name)  # 인증 실패 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# SMTP 서비스 접속 시도 함수
def SMTP_conn(target_host, port, username, password):
    import smtplib  # SMTP 프로토콜을 위한 모듈
    service_name = "SMTP"
    try:
        smtp_server = smtplib.SMTP(target_host, port)  # SMTP 서버 객체 생성
        smtp_server.login(username, password)  # SMTP 서버에 로그인 시도
        smtp_server.quit()  # 연결 종료
        return (True, service_name)  # 성공적으로 연결되면 True 반환
    except smtplib.SMTPAuthenticationError as e:
        return (True, service_name)  # 인증 실패 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# Daytime 프로토콜을 이용해 서버에서 현재 시간 정보를 가져오는 함수
def Daytime_conn(target_host, port, username, password):
    import re  # 정규 표현식 모듈
    service_name = "Daytime"  # 서비스 이름 지정
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성
        client_socket.connect((target_host, port))  # 대상 호스트와 포트에 연결

        data = client_socket.recv(1024)  # 서버로부터 데이터 수신
        daytime_data = data.decode('utf-8').strip()  # 수신된 데이터 디코딩 및 공백 제거
        client_socket.close()  # 소켓 연결 종료

        # 수신된 데이터에서 시간 정보를 추출하기 위한 정규 표현식 패턴 정의
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"

        match = re.search(pattern, daytime_data)  # 정규 표현식으로 시간 정보 검색
        if match:
            extracted_time = match.group(1)  # 검색된 시간 정보 추출
            return (True, service_name)  # 시간 정보 추출 성공 시 True 반환
        else:
            return (None, service_name)  # 시간 정보를 찾지 못한 경우 None 반환
    except Exception as e:
        print(f"Daytime Error: {e}")  # 예외 발생 시 에러 메시지 출력
        return (None, service_name)  # 예외 발생 시 None 반환

# Telnet 프로토콜을 이용해 서버에 접속을 시도하는 함수
def telnet_conn(target_host, port, username, password):
    import telnetlib  # Telnet 클라이언트 모듈
    service_name = "telnet"  # 서비스 이름 지정
    try:
        tn = telnetlib.Telnet(target_host, port)  # Telnet 객체 생성 및 서버에 연결
        tn.read_until(b"login: ")  # 로그인 프롬프트 대기
        tn.write(username.encode('utf-8') + b"\n")  # 사용자 이름 전송
        tn.read_until(b"Password: ")  # 패스워드 프롬프트 대기
        tn.write(password.encode('utf-8') + b"\n")  # 패스워드 전송
        tn.read_until(b"$ ")  # 쉘 프롬프트 대기

        tn.write(b"ls -l\n")  # 'ls -l' 명령어 실행
        result = tn.read_until(b"$ ").decode('utf-8')  # 명령어 실행 결과 수신 및 디코딩

        tn.close()  # Telnet 연결 종료
        if tn is not None:
            return (True, service_name)  # 연결 성공 시 True 반환
        else:
            return (None, service_name)  # 연결 실패 시 None 반환
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환

# DNS 서버에 대해 역방향 조회를 수행하는 함수 
#역방향 IP -> DNS #정방향 DNS -> IP #정방향 DNS 조회에서는 도메인 이름(예: www.example.com)을 사용하여 해당 도메인의 IP 주소를 찾는다
def DNS_conn(target_host, port, username, password):
    import dns.reversename  # 역방향 DNS 조회를 위한 모듈
    import dns.resolver  # DNS 조회를 위한 모듈
    service_name = "DNS"  # 서비스 이름 지정
    try:
        ptr_query = dns.reversename.from_address(target_host)  # 주소에 대한 역방향 DNS 질의 객체 생성
        result = dns.resolver.resolve(ptr_query, 'PTR')  # PTR 레코드 조회
        #PTR 레코드(Pointer Record)는 DNS(Domain Name System)에서 사용되는 한 유형의 레코드로, IP 주소를 도메인 이름으로 매핑하는 데 사용
        #예를 들어, IP 주소 192.0.2.1에 대한 역방향 DNS 조회를 수행하고자 한다면, 이 IP 주소를 역방향 조회 포맷(1.2.0.192.in-addr.arpa)으로 변환한 후, 이 주소에 대한 PTR 레코드 조회를 수행. 조회 결과로 도메인 이름이 반환되면, 이 IP 주소가 해당 도메인 이름과 연결되어 있음을 의미
        val = "SMTP" in result  # 조회된 결과 중 'SMTP' 문자열 포함 여부 확인
        if val:
            return (True, "SMTP")  # 'SMTP' 포함 시 True 반환
        else:
            return (True, service_name)  # 'SMTP' 미포함 시 True 반환
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환

# TFTP 프로토콜을 이용해 서버에 파일 전송 시도를 하는 함수
def TFTP_conn(target_host, port, username, password):
    from tftpy import TftpClient, TftpTimeout  # TFTP 클라이언트 및 타임아웃 예외 모듈
    service_name = "TFTP"  # 서비스 이름 지정
    try:
        client = TftpClient(target_host, port)  # TFTP 클라이언트 객체 생성
        if client:
            return (True, service_name)  # 클라이언트 객체 생성 성공 시 True 반환
        else:
            return (None, service_name)  # 클라이언트 객체 생성 실패 시 None 반환
    except TftpTimeout:
        return (None, service_name)  # TFTP 타임아웃 예외 발생 시 None 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# Finger 프로토콜을 이용해 사용자 정보를 조회하는 함수
def finger_conn(target_host, port, username, password):
    service_name = "finger"  # 서비스 이름 지정
    try:
        sock = socket.create_connection((target_host, port))  # TCP 소켓 생성 및 서버에 연결
        query = f"{username}\r\n"  # 사용자 정보 조회 쿼리 생성
        sock.send(query.encode())  # 쿼리 전송
        response = sock.recv(4096).decode()  # 서버로부터 응답 수신 및 디코딩
        sock.close()  # 소켓 연결 종료
        return (True, service_name)  # 조회 성공 시 True 반환
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환

# HTTP 프로토콜을 이용해 웹 서버에 접속 시도하는 함수
def HTTP_conn(target_host, port, username, password):
    import requests  # HTTP 요청을 위한 모듈
    service_name = "HTTP"  # 서비스 이름 지정
    try:
        url = f"http://{target_host}:{port}"  # 대상 웹 서버의 URL 생성
        response = requests.get(url)  # HTTP GET 요청 전송
        socket.setdefaulttimeout(5)  # 소켓 타임아웃 설정
        return (True, service_name)  # 요청 성공 시 True 반환
    except requests.exceptions.HTTPError as http_err:
        return (None, service_name)  # HTTP 에러 발생 시 None 반환
    except requests.exceptions.ConnectionError as conn_err:
        return (None, service_name)  # 연결 에러 발생 시 None 반환
    except requests.exceptions.RequestException as req_err:
        return (None, service_name)  # 요청 에러 발생 시 None 반환

# POP3 프로토콜을 이용해 메일 서버에 접속 시도하는 함수
def POP3_conn(target_host, port, username, password):
    import poplib  # POP3 클라이언트 모듈
    service_name = "POP3"  # 서비스 이름 지정
    try:
        pop3_connection = poplib.POP3(target_host)  # POP3 객체 생성 및 서버에 연결
        pop3_connection.user(username)  # 사용자 이름 전송
        pop3_connection.pass_(password)  # 패스워드 전송
        return (True, service_name)  # 접속 성공 시 True 반환
    except poplib.error_proto as e:
        return (True, service_name)  # 프로토콜 에러 발생 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# SunRPC 서비스에 대한 접속 시도를 하는 함수
def Sunrpc_conn(target_host, port, username, password):
    import xmlrpc.client  # XML-RPC 클라이언트 모듈
    service_name = "SunRPC"  # 서비스 이름 지정
    try:
        server_address = f"{target_host}:{port}"  # SunRPC 서버의 주소 생성
        client = xmlrpc.client.ServerProxy(server_address)  # XML-RPC 클라이언트 객체 생성
        return (True, service_name)  # 클라이언트 객체 생성 성공 시 True 반환
    except xmlrpc.client.Fault as e:
        return (True, service_name)  # XML-RPC Fault 예외 발생 시 True 반환 (서비스는 실행 중이나 요청 처리 실패)
    except ConnectionError as e:
        return (None, service_name)  # 연결 에러 발생 시 None 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# NNTP 프로토콜을 이용해 뉴스 서버에 접속 시도하는 함수
def NNTP_conn(target_host, port, username, password):
    import nntplib  # NNTP 클라이언트 모듈
    service_name = "NNTP"  # 서비스 이름 지정
    try:
        nntp_connection = nntplib.NNTP(target_host)  # NNTP 객체 생성 및 서버에 연결
        return (True, service_name)  # 연결 성공 시 True 반환
    except nntplib.NNTPError as e:
        return (None, service_name)  # NNTP 에러 발생 시 None 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환
    finally:
        nntp_connection.quit()  # NNTP 연결 종료

# NetBIOS 프로토콜을 이용해 호스트 이름을 조회하는 함수
def NetBIOS_conn(target_host, port, username, password):
    from impacket import nmb  # NetBIOS 프로토콜 모듈
    service_name = "NetBIOS"  # 서비스 이름 지정
    try:
        netbios = nmb.NetBIOS()  # NetBIOS 객체 생성
        name = netbios.getnetbiosname(target_host)  # 대상 호스트의 NetBIOS 이름 조회
        if name:
            return (True, service_name)  # 이름 조회 성공 시 True 반환
        else:
            return (None, service_name)  # 이름 조회 실패 시 None 반환
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환

# IMAPS 프로토콜을 이용해 메일 서버에 안전하게 접속 시도하는 함수
def IMAPS_conn(target_host, port, username, password):
    import imaplib  # IMAP 클라이언트 모듈
    service_name = "IMAPS"  # 서비스 이름 지정
    try:
        imap_server = imaplib.IMAP4_SSL(target_host)  # IMAPS 객체 생성 및 서버에 연결
        imap_server.login(username, password)  # 서버에 로그인 시도
        response, _ = imap_server.login(username, password)  # 로그인 결과 확인
        if response == 'OK':
            return (True, service_name)  # 로그인 성공 시 True 반환
        else:
            return (True, service_name)  # 로그인 실패 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except imaplib.IMAP4_SSL.error as ssl_error:
        return (None, service_name)  # SSL 에러 발생 시 None 반환
    except imaplib.IMAP4.error as imap_error:
        return (None, service_name)  # IMAP 에러 발생 시 None 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# IRC 프로토콜을 이용해 IRC 서버에 접속 시도하는 함수
def IRC_conn(target_host, port, username, password):
    import irc.client  # IRC 클라이언트 모듈
    service_name = "IRC"  # 서비스 이름 지정
    class IRCClient(irc.client.SimpleIRCClient):
        def on_welcome(self, connection, event):
            return (True, service_name)  # 서버로부터 환영 메시지 수신 시 True 반환
    client = IRCClient()  # IRCClient 객체 생성
    try:
        client.connect(target_host, port, username)  # IRC 서버에 연결 시도
        client.start()  # IRC 클라이언트 시작
        client.connection.disconnect()  # IRC 연결 종료
        return (True, service_name)  # 연결 성공 시 True 반환
    except irc.client.ServerConnectionError as e:
        print("Error:", e)  # 서버 연결 에러 발생 시 에러 메시지 출력
        return (None, service_name)  # 연결 에러 발생 시 None 반환

# LDAP 프로토콜을 이용해 디렉토리 서비스에 접속 시도하는 함수
def LDAP_conn(target_host, port, username, password):
    from ldap3 import Server, Connection  # LDAP 클라이언트 모듈
    service_name = "LDAP"  # 서비스 이름 지정
    server = Server(f'ldap://{target_host}:{port}')  # LDAP 서버 객체 생성
    conn = Connection(server)  # LDAP 연결 객체 생성
    if conn.bind():
        conn.unbind()  # LDAP 연결 종료
        return (True, service_name)  # 연결 성공 시 True 반환
    else:
        return (None, service_name)  # 연결 실패 시 None 반환

# SSL 프로토콜을 이용해 안전하게 서버에 접속 시도하는 함수
def SSL_conn(target_host, port, username, password):
    import ssl  # SSL 모듈
    service_name = "SSL"  # 서비스 이름 지정
    server_address = (target_host, port)  # 서버 주소 및 포트
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성
    ssl_sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)  # SSL 소켓 생성
    try:
        ssl_sock.connect(server_address)  # SSL 소켓을 이용한 서버 연결 시도
        return (True, service_name)  # 연결 성공 시 True 반환
    except socket.error as e:
        return (None, service_name)  # 소켓 에러 발생 시 None 반환
    finally:
        ssl_sock.close()  # SSL 소켓 연결 종료

# SMB 프로토콜을 이용해 서버의 파일 공유 서비스에 접속 시도하는 함수
def SMB_conn(target_host, port, username, password):
    from smbprotocol import exceptions  # SMB 프로토콜 예외 모듈
    import smbclient  # SMB 클라이언트 모듈
    service_name = "SMB"  # 서비스 이름 지정
    try:
        smbclient.register_session(target_host, username=username, password=password)  # SMB 세션 등록 및 로그인 시도
        return (True, service_name)  # 로그인 성공 시 True 반환
    except exceptions.LogonFailure:
        return (True, service_name)  # 로그온 실패 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except ValueError:
        return (None, service_name)  # 값 에러 발생 시 None 반환
    else:
        return (True, service_name)  # 그 외 경우 True 반환

# SMTPS 프로토콜을 이용해 안전하게 메일 서버에 접속 시도하는 함수
def SMTPS_conn(target_host, port, username, password):
    import smtplib  # SMTP 클라이언트 모듈
    service_name = "SMTPS"  # 서비스 이름 지정
    try:
        smtp = smtplib.SMTP_SSL(target_host, port)  # SMTPS 객체 생성 및 서버에 연결
        smtp.quit()  # SMTPS 연결 종료
        return (True, service_name)  # 연결 성공 시 True 반환
    except:
        return (None, service_name)  # 예외 발생 시 None 반환

# LPD 프로토콜을 이용해 프린터 서비스에 접속 시도하는 함수
def LPD_conn(target_host, port, username, password):
    lpd_signature = b'\x02'  # LPD 프로토콜 시그니처
    service_name = "LPD"  # 서비스 이름 지정
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성
        sock.connect((target_host, port))  # 대상 호스트 및 포트에 연결
        
        sock.settimeout(2)  # 소켓 타임아웃 설정

        data = sock.recv(1)  # 서버로부터 1바이트 수신

        if data == lpd_signature:  # 수신된 데이터가 LPD 시그니처와 일치하는지 확인
            return (True, service_name)  # 일치 시 True 반환
        else:
            return (None, service_name)  # 일치하지 않을 경우 None 반환
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환
    finally:
        sock.close()  # 소켓 연결 종료

# Syslog 프로토콜을 이용해 로그 메시지를 서버로 전송하는 함수
def Syslog_conn(target_host, port, username, password):
    facility = 1  # 패실리티 (예: user-level messages)
    severity = 3  # 심각도 (예: Critical)
    message = "This is a test message"  # 전송할 테스트 메시지

    pri = facility * 8 + severity  # PRI 값 계산

    syslog_message = f"<{pri}>{message}"  # Syslog 메시지 포맷 생성

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP 소켓 생성
    
    try:
        sock.sendto(syslog_message.encode("utf-8"), (target_host, port))  # Syslog 메시지를 UDP로 전송
        #print("Syslog 메시지 전송 완료")
    except Exception as e:
        #print(f"전송 중 오류 발생: {e}")
    #finally:
        sock.close()  # 소켓 연결 종료

# NNTPS 프로토콜을 이용해 안전하게 뉴스 서버에 접속 시도하는 함수
def NNTPS_conn(target_host, port, username, password):
    import nntplib  # NNTP 클라이언트 모듈
    import ssl  # SSL 모듈
    service_name = "NNTPS"  # 서비스 이름 지정
    try:
        nntp_connection = nntplib.NNTP_SSL(target_host, port)  # NNTPS 객체 생성 및 서버에 연결
        return (True, service_name)  # 연결 성공 시 True 반환
    except nntplib.NNTPError as e:
        return (None, service_name)  # NNTP 에러 발생 시 None 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# LDAPS 프로토콜을 이용해 안전하게 디렉토리 서비스에 접속 시도하는 함수
def LDAPS_conn(target_host, port, username, password):
    from ldap3 import Server, Connection, ALL  # LDAP 클라이언트 모듈
    import ssl  # SSL 모듈
    from ldap3.core.exceptions import LDAPBindError  # LDAP 바인드 에러 모듈
    service_name = "LDAPS"  # 서비스 이름 지정
    try:
        server = Server(target_host, port=port, use_ssl=True, get_info=ALL)  # LDAPS 서버 객체 생성
        conn = Connection(server, user=username, password=password, auto_bind=True, auto_referrals=False, client_strategy='SYNC', authentication='SIMPLE')  # LDAPS 연결 객체 생성
        if conn.bind():
            try:
                conn.start_tls(validate=ssl.CERT_NONE)  # TLS 시작 (인증서 검증 없음)
                conn.unbind()  # LDAPS 연결 종료
                return (True, service_name)  # 연결 성공 시 True 반환
            except Exception as tls_error:
                return (None, service_name)  # TLS 설정 실패 시 None 반환
        else:
            return (None, service_name)  # 연결 실패 시 None 반환
    except LDAPBindError as bind_error:
        return (True, service_name)  # LDAP 바인드 에러 발생 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except Exception as general_error:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# Kerberos 프로토콜을 이용해 서버에 인증 시도하는 함수
def Kerberos_conn(target_host, port, username, password):
    import requests  # HTTP 요청을 위한 모듈
    from requests_kerberos import HTTPKerberosAuth, OPTIONAL  # Kerberos 인증 모듈
    service_name = "Kerberos"  # 서비스 이름 지정
    try:
        session = requests.Session()  # HTTP 세션 생성
        session.verify = False  # SSL 검증 비활성화 (실제 사용 시 보안 위험, 테스트 목적으로만 사용 권장)
        auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)  # Kerberos 인증 설정
        response = session.get(f"https://{target_host}:{port}", auth=auth)  # Kerberos 인증을 사용한 HTTP GET 요청
        if response.status_code == 200:
            return (True, service_name)  # 인증 성공 시 True 반환
        else:
            return (True, service_name)  # 인증 실패 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환

# FTPS 프로토콜을 이용해 안전하게 파일 전송 서버에 접속 시도하는 함수
def FTPS_conn(target_host, port, username, password):
    from ftplib import FTP_TLS  # FTPS 클라이언트 모듈
    from ftplib import FTP, error_perm  # FTP 클라이언트 및 권한 에러 모듈
    service_name = "FTPS"  # 서비스 이름 지정
    try:
        ftps = FTP_TLS()  # FTPS 객체 생성
        ftps.connect(target_host, port)  # FTPS 서버에 연결
        ftps.login(username, password)  # FTPS 서버에 로그인
        ftps.quit()  # FTPS 연결 종료
        return (True, service_name)  # 연결 성공 시 True 반환
    except error_perm as e:
        print(f"FTPS Connection Error: {e}")  # 권한 에러 발생 시 에러 메시지 출력
        return (None, service_name)  # 권한 에러 발생 시 None 반환
    except Exception as e:
        print(f"FTPS Error: {e}")  # 그 외 예외 발생 시 에러 메시지 출력
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# IMAP 프로토콜을 이용해 메일 서버에 접속 시도하는 함수
def IMAP_conn(target_host, port, username, password):
    import imaplib  # IMAP 클라이언트 모듈
    service_name = "IMAP"  # 서비스 이름 지정
    try:
        imap_server = imaplib.IMAP4(target_host)  # IMAP 객체 생성 및 서버에 연결
        imap_server.login(username, password)  # 서버에 로그인
        response = imap_server.select()  # 메일박스 선택 (기본값: "INBOX")
        if response[0] == 'OK':
            return (True, service_name)  # 로그인 성공 시 True 반환
        else:
            return (True, service_name)  # 로그인 실패 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except imaplib.IMAP4.error as imap_error:
        return (None, service_name)  # IMAP 에러 발생 시 None 반환
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# POP3S 프로토콜을 이용해 안전하게 메일 서버에 접속 시도하는 함수
def POP3S_conn(target_host, port, username, password):
    import poplib  # POP3 클라이언트 모듈
    service_name = "POP3S"  # 서비스 이름 지정
    try:
        pop3s_connection = poplib.POP3_SSL(target_host, port)  # POP3S 객체 생성 및 서버에 연결
        pop3s_connection.user(username)  # 사용자 이름 전송
        pop3s_connection.pass_(password)  # 패스워드 전송
        print("POP3S Connection Success")  # 연결 성공 메시지 출력
        return (True, service_name)  # 연결 성공 시 True 반환
    except poplib.error_proto as e:
        return (True, service_name)  # 프로토콜 에러 발생 시 True 반환 (서비스는 실행 중이나 인증 실패)
    except Exception as e:
        return (None, service_name)  # 그 외 예외 발생 시 None 반환

# MySQL 데이터베이스 서버에 접속 시도하는 함수
def MySQL_conn(target_host, port, username, password):
    import mysql.connector  # MySQL 클라이언트 모듈
    service_name = "MySQL"  # 서비스 이름 지정
    try:
        connection = mysql.connector.connect(
            host=target_host,
            user=username,
            password=password,
            database="mysql"  # 기본 데이터베이스 지정
        )
        if connection.is_connected():
            print("Connected to MySQL")  # 연결 성공 메시지 출력
            connection.close()  # 데이터베이스 연결 종료
            return (True, service_name)  # 연결 성공 시 True 반환
    except mysql.connector.Error as e:
        if e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            return (True, service_name)  # 액세스 거부 에러 발생 시 True 반환 (서비스는 실행 중이나 인증 실패)
        elif e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            return (True, service_name)  # 데이터베이스 없음 에러 발생 시 True 반환 (서비스는 실행 중이나 데이터베이스 없음)
        else:
            return (None, service_name)  # 그 외 MySQL 에러 발생 시 None 반환

# RDP 프로토콜을 이용해 원격 데스크톱에 접속 시도하는 함수
def RDP_conn(target_host, port, username, password):
    import subprocess  # 외부 프로세스 실행을 위한 모듈
    import time  # 시간 관련 모듈
    import pyautogui  # GUI 자동화를 위한 모듈
    service_name = "RDP"  # 서비스 이름 지정
    try:
        rdp_client_cmd = f"mstsc /v:{target_host}"  # RDP 클라이언트 실행 명령어
        subprocess.Popen(rdp_client_cmd, shell=True)  # RDP 클라이언트 실행

        time.sleep(5)  # RDP 클라이언트가 실행될 때까지 대기

        pyautogui.write(username)  # 사용자 이름 입력
        pyautogui.press('tab')  # 탭 키 입력 (패스워드 필드로 이동)
        pyautogui.write(password)  # 패스워드 입력
        pyautogui.press('enter')  # 엔터 키 입력 (로그인 시도)
        if rdp_client_cmd.find("command not") == -1:
            return (None, service_name)  # 명령어 실행 실패 시 None 반환
        else:
            return (True, service_name)  # 그 외 경우 True 반환
    except Exception as e:
        return (None, service_name)  # 예외 발생 시 None 반환

# PostgreSQL 데이터베이스 서버에 접속 시도하는 함수
def PostgreSQL_conn(target_host, port, username, password):
    from psycopg2 import errors  # PostgreSQL 에러 모듈
    import psycopg2  # PostgreSQL 클라이언트 모듈
    service_name = "PostgreSQL"  # 서비스 이름 지정
    try:
        connection = psycopg2.connect(
            host=target_host,
            port=port,
            database="postgres",  # 기본 데이터베이스 지정
            user=username,
            password=password
        )
        if connection:
            return (True, service_name)  # 연결 성공 시 True 반환
    except errors.OperationalError as e:
        if e.pgcode == errors.InvalidPassword.pgcode:
            return (True, service_name)  # 인증 에러 발생 시 True 반환 (서비스는 실행 중이나 인증 실패)
        else:
            return (None, service_name)  # 운영 에러 발생 시 None 반환

# 서비스 접속 시도 및 결과 반환 함수
def try_service(target_host, port, username, password, service_func):
    result = service_func(target_host, port, username, password)  # 지정된 서비스 함수 실행
    service_status, service_name = result  # 실행 결과에서 서비스 상태 및 이름 추출
    print(result)  # 결과 출력
    return result  # 결과 반환

# 대상 호스트의 열린 포트에 대해 서비스 스캔을 수행하고 배너 정보를 수집하는 함수
# 대상 호스트의 열린 포트에 대해 다양한 네트워크 서비스를 스캔하고 배너 정보를 수집하는 함수 정의
def service_scan_service_banner(target_host, open_ports, username, password):
    # 스캔할 서비스 목록 정의. 특정 서비스에 대한 접속 시도 함수를 리스트에 추가함.
    # 필요에 따라 주석 처리된 서비스를 활성화하여 추가적인 스캔을 수행할 수 있음.
    services_to_try = [
        FTP_conn, SSH_conn, SMTP_conn, DNS_conn, HTTP_conn, POP3_conn, NetBIOS_conn, IMAP_conn, SSL_conn, SMB_conn, LPD_conn,
        MySQL_conn, RDP_conn,  # RDP는 윈도우 전용 서비스임을 표시
        PostgreSQL_conn, Daytime_conn, telnet_conn,
        # 다음 서비스는 필요에 따라 주석 해제하여 활성화 가능
        # TFTP_conn, finger_conn, Sunrpc_conn, NNTP_conn, IRC_conn, LDAP_conn, SMTPS_conn, Syslog_conn, NNTPS_conn, LDAPS_conn, Kerberos_conn, FTPS_conn, IMAPS_conn, POP3S_conn,
    ]

    # 감지된 서비스, 닫힌 서비스, 감지되지 않은 서비스를 저장할 딕셔너리 및 리스트 초기화
    Detected_service = {}
    Closed_service = {}
    Not_Detected_service = []
    banner = {}  # 배너 정보를 저장할 딕셔너리

    # 열린 포트에 대해 진행률 표시를 사용하여 서비스 스캔 수행
    with tqdm(total=len(open_ports), desc="Scanning Services", unit="port") as pbar:
        for port in open_ports:  # 각 열린 포트에 대해 반복
            pbar.update(1)  # 진행률 바 업데이트
            service_Detected = False  # 서비스 감지 여부를 False로 초기화
            
            for service_func in services_to_try:  # 스캔할 서비스 목록에 대해 반복
                service_status, service_name = service_func(target_host, port, username, password)  # 서비스 함수 호출
                
                if service_status:  # 서비스가 감지된 경우
                    Detected_service[port] = service_name  # 감지된 서비스를 딕셔너리에 추가
                    service_Detected = True  # 서비스 감지 여부를 True로 설정
                    break  # 현재 포트에 대한 스캔 종료
                elif service_status == "Closed":  # 서비스가 닫혀 있는 경우
                    Closed_service[port] = service_name  # 닫힌 서비스를 딕셔너리에 추가
                    service_Detected = True  # 서비스 감지 여부를 True로 설정
                    break  # 현재 포트에 대한 스캔 종료
            
            if not service_Detected:  # 서비스가 감지되지 않은 경우
                Not_Detected_service.append(port)  # 감지되지 않은 서비스를 리스트에 추가

    # 감지된 서비스, 닫힌 서비스, 감지되지 않은 서비스의 결과를 출력
    service_result_printing(Detected_service, Closed_service, Not_Detected_service)
    
    # 열린 포트의 배너 정보 수집
    with tqdm(total=len(open_ports), desc="Banner Info", unit="port") as pbar:
        for port in open_ports:  # 각 열린 포트에 대해 반복
            pbar.update(1)  # 진행률 바 업데이트
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 생성
            sock.settimeout(1)  # 소켓 타임아웃 1초로 설정
            
            banner_info = banner_grabbing(target_host, port, sock)  # 배너 그래빙 함수 호출
            if banner_info:  # 배너 정보가 있는 경우
                banner[port] = banner_info  # 배너 정보를 딕셔너리에 저장
    
    # 배너 정보 출력
    print("Banner Information:")
    for port, banner_info in banner.items():
        print(f"Port {port}: {banner_info}")  # 각 포트의 배너 정보 출력

# 메인 함수 정의. 테스트 목적으로 사용.
def main():
    target_host = "test.kr"  # 테스트 대상 호스트
    port = 22  # 테스트 포트 (SSH 예시)
    username = "username"  # 테스트 사용자 이름
    password = "password"  # 테스트 비밀번호
    
    # 서비스 스캔 및 배너 그래빙 테스트를 위한 함수 호출 예시들이 주석 처리되어 있음
    # 필요에 따라 특정 서비스에 대한 테스트를 위해 주석 해제하여 사용 가능
    #banner_grabbing(target_host, port, sock)
    #Daytime_conn(target_host, port) #13
    #FTP_conn(target_host, port, username, password) #21
    #SSH_conn(target_host, port, username, password) #22
    #telnet_conn(target_host, port) #23
    #SMTP_conn(target_host, port, username, password) #25
    #DNS_conn(target_host, port, username, password) #53
    #TFTP_conn(target_host, port) #69
    #finger_conn(target_host, port, username) #79
    #HTTP_conn(target_host, port, username, password) #80
    #POP3_conn(target_host, port, username, password) #110
    #Sunrpc_conn(target_host, port, username, password) #111
    #NNTP_conn(target_host, port, username, password) #119
    #NetBIOS_conn(target_host, port, username, password) #139
    #IMAP_conn(target_host, port, username, password) #143
    #IRC_conn(target_host, port, username, password) #194, 6667
    #LDAP_conn(target_host, port, username, password)
    #SSL_conn(target_host, port, username, password) #44
    #SMB_conn(target_host, port, username, password) #445 #모듈수정
    #SMTPS_conn(target_host, port, username, password) #465
    #LPD_conn(target_host, port, username, password) #515
    #Syslog_conn(target_host, port, username, password)#514
    #NNTPS_conn(target_host, port, username, password)
    #Message Submission #587 == SMTP 서비스와 동일
    #LDAPS_conn(target_host, port, username, password) #636
    #Kerberos_conn(target_host, port, username, password) #749
    #FTPS_conn(target_host, port, username, password) #990
    #IMAPS_conn(target_host, port, username, password) #903
    #POP3S_conn(target_host, port, username, password) #905
    #MySQL_conn(target_host, port, username, password) # 3306
    #RDP_conn(target_host, port, username, password) #3389
    #PostgreSQL_conn(target_host, port, username, password)#5432

# 스크립트가 직접 실행될 때만 main 함수 호출
if __name__ == "__main__":
    main()
