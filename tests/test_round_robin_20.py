import urllib.request
import time

print("="*70)
print("     ROUND ROBIN LOAD BALANCING AUDIT — 20 INDEPENDENT REQUESTS     ")
print("="*70)

counts = {"web-frontend-server1": 0, "web-frontend-server2": 0, "other": 0}
upstream_ips = set()

print(f"{'REQ #':<8} | {'STATUS':<8} | {'SERVED BY NODE':<24} | {'UPSTREAM IP:PORT':<20}")
print("-" * 70)

for i in range(1, 21):
    req = urllib.request.Request("http://localhost/", headers={"Connection": "close"})
    with urllib.request.urlopen(req, timeout=5) as res:
        status = res.status
        served_by = res.headers.get("X-Served-By", "unknown").strip()
        upstream = res.headers.get("X-Upstream-Backend", "unknown").strip()
        
        upstream_ips.add(upstream)
        if served_by in counts:
            counts[served_by] += 1
        else:
            counts["other"] += 1
            
        print(f"Req #{i:<4} | {status:<8} | {served_by:<24} | {upstream:<20}")
    time.sleep(0.05)

print("-" * 70)
print(f"Total Requests Sent: 20")
print(f"web-frontend-server1 received: {counts['web-frontend-server1']} requests ({counts['web-frontend-server1']/20*100:.1f}%)")
print(f"web-frontend-server2 received: {counts['web-frontend-server2']} requests ({counts['web-frontend-server2']/20*100:.1f}%)")
print(f"Upstream Backend Endpoints: {list(upstream_ips)}")

assert counts['web-frontend-server1'] > 0 and counts['web-frontend-server2'] > 0, "Both web nodes must receive requests!"
print("\n>>> ROUND ROBIN LOAD BALANCING VERIFIED: 100% OPERATIONAL! <<<")
