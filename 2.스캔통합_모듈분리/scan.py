import socket
import struct
import time
import uuid
from smbprotocol.connection import Connection

def port123_ntp(host, timeout=1):
    port = 123
    # NTP 메시지 포맷 설정 (모드 3 - 클라이언트 요청)
    message = '\x1b' + 47 * '\0'

    # UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        # NTP 서버로 메시지 전송
        sock.sendto(message.encode('utf-8'), (host, port))

        # 서버 응답 대기
        response, _ = sock.recvfrom(1024)
        
        # 응답 받음 - 포트가 열려 있음
        print(f"NTP port {port} is open on {host}.")

        # NTP 응답 패킷 분석
        unpacked = struct.unpack('!B B B b 11I', response)
        stratum = unpacked[1]
        poll = unpacked[2]
        precision = unpacked[3]
        root_delay = unpacked[4]
        root_dispersion = unpacked[5]
        ref_id = unpacked[6]

        # 추가 정보 출력
        print(f"Stratum: {stratum}, Poll: {poll}, Precision: {precision}")
        print(f"Root Delay: {root_delay / 2**16} seconds, Root Dispersion: {root_dispersion / 2**16} seconds")
        print(f"Reference ID: {ref_id}")

        # NTP 타임스탬프 추출 및 변환 (응답 패킷의 40번째 바이트부터 8바이트)
        t = struct.unpack('!12I', response)[10]
        t -= 2208988800  # 1900년부터 1970년까지의 초를 빼서 Unix epoch으로 변환

        # 현지 시간으로 변환
        print(f"Server time: {time.ctime(t)}\n")
        return True
    except socket.timeout:
        # 타임아웃 - 응답 없음
        print(f"NTP port {port} did not respond on {host}.\n")
        return False
    except Exception as e:
        # 기타 오류
        print(f"Error scanning NTP port {port} on {host}: {e}\n")
        return False
    finally:
        sock.close()

def port445_smb(host, timeout=1):
    try:
        # SMB 연결을 위한 Connection 객체 생성
        connection = Connection(uuid.uuid4(), host, 445)
        connection.connect(timeout=timeout)  # 연결 시도에 타임아웃 적용

        # 연결 성공 시, SMB 서비스에 대한 정보 출력
        negotiated_dialect = connection.dialect
        print(f"SMB service is responding on {host}, port 445 is open.")
        print(f"Negotiated SMB Protocol Dialect: {negotiated_dialect}\n")

        # 연결 종료
        connection.disconnect()
    except Exception as e:
        print(f"Failed to connect to SMB service on {host}:445 - {e}\n")

def port902_vmware_soap(host, timeout=1):
    soap_request = """POST /Service.asmx HTTP/1.1
Host: {host}
Content-Type: text/xml; charset=utf-8
Content-Length: {length}
SOAPAction: "SomeSOAPAction"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <ExampleMethod xmlns="http://tempuri.org/" />
    </soap:Body>
</soap:Envelope>
"""
    ports = [902, 912]
    for port in ports:
        try:
            # 소켓 객체 생성
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # 지정된 호스트와 포트로 연결 시도
            sock.connect((host, port))
            
            # SOAP 요청 본문 준비
            body = soap_request.format(host=host, length=len(soap_request))
            
            # SOAP 요청 전송
            sock.sendall(body.encode('utf-8'))
            
            # 서비스로부터 응답 받기
            response = sock.recv(4096)
            
            # 받은 데이터 출력
            if response:
                print(f"Received SOAP response from {host}:{port}:")
                print(response.decode('utf-8', errors='ignore\n'))
            else:
                print(f"No response received from {host}:{port}\n")
            
        except socket.error as e:
            print(f"Error connecting to {host}:{port}: {e}\n")
        finally:
            sock.close()

def port3306_mysql(host, timeout=1):
    port=3306
    try:
        # 소켓 객체 생성 및 타임아웃 설정
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # MySQL 서버의 3306 포트로 연결 시도
        s.connect((host, port))
        
        # 서버로부터 초기 핸드셰이크 메시지 수신
        packet = s.recv(1024)
        
        if packet:
            print(f"MySQL service is running on {host}:{port}")
            
            # 서버 버전 정보
            end_index = packet.find(b'\x00', 5)
            server_version = packet[5:end_index].decode('utf-8')
            
            # 스레드 ID / 클라이언트 연결에 고유한 id생성
            thread_id = struct.unpack('<I', packet[0:4])[0]
            #pid는 파일위치를 특정해야하므로 제외.
            
            # 서버 능력 설명, 비트마스크 형태, 비트가 설정되어있으면 기능을 지원하는것
            cap_low_bytes = struct.unpack('<H', packet[end_index + 1:end_index + 3])[0]
            cap_high_bytes = struct.unpack('<H', packet[end_index + 19:end_index + 21])[0]
            server_capabilities = (cap_high_bytes << 16) + cap_low_bytes

            print(f"Server Version: {server_version}")
            print(f"Thread ID: {thread_id}")
            print(f"Server Capabilities: {server_capabilities:032b}")
        else:
            print(f"No response received from MySQL service on {host}:{port}")
        
    except socket.error as e:
        print(f"Error connecting to MySQL service on {host}:{port}: {e}")
    finally:
        s.close()

host = '127.0.0.1' #'pool.ntp.org'

port123_ntp(host)
port445_smb(host)
port902_vmware_soap(host)
port3306_mysql(host)

