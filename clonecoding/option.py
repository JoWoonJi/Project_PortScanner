# argparse 모듈을 사용하여 커맨드 라인 인터페이스(CLI)를 구성하는 방법
import argparse  # 파이썬 표준 라이브러리에서 argparse 모듈을 임포트합니다. 이 모듈은 커맨드 라인 인자를 파싱하는데 사용됩니다.
# 파싱은 데이터를 분석하여 구조를 이해하고 필요한 정보를 추출하는 과정
def option_set():
    # argparse.ArgumentParser 객체를 생성합니다. 이 객체는 프로그램의 커맨드 라인 인터페이스를 정의하는 데 사용됩니다.
    parser = argparse.ArgumentParser(description="CatchHacker Scanner - 포트 스캐닝 도구")

    # 'target_host'라는 필수 위치 인자를 추가합니다. 사용자는 이 인자를 통해 대상 호스트의 IP 주소를 입력해야 합니다.
    parser.add_argument("target_host", help="대상 호스트의 IP 주소")

    # '-p' 또는 '--ports'라는 선택적 인자를 추가합니다. 이 인자는 하나 이상의 값을 받으며(int 타입), 기본값으로 1부터 100까지의 범위를 갖습니다.
    # 사용자는 이 옵션을 통해 스캔할 특정 포트 번호를 공백으로 구분하여 입력할 수 있습니다.
    parser.add_argument("-p", "--ports", nargs="+", type=int, default=range(1, 100),
                        help="스캔할 특정 포트 번호 (공백으로 구분하여 입력)")

    # '-t' 또는 '--threads'라는 선택적 인자를 추가합니다. 이 인자는 스레드의 수를 정의하며, int 타입의 값을 받습니다. 기본값은 5입니다.
    parser.add_argument("-t", "--threads", type=int, default=5, help="Thread")

    # '-sT' 또는 '--tcp'라는 선택적 인자를 추가합니다. 이 옵션은 TCP 스캔을 수행할지 여부를 결정하는 플래그입니다.
    # 'action="store_true"'는 이 옵션이 명시될 경우 True 값을 저장하라는 의미입니다. 기본값은 True로 설정되어 있습니다.
    parser.add_argument("-sT", "--tcp", action="store_true", default=True, help="TCP Scan")

    # 설정된 인자를 파싱하여 반환합니다. 사용자가 입력한 커맨드 라인 인자들은 이 함수를 통해 처리되고, 프로그램에서 사용할 수 있는 형태로 제공됩니다.
    return parser.parse_args()