# 수정사항
# servicename 출력하도록 수정하기
# 함수 이름 통합
# 443, 3389추가
# 중복 코드 병합 - ftp, ssh 통합/smtp, ldap 통합
# IMAP 시간 설정하기

import socket
import struct
import time
import uuid
import imaplib
import telnetlib
import ssl
from pysnmp.hlapi import *
from smbprotocol.connection import Connection
from scapy.all import sr, IP, TCP, UDP, ICMP, sr1
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import dns.resolver
import dns.query
import dns.message
from ldap3 import Server, Connection, ALL

#SMTPS, HTTPS, LDAPS
def scan_ssl_port(ip, port):
    if port == 465:
        service_name = "SMTPS/TCP"
    # elif port == 443:
    #     service_name = "HTTPS/TCP"
    elif port == 636:
        service_name = "LDAPS/TCP"
    else:
        service_name = "알 수 없는 서비스"

    response_data = {'service':service_name, 'port': port, 'state': 'closed'}
    if syn_scan(ip, port):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((ip, port)) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    banner = ssock.recv(1024).decode('utf-8')
                    response_data.update({'state': 'open', 'banner': banner})
        except Exception as err:
            response_data.update({'state': 'closed or filtered', 'error': str(err)})
    else:
        response_data['state'] = 'closed or filtered'
    return response_data

#SMTP, LDAP
# def scan_smtp1_port(ip, port):
#     # if port == 25:
#     #     service_name = "SMTP"
#     if port == 587:
#         service_name = "SMTP"
#     # elif port == 389:
#     #     service_name = "LDAP"
#     else:
#         service_name = "알 수 없는 서비스"

#     response_data = {'service':service_name, 'port': port, 'state': 'closed', 'error': None}
    
#     if syn_scan(ip, port):
#         try:
#             with socket.create_connection((ip,port), timeout=10) as connection:
#                banner = connection.recv(1024).decode('utf-8')
#                response_data.update({'state': 'open', 'banner': banner})
#         except socket.error as err:
#             response_data.update({'state': 'open but unable to receive banner', 'error': str(err)})
#     else:
#         response_data['state'] = 'closed or filtered'
#     return response_data 

def syn_scan(ip, port):
    packet = IP(dst=ip)/TCP(dport=port, flags="S")
    # sr 함수는 (발송된 패킷, 받은 응답) 튜플의 리스트를 반환
    # 여기서는 받은 응답만 필요하므로, _ 를 사용해 발송된 패킷 부분을 무시
    ans, _ = sr(packet, timeout=2, verbose=0)  # ans는 받은 응답 리스트
    for sent, received in ans:
        if received and received.haslayer(TCP):
            if received[TCP].flags & 0x12:  # SYN-ACK 확인
                return True  # 포트열림
            elif received[TCP].flags & 0x14:  # RST-ACK 확인
                return False  # 포트 닫힘
    return False  # 응답없거나 다른에러

# def scan_udp_port(host, port):
#     #port = 520
#     response_data = {
#         'service': "UDP",
#         'port': port,
#         'state': 'open or filterd'
#     }
#     packet = IP(dst=host)/UDP(dport=port)
#     response = sr1(packet, timeout=3, verbose=0)
    
#     if response is None:
#         response_data['error'] = 'No response (possibly open or filtered).'
#     elif response.haslayer(ICMP):
#         if int(response.getlayer(ICMP).type) == 3 and int(response.getlayer(ICMP).code) == 3:
#             response_data['state'] = 'closed'
#         else:
#             response_data['error'] = f"ICMP message received (type: {response.getlayer(ICMP).type}, code: {response.getlayer(ICMP).code})"
#     else:
#         response_data['error'] = 'Received unexpected response.'
        
#     return response_data


def scan_telnet_port(host, port):
    #port = 23
    response_data = {'serivce': "Telnet/TCP", 'port': port, 'state': 'closed'}
    
    try:
        tn = telnetlib.Telnet(host, port, timeout=5)  # Telnet 객체 생성 및 서버에 연결 (타임아웃 설정)
        banner = tn.read_until(b"\r\n", timeout=5).decode('utf-8').strip()  # 배너 정보 읽기
        tn.close()  # 연결 종료
        response_data['state'] = 'open'
        response_data['banner'] = banner
    except ConnectionRefusedError:
        response_data['error'] = '연결거부'
    except Exception as e:
        response_data['state'] = 'error'
        response_data['error'] = str(e)
    return response_data

#123 jo
def scan_ntp_port(host, port, timeout=1):
    message = '\x1b' + 47 * '\0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    response_data = {}

    sock.sendto(message.encode('utf-8'), (host, port))
    response, _ = sock.recvfrom(1024)
    sock.close()

    unpacked = struct.unpack('!B B B b 11I', response)
    t = struct.unpack('!12I', response)[10] - 2208988800
    response_data = {
        'service':'NTP/UDP',
        'port': port,
        'state': 'open',
        'stratum': unpacked[1],
        'poll': unpacked[2],
        'precision': unpacked[3],
        'root_delay': unpacked[4] / 2**16,
        'root_dispersion': unpacked[5] / 2**16,
        'ref_id': unpacked[6],
        'server_time': time.ctime(t)
    }
    return response_data
#445 jo
def scan_smb_port(host, port=445, timeout=1):
    response_data = {
        'service': 'SMB/TCP',
        'port': port,
        'state': 'closed',
        'negotiated_dialect': None,
        'error_message': None
    }

    try:
        connection = Connection(uuid.uuid4(), host, port)
        
        connection.connect(timeout=timeout)

        response_data['state'] = 'open'
        response_data['negotiated_dialect'] = str(connection.negotiated_dialect)
    
    except Exception as e:
        response_data['error_message'] = str(e)
    
    finally:
        if response_data['state'] == 'open':
            connection.disconnect()

    return response_data
#902 jo
# def scan_vmware_port(host, port=902, timeout=1):
#     response_data = {'service': 'VMWARE/TCP', 'port': port, 'state': 'closed'}
#     sock = None 

#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.settimeout(timeout)
#         sock.connect((host, port))

#         response = sock.recv(1024) 

#         if response:
#             response_data['state'] = 'open'
#             try:
#                 response_data['banner'] = response.decode('utf-8').strip()
#             except UnicodeDecodeError:
#                 response_data['banner'] = response.hex()
#         else:
#             response_data['state'] = 'no response'

#     except socket.timeout:
#         response_data['error_message'] = 'Connection timed out'
#     except socket.error as e:
#         response_data['state'] = 'error'
#         response_data['error_message'] = str(e)
#     finally:
#         if sock:
#             sock.close()  

#     return response_data

#3306 jo
def scan_mysql_port(host, port, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((host, port))
    packet = s.recv(1024)
    s.close()

    if packet:
        end_index = packet.find(b'\x00', 5)
        server_version = packet[5:end_index].decode('utf-8')
        thread_id = struct.unpack('<I', packet[0:4])[0]
        cap_low_bytes = struct.unpack('<H', packet[end_index + 1:end_index + 3])[0]
        cap_high_bytes = struct.unpack('<H', packet[end_index + 19:end_index + 21])[0]
        server_capabilities = (cap_high_bytes << 16) + cap_low_bytes
        response_data = {
            'service': 'MY SQL/TCP',
            'port': port,
            'state': 'open',
            'server_version': server_version,
            'thread_id': thread_id,
            'server_capabilities': f'{server_capabilities:032b}'
        }
        return response_data
    

def scan_imap_port(host, port, timeout = 5):
    response_data = {'service':'','port': port, 'state': 'closed'}
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)

    try:
        if port == 993:
            imap_server = imaplib.IMAP4_SSL(host,port)
            response_data['service'] = 'IMAPS/TCP'
        else:
            imap_server = imaplib.IMAP4(host,port)
            response_data['service'] = 'IMAP/TCP'

        banner_info = imap_server.welcome
        response_data['state'] = 'open'
        response_data['banner'] = banner_info
        imap_server.logout()

    except imaplib.IMAP4.error as imap_error:
        response_data['state'] = 'error'
        response_data['error'] = imap_error

    except Exception as e:
        response_data['state'] = 'error'
        response_data['error'] = str(e)

    finally:
        socket.setdefaulttimeout(original_timeout)

    return response_data
#승희님 161    
def scan_snmp_port(host, port):
    community = 'public'
    response_data = {'service':'SNMP/UDP', 'port': port, 'state': 'closed'}

    # OID 객체 생성
    sysname_oid = ObjectIdentity('SNMPv2-MIB', 'sysName', 0) #시스템 이름
    sysdesc_oid = ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0) #시스템 설명 정보 
    
    try: 
        #SNMPD 요청 생성 및 응답
        snmp_request = getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, port), timeout=2, retries=2),
            ContextData(),
            ObjectType(sysname_oid),
            ObjectType(sysdesc_oid)
        )
        
        #요청에 대한 결과 추출
        error_indication, error_status, error_index, var_binds = next(snmp_request)
                
        if error_indication:
            response_data['state'] = 'error'
            response_data['error'] = str(error_indication)
        elif error_status:
            response_data['state'] = 'error'
            response_data['error'] = f'SNMP error state: {error_status.prettyPrint()} at {error_index}'
        else:
            response_data['state'] = 'open'
            for var_bind in var_binds:
                if sysname_oid.isPrefixOf(var_bind[0]):
                    response_data['sysname'] = var_bind[1].prettyPrint()
                elif sysdesc_oid.isPrefixOf(var_bind[0]):
                    response_data['sysinfo'] = var_bind[1].prettyPrint()
    
    except socket.timeout as timeout_error:
        response_data['state'] = 'error'
        response_data['error'] = timeout_error

    except socket.error as socket_error:
        response_data['state'] = 'error'
        response_data['error'] = socket_error

    except Exception as e:
        response_data['state'] = 'error'
        response_data['error'] = f'Unexpected error: {str(e)}'
    
    return response_data



# 영창님 21, 22 통합
def scan_ftp_ssh_port(host,port):
    if port == 21:
        service_name = 'FTP/TCP'
    elif port == 22:
        service_name = 'SSH/TCP'
    else:
        service_name = '알 수 없는 서비스'
        
    response_data = {'service':service_name,'port': port, 'state': 'closed'}

    try:
        # FTP 서버에 연결 시도
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 연결 시도 시간 초과 설정
        result = sock.connect_ex((host, port))
        
        if result == 0:
            # 포트가 열려 있을 때
            banner = sock.recv(1024).decode('utf-8')
            response_data['state'] = 'open'
            response_data['banner'] = banner
        else:
            # 포트가 닫혀 있거나 필터링됐을 때
            response_data['state'] = 'closed'
        
    except socket.error as err:
        response_data['state'] = 'error'
        response_data['error'] = str(err)
        
    finally:
        # 소켓 닫기
        sock.close()
        
    return response_data

#다솜님 80
def scan_http_port(target_host, port):
    response_data = {
        'service': 'HTTP/TCP',
        'port': port,
        'state': 'closed',
    }

    try:
        with socket.create_connection((target_host, port), timeout=5) as sock:
            sock.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target_host.encode() + b"\r\n\r\n")
            response = b""
            while b"\r\n\r\n" not in response:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response += chunk

            banner = response.decode("utf-8").strip()
            response_data['state'] = 'open'
            response_data['banner'] = banner
    except socket.timeout:
        response_data['state'] = 'timeout'
        response_data['error'] = 'Connection timed out'
    except socket.error as e:
        response_data['state'] = 'error'
        response_data['error'] = str(e)

    return response_data

#다솜님 110
def scan_pop3_port(target_host, port):
    response_data = {'service':'POP3/TCP','port': port, 'state': 'closed'}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((target_host, port))
        response = sock.recv(1024).decode('utf-8')
        response_data['state'] = 'open'
        response_data['banner'] = response.strip()
    except socket.timeout:
        response_data['state'] = 'no response'
    except Exception as e:
        response_data['state'] = 'error'
        response_data['error'] = str(e)
    finally:
        if sock:
            sock.close()

    return response_data

# def scan_rdp_port(ip, port=3389):
#     response_data = {'port': port, 'state': 'closed', 'error': None}
#     if syn_scan(ip, port):
#         try:
#             # RDP 서버에 TCP 연결 시도
#             connection = socket.create_connection((ip, port), timeout=10)
#             response_data['state'] = 'open'
#             # RDP 서비스의 배너 정보를 직접 받는 것은 일반적이지 않으므로, 연결 성공 여부만 확인
#         except socket.error as err:
#             response_data['state'] = 'open but unable to connect'
#             response_data['error'] = str(err)
#         finally:
#             # 연결이 성공적으로 생성되었으면 종료
#             if 'connection' in locals():
#                 connection.close()
#     else:
#         response_data['state'] = 'closed or filtered'
#     return response_data

# 135
def scan_rsync_port(ip, port):
    response_data = {
        'port': port,
        'state': None,
        'banner': None,
        'error_message': None
    }
    try:
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        response = s.recv(1024).decode('utf-8').strip()
        response_data['state'] = 'open'
        response_data['banner'] = response
    except socket.timeout:
        response_data['state'] = 'closed'
    except Exception as e:
        response_data['state'] = 'error'
        response_data['error_message'] = str(e)
    finally:
        s.close() if 's' in locals() else None

    return response_data

#443 jo
def scan_https_port(host, port=443, timeout=5):
    response_data = {'service': 'HTTPS/TCP', 'port': port, 'state': 'open', 'banner': None}
    urllib3.disable_warnings(InsecureRequestWarning)
    url = f"https://{host}:{port}"

    try:
        response = requests.get(url, timeout=timeout, verify=False)

        server_header = response.headers.get('Server', None)
        if server_header:
            response_data['banner'] = server_header
        else:
            response_data['error'] = 'Server header not found'
    except requests.exceptions.Timeout:
        response_data['error'] = 'Connection timed out'
    except requests.exceptions.SSLError as e:
        response_data['error'] = 'SSL Error: ' + str(e)
    except requests.exceptions.RequestException as e:
        response_data['error'] = 'Request Error: ' + str(e)

    return response_data
#53 jo
def scan_dns_port(host, timeout=5):
    response_data = {'service': 'DNS/TCP|UDP', 'port': 53, 'state': 'closed', 'banner': None}

    try:        
        query = dns.message.make_query('version.bind', dns.rdatatype.TXT, dns.rdataclass.CHAOS)

        response = dns.query.udp(query, host, timeout=timeout)

        for rrset in response.answer:
            for txt in rrset:
                response_data['state'] = 'open'
                response_data['banner'] = txt.strings[0].decode('utf-8')
                break

    except (dns.exception.Timeout, dns.query.BadResponse, dns.query.UnexpectedSource) as e:
        response_data['error'] = f'DNS Query Error: {e}'
    except Exception as e:
        response_data['error'] = f'Error: {e}'

    return response_data
#389 jo
def scan_ldap_port(host, port=389, timeout=1):
    response_data = {
        'service': 'LDAP/TCP',
        'port': port,
        'state': 'closed',
    }

    server = Server(host, port=port, get_info=ALL, connect_timeout=timeout)

    try:
        with Connection(server, auto_bind=True) as conn:
            response_data['state'] = 'open'

            if server.info:
                ldap_versions = server.info.supported_ldap_versions
                if ldap_versions:
                    response_data['supported_ldap_versions'] = ldap_versions

                naming_contexts = server.info.naming_contexts
                if naming_contexts:
                    response_data['naming_contexts'] = naming_contexts

                Supported_SASL_mechanisms = server.info.supported_sasl_mechanisms
                if Supported_SASL_mechanisms:
                    response_data['Supported SASL mechanisms'] = Supported_SASL_mechanisms

    except Exception as e:
        response_data['error'] = f'LDAP Error: {e}'

    return response_data

#3389 jo
def scan_rdp_port(ip, port=3389, timeout=5):
    response_data = {'service': 'RDP/TCP', 'port': port, 'state': 'closed', 'error': None}
    
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        response_data['state'] = 'open'

        
    except socket.timeout:
        response_data['error'] = 'Connection timed out'
    except socket.error as err:
        response_data['state'] = 'closed or filtered'
        response_data['error'] = str(err)
    finally:
        if 'sock' in locals():
            sock.close()
    
    return response_data

#520 jo
def scan_rip_port(host, port=520, timeout=3):
    response_data = {'service': 'RIP', 'port': port, 'state': 'closed or filtered'}
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    try:
        sock.sendto(b"Hello", (host, port))
        data, _ = sock.recvfrom(1024)
        response_data['state'] = 'open'
    except socket.timeout:
        response_data['error'] = 'No response (possibly open or filtered).'
    except Exception as e:
        response_data['error'] = str(e)
    finally:
        sock.close()
    
    return response_data
#69 jo
# def scan_tftp_server(host, port=69):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     message = b"\x00\x01fakefile\x00octet\x00"
#     response_data = {'service': 'TFTP/UDP', 'port': port,  'info': 'unknown'}

#     try:
#         sock.sendto(message, (host, port))
#         data, _ = sock.recvfrom(1024) 

#         # TFTP 에러 패킷의 OpCode는 5, 에러 메시지는 패킷의 나머지 부분
#         if data[1] == 5: 
#             error_message = data[4:].decode('utf-8').lower()
#             if 'netkit' in error_message:
#                 response_data['info'] = 'Netkit TFTP'
#             elif 'atftp' in error_message:
#                 response_data['info'] = 'atftp'
#             else:
#                 response_data['info'] = 'Other TFTP Server'

#     except socket.timeout:
#         print('No response from server')
#     except Exception as e:
#         print(f'Error: {e}')
#     finally:
#         sock.close()

#     return response_data

#111 jo
# def scan_rpcbind_port(host, port=111, timeout=3):
#     response_data = {'service': 'RPC/TCP', 'port': port, 'state': 'closed', 'details': None}

#     rpc_request = b'\x72\xFE\x1D\x13' 

#     try:
#         with socket.create_connection((host, port), timeout=timeout) as sock:
#             sock.sendall(rpc_request)  
#             response = sock.recv(1024) 

#             if response:
#                 response_data['state'] = 'open'
#                 response_data['details'] = 'Received RPC response'
#             else:
#                 response_data['details'] = 'No response from RPC service'

#     except socket.timeout:
#         response_data['details'] = 'Connection timed out'
#     except socket.error as e:
#         response_data['details'] = f'Socket Error: {e}'

#     return response_data

#995 jo
# def scan_pop3S_port(host, port=995, timeout=3):
#     response_data = {'service': 'POP3S/TCP', 'port': port, 'state': 'closed or filtered', 'banner': None}

#     try:
#         with socket.create_connection((host, port), timeout=timeout) as sock:
#             banner = sock.recv(1024).decode('utf-8').strip()
#             response_data['state'] = 'open'
#             response_data['banner'] = banner

#     except socket.timeout:
#         response_data['error'] = 'Connection timed out'
#     except socket.error as e:
#         response_data['error'] = 'Socket Error: ' + str(e)

#     return response_data
#25 jo
def scan_smtp_port(host, port=25, timeout=7):
    response_data = {'service': 'SMTP/TCP', 'port': port, 'state': 'closed', 'banner': None}

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            banner = sock.recv(1024).decode('utf-8').strip()
            if banner:
                response_data['state'] = 'open'
                response_data['banner'] = banner
            else:
                response_data['details'] = 'No response from SMTP service'

    except socket.timeout:
        response_data['details'] = 'Connection timed out'
    except socket.error as e:
        response_data['details'] = f'Socket Error: {e}'

    return response_data
#587 jo
def scan_smtp_submission_port(host, port=587, timeout=7):
    response_data = {'service': 'SMTP-Submission/TCP', 'port': port, 'state': 'closed', 'banner': None}

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            banner = sock.recv(1024).decode('utf-8').strip()
            if banner:
                response_data['state'] = 'open'
                response_data['banner'] = banner
            else:
                response_data['details'] = 'No response from SMTP-Submission service'

    except socket.timeout:
        response_data['details'] = 'Connection timed out'
    except socket.error as e:
        response_data['details'] = f'Socket Error: {e}'

    return response_data