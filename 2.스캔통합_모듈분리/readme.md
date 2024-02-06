5일에 팀원 각자 포트 3개씩 구현해오면 서비스스캔 통합 시도 / requirements.txt 생성 / 모듈 분리 - 메인, 출력, 옵션, 멀티스레딩, 통합스캐너 등

2/5 포트3개 통합 어찌저찌 성공. 445_SMB 안열린 포트 무한로딩 해결하는데 하루를 다잡아먹음.  
    멀티스레딩 분리해서 구현해봤지만 스레딩 출력결과가 중구난방이라 포트 순서대로 출력이 되지가 않음. 
    포문으로 저장받아서 간단하게 돌리면 되지않나 생각했지만 생각보다 간단하지 않음. 중복출력 이슈, 재접근 트러블 
    
2/6 다른분들꺼까지 통합하고 멀티스레딩 성공해야함

### 출력순서, 중복출력, 재접근 트러블슈팅 완료 / 모듈분리해서 멀티스레딩 구현까지는 성공 
멀티스레딩 futures 모듈 성공

![멀티스레딩_futures성공.jpg](https://github.com/JoWoonJi/PortScanner/blob/main/img/%EB%A9%80%ED%8B%B0%EC%8A%A4%EB%A0%88%EB%94%A9_futures%EC%84%B1%EA%B3%B5.jpg)

---

멀티스레딩 threading 모듈 성공

![멀티스레딩_threading성공.jpg](https://github.com/JoWoonJi/PortScanner/blob/main/img/%EB%A9%80%ED%8B%B0%EC%8A%A4%EB%A0%88%EB%94%A9_threading%EC%84%B1%EA%B3%B5.jpg)

---

2월 7일 : 다른분들꺼 통합, 메인과 옵션등 기타 모듈 구현
