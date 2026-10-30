import urllib.request
import urllib.parse
import json

def prom_query(expr):
    url = f"http://localhost:9090/api/v1/query?query={urllib.parse.quote(expr)}"
    res = urllib.request.urlopen(url)
    data = json.loads(res.read())
    return data.get("data", {}).get("result", [])

print("=== 1. PROMQL: up ===")
for r in prom_query("up"):
    instance = r["metric"].get("instance")
    job = r["metric"].get("job")
    val = r["value"][1]
    ts = r["value"][0]
    print(f"Target: {instance} | Job: {job} => Value: {val} (UnixTime: {ts})")

print("\n=== 2. PROMQL: flask_http_requests_total ===")
for r in prom_query("flask_http_requests_total"):
    ep = r["metric"].get("endpoint")
    m = r["metric"].get("method")
    s = r["metric"].get("status")
    print(f"Flask API: endpoint={ep}, method={m}, status={s} => Count: {r['value'][1]}")

print("\n=== 3. PROMQL: node_cpu_seconds_total (Idle Rate) ===")
for r in prom_query('rate(node_cpu_seconds_total{mode="idle"}[1m])')[:4]:
    cpu = r["metric"].get("cpu")
    print(f"Host CPU {cpu} idle rate: {float(r['value'][1]):.4f}")

print("\n=== 4. PROMQL: node_memory_MemAvailable_bytes ===")
for r in prom_query("node_memory_MemAvailable_bytes"):
    mem_mb = float(r["value"][1]) / (1024 * 1024)
    print(f"Host Available RAM: {mem_mb:.2f} MB")

print("\n=== 5. PROMQL: nginx_up ===")
for r in prom_query("nginx_up"):
    inst = r["metric"].get("instance")
    print(f"Web Node {inst} => Status: {r['value'][1]}")
