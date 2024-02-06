# 파이썬 멀티스레딩 방법론

Python에서는 멀티스레딩과 멀티프로세싱을 위해 주로 **`threading`**, **`concurrent.futures`**, 그리고 **`multiprocessing`** 모듈을 사용합니다. 각각의 모듈은 병렬 실행을 위한 다른 메커니즘과 추상화 수준을 제공합니다.

### **1. `threading` 모듈**

- Python의 기본 스레딩 인터페이스를 제공합니다.
- 가벼운 작업을 병렬로 수행할 때 사용합니다.
- **`Thread`** 클래스를 사용하여 직접 스레드를 생성하고 관리합니다.
- Global Interpreter Lock(GIL) 때문에, CPU 바운드 작업에는 적합하지 않을 수 있습니다. GIL은 한 번에 하나의 스레드만 Python 코드를 실행할 수 있도록 제한합니다.

### **2. `concurrent.futures` 모듈**

- **`ThreadPoolExecutor`**와 **`ProcessPoolExecutor`** 클래스를 통해 높은 수준의 스레드 및 프로세스 기반 병렬 실행 인터페이스를 제공합니다.
- **`submit()`** 함수를 사용해 실행할 작업을 스케줄하고 **`Future`** 객체로 결과를 반환받습니다.
- **`map()`** 함수를 사용해 여러 작업을 동시에 실행할 수 있으며, 결과는 반복 가능한 순서대로 반환됩니다.
- 스레딩과 프로세싱을 모두 지원하기 때문에, CPU 바운드와 I/O 바운드 작업에 모두 사용할 수 있습니다.

### **3. `multiprocessing` 모듈**

- 별도의 메모리 공간을 가진 프로세스를 생성하여 병렬 실행을 가능하게 합니다.
- CPU 바운드 작업에 적합하며, GIL의 영향을 받지 않습니다.
- **`Process`** 클래스를 사용해 직접 프로세스를 생성하고 관리할 수 있습니다.
- 프로세스 간 통신을 위한 **`Queue`**, **`Pipe`** 등의 메커니즘을 제공합니다.
- **`Pool`** 클래스를 사용해 작업을 프로세스 풀에 분산시키고 결과를 수집할 수 있습니다.

### **차이점**

- **GIL 영향**: **`threading`**과 **`concurrent.futures.ThreadPoolExecutor`**는 GIL의 영향을 받지만, **`multiprocessing`**은 프로세스 기반이므로 GIL의 제약에서 자유롭습니다.
- **메모리 공유**: **`threading`**과 **`concurrent.futures.ThreadPoolExecutor`**는 메모리를 공유하지만, **`multiprocessing`**은 각 프로세스가 별도의 메모리 공간을 가집니다.
- **사용 용이성**: **`concurrent.futures`**는 **`threading`**이나 **`multiprocessing`**에 비해 더 높은 수준의 추상화를 제공하여 사용하기 쉽습니다.
- **적용 사례**: I/O 바운드 작업에는 **`threading`**이나 **`concurrent.futures.ThreadPoolExecutor`**가 적합할 수 있고, CPU 바운드 작업에는 **`multiprocessing`**이나 **`concurrent.futures.ProcessPoolExecutor`**가 더 적합할 수 있습니다.

## 포트스캐닝에는 어떤 멀티스레딩 모델이 적합할까?

포트 스캐닝과 같은 네트워크 작업은 일반적으로 I/O 바운드 작업에 속합니다. I/O 바운드 작업은 CPU의 계산 능력보다는 입출력 작업(예: 네트워크 요청, 디스크 읽기/쓰기)의 완료를 기다리는 시간이 주를 이루는 작업입니다. 이러한 특성 때문에, 포트 스캐닝에는 **`threading`** 모듈이나 **`concurrent.futures.ThreadPoolExecutor`**를 사용하는 멀티스레딩이 적합합니다.

### **`concurrent.futures.ThreadPoolExecutor`**

- **`concurrent.futures.ThreadPoolExecutor`**는 높은 수준의 추상화를 제공하므로, 코드를 간결하게 작성할 수 있습니다.
- **`ThreadPoolExecutor`**는 내부적으로 스레드 풀을 관리하므로, 작업자 스레드의 생성과 재사용, 작업의 스케줄링 등을 사용자가 직접 관리할 필요가 없습니다.
- **`submit()`** 또는 **`map()`** 메서드를 사용해 비동기적으로 작업을 제출하고, Future 객체를 통해 결과를 쉽게 처리할 수 있습니다.
- 포트 스캐닝과 같이 동시에 많은 네트워크 연결을 시도하고 각 연결의 결과를 처리하는 경우에 특히 유용합니다.

### **`threading`**

- **`threading`** 모듈은 Python의 기본 스레딩 인터페이스를 제공하며, 더 낮은 수준의 제어를 가능하게 합니다.
- **`Thread`** 객체를 직접 생성하고 관리해야 하므로, **`ThreadPoolExecutor`**보다는 구현이 조금 더 복잡할 수 있습니다.
- 세밀한 스레드 관리가 필요하거나, 스레드 간 통신과 동기화를 직접 제어해야 하는 상황에 적합할 수 있습니다.

포트 스캐닝의 경우, 각 포트 연결 시도는 대체로 서로 독립적이며 복잡한 CPU 연산을 필요로 하지 않기 때문에, **`concurrent.futures.ThreadPoolExecutor`**를 사용하는 것이 일반적으로 더 쉽고 효율적입니다. 코드를 간단하게 유지하면서도 높은 I/O 병렬성을 달성할 수 있기 때문입니다.

### 결론: 둘 다 시도, **`concurrent.futures.ThreadPoolExecutor`를 우선순위**
