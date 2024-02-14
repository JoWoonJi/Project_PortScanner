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

import socket

def port902_vmware_soap(host, port=902, timeout=1):
    response_data = {'port': port, 'status': 'closed'} 

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        soap_request = f"""POST /sdk HTTP/1.1\r
                            Host: {host}:{port}\r
                            Content-Type: text/xml; charset=utf-8\r
                            Content-Length: {{length}}\r
                            SOAPAction: "urn:internalvim25/5.5"\r
                            \r
                            <?xml version="1.0" encoding="utf-8"?>
                            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:vim25="urn:vim25">
                            <soapenv:Header/>
                            <soapenv:Body>
                                <vim25:RetrieveServiceContent>
                                <vim25:_this type="ServiceInstance">ServiceInstance</vim25:_this>
                                </vim25:RetrieveServiceContent>
                            </soapenv:Body>
                            </soapenv:Envelope>"""

        body = soap_request.format(length=len(soap_request) - 2)  # '{{length}}' 자리에 실제 길이, -2는 '{{}}' 문자 길이 조정
        sock.sendall(body.encode('utf-8'))

        response = sock.recv(4096)
        sock.close()

        if response:
            response_data['status'] = 'open'
            response_data['response'] = response.decode('utf-8', errors='ignore')
        else:
            response_data['status'] = 'no response'

    except socket.error as e:
        response_data['status'] = 'error'
        response_data['error_message'] = str(e)

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
