# WAL-Replicated KV Store

Extend the single-node WAL crash recovery in `query_engine` into a 2-node leader/follower replicated KV store.

## Architecture

```
┌──────────────┐         TCP/JSON-RPC          ┌──────────────┐
│   Leader     │ ◄──────────────────────────►   │   Follower   │
│              │    AppendEntries / Heartbeat   │              │
│  ┌────────┐  │    FetchLog / AppendAck        │  ┌────────┐  │
│  │   WAL  │  │                                │  │   WAL  │  │
│  ├────────┤  │                                │  ├────────┤  │
│  │  State │  │                                │  │  State │  │
│  │ Machine│  │                                │  │ Machine│  │
│  └────────┘  │                                │  └────────┘  │
└──────┬───────┘                                └──────────────┘
       │
  External Clients (INSERT/SELECT)
```

## File Structure

```
quiry_engine/
├── main.py              # CLI entry point
├── config.py            # Config loading (node_role, listen_addr, peer_addr)
├── wal.py               # Upgraded WAL: LSNs, fsync, read-from-position, checksums
├── state_machine.py     # Deterministic tables + indexes (extracted from engine.py)
├── rpc.py               # TCP framing: length-prefixed JSON messages
├── replication.py       # Leader/follower protocol logic
├── server.py            # Node: accepts client + peer connections
├── client.py            # External CLI client for sending queries
├── data/                # Runtime data (gitignored)
│   ├── wal/             # WAL segment files
│   ├── snapshot.json    # Periodic state snapshot
│   └── config.json      # Node configuration
└── README.md            # This file
```

## Phases

### Phase 1 — WAL Upgrade (`wal.py`)

Replace the staging-buffer WAL with a full commit log:

- Monotonic LSNs (persisted counter across restarts)
- `fsync` after each append
- Read from any LSN (for follower catch-up)
- CRC32 checksums per entry
- Segment rotation by size
- API: `append() → LSN`, `read_from(LSN) → entries[]`, `recover() → (last_lsn, entries)`

### Phase 2 — State Machine (`state_machine.py`)

Extract the table store and index management into a deterministic class:

- Class wrapping `tables` dict + `indexes`
- `apply(entry)` — single deterministic mutation path
- `snapshot()` / `restore()` for checkpointing
- `execute_query()` for SELECT reads

### Phase 3 — RPC Layer (`rpc.py`)

TCP-based RPC with JSON-framed messages:

- Framing: `{4-byte length (big-endian)}{JSON payload}`
- Message types: `AppendEntries`, `AppendAck`, `Heartbeat`, `FetchLogRequest/Response`, `WriteRequest/Response`, `ReadRequest/Response`
- Thread-per-connection model

### Phase 4 — Replication Protocol (`replication.py` + `server.py`)

**Sync mode first:**
1. Client writes to leader → leader appends WAL (fsync) → sends `AppendEntries` to follower
2. Follower appends to WAL (fsync) → applies to state machine → acks
3. Leader commits, responds to client
4. Linearizable writes; writes fail if follower is down

**Then add Async mode:**
- Config flag: `replication_mode = "sync" | "async"`
- Async: leader acks client immediately after local WAL write, replicates in background

**Follower catch-up:**
- On connect, follower sends `FetchLogRequest(from_lsn=F+1)` to leader
- Leader reads WAL from LSN F+1, streams entries back
- Follower replays, then enters normal mode

### Phase 5 — Recovery

- Both nodes replay WAL on startup → rebuild state machine
- Follower then reaches out to leader for catch-up
- Leader failure: admin updates config, promotes follower (manual)
- WAL + snapshot for efficient restart (skip already-snapshotted entries)

### Phase 6 — Split-Brain & Edge Cases

With 2 nodes and manual config, split-brain is unavoidable during a partition:

- Both nodes accept writes if both think they're leader
- **Mitigations:** startup sanity check (follower pings leader before allowing writes), LSN conflict detection on reconnect, manual reconciliation tool
- **Document explicitly:** known limitation, tradeoff vs. 3-node Raft, how production systems handle it (lease-based with fencing, or external sequencer)

## Key Concepts

| Concept | Where it appears |
|---|---|
| WAL as source of truth | Full commit log, not staging buffer |
| Replication lag | Follower trails leader by N entries; stale reads in async mode |
| Follower catch-up | `FetchLog` from LSN; segment-based log transfer |
| Durability vs. availability | Sync vs. async tradeoff |
| Split-brain | 2-node limitation; fencing tokens; lease expiration |
| State machine determinism | `apply()` must produce same state on both nodes |
| Crash recovery | WAL replay + snapshot on both nodes |

## Dependencies

Zero external deps. Python 3.14 stdlib: `socket`, `threading`, `json`, `os`, `struct`, `zlib`, `argparse`.
