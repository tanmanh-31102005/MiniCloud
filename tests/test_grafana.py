import urllib.request
import urllib.parse
import json

base_url = "http://localhost:3000"
headers = {"Authorization": "Basic YWRtaW46YWRtaW4="}  # admin:admin

# 1. Query CPU Usage via Grafana Datasource Proxy
q_cpu = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
url_cpu = f"{base_url}/api/datasources/proxy/1/api/v1/query?query={urllib.parse.quote(q_cpu)}"
req = urllib.request.Request(url_cpu, headers=headers)
res = urllib.request.urlopen(req)
data = json.loads(res.read())
cpu_usage = float(data["data"]["result"][0]["value"][1])
print(f"Grafana Datasource Proxy -> CPU Usage Query: {cpu_usage:.2f}%")

# 2. Query Memory Usage via Grafana Datasource Proxy
q_mem = "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / (1024 * 1024)"
url_mem = f"{base_url}/api/datasources/proxy/1/api/v1/query?query={urllib.parse.quote(q_mem)}"
req = urllib.request.Request(url_mem, headers=headers)
res = urllib.request.urlopen(req)
data_mem = json.loads(res.read())
mem_used = float(data_mem["data"]["result"][0]["value"][1])
print(f"Grafana Datasource Proxy -> Memory Used Query: {mem_used:.2f} MB")

# 3. Query Network Traffic
q_net = "sum(rate(node_network_receive_bytes_total[1m]))"
url_net = f"{base_url}/api/datasources/proxy/1/api/v1/query?query={urllib.parse.quote(q_net)}"
req = urllib.request.Request(url_net, headers=headers)
res = urllib.request.urlopen(req)
data_net = json.loads(res.read())
net_rate = float(data_net["data"]["result"][0]["value"][1])
print(f"Grafana Datasource Proxy -> Network Receive Rate: {net_rate:.2f} Bps")

# 4. Verify Dashboard Structure
req_dash = urllib.request.Request(f"{base_url}/api/dashboards/uid/myminicloud-health", headers=headers)
res_dash = urllib.request.urlopen(req_dash)
dash = json.loads(res_dash.read())["dashboard"]
print(f"Grafana Provisioned Dashboard Title: '{dash['title']}' (UID: {dash['uid']})")
print("Configured Panels:")
for p in dash["panels"]:
    print(f" - Panel ID {p['id']}: '{p['title']}' (Type: {p['type']})")

