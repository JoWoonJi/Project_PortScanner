# 

플라스크를 처음 구현하는 것이라 가장 간단한 형태로 만들었는데도

스캔 값이 results로 넘어가지가 않았는데 결국엔 app.py도 templates같은 flask상의 문제가 아닌

기존 multi코드의 값 형태가 flask의 results의 요건에 맞지 않아서 생긴 문제였고 

scan.py에서도 902_vmware함수에서 딕셔너리 값을 넘겨주지 않는등 복합적으로 생긴 문제였다.

이틀동안 이리해보고 저리해보고 하다가 포기하고 CLI 그냥 하자 하고 GUI도 건드려보다가 

다시 붙잡고 하다보니 결국 해결

#

플라스크 웹서버 실행

![app_code.jpg](https://github.com/JoWoonJi/PortScanner/blob/main/flask_portscanner/img/app_code.jpg)

index page

![index.jpg](https://github.com/JoWoonJi/PortScanner/blob/main/flask_portscanner/img/index.jpg)

result page

![results.jpg](https://github.com/JoWoonJi/PortScanner/blob/main/flask_portscanner/img/results.jpg)

외부 ntp서버인 [pool.ntp.org](http://pool.ntp.org) 에 스캐닝 성공,  덤으로 ntp서버에 mysql포트가 열려 있다는 것과 DB 버전 정보까지 겟.  pool.ntp.org 사이트에 수백번은 포트스캐닝한거같은데 괜찮은거맞는지… 하도 gpt가 경고해서 슬슬 걱정되기 시작
![외부url_ntp서버로포트스캐닝성공_mysql까지.jpg](https://github.com/JoWoonJi/PortScanner/blob/main/flask_portscanner/img/%EC%99%B8%EB%B6%80url_ntp%EC%84%9C%EB%B2%84%EB%A1%9C%ED%8F%AC%ED%8A%B8%EC%8A%A4%EC%BA%90%EB%8B%9D%EC%84%B1%EA%B3%B5_mysql%EA%B9%8C%EC%A7%80.jpg)
