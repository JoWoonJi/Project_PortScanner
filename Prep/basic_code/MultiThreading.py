import threading
import time

def print_numbers(thread_name, delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count += 1
        print(f"{thread_name}: {count}")

# 스레드 생성 및 시작
thread1 = threading.Thread(target=print_numbers, args=("Thread-1", 1))
thread2 = threading.Thread(target=print_numbers, args=("Thread-2", 2))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("Main thread ends")