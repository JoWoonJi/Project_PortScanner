import socket

def scan_ports(host, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port):
        print(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
            print(f'Port {port} is open')
        sock.close()
    return open_ports

scan_ports('127.0.0.1', 1, 501)
