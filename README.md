# OpenCorde Server Registry

Public list of OpenCorde servers. Every OpenCorde instance syncs this list on startup and every 24 hours — your server becomes automatically discoverable to the entire network the moment your PR is merged.

## How servers find each other

1. Your server fetches this file on startup
2. For each new entry, it sends a cryptographic handshake (`POST /api/v1/federation/introduce`) signed with its Ed25519 private key
3. The receiving server verifies the signature and stores the peer
4. Messages in federated channels flow between peered servers, signed and verified end-to-end

## Add your server

1. Fork this repository
2. Add your server to `servers.json`:

```json
{
  "hostname": "chat.yourserver.com",
  "pubkey": "<your 64-char Ed25519 public key>",
  "name": "Your Community Name",
  "description": "Optional short description",
  "region": "EU",
  "language": "en",
  "open_registration": true,
  "added": "2026-03-26"
}
```

3. Get your public key by running:
```
curl https://chat.yourserver.com/api/v1/federation/identity
```
Copy the `public_key` field.

4. Open a pull request — CI will automatically:
   - Verify your server is reachable
   - Verify the public key matches what your server reports
   - Check for duplicate hostnames

5. Once merged, every OpenCorde server in the world will discover yours within 24 hours.

## Fields

| Field | Required | Description |
|---|---|---|
| `hostname` | yes | Your server's domain (no `https://`, no trailing slash) |
| `pubkey` | yes | Ed25519 public key, 64-char hex — from `/api/v1/federation/identity` |
| `name` | yes | Human-readable server name |
| `description` | no | Short description shown in discovery |
| `region` | yes | Two-letter region code: `EU`, `NA`, `AS`, `OC`, `SA`, `AF` |
| `language` | no | Primary language (ISO 639-1), e.g. `en`, `da`, `de` |
| `open_registration` | no | Whether new users can register (default: `true`) |
| `added` | yes | Date added, `YYYY-MM-DD` |

## Removal

Open a PR removing your entry, or open an issue if you no longer control the server.

## Requirements

- Your server must be running OpenCorde v0.1.0 or later
- `https://{hostname}/api/v1/federation/identity` must be publicly reachable
- The `pubkey` in this file must match what your server reports at that endpoint
