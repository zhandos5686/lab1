import json

with open(r"C:\Users\Zhandos\Downloads\githowto\githowto\repositories\lab 4\jsonnn\sample-data.json") as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print("-" * 80)

for item in data["imdata"]:
    dn = item["l1PhysIf"]["attributes"]["dn"]
    desc = item["l1PhysIf"]["attributes"].get("descr", "")
    speed = item["l1PhysIf"]["attributes"].get("speed", "inherit")
    mtu = item["l1PhysIf"]["attributes"]["mtu"]

    print(f"{dn:<50} {desc:<20} {speed:<7} {mtu:<6}")