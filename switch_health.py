"""
switch_health.py
----------------
Queries all 9 campus switches and prints a network health report.
Shows hostname, port status, VLAN summary, and unused ports.

Make sure switch_server.py is running in Terminal 1 first.
Then run this in Terminal 2:
    python switch_health.py
"""

import requests

BASE = "http://localhost:8081"
HEADERS = {"Accept": "application/yang-data+json"}

SWITCHES = [
    "10.10.99.1",
    "10.10.99.2",
    "10.10.99.3",
    "10.10.99.4",
    "10.10.99.5",
    "10.10.99.6",
    "10.10.99.7",
    "10.10.99.8",
    "10.10.99.9",
]

def get(ip, endpoint):
    url = f"{BASE}/switch/{ip}/restconf/data/{endpoint}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def check_switch(ip):
    hostname = get(ip, "Cisco-IOS-XE-native:native/hostname")\
        .get("Cisco-IOS-XE-native:hostname", "Unknown")

    iface_states = get(ip, "ietf-interfaces:interfaces-state/interface")\
        .get("ietf-interfaces:interface", [])

    vlans_data = get(ip, "Cisco-IOS-XE-vlan:vlans")\
        .get("Cisco-IOS-XE-vlan:vlan", [])

    total    = len(iface_states)
    up       = sum(1 for p in iface_states if p.get("oper-status") == "up")
    down     = total - up
    vlans_used = {p.get("vlan") for p in iface_states if p.get("vlan")}
    vlan_names = {v["id"]: v["name"] for v in vlans_data}

    return {
        "hostname":    hostname,
        "ip":          ip,
        "total":       total,
        "up":          up,
        "down":        down,
        "unused":      down,
        "vlans_active": sorted(vlans_used),
        "vlan_names":  vlan_names,
    }

# ── Report ────────────────────────────────────────────────────────────────────

print(f"\n{'='*65}")
print(f"   CAMPUS SWITCH HEALTH REPORT")
print(f"   Building: Vo-Tech Campus — 9 switches")
print(f"   Checking all switches...")
print(f"{'='*65}")

results       = []
total_ports   = 0
total_up      = 0
total_unused  = 0

for ip in SWITCHES:
    try:
        sw = check_switch(ip)
        results.append(sw)
        total_ports  += sw["total"]
        total_up     += sw["up"]
        total_unused += sw["unused"]

        vlan_list = ", ".join(
            f"VLAN{v}({sw['vlan_names'].get(v, '?')})"
            for v in sw["vlans_active"]
            if v != 1
        )

        print(f"\n  {sw['hostname']:<24} {sw['ip']}")
        print(f"  {'─'*50}")
        print(f"  Ports   : {sw['total']} total  |  {sw['up']} active  |  {sw['unused']} unused")
        print(f"  VLANs   : {vlan_list}")

    except Exception as e:
        print(f"\n  [ERR] {ip}  ({e})")

# ── Summary ───────────────────────────────────────────────────────────────────

print(f"\n{'='*65}")
print(f"  CAMPUS SUMMARY")
print(f"{'─'*65}")
print(f"  Switches checked : {len(results)}")
print(f"  Total ports      : {total_ports}")
print(f"  Active ports     : {total_up}  ({round(total_up/total_ports*100)}% utilization)")
print(f"  Unused ports     : {total_unused}  ({round(total_unused/total_ports*100)}% available)")
print(f"\n  This report took Python a few seconds.")
print(f"  Manually? About {len(results) * 10} minutes — just for this building.")
print(f"  Across 50 district switches? About {50 * 10 // 60} hours of manual work.")
print(f"{'='*65}\n")
