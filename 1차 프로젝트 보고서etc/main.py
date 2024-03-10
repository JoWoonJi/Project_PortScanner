import concurrent.futures
import time
from scan import *

def scan_all(host):
    scan_tasks = [
        (scan_ftp_ssh_port, {'port': 21}),
        (scan_ftp_ssh_port, {'port': 22}),
        (scan_telnet_port, {'port': 23}),
        (scan_smtp_port, {'port': 25}),
        (scan_dns_port, {'port': 53}),
        # (scan_tftp_server, {'port': 69}),
        (scan_http_port, {'port': 80}),
        (scan_pop3_port, {'port': 110}),
        #(scan_rpcbind_port, {'port': 111}),
        (scan_ntp_port, {'port': 123}),
        (scan_imap_port, {'port': 143}),
        (scan_snmp_port, {'port': 161}),
        (scan_ldap_port, {'port': 389}),
        (scan_https_port, {'port': 443}),
        (scan_smb_port, {'port': 445}),
        (scan_ssl_port, {'port': 465}),
        (scan_rip_port, {'port': 520}),
        (scan_smtp_submission_port, {'port': 587}),
        (scan_ssl_port, {'port': 636}),
        #(scan_vmware_port, {'port': 902}),
        (scan_imap_port, {'port': 993}),
        # (scan_pop3S_port, {'port': 995}),
        (scan_mysql_port, {'port': 3306}),
        (scan_rdp_port, {'port': 3389}),
        (scan_rsync_port, {'port': 135})
    ]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(task, host, metadata['port']): metadata for task, metadata in scan_tasks}
        for future in concurrent.futures.as_completed(futures):
            metadata = futures[future]
            try:
                result = future.result()
                if 'closed' not in result.get('state', '').lower() and 'closed or filtered' not in result.get('state', '').lower():
                    results.append(result)
            except Exception as e:
                error_result = {'port': metadata['port'], 'state': 'error', 'error': str(e)}
                results.append(error_result)

    sorted_results = sorted(results, key=lambda x: x['port'])
    return sorted_results

if __name__ == "__main__":
    host = '127.0.0.1'
    startTime = time.time()
    scan_all(host)
    endTime = time.time()
    print("Executed Time:", (endTime - startTime))
