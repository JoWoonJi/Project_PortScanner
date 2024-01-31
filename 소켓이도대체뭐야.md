# 소켓의 모든 것

### **소켓의 유래**

- **용어의 유래**: "소켓"이라는 용어는 전기 소켓에서 차용된 것으로 추정됩니다. 전기 소켓이 전기 장치를 전원에 연결하는 접점 역할을 하는 것처럼, 네트워크 소켓은 네트워크 상의 두 프로그램이 데이터를 주고받을 수 있는 가상의 연결 점을 제공합니다.

### **기원과 역사**

- **ARPANET과 TCP/IP**: 소켓의 개념은 **1970년대** 초 ARPANET의 발전과 함께 등장했습니다. ARPANET은 미국 국방부의 연구 네트워크였으며, 인터넷의 전신으로 볼 수 있습니다. 이 시기에 Vinton Cerf와 Robert Kahn은 TCP/IP 프로토콜을 개발했으며, 이는 네트워크 간의 통신을 가능하게 하는 핵심 기술이 되었습니다. TCP/IP 프로토콜 스택의 개발은 소켓 프로그래밍 모델의 기반이 되었습니다.
- **BSD 소켓**: 소켓 프로그래밍 모델은 **1980년대** 초 BSD UNIX에서 크게 발전했습니다. 4.2BSD UNIX 릴리즈는 소켓 API를 포함하고 있었으며, 이는 네트워크 애플리케이션 개발을 위한 표준 인터페이스로 자리잡았습니다. BSD 소켓 API는 TCP/IP 네트워킹을 위한 프로그래밍 인터페이스를 제공했으며, 오늘날에도 여전히 사용되고 있습니다.
- **Winsock**: **1990년대** 초, 마이크로소프트와 다른 회사들은 Windows 운영 체제를 위한 소켓 API 버전인 Winsock(Windows Sockets)을 개발했습니다. Winsock은 BSD 소켓 API에 기반을 둔 것으로, Windows 기반 애플리케이션에서 네트워크 통신을 가능하게 했습니다.

### **소켓의 주요 역할:**

1. **통신 채널 제공**: 소켓은 네트워크 상의 두 엔드포인트 간에 통신 채널을 생성합니다. 이 채널을 통해 데이터 패킷을 안전하게 송수신할 수 있습니다.
2. **데이터 교환**: 소켓은 서로 다른 네트워크 장치 간, 또는 동일한 장치 내의 프로세스 간에 데이터를 교환할 수 있는 메커니즘을 제공합니다.
3. **프로토콜 추상화**: 소켓 API는 TCP, UDP와 같은 다양한 네트워크 프로토콜을 추상화하여 애플리케이션 개발자가 손쉽게 네트워크 통신 기능을 구현할 수 있게 해줍니다.
4. **연결 관리**: TCP 소켓의 경우, 연결 설정, 데이터 전송, 연결 종료와 같은 연결 지향적 통신을 관리합니다. UDP 소켓의 경우에는 비연결 지향적 통신을 지원합니다.

### **소켓이 없다면:**

1. **통신 복잡성 증가**: 소켓이 없다면, 애플리케이션 개발자는 네트워크 프로토콜의 모든 세부 사항을 직접 관리해야 합니다. 이는 네트워크 통신을 구현하는 과정을 복잡하게 만들고, 오류 발생 가능성을 높일 수 있습니다.
2. **표준화 부족**: 소켓 API는 네트워크 통신을 위한 표준화된 인터페이스를 제공합니다. 소켓이 없으면 각 애플리케이션 또는 시스템마다 고유한 통신 메커니즘이 필요하게 되어 호환성과 재사용성이 크게 저하될 수 있습니다.
3. **개발 및 유지보수 어려움**: 소켓 API를 사용하면 네트워크 통신 기능을 비교적 쉽게 구현하고 유지보수할 수 있습니다. 소켓이 없다면 이러한 작업이 훨씬 더 어려워지고 시간이 많이 소요될 것입니다.
4. **애플리케이션 간의 통신 제한**: 소켓이 제공하는 통신 채널이 없다면, 분산 시스템, 클라이언트-서버 애플리케이션, P2P 애플리케이션과 같은 네트워크 기반의 다양한 애플리케이션이 제대로 작동할 수 없을 것입니다.

에코서버로 간단한 소켓통신 구현

에코 서버는 클라이언트로부터 받은 메시지를 그대로 돌려보내는 간단한 서비스

### **TCP 에코 서버**

```python

import socket

def echo_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server is listening on {host}:{port}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

if __name__ == "__main__":
    HOST = '127.0.0.1'  # 서버의 주소
    PORT = 65432        # 서버가 통신할 포트

    echo_server(HOST, PORT)

```

### **TCP 에코 클라이언트**
```python

import socket

def echo_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b'Hello, server')
        data = s.recv(1024)

    print(f"Received from server: {data!r}")

if __name__ == "__main__":
    HOST = '127.0.0.1'  # 서버의 주소
    PORT = 65432        # 서버가 리스닝하는 포트

    echo_client(HOST, PORT)

```
