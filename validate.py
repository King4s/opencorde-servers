#!/usr/bin/env python3
"""
Validates servers.json entries for the OpenCorde server registry.

Checks per entry:
  1. Required fields present (hostname, pubkey, name, region, added)
  2. Hostname resolves via DNS
  3. GET https://{hostname}/api/v1/federation/identity responds with 200
  4. Returned public_key matches the pubkey in servers.json
  5. No duplicate hostnames

Exit code 0 = all valid, 1 = failures found.
"""

import json
import sys
import socket
import urllib.request
import urllib.error
from datetime import datetime

REQUIRED_FIELDS = {"hostname", "pubkey", "name", "region", "added"}
TIMEOUT = 10


def check_entry(entry: dict, seen_hostnames: set) -> list[str]:
    errors = []
    hostname = entry.get("hostname", "<missing>")

    # 1. Required fields
    for field in REQUIRED_FIELDS:
        if not entry.get(field):
            errors.append(f"[{hostname}] missing required field: {field}")

    # 2. Pubkey format: 64-char hex string
    pubkey = entry.get("pubkey", "")
    if len(pubkey) != 64 or not all(c in "0123456789abcdef" for c in pubkey.lower()):
        errors.append(f"[{hostname}] pubkey must be a 64-char lowercase hex string")

    # 3. Date format
    added = entry.get("added", "")
    try:
        datetime.strptime(added, "%Y-%m-%d")
    except ValueError:
        errors.append(f"[{hostname}] 'added' must be YYYY-MM-DD format, got: {added!r}")

    # 4. Duplicate check
    if hostname in seen_hostnames:
        errors.append(f"[{hostname}] duplicate hostname")
    seen_hostnames.add(hostname)

    # 5. DNS resolution
    try:
        socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        errors.append(f"[{hostname}] DNS resolution failed: {e}")
        return errors  # No point checking HTTP if DNS fails

    # 6. Federation identity endpoint reachable
    url = f"https://{hostname}/api/v1/federation/identity"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "opencorde-registry-validator/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read())

        # 7. Public key matches
        reported_pubkey = body.get("public_key", "")
        if reported_pubkey != pubkey:
            errors.append(
                f"[{hostname}] pubkey mismatch:\n"
                f"  servers.json: {pubkey}\n"
                f"  server reports: {reported_pubkey}"
            )
        else:
            print(f"  [ok] {hostname} — pubkey verified")

    except urllib.error.URLError as e:
        errors.append(f"[{hostname}] federation endpoint unreachable: {e.reason}")
    except json.JSONDecodeError:
        errors.append(f"[{hostname}] federation endpoint returned non-JSON")

    return errors


def main():
    with open("servers.json") as f:
        servers = json.load(f)

    if not isinstance(servers, list):
        print("FAIL: servers.json must be a JSON array")
        sys.exit(1)

    print(f"Validating {len(servers)} server(s)...\n")

    all_errors = []
    seen = set()
    for entry in servers:
        errs = check_entry(entry, seen)
        all_errors.extend(errs)

    if all_errors:
        print("\nValidation FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"\nAll {len(servers)} server(s) passed validation.")


if __name__ == "__main__":
    main()
