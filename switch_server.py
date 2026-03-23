"""
switch_server.py — Multi-switch Cisco REST API mock for classroom use
----------------------------------------------------------------------
Simulates 9 switches at a vocational school campus.
Each switch has realistic hostname, 48 ports, VLANs, and port status.

Run with:
    python switch_server.py

Listens on http://localhost:8081  (different port from router mock)
Leave running in Terminal 1, use Terminal 2 for switch_health.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# ── VLAN definitions ──────────────────────────────────────────────────────────
VLANS = {
    1:   "Default",
    10:  "Staff",
    20:  "Students",
    30:  "Admin",
    40:  "Lab-Computers",
    50:  "VoIP",
    99:  "Management",
    100: "Adult-Ed",
}

# ── Helper: build a port list ─────────────────────────────────────────────────
def make_ports(up_count, total=48, vlan_map=None, descriptions=None):
    """
    Build a list of switch ports.
    up_count   — how many ports are active (up)
    total      — total port count
    vlan_map   — dict of port_index: vlan_id (overrides default)
    descriptions — dict of port_index: description string
    """
    ports = []
    vlan_map    = vlan_map    or {}
    descriptions = descriptions or {}

    for i in range(1, total + 1):
        name   = f"FastEthernet0/{i}" if i <= 24 else f"GigabitEthernet0/{i-24}"
        status = "up" if i <= up_count else "down"
        vlan   = vlan_map.get(i, 20)
        desc   = descriptions.get(i, "")
        ports.append({
            "name":        name,
            "oper-status": status,
            "enabled":     status == "up",
            "vlan":        vlan,
            "description": desc,
        })

    # Add uplink port
    ports.append({
        "name":        "GigabitEthernet0/49",
        "oper-status": "up",
        "enabled":     True,
        "vlan":        99,
        "description": "Uplink to MDF-CORE-01",
    })

    return ports

# ── Switch inventory ──────────────────────────────────────────────────────────

SWITCHES = {
    "10.10.99.1": {
        "hostname":    "MDF-CORE-01",
        "location":    "Main Distribution Frame - Server Room",
        "vlans":       VLANS,
        "ports": make_ports(
            up_count=38,
            total=48,
            vlan_map={1: 99, 2: 99, 3: 10, 4: 10, 5: 30, 6: 30,
                      7: 50, 8: 50, 9: 40, 10: 40},
            descriptions={
                1:  "Uplink - ISP Firewall",
                2:  "Uplink - Backup Link",
                3:  "To IDF-COMP-LAB-01",
                4:  "To IDF-CS-CLASS-01",
                5:  "To IDF-NET-CLASS-01",
                6:  "To IDF-ADMIN-01",
                7:  "To IDF-ADULT-ED-01",
                8:  "To IDF-WING-A-01",
                9:  "To IDF-WING-B-01",
                10: "To IDF-WING-C-01",
            }
        )
    },
    "10.10.99.2": {
        "hostname":    "IDF-NET-CLASS-01",
        "location":    "Networking Classroom",
        "vlans":       {1: "Default", 20: "Students", 40: "Lab-Computers", 99: "Management"},
        "ports": make_ports(
            up_count=28,
            total=48,
            vlan_map={i: 40 for i in range(1, 25)} |
                     {i: 20 for i in range(25, 49)},
            descriptions={
                **{i: f"Student workstation {i}" for i in range(1, 25)},
                **{i: f"Lab device {i-24}" for i in range(25, 33)},
            }
        )
    },
    "10.10.99.3": {
        "hostname":    "IDF-COMP-LAB-01",
        "location":    "Computer Lab",
        "vlans":       {1: "Default", 20: "Students", 40: "Lab-Computers", 99: "Management"},
        "ports": make_ports(
            up_count=35,
            total=48,
            vlan_map={i: 40 for i in range(1, 37)} |
                     {i: 20 for i in range(37, 49)},
            descriptions={
                **{i: f"Lab PC {i}" for i in range(1, 37)},
                37: "Teacher workstation",
                38: "Printer",
            }
        )
    },
    "10.10.99.4": {
        "hostname":    "IDF-CS-CLASS-01",
        "location":    "Computer Science Classroom",
        "vlans":       {1: "Default", 20: "Students", 40: "Lab-Computers", 99: "Management"},
        "ports": make_ports(
            up_count=22,
            total=48,
            vlan_map={i: 40 for i in range(1, 25)} |
                     {i: 20 for i in range(25, 49)},
            descriptions={
                **{i: f"Student PC {i}" for i in range(1, 23)},
                23: "Teacher workstation",
                24: "Projector",
            }
        )
    },
    "10.10.99.5": {
        "hostname":    "IDF-ADMIN-01",
        "location":    "Administrative Offices",
        "vlans":       {1: "Default", 10: "Staff", 30: "Admin", 50: "VoIP", 99: "Management"},
        "ports": make_ports(
            up_count=18,
            total=48,
            vlan_map={i: 30 for i in range(1, 13)} |
                     {i: 50 for i in range(13, 25)} |
                     {i: 10 for i in range(25, 49)},
            descriptions={
                **{i: f"Admin office {i}" for i in range(1, 13)},
                **{i: f"VoIP phone {i-12}" for i in range(13, 25)},
                25: "Principal office",
                26: "Guidance office",
                27: "Main office printer",
            }
        )
    },
    "10.10.99.6": {
        "hostname":    "IDF-ADULT-ED-01",
        "location":    "Adult Education Wing",
        "vlans":       {1: "Default", 100: "Adult-Ed", 20: "Students", 99: "Management"},
        "ports": make_ports(
            up_count=14,
            total=48,
            vlan_map={i: 100 for i in range(1, 37)} |
                     {i: 20 for i in range(37, 49)},
            descriptions={
                **{i: f"Adult Ed workstation {i}" for i in range(1, 15)},
                15: "Instructor workstation",
                16: "Printer",
            }
        )
    },
    "10.10.99.7": {
        "hostname":    "IDF-WING-A-01",
        "location":    "Wing A",
        "vlans":       {1: "Default", 10: "Staff", 20: "Students", 99: "Management"},
        "ports": make_ports(
            up_count=20,
            total=48,
            vlan_map={i: 10 for i in range(1, 13)} |
                     {i: 20 for i in range(13, 49)},
        )
    },
    "10.10.99.8": {
        "hostname":    "IDF-WING-B-01",
        "location":    "Wing B",
        "vlans":       {1: "Default", 10: "Staff", 20: "Students", 99: "Management"},
        "ports": make_ports(
            up_count=16,
            total=48,
            vlan_map={i: 10 for i in range(1, 13)} |
                     {i: 20 for i in range(13, 49)},
        )
    },
    "10.10.99.9": {
        "hostname":    "IDF-WING-C-01",
        "location":    "Wing C",
        "vlans":       {1: "Default", 10: "Staff", 20: "Students", 99: "Management"},
        "ports": make_ports(
            up_count=12,
            total=48,
            vlan_map={i: 10 for i in range(1, 13)} |
                     {i: 20 for i in range(13, 49)},
        )
    },
}

# ── Build URL routes ──────────────────────────────────────────────────────────

def build_routes():
    routes = {}
    for ip, sw in SWITCHES.items():

        # Hostname
        routes[f"/switch/{ip}/restconf/data/Cisco-IOS-XE-native:native/hostname"] = {
            "Cisco-IOS-XE-native:hostname": sw["hostname"]
        }

        # Interface list
        routes[f"/switch/{ip}/restconf/data/ietf-interfaces:interfaces/interface"] = {
            "ietf-interfaces:interface": [
                {
                    "name":                      p["name"],
                    "ietf-interfaces:enabled":   p["enabled"],
                    "description":               p["description"],
                }
                for p in sw["ports"]
            ]
        }

        # Interface status
        routes[f"/switch/{ip}/restconf/data/ietf-interfaces:interfaces-state/interface"] = {
            "ietf-interfaces:interface": [
                {
                    "name":        p["name"],
                    "oper-status": p["oper-status"],
                    "vlan":        p["vlan"],
                }
                for p in sw["ports"]
            ]
        }

        # VLAN table
        routes[f"/switch/{ip}/restconf/data/Cisco-IOS-XE-vlan:vlans"] = {
            "Cisco-IOS-XE-vlan:vlan": [
                {"id": vid, "name": vname}
                for vid, vname in sw["vlans"].items()
            ]
        }

    return routes

ALL_ROUTES = build_routes()

# ── Request handler ───────────────────────────────────────────────────────────

class SwitchMockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ALL_ROUTES:
            self.send_response(200)
            self.send_header("Content-Type", "application/yang-data+json")
            self.end_headers()
            self.wfile.write(json.dumps(ALL_ROUTES[path]).encode())
            print(f"  200  GET {path}")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "endpoint not found"}')

    def log_message(self, format, *args):
        pass

# ── Start ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8081
    server = HTTPServer((HOST, PORT), SwitchMockHandler)

    total_ports = sum(len(sw["ports"]) for sw in SWITCHES.values())
    total_up    = sum(
        sum(1 for p in sw["ports"] if p["oper-status"] == "up")
        for sw in SWITCHES.values()
    )

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       Cisco Switch Mock Server — {len(SWITCHES)} switches ready           ║
╠══════════════════════════════════════════════════════════════╣""")

    for ip, sw in SWITCHES.items():
        up    = sum(1 for p in sw["ports"] if p["oper-status"] == "up")
        total = len(sw["ports"])
        vlans = len(sw["vlans"])
        print(f"║  {sw['hostname']:<22} {ip:<14} {up:>2}/{total} up  {vlans} VLANs  ║")

    print(f"""╠══════════════════════════════════════════════════════════════╣
║  Total ports across campus: {total_ports:<5}  Active: {total_up:<5}              ║
║  Running at: http://{HOST}:{PORT}                         ║
║  Leave this terminal open.                                   ║
║  Open a NEW terminal and run: python switch_health.py        ║
║  Press Ctrl+C to stop.                                       ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
