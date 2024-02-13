# Service Scanner

This Scanner use Only TCP Open Scan and Detected Service in Port

This service identification tool consists largely of two parts. 

First, the port scan part uses TCP Open Scan to provide reliable scan results. 

Next, the service identification part directly accesses the service in the port detected as open, 
not limited to the previously known well-known service matching, and uses the port to identify which service is actually accessible

---
## How to Use
1. Download all files in repository and unzip this project
2. Please Pip install requirements before run this Scanner
```python
pip install -r requirements.txt
```
3. Go to project folder and Run "catchhacker_scanner.py"
```python
python3 catchhacker_scanner.py [IP]
```

---
## How to Modify Option
1. Option.py
Modify Default Option Like Multi Thread numbers(Just Port Scan), PortRange
2. Port_Scan.py
Modify Port Scanning Method
3. Service_Scan.py
Modify Service Scanning Method and Test Service Scan Separately
* Help for Kerberos for Windows Error 
* -> Please Download Kerberos for Windows MSI (https://web.mit.edu/KERBEROS/dist) 

---
## *Notice
Reckless port scanning can be legally responsible, so please use it only in agreed situations.

TCP Open Scan is theoretically expected to be more reliable than stealth scan, but TCP Open Scan, which is trusted, uses only TCP Open Scan to identify a port, performs all three-way Handshaking processes, and reflects the result value depending on the performance of the server and the firewall policy of the connected server.
If access to a number of services is not possible according to the performance of the server running the service scanner, the performance of the server to be identified, and the firewall policy of the server to be connected, there is a limit to speed and access rights.
