# DNS Server — Architecture

Scope: [CodeCrafters "Build your own DNS server"](https://app.codecrafters.io) challenge — UDP-only forwarding resolver. This is deliberately smaller than a full authoritative server; see Section 7 for what's left out and why.

---

## 1. Scope

**What this is:** a UDP server that parses incoming DNS query packets, builds DNS response packets by hand (no `dnspython`, no `socket.getaddrinfo` shortcuts), and forwards unresolved queries to a real upstream resolver (e.g. `8.8.8.8:53`).

**What this deliberately is NOT** — matches CodeCrafters' stage list, not the bigger "authoritative server + zone file" version of this project:

- No zone file parsing, no authoritative answers for your own domains
- No TCP support (UDP only, until responses exceed 512 bytes)
- No recursive resolution (root → TLD → authoritative) — forwarding to one upstream only
- No DNSSEC, EDNS0, caching, or record types beyond what's needed to get an A record round-tripping

These map onto stretch goals if you extend this later (Section 7).

---

## 2. Pipeline

```
Client                  Your DNS server                          Upstream
  │
  │  query bytes   ┌────────────┐    ┌────────────────────┐    ┌──────────────┐
  ├───────────────→│  Decoder    │───→│  Handler/resolver   │───→│  Upstream DNS │
  │                │ header + Q  │    │  answer locally OR  │    │  e.g. 8.8.8.8 │
  │                └────────────┘    │  forward            │    └──────────────┘
  │                                   └──────────┬──────────┘
  │                                              │ parsed response
  │  response bytes                  ┌───────────▼──────────┐
  ←───────────────────────────────────│       Encoder         │
                                       │ header + Q + answer  │
                                       └───────────────────────┘
```

Three internal stages plus one external dependency. The Decoder and Encoder are mirror images of each other (same byte layout, opposite direction) — build the Encoder first, since CodeCrafters stages force that order anyway, and it gives you known-good bytes to test the Decoder against later.

---

## 3. Module layout

```
dns_server/
├── main.py            UDP socket loop — recvfrom/sendto, dispatch to handler
├── message.py         DNSMessage — container: header + questions[] + answers[]
├── header.py          DNSHeader — 12-byte header, to_bytes() / from_bytes()
├── question.py        DNSQuestion — name + qtype + qclass, to_bytes() / from_bytes()
├── record.py          DNSResourceRecord — name + type + class + ttl + rdlength + rdata
├── name_codec.py       shared label encoding + compression pointer resolution
└── forwarder.py        opens a 2nd UDP socket to upstream, relays query/response
```

**What each file owns:**

- **main.py** — the only socket bound to your listening port. Receives raw bytes, hands them to the decoder, hands the decoded message to the handler, encodes whatever comes back, sends it. No protocol logic lives here.
- **header.py / question.py / record.py** — pure data + encode/decode, no I/O. Each should be testable without ever opening a socket: build the object, call `.to_bytes()`, feed those bytes into `.from_bytes()`, assert the fields match.
- **name_codec.py** — the one piece of logic both `question.py` and `record.py` need (names appear in both sections), and the only place compression-pointer-following lives. Don't duplicate this logic into the other two files — if a name bug shows up, you want exactly one place to fix it.
- **forwarder.py** — the only file that knows a second DNS server exists. Takes a parsed question, builds a fresh query, sends it upstream, parses the response, hands back a `DNSMessage`. It doesn't need to know it's specifically "stage 8" — it produces the same shape `main.py` already knows how to encode and send.

---

## 4. Data model

**DNSHeader** — 12 bytes, all fields big-endian:

| Field | Size | Meaning |
|---|---|---|
| ID | 16 bits | random per query; response must echo it back (this is your spoofing defense) |
| QR | 1 bit | 0 = query, 1 = response |
| OPCODE | 4 bits | 0 = standard query |
| AA | 1 bit | authoritative answer (always 0 here — you're a forwarder, not an authority) |
| TC | 1 bit | truncated, retry over TCP |
| RD | 1 bit | recursion desired |
| RA | 1 bit | recursion available |
| Z | 3 bits | reserved, always 0 |
| RCODE | 4 bits | 0 = OK, 2 = SERVFAIL, 3 = NXDOMAIN |
| QDCOUNT | 16 bits | number of questions |
| ANCOUNT | 16 bits | number of answers |
| NSCOUNT | 16 bits | number of authority records (0 for you) |
| ARCOUNT | 16 bits | number of additional records (0 for you) |

**DNSQuestion** — name (length-prefixed labels, root-terminated), QTYPE (2 bytes), QCLASS (2 bytes).

**DNSResourceRecord** — name, TYPE (2 bytes), CLASS (2 bytes), TTL (4 bytes), RDLENGTH (2 bytes), RDATA (variable — 4 raw bytes for an A record).

**DNSMessage** — `header` + `questions: list[DNSQuestion]` + `answers: list[DNSResourceRecord]`. This is the object that flows through Decoder → Handler → Encoder unchanged in shape — build it once, don't reinvent it per stage.

---

## 5. Build order (maps 1:1 to CodeCrafters stages)

| # | Stage | Files touched | Done when |
|---|---|---|---|
| 1 | Setup UDP server | `main.py` | socket bound, `dig` gets *any* reply (even garbage) without timing out |
| 2 | Write header section | `header.py` | `Header().to_bytes()` is exactly 12 bytes, flags byte correctly packed |
| 3 | Write question section | `question.py`, `name_codec.py` | a hardcoded question encodes to the expected byte sequence |
| 4 | Write answer section | `record.py` | a hardcoded A record encodes correctly; `dig` shows an answer for any query |
| 5 | Parse header section | `header.py` | `from_bytes()` round-trips: encode → decode → same fields |
| 6 | Parse question section | `question.py` | can read a real query's question section back out correctly |
| 7 | Parse compressed packet | `name_codec.py` | a name appearing twice in one message decodes correctly both times, including pointer-to-pointer chains |
| 8 | Forwarding server | `forwarder.py` | querying your server for a real domain (not hardcoded) returns the real IP, sourced from upstream |

---

## 6. Testing

```bash
# basic round trip (any stage once the header/question encode)
dig @127.0.0.1 -p 5353 example.com

# forwarding stage — should match a real lookup
dig @127.0.0.1 -p 5353 codecrafters.io
dig @8.8.8.8 codecrafters.io          # compare against this
```

Use `tcpdump`/Wireshark on `lo` to diff your encoded bytes against what a real upstream sends — fastest way to catch a wrong byte offset before it becomes a multi-hour mystery bug.

---

## 7. Stretch goals (after CodeCrafters, not part of it)

- **Recursive resolution** — hardcode root server IPs, walk root → TLD → authoritative yourself instead of forwarding to a single upstream
- **TCP fallback** — when responses exceed 512 bytes (length-prefix framing, same as a normal TCP server)
- **More record types** — AAAA, CNAME, NS, MX, TXT
- **Real caching** — TTL-respecting eviction, shared across queries
