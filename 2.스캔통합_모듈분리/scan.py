import socket
import struct
import time
import uuid
from smbprotocol.connection import Connection

def port123_ntp(host, timeout=1):
    port = 123
    message = '\x1b' + 47 * '\0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    response_data = {}

    # NTP 서버로 메시지 전송 및 응답 처리
    sock.sendto(message.encode('utf-8'), (host, port))
    response, _ = sock.recvfrom(1024)
    sock.close()

    unpacked = struct.unpack('!B B B b 11I', response)
    t = struct.unpack('!12I', response)[10] - 2208988800
    response_data = {
        'port': port,
        'status': 'open',
        'stratum': unpacked[1],
        'poll': unpacked[2],
        'precision': unpacked[3],
        'root_delay': unpacked[4] / 2**16,
        'root_dispersion': unpacked[5] / 2**16,
        'ref_id': unpacked[6],
        'server_time': time.ctime(t)
    }
    return response_data

def port445_smb(host, timeout=1):
    response_data = {}
    connection = Connection(uuid.uuid4(), host, 445)
    connection.connect(timeout=timeout)
    response_data = {
        'port': 445,
        'status': 'open',
        'negotiated_dialect': connection.dialect
    }
    connection.disconnect()
    return response_data

def port902_vmware_soap(host, timeout=1):
    ports = [902]  # 902 포트만 스캔
    response_data = []

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            sock.connect((host, port))

            # SOAP 요청 본문 준비
            soap_request = f"""POST /sdk HTTP/1.1
            Host: {host}:{port}
            Content-Type: text/xml; charset=utf-8
            Content-Length: {{length}}
            SOAPAction: "urn:internalvim25/5.5"

            <?xml version="1.0" encoding="utf-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:vim25="urn:vim25">
            <soapenv:Header/>
            <soapenv:Body>
                <vim25:RetrieveServiceContent>
                <vim25:_this type="ServiceInstance">ServiceInstance</vim25:_this>
                </vim25:RetrieveServiceContent>
            </soapenv:Body>
            </soapenv:Envelope>"""

            body = soap_request.format(length=len(soap_request))
            sock.sendall(body.encode('utf-8'))

            # 서비스로부터 응답 받기
            response = sock.recv(4096)

            if response:
                response_data.append({
                    'port': port,
                    'status': 'open',
                    'response': response.decode('utf-8', errors='ignore')
                })
            else:
                response_data.append({'port': port, 'status': 'no response'})

        except socket.error as e:
            response_data.append({'port': port, 'status': 'error', 'error': str(e)})
        finally:
            sock.close()

    return response_data


def port3306_mysql(host, timeout=1):
    port = 3306
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
            'port': port,
            'status': 'open',
            'server_version': server_version,
            'thread_id': thread_id,
            'server_capabilities': f'{server_capabilities:032b}'
        }
        return response_data
