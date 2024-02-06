import concurrent.futures
from scan import port123_ntp, port445_smb, port902_vmware_soap, port3306_mysql

def scan_all(host):
    scan_tasks = [
        (port123_ntp, {'port': 123}),
        (port445_smb, {'port': 445}),
        (port902_vmware_soap, {'port': 902}),
        (port3306_mysql, {'port': 3306})
    ]

    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_port = {executor.submit(task[0], host, task[1]['port']): task[1] for task in scan_tasks}

        for future in concurrent.futures.as_completed(future_to_port):
            task_metadata = future_to_port[future]
            try:
                result = future.result()
                if isinstance(result, dict):  # 결과가 딕셔너리인지 확인
                    results.append(result)
                else:
                    raise ValueError("Result is not a dictionary")
            except Exception as e:
                error_result = {'port': task_metadata['port'], 'status': 'error', 'error_message': str(e)}
                results.append(error_result)

    sorted_results = sorted(results, key=lambda x: x.get('port', 0))  # x['port'] 대신 x.get('port', 0)을 사용하여 오류 방지
    return sorted_results

if __name__ == "__main__":
    host = '127.0.0.1'
    scan_all_results = scan_all(host)
    for result in scan_all_results:
        print(result)
