import asyncio

async def print_numbers(name, delay):
    count = 0
    while count < 5:
        await asyncio.sleep(delay)  # 비동기 대기
        count += 1
        print(f"{name}: {count}")

async def main():
    # 두 개의 비동기 작업 생성 및 동시 실행
    task1 = asyncio.create_task(print_numbers("Task-1", 1))
    task2 = asyncio.create_task(print_numbers("Task-2", 2))

    # 모든 비동기 작업이 완료될 때까지 대기
    await task1
    await task2

# 이벤트 루프 실행
asyncio.run(main())