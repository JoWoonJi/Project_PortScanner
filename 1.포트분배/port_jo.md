# 123,445,902/912,3306port by jo

- [123,445,902/912,3306port by jo](#123-445-902-912-3306port-by-jo)
- [123번 NTP](#123번-ntp)
- [445번 SMB](#445번-smb)
- [902번,912번 vmware/SOAP 프로토콜](#902번912번-vmwaresoap-프로토콜)
- [3306번 mysql](#3306번-mysql)

# 123번 NTP

123번 포트는 주로 네트워크 시간 프로토콜(Network Time Protocol, NTP) 서비스에 사용되는 포트 번호. NTP는 컴퓨터 네트워크 상의 기기들이 시간을 동기화하는 데 사용되는 프로토콜로, 시간 소스로부터 시간 정보를 받아 로컬 시계를 조정

### **NTP는 누가 개발했을까?**

NTP는 1980년대 초에 데이비드 L. 밀스(David L. Mills) 교수에 의해 개발. 초기 목적은 대학 캠퍼스 내의 다양한 시스템 간에 시간을 동기화하는 것. 이후 NTP는 인터넷을 통해 전 세계 컴퓨터들이 정확한 시간을 유지할 수 있도록 확장.

### **NTP의 역사**

- **NTPv0**: NTP의 첫 번째 버전(NTPv0)은 1985년에 RFC 958로 문서화. 이 초기 버전은 기본적인 시간 동기화 기능을 제공.
- **NTPv1**: NTP의 첫 공식 버전인 NTPv1은 1988년 RFC 1059에서 발표. 이 버전에서는 인증과 에러 검출 기능이 추가.
- **NTPv2**: NTPv2는 1989년 RFC 1119에서 소개, 분산 클라이언트-서버 모델을 도입.
- **NTPv3**: NTPv3는 1992년 RFC 1305에서 발표, 보안, 관리, 그리고 알고리즘 개선.
- **NTPv4**: NTPv4는 여전히 널리 사용되는 버전, 더 나은 성능과 확장성을 제공, RFC 5905에서 정의.

### **프로토콜의 구조**

NTP 프로토콜은 클라이언트-서버 모델을 기반. 클라이언트는 서버에 현재 시간을 요청하고, 서버는 자신의 시계 시간을 기반으로 응답. NTP 메시지는 다음과 같은 주요 필드로 구성:

- **Leap Indicator (LI)**: 윤초 조정을 위한 필드.
- **Version Number (VN)**: NTP 버전.
- **Mode**: 작업 모드(예: 클라이언트, 서버, 방송).
- **Stratum**: 시간 소스의 계층. Stratum 1은 가장 높은 정확도를 가진 시간 소스(예: 원자 시계)를 의미.
- **Poll Interval**: 클라이언트가 서버에 시간을 요청하는 간격.
- **Precision**: 시스템 시계의 정밀도.
- **Root Delay & Root Dispersion**: 시스템과 참조 시계 소스 간의 지연 및 변동.
- **Reference Identifier**: 참조 시계 소스의 식별자.
- **Reference Timestamp**: 마지막으로 시계가 설정된 시간.
- **Originate Timestamp**: 클라이언트가 요청을 보낸 시간.
- **Receive Timestamp**: 서버가 요청을 받은 시간.
- **Transmit Timestamp**: 서버가 응답을 보낸 시간.

NTP를 통한 시간 동기화의 정확도는 밀리초 단위 또는 그 이하로 매우 높다.

### NTP 통신 과정

클라이언트 요청: NTP 클라이언트는 서버로 NTP 요청 메시지를 전송. 이 메시지에는 Originate Timestamp 필드가 포함되며, 이는 클라이언트가 요청을 전송한 시각을 나타낸다.

서버 응답: NTP 서버는 요청을 받고, Receive Timestamp 필드에 요청을 받은 시각을 기록. 서버는 응답 메시지를 준비하고, Transmit Timestamp 필드에 응답을 전송한 시각을 기록한 후, 이 메시지를 클라이언트에게 전송.

시간 계산 및 동기화: 클라이언트는 서버로부터 응답을 받고, 네트워크 지연 시간과 시계 오차를 계산하여 로컬 시계를 조정

### **struct 모듈:**

- **`struct`** 모듈은 바이트 문자열을 파이썬의 데이터 구조로 패킹하거나 언패킹하는 데 사용됩니다. 이 스크립트에서는 NTP 서버로부터 받은 응답(바이트 문자열)을 처리할 때 사용됩니다.
- **`struct.unpack('!12I', response)`** 코드는 네트워크에서 받은 바이트 문자열(**`response`**)을 12개의 unsigned integer (**`I`**)로 언패킹합니다. **`!`**는 네트워크 바이트 오더(big-endian)를 나타냅니다.
- 이러한 방식으로 언패킹된 데이터 중 10번째 unsigned integer는 NTP 타임스탬프를 포함하고 있으며, 이를 Unix 시간으로 변환하는 데 사용됩니다.

### **time 모듈:**

- **`time`** 모듈은 시간 관련 함수를 제공합니다. 이 스크립트에서는 NTP 응답으로부터 얻은 시간 스탬프를 사람이 읽을 수 있는 형태로 변환하는 데 사용됩니다.
- **`time.ctime(t)`** 함수는 초 단위의 시간(여기서는 **`t`**)을 받아서 날짜와 시간을 나타내는 문자열로 변환합니다. 이 문자열은 현지 시간대를 기준으로 합니다.
- **`t -= 2208988800`** 코드는 NTP 타임스탬프에서 1900년부터 1970년까지의 초를 빼서 Unix epoch(1970년 1월 1일 자정 UTC 이후의 시간을 초 단위로 나타낸 것)으로 변환합니다. 이 변환은 NTP 시간이 1900년을 기준으로 하고 Unix 시간이 1970년을 기준으로 하기 때문에 필요합니다.

위 정보들을 기반으로 코드 구현

```python
import socket
import struct
import time

def port123_ntp(host, port=123, timeout=3):
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
        print(f"Server time: {time.ctime(t)}")
        return True
    except socket.timeout:
        # 타임아웃 - 응답 없음
        print(f"NTP port {port} did not respond on {host}.")
        return False
    except Exception as e:
        # 기타 오류
        print(f"Error scanning NTP port {port} on {host}: {e}")
        return False
    finally:
        sock.close()

target_host = 'pool.ntp.org' #"time.windows.com" 'pool.ntp.org' # 로컬은 시간 업데이트 수동으로 할때 열리고 닫힌다.

port123_ntp(target_host)
```

![123ntp_success.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/a4983dbd-4924-435d-b0f1-3ca8d60a02fa/bd6d1f33-96fb-4776-827d-12f3eb159721/123ntp_success.jpg)

포트가 열려있는 것을 확인하고 직접 시간 정보와 여러 정보를 받아와 띄우기

---

# 445번 SMB

SMB (Server Message Block) 프로토콜은 파일, 프린터, 직렬 포트 및 통신 리소스 등 네트워크상의 다양한 리소스에 대한 액세스를 제공하는 네트워크 파일 공유 프로토콜입니다. SMB는 일반적으로 Microsoft Windows 네트워크에서 파일 및 프린터 공유를 위해 사용되며, Linux 및 macOS를 포함한 다른 운영 체제에서도 널리 지원.

### **SMB:**

"Server Message Block"이라는 이름은 이 프로토콜이 서버와 클라이언트 간에 "메시지 블록"을 전송하는 방식으로 통신한다는 사실에서 유래..

### **SMB의 역사:**

1. **초기 버전**: SMB 프로토콜은 IBM에 의해 1980년대 중반에 개발되었습니다. 초기에는 PC 네트워크에서 파일 및 프린터 공유를 위해 사용되었습니다. DOS 네트워크에서 파일 공유를 위해 설계
2. **Microsoft와의 발전**: Microsoft는 SMB 프로토콜을 채택하고 확장하여, Windows for Workgroups 및 이후 버전의 Windows에서 네트워크 파일 및 프린터 공유의 기본 프로토콜로 만들었습니다.
3. **CIFS**: 1990년대에 Microsoft는 SMB를 확장하여 "Common Internet File System" (CIFS)을 개발했습니다. CIFS는 인터넷을 통한 파일 공유를 목적으로 했으며, SMB 프로토콜의 향상된 버전으로 간주됩니다.
4. **SMB 2.0**: 2006년, Microsoft는 Windows Vista와 Windows Server 2008에 SMB 2.0을 도입했습니다. 이 버전은 성능 향상, 보안 강화, 그리고 프로토콜의 단순화를 목표로 했습니다.
5. **SMB 3.0**: SMB 프로토콜의 더욱 발전된 형태인 SMB 3.0은 Windows 8과 Windows Server 2012에서 처음 소개되었습니다. 이 버전은 더 나은 성능, 향상된 보안 기능, 그리고 클러스터링 및 가상화 지원과 같은 새로운 기능을 제공했습니다.

SMB 프로토콜은 TCP/UDP 포트 445를 사용하여 통신. 이 포트는 Microsoft의 디렉터리 서비스와 통신하는 데 사용되며, Windows 2000 이후 버전에서는 NetBIOS 대신 SMB의 직접 전송에 주로 사용

## smb 프로토콜의 구조

### **메시지 형식:**

- **헤더**: 모든 SMB 메시지는 헤더를 포함합니다. 헤더에는 프로토콜의 버전, 명령 유형, 상태 코드, 플래그, 메시지에 대한 다양한 필드 등이 포함됩니다. 이는 메시지의 유형을 식별하고, 요청과 응답을 적절히 처리하기 위한 정보를 제공합니다.
- **파라미터**: 명령에 따라, 메시지에는 다양한 파라미터가 포함될 수 있습니다. 이 파라미터는 명령을 실행하는 데 필요한 추가 정보를 제공합니다.
- **데이터**: 메시지에 포함된 실제 데이터 또는 페이로드입니다. 이 부분에는 파일 데이터, 디렉터리 목록, 상태 정보 등 실제로 전송하려는 정보가 포함됩니다.

### **명령 및 응답:**

- SMB 프로토콜은 다양한 유형의 명령을 정의하며, 이를 통해 파일 열기, 읽기, 쓰기, 닫기, 디렉터리 생성 및 삭제, 파일 공유 등의 작업을 수행할 수 있습니다. 각 명령에 대한 응답은 요청을 처리한 결과를 포함합니다.

### **세션 및 인증:**

- SMB 프로토콜은 네트워크 상의 서버와 클라이언트 간에 세션을 설정하여 통신합니다. 인증 과정을 통해 사용자의 접근 권한을 확인하고, 이후 세션을 통해 안전하게 데이터를 교환합니다.

### **보안:**

- 초기 버전의 SMB는 보안 측면에서 취약점을 가지고 있었으나, SMB 2.x 및 SMB 3.x에서는 보안이 크게 강화되었습니다. SMB 3.x에서는 암호화, 보안 연결, 더 나은 인증 메커니즘 등을 포함하여 데이터의 안전성을 보장합니다.

파이썬 smb 라이브러리를 이용한 스캐닝 

```python
import uuid
from smbprotocol.connection import Connection
from smbprotocol.session import Session

def port445_smb(target_host):
    try:
        # SMB 연결을 위한 Connection 객체 생성
        connection = Connection(uuid.uuid4(), target_host, 445)
        connection.connect()

        # Session 객체 생성 및 익명 로그인 시도
        session = Session(connection, username="", password="")
        session.connect()

        # 연결 성공 시, SMB 서비스에 대한 정보 출력
        negotiated_dialect = connection.dialect
        print(f"SMB service is responding on {target_host}, port 445 is open.")
        print(f"Negotiated SMB Protocol Dialect: {negotiated_dialect}") # 버전 정보에 대응하는 내부상수값 도출. 예로 785가 나오면 SMB 2.0.2 버전임을 파악가. 

        # 추가 정보가 필요하면 여기서 추출
        # tree모듈에서 treeconnect클래스로 공유목록 불러오려고 했으나 파라미터값 설정이 어려움. IPC$공유등

        return True
    except Exception as e:
        print(f"Failed to connect to SMB service on {target_host}:445 - {e}")
        return False

target_host = "127.0.0.1"

port445_smb(target_host)
```

```
uuid란? "Universally Unique Identifier"의 약자로, 전 세계적으로 고유한 식별자를 생성하기 위한 표준입니다. Python의 uuid 모듈은 이러한 식별자를 생성하는 데 사용됩니다. UUID는 128비트의 길이를 가지며, 보통 32자리의 16진수로 표현되며, 이들 사이에는 일반적으로 4개의 하이픈이 포함됩니다 (예: 123e4567-e89b-12d3-a456-426614174000).

UUID는 다양한 목적으로 사용될 수 있지만, 주로 네트워크 상에서 객체를 고유하게 식별하는 데 사용됩니다. 예를 들어, 데이터베이스의 레코드, 네트워크 상의 서비스 인스턴스, 파일의 일부 등을 고유하게 식별하는 데 사용될 수 있습니다.

Python의 uuid 모듈은 여러 가지 방법으로 UUID를 생성할 수 있습니다:

uuid1(): 호스트의 MAC 주소와 현재 시각을 기반으로 UUID를 생성합니다. 이 방식은 UUID의 고유성을 보장하지만, MAC 주소를 기반으로 하므로 일부 프라이버시 문제를 일으킬 수 있습니다.
uuid3(namespace, name): 지정된 네임스페이스와 이름(문자열)을 기반으로 MD5 해시를 사용하여 UUID를 생성합니다.
uuid4(): 무작위로 생성된 UUID입니다. 이 방식은 가장 일반적으로 사용되며, 고유성이 매우 높지만 완전히 무작위이기 때문에 충돌의 가능성은 이론적으로 존재합니다.
uuid5(namespace, name): uuid3()과 유사하지만, SHA-1 해시를 사용하여 UUID를 생성합니다.
```

![445smb_success.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/a4983dbd-4924-435d-b0f1-3ca8d60a02fa/6d481d3c-6500-416f-9fd6-8f0abbca4d12/445smb_success.jpg)

포트가 열려있음을 확인.

```python
SMB 프로토콜을 사용할 때 Banner Grabbing을 수행하는 것은 HTTP나 FTP와 같은 텍스트 기반 프로토콜과는 다르다. SMB는 복잡한 이진 프로토콜이기 때문에, 연결 초기에 교환되는 메시지에서 직접적으로 "배너" 정보를 얻는 것은 표준적인 접근 방식이 아니고,
**impacket** 라이브러리의 smb.SMBConnection 객체를 사용하면 서버와의 네고시에이션 후 서버의 SMB 프로토콜 버전을 확인할 수 있다.
아래의 코드는 impacket 라이브러리를 사용하여 서버의 SMB 프로토콜 버전을 추출하는 방법이지만 익명으로는 접근이 어렵고 정확한 username과 password가 필요하므로 제외.
```

```python
# from impacket.smbconnection import SMBConnection

# def grab_smb_banner(target_host, username, password):
#     try:
#         # SMB 연결을 위한 객체 생성 및 로그인 시도
#         conn = SMBConnection(target_host, target_host, sess_port=445)
#         conn.login(username, password)

#         # 연결된 SMB 서버의 정보 추출
#         server_name = conn.getServerName()
#         server_domain = conn.getServerDomain()
#         server_os = conn.getServerOS()
#         server_signing = conn.isSigningRequired()

#         # 추출된 정보를 기반으로 배너 정보 출력
#         print(f"SMB Server Name: {server_name}")
#         print(f"SMB Server Domain: {server_domain}")
#         print(f"SMB Server OS: {server_os}")
#         print(f"SMB Signing Required: {server_signing}")
#         return True

#     except Exception as e:
#         print(f"Failed to grab SMB banner for {target_host}: {e}")
#         return False

# target_host = "127.0.0.1" 
# username = "" 
# password = "" 

# grab_smb_banner(target_host, username, password)
```

---

# 902번,912번 vmware/SOAP 프로토콜

IANA에서 정의한 1023번 내의 웰노운포트지만(apex 프로토콜로 할당되어있음) 표준 규약일뿐 같은 번호를 사용한다고해서 그 프로토콜을 쓴다는 의미는 아니다. 충돌가능성이 있을뿐. 

로컬 pc에는 902, 912 번 포트를 vmware가 차지하고 있었고 soap프로토콜을 사용한다고 한다. 

soap프로토콜에 대해 알아보자.

SOAP(Simple Object Access Protocol)는 웹 서비스 통신을 위한 프로토콜로, XML 기반 메시지를 사용하여 애플리케이션 간의 정보를 교환, SOAP의 설계는 인터넷 상에서 분산된 애플리케이션들이 HTTP, SMTP 등의 표준 네트워크 프로토콜을 통해 서로 통신할 수 있도록 하기 위한 것이라고 한다.

### **SOAP의 발전:**

- **개발 초기**: SOAP는 1998년에 마이크로소프트(Microsoft)에서 처음 개발되었습니다. 초기 버전은 XML-RPC라는 더 간단한 프로토콜을 기반으로 하고 있었으며, 원격 프로시저 호출(RPC)에 XML을 사용하는 형태였습니다.
- **버전 1.1**: SOAP 1.1은 2000년에 발표되었으며, 인터넷 프로토콜을 통해 구조화된 정보를 교환하는 표준 방법으로 널리 받아들여졌습니다. 이 버전은 W3C(World Wide Web Consortium)에 의해 표준으로 채택되었습니다.
- **버전 1.2**: SOAP 1.2는 2003년에 W3C 권고안으로 발표되었습니다. 이 버전은 전송 중 오류 처리 개선, 메시징 프레임워크의 명확한 정의, 프로토콜의 확장성 개선 등을 포함한 여러 가지 중요한 개선 사항을 도입했습니다.

### **SOAP의 현재:**

REST(Representational State Transfer)와 같은 더 간단하고 유연한 통신 방법의 등장으로 SOAP의 사용은 감소하는 추세에 있습니다. 그러나 여전히 보안, 거래성, 정형화된 계약이 필요한 엔터프라이즈급 애플리케이션에서는 SOAP가 널리 사용되고 있습니다. SOAP의 엄격한 표준 준수와 확장 가능한 프레임워크는 복잡한 비즈니스 로직을 처리하는 대규모 시스템에서 여전히 중요한 역할을 하고 있습니다.

## 프로토콜의 구조

### **1. Envelope**

SOAP Envelope는 SOAP 메시지의 가장 바깥쪽 요소로, 메시지가 SOAP 메시지임을 나타냅니다. Envelope는 메시지 내의 모든 데이터를 포함하며, **`Header`**와 **`Body`** 두 가지 주요 부분으로 구성됩니다.

### **2. Header (선택적)**

SOAP Header는 메시지에 대한 메타데이터를 포함합니다. 이는 메시지를 어떻게 처리할지에 대한 지시사항(예: 인증, 트랜잭션, 세션 관리 등)을 포함할 수 있습니다. Header 요소는 선택적이며, 메시지에 필요한 추가적인 정보가 없는 경우 생략될 수 있습니다.

### **3. Body**

SOAP Body는 실제로 전송하고자 하는 정보를 담고 있는 부분입니다. 이는 웹 서비스 호출에 필요한 매개변수나, 웹 서비스 응답에 포함된 반환 데이터 등을 포함할 수 있습니다. Body는 메시지의 핵심적인 내용을 담고 있으며, 하나 이상의 SOAP 메시지를 포함할 수 있습니다.

### **4. Fault (선택적)**

SOAP Fault는 메시지 처리 과정에서 발생한 오류 정보를 포함하는 요소입니다. Fault 요소는 Body 내에 위치할 수 있으며, 오류가 발생했을 때 오류 코드, 오류 메시지, 오류 발생 위치 등의 정보를 제공합니다. Fault 요소는 문제 해결을 위한 중요한 정보를 제공하며, 오류 처리 로직에서 활용됩니다.

soap 프로토콜을 바탕으로 코드를 짜면 soap 프로토콜의 endpoint를 알아내야하고 포트스캐너용으로 적합하지 않으므로 소켓과 배너그래빙으로 서비스가 실행중인지, 서비스의 정보를 받아오는 것으로 구현

```python
import socket

def port902_vmware_soap(host, ports, timeout=5):
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
                print(response.decode('utf-8', errors='ignore'))
            else:
                print(f"No response received from {host}:{port}")
            
        except socket.error as e:
            print(f"Error connecting to {host}:{port}: {e}")
        finally:
            sock.close()

target_host = "127.0.0.1"
ports = [902, 912]  

port902_vmware_soap(target_host, ports)
```

![902_912_success.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/a4983dbd-4924-435d-b0f1-3ca8d60a02fa/2e0d7e99-d5ed-4d87-bc47-59ff67b1317b/902_912_success.jpg)

902, 912 포트스캔으로 열려있음을 확인하고 vmware 버전정보와 프로토콜들을 받아오는데 성공

---

# 3306번 mysql

MySQL의 3306번 포트는 이 데이터베이스 관리 시스템을 위한 기본 TCP 포트. 

MySQL은 1995년에 스웨덴의 회사인 TcX에 의해 처음 개발. 

개발자인 Michael Widenius(별명 'Monty')와 David Axmark은 이 프로젝트를 시작. 

이 이름은 'Monty'의 딸 'My'의 이름과 'SQL'(Structured Query Language의 약자)을 결합한 것이군.

3306번 포트는 MySQL의 표준 포트로 자리 잡게 되었다.

시간이 지남에 따라 다양한 버전과 포크가 개발. 가장 주목할 만한 포크 중 하나는 Oracle Corporation이 Sun Microsystems를 인수한 후에 발생한 MariaDB입니다. 

## mysql 프로토콜의 구조

MySQL 프로토콜은 클라이언트와 서버 간의 통신을 관리하는 복잡한 구조를 가지고 있습니다. 이 프로토콜은 여러 단계의 핸드셰이크와 데이터 교환 과정을 포함하여, 클라이언트가 서버에 연결하고 쿼리를 실행하며 결과를 받아볼 수 있도록 설계되었습니다. MySQL 프로토콜의 주요 구조와 단계

### **1. 연결 설정 (Connection Establishment)**

- 클라이언트가 서버의 3306 포트에 TCP 연결을 시도합니다.
- 서버는 클라이언트에게 초기 핸드셰이크 패킷을 보내고, 이에는 서버의 버전, 스레드 ID, 인증 salt, 그리고 서버가 지원하는 기능들의 플래그 등이 포함됩니다.

### **2. 인증 및 핸드셰이크 (Authentication and Handshake)**

- 클라이언트는 사용자 이름, 인증 방식, 인증 데이터(패스워드와 살트를 이용하여 암호화됨), 초기 데이터베이스 이름 등을 포함한 인증 응답 패킷을 서버로 보냅니다.
- 서버는 인증 데이터를 검증하고, 성공 또는 실패 응답을 클라이언트에게 보냅니다.

### **3. 명령 실행 (Command Phase)**

- 인증이 성공하면, 클라이언트는 서버에 명령 패킷을 보낼 수 있습니다. 이 명령은 쿼리 실행, 데이터베이스 변경, 커넥션 설정 조회 등이 될 수 있습니다.
- 서버는 명령을 실행하고 결과를 클라이언트에게 보냅니다. 결과는 결과 세트, 오류 메시지, 상태 변경 알림 등 다양한 형태가 될 수 있습니다.

### **4. 데이터 전송 (Data Transfer)**

- 쿼리 결과(예: SELECT 명령의 결과)는 여러 개의 패킷으로 나뉘어 클라이언트에게 전송될 수 있습니다. 이때 각 패킷은 레코드의 한 행을 나타낼 수 있습니다.
- 또한, 서버는 결과 세트의 메타데이터(열 이름, 타입 등)도 함께 보냅니다.

### **5. 연결 종료 (Connection Termination)**

- 클라이언트 또는 서버 양쪽에서 연결을 종료할 수 있습니다. 클라이언트가 연결을 종료하려면, 종료 명령을 서버로 보냅니다.
- 서버는 연결 종료를 확인하는 응답을 보내고, TCP 연결을 닫습니다.

MySQL 프로토콜의 각 패킷은 길이, 시퀀스 번호, 그리고 페이로드를 포함하는 헤더로 시작합니다. 이 프로토콜은 확장성과 유연성을 고려하여 설계되었으며, 다양한 인증 방식, 압축, SSL/TLS를 통한 암호화 등을 지원

프로토콜 구조를 바탕으로 포트스캔 구현

```python
import socket
import struct

def port3306_mysql(host, port=3306, timeout=5):
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

target_host = "127.0.0.1"

port3306_mysql(target_host)
```

포트와 연결하고 서버버전과 스레드id 서버 캐퍼 정보를 가져옴
