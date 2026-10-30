"""
MyMiniCloud - Automated Integration Test Suite
Validates all 9 core services and 10 extended features.
"""

import sys
import time
import json
import socket
import urllib.request
import urllib.error
import urllib.parse
import subprocess

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
WARN = "\033[93m[WARN]\033[0m"

results = []

def record(test_id, name, success, details=""):
    status = PASS if success else FAIL
    print(f"{status} {test_id}: {name}")
    if details:
        print(f"       Details: {details}")
    results.append({"id": test_id, "name": name, "success": success, "details": details})

def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8"), dict(response.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8"), dict(e.headers)
    except Exception as e:
        return 0, str(e), {}

def http_post_form(url, data_dict):
    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8"), dict(response.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8"), dict(e.headers)
    except Exception as e:
        return 0, str(e), {}

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return res.returncode == 0, res.stdout + res.stderr
    except Exception as e:
        return False, str(e)

print("\n" + "="*80)
print("             MYMINICLOUD AUTOMATED INTEGRATION TEST SUITE")
print("="*80 + "\n")

# ------------------------------------------------------------------------------
# Test 1: Web Frontend Server & Blog
# ------------------------------------------------------------------------------
code, body, _ = http_get("http://localhost:8080/")
home_ok = (code == 200 and "MyMiniCloud – Home" in body)

code_blog, body_blog, _ = http_get("http://localhost:8080/blog/")
blog_ok = (code_blog == 200 and ("MyMiniCloud – Blog" in body_blog or "Blog" in body_blog))

code_b1, _, _ = http_get("http://localhost:8080/blog/blog1.html")
code_b2, _, _ = http_get("http://localhost:8080/blog/blog2.html")
code_b3, _, _ = http_get("http://localhost:8080/blog/blog3.html")
articles_ok = (code_b1 == 200 and code_b2 == 200 and code_b3 == 200)

record("TEST-01", "Web Frontend & 3 Blog Posts", home_ok and blog_ok and articles_ok,
       f"Home: {code}, Blog: {code_blog}, Blog1/2/3: {code_b1}/{code_b2}/{code_b3}")

# ------------------------------------------------------------------------------
# Test 2: Flask API - Students JSON
# ------------------------------------------------------------------------------
code, body, _ = http_get("http://localhost:8085/student")
students_ok = False
student_count = 0
try:
    if code == 200:
        data = json.loads(body)
        student_list = data.get("data", data)
        student_count = len(student_list)
        students_ok = (student_count == 5)
except Exception:
    pass

record("TEST-02", "Flask API GET /student (5 Students JSON)", students_ok,
       f"Status: {code}, Students returned: {student_count}")

# ------------------------------------------------------------------------------
# Test 3: Relational Database (MariaDB studentdb & students table)
# ------------------------------------------------------------------------------
code, body, _ = http_get("http://localhost:8085/api/students-db")
db_ok = False
db_count = 0
try:
    if code == 200:
        data = json.loads(body)
        db_records = data.get("data", [])
        db_count = len(db_records)
        db_ok = (db_count >= 5)
except Exception:
    pass

record("TEST-03", "MariaDB Connection & studentdb.students Query", db_ok,
       f"Status: {code}, DB records found: {db_count}")

# ------------------------------------------------------------------------------
# Test 4: Keycloak IAM & JWT Verification (Protected Endpoint)
# ------------------------------------------------------------------------------
# 4a: Endpoint /secure must reject request without token
code_unauth, _, _ = http_get("http://localhost:8085/secure")
rejected_ok = (code_unauth == 401)

# 4b: Obtain token from Keycloak token endpoint
token_url = "http://localhost:8081/realms/MyMiniCloud/protocol/openid-connect/token"
token_payload = {
    "client_id": "flask-app",
    "grant_type": "password",
    "username": "sv01",
    "password": "password123"
}
code_tok, body_tok, _ = http_post_form(token_url, token_payload)
token = None
try:
    if code_tok == 200:
        tok_data = json.loads(body_tok)
        token = tok_data.get("access_token")
except Exception:
    pass

jwt_auth_ok = False
if token:
    code_sec, body_sec, _ = http_get("http://localhost:8085/secure", headers={"Authorization": f"Bearer {token}"})
    jwt_auth_ok = (code_sec == 200 and "sv01" in body_sec)

record("TEST-04", "Keycloak OIDC JWT Verification (Missing token -> 401, Valid JWT -> 200)", rejected_ok and jwt_auth_ok,
       f"Unauth status: {code_unauth}, Token request: {code_tok}, Secure access: {jwt_auth_ok}")

# ------------------------------------------------------------------------------
# Test 5: MinIO Object Storage (Buckets & Uploaded Files)
# ------------------------------------------------------------------------------
ok, minio_out = run_cmd("docker exec object-storage-server mc ls /data")
profile_bucket = "profile-pics" in minio_out
docs_bucket = "documents" in minio_out
record("TEST-05", "MinIO S3 Buckets (profile-pics & documents)", profile_bucket and docs_bucket,
       f"Buckets verified in MinIO storage: profile-pics={profile_bucket}, documents={docs_bucket}")

# ------------------------------------------------------------------------------
# Test 6: Internal DNS Server (BIND9 Resolution)
# ------------------------------------------------------------------------------
ok, dns_out = run_cmd("docker exec internal-dns-server dig @127.0.0.1 web-frontend-server.cloud.local +short")
dns_resolved = "10.10.10.10" in dns_out
record("TEST-06", "BIND9 DNS Resolution (web-frontend-server.cloud.local)", dns_resolved,
       f"Resolved IP: {dns_out.strip()}")

# ------------------------------------------------------------------------------
# Test 7: Prometheus Monitoring (Targets State UP)
# ------------------------------------------------------------------------------
code_prom, body_prom, _ = http_get("http://localhost:9090/api/v1/targets")
targets_up = False
up_count = 0
try:
    if code_prom == 200:
        prom_data = json.loads(body_prom)
        active_targets = prom_data.get("data", {}).get("activeTargets", [])
        up_targets = [t for t in active_targets if t.get("health") == "up"]
        up_count = len(up_targets)
        targets_up = (up_count >= 2)
except Exception:
    pass

record("TEST-07", "Prometheus Scrape Targets Status (UP)", targets_up,
       f"Status: {code_prom}, Targets UP: {up_count}")

# ------------------------------------------------------------------------------
# Test 8: Grafana Dashboard Provisioning
# ------------------------------------------------------------------------------
code_graf, body_graf, _ = http_get("http://localhost:3000/api/health")
graf_ok = (code_graf == 200 and "ok" in body_graf)
record("TEST-08", "Grafana Observability Dashboard Service", graf_ok,
       f"Grafana Health Status: {code_graf}")

# ------------------------------------------------------------------------------
# Test 9: API Gateway Reverse Proxy Routing
# ------------------------------------------------------------------------------
code_gw_web, _, hdrs_web = http_get("http://localhost/")
code_gw_api, body_gw_api, _ = http_get("http://localhost/api/hello")
code_gw_stu, body_gw_stu, _ = http_get("http://localhost/student")

gw_ok = (code_gw_web == 200 and code_gw_api == 200 and code_gw_stu == 200 and "Hello from App Server!" in body_gw_api)
record("TEST-09", "API Gateway Reverse Proxy (Path-based Routing)", gw_ok,
       f"Gateway / -> {code_gw_web}, /api/hello -> {code_gw_api}, /student -> {code_gw_stu}")

# ------------------------------------------------------------------------------
# Test 10: Round Robin Load Balancing Distribution
# ------------------------------------------------------------------------------
servers_seen = set()
for _ in range(10):
    _, _, hdrs = http_get("http://localhost/")
    backend = hdrs.get("X-Upstream-Backend") or hdrs.get("x-upstream-backend")
    if backend:
        servers_seen.add(backend)
    time.sleep(0.1)

rr_ok = (len(servers_seen) >= 2)
record("TEST-10", "Round Robin Load Balancing between Web 1 & Web 2", rr_ok,
       f"Distinct Upstream Backend Nodes hit: {list(servers_seen)}")

# ------------------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------------------
print("\n" + "="*80)
total_tests = len(results)
passed_tests = sum(1 for r in results if r["success"])
print(f"SUMMARY: {passed_tests}/{total_tests} Tests Passed.")
print("="*80 + "\n")

if passed_tests == total_tests:
    print("\033[92m>>> ALL INTEGRATION TESTS PASSED SUCCESSFULLY! <<<\033[0m\n")
    sys.exit(0)
else:
    print("\033[91m>>> SOME TESTS FAILED. PLEASE CHECK DETAILS ABOVE. <<<\033[0m\n")
    sys.exit(1)
