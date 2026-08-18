# 27. Designing Data-Intensive Applications — Martin Kleppmann, Chris Riccomini

> Every serious system is a pile of copies of the same facts, and the interesting bugs live in the gaps between them. Data does not get corrupted by dramatic failures; it drifts, silently, because two writers raced, a replica lagged, a clock lied, or a retry landed twice — and nothing raised an error. A reviewer working from this book keeps asking which store is authoritative, what happens when a call neither succeeds nor fails, and whether the change can be undone once it is wrong. Correctness under concurrency and partial failure is a property of the design, not of careful coding.

## Principles

### 27.1 Name the system of record and make every other copy a rerunnable function of it
- **Why:** Caches, indexes, materialized views, denormalized columns and search stores are derived data; if the diff does not say which store wins on disagreement and how the copy is refreshed, the copies drift and nobody can tell which value is true. Two independent writes to two stores have no agreed order and can land reversed permanently.
- **Applies:** Any change adding a cache, index, precomputed view, duplicated column, second store, or a write to a search/analytics system alongside the primary write. Also any projection or consumer: derivation must be deterministic — no live external lookups, no wall-clock reads, no outbound side effects — or it cannot be rebuilt.
- **Unless:** Both writes inside one database transaction (outbox) are fine, and a copy trivially recomputed on read with harmless bounded staleness needs no pipeline. Derivation is asynchronous, so read-your-own-write paths still need a synchronous route.
- **Source:** Ch. 1 Systems of Record and Derived Data; Ch. 12 Keeping Systems in Sync; Ch. 13 Reasoning about dataflows

### 27.2 Make every read path state the freshness it needs, and route it accordingly
- **Why:** Asynchronous replication produces three distinct user-visible defects — not seeing your own write, data moving backwards between refreshes, and effects appearing before their causes — each with a different remedy. Leaving the requirement unstated means picking none of them.
- **Applies:** New reads against replicas or caches, read-only endpoints, and any write-then-read-back sequence.
- **Unless:** Do not route everything to the leader; stale reads are the point of having replicas, and over-routing destroys the read scaling you paid for.
- **Source:** Ch. 6 Problems with Replication Lag

### 27.3 Reject application-side read-modify-write on shared rows, and treat check-then-write across rows as write skew
- **Why:** Two concurrent cycles read the same starting value and the later write silently discards the earlier one — no error anywhere. Two transactions can each read a premise that holds and then write different rows, together breaking an invariant neither violated alone; snapshot isolation does not catch it, so it survives review and tests and appears only under load.
- **Applies:** SELECT-compute-UPDATE on counters, balances, JSON patches, whole-record form saves (ORM code makes this the default shape); and any "is the username free / is anyone still on call / does this booking overlap" query followed by a write.
- **Unless:** Use the engine's atomic operation, conditional/compare-and-set write, version column, or a plain uniqueness constraint before hand-rolling locks. Private per-request rows and trivial consequences (duplicated work, not lost data) do not need it.
- **Source:** Ch. 8 Preventing Lost Updates; Write Skew and Phantoms

### 27.4 Never order events across machines by wall-clock time, and treat last-write-wins as an accepted data-loss policy
- **Why:** Clocks drift, jump backwards, and are skewed by more than the network delay between the nodes, so a causally later write can carry an earlier timestamp. Which of two concurrent writes has the greater timestamp is arbitrary, so LWW silently discards a write that was acknowledged to its author.
- **Applies:** Multi-writer paths, offline sync, multi-region writes, conflict resolution, and any comparison of timestamps or independently generated IDs (UUIDs, sharded sequences, Snowflake-style) to infer happened-before — including in pagination, MVCC visibility, and permission checks.
- **Unless:** Monotonic clocks are correct for local durations; single-node autoincrement is fine while it stays single-node; systems that wait out a measured uncertainty interval are using time properly. LWW is acceptable for insert-once keys and disposable cache entries.
- **Source:** Ch. 9 Unreliable Clocks; Ch. 6 Last write wins; Ch. 10 ID Generators and Logical Clocks

### 27.5 Give every remote call three outcomes — success, failure, unknown — and carry one idempotency key end to end
- **Why:** A timeout cannot distinguish a lost request from a crashed peer from a lost reply, so the caller does not know whether the work happened; blind retries duplicate it. Deduplication in a lower layer only covers that layer — TCP within a connection, a transaction within its scope — and a user hitting submit again defeats all of them. Only an identifier known at both endpoints, enforced unique where the write lands, suppresses the duplicate.
- **Applies:** New service clients, RPC and cross-service writes, message consumers, webhook receivers, retried jobs, payments and order placement.
- **Unless:** Naturally idempotent operations need no key. Handling a fault is not the same as tolerating it — an honest error to the user is often the right answer, and needs no retry machinery. Effects that leave the system (email, external charge) need their own key at the far end.
- **Source:** Ch. 9 Unreliable Networks; Ch. 13 The End-to-End Argument for Databases; Ch. 8 Exactly-Once Message Processing

### 27.6 Route hard invariants through one sequential decision point, and never hand-roll the agreement protocol
- **Why:** Uniqueness, mutual exclusion, non-negative balances and last-seat booking all reduce to deciding a single winner, which is consensus. Two writers each seeing a valid state can produce an invalid combination, and asynchronous convergence discovers it only after both writes commit. Homegrown failover loses committed writes or splits the brain in exactly the fault combinations nobody tested.
- **Applies:** Username/email registration, inventory decrement, seat booking, leader election, distributed locks, shard assignment, bespoke quorum voting.
- **Unless:** Constraints the business can settle afterwards with compensation do not need coordination — and coordination is expensive: a majority, per-operation latency, and a blocked minority during a partition. Local single-shard constraints and commutative data (counters, add-only sets) are fine as they are.
- **Source:** Ch. 10 Relying on Linearizability; Consensus; Ch. 13 Enforcing Constraints

### 27.7 Do not let a lock check protect the work that follows it — fence at the resource
- **Why:** A process can be paused arbitrarily long between checking its lease and acting on it (GC, VM suspension, page fault, scheduling), and its request can sit in the network past expiry. The former holder then writes as if still in charge, and only the storage side can refuse it, via a monotonically increasing token or a conditional write on a version.
- **Applies:** Leader election, distributed locks and leases, single-writer file or object access, any code whose correctness rests on "only one node is doing this now".
- **Unless:** Where duplicate execution only wastes compute, a plain lease suffices. If writes already go to one store with conditional writes, that store can carry the lease and a separate lock service adds nothing.
- **Source:** Ch. 9 Fencing off zombies and delayed requests; Ch. 10 Coordination Services

### 27.8 Assume old and new code run simultaneously, in both directions
- **Why:** Deployments roll node by node, so a format only the new code can parse breaks nodes not yet updated, and records written before the change must still be read after it. The subtle version: a consumer that decodes to its own model and re-encodes silently deletes fields it did not understand, losing data in a path that looks like a harmless pass-through.
- **Applies:** Any change to a wire message, event, API payload, or persisted record shared across processes or time; read-modify-write over a shared schema; republishing consumers, proxies, backfills. Schemaless stores are schema-on-read — adding a field ships an obligation onto every reader of older documents.
- **Unless:** Not worth the ceremony for data produced and consumed inside one deployment unit. Deliberate projection or redaction is not accidental field loss. Once a version genuinely has no traffic, delete it.
- **Source:** Ch. 5 Encoding and Evolution; Ch. 3 Schema flexibility in the document model

### 27.9 Choose the model, engine and layout from the access pattern the code actually has — and distrust benchmarks on fresh data
- **Why:** Each model makes one pattern cheap and another awkward: trees of one-to-many fit documents, variable-depth traversals turn into thirty unmaintainable lines outside a graph or recursive model. Analytical access touches few attributes across enormous numbers of rows, which is why it wants columns, a separate copy, and its own resources — bolting scans onto the operational store lands the interference on user-facing latency. And the costs that decide storage engines (write amplification, compaction, fragmentation) only appear once the dataset has grown.
- **Applies:** New entities or stores, queries whose join count is unknown in advance, reporting endpoints and dashboards pointed at production tables, new indexes (each must name the query it serves and pay for itself on every write), and any performance claim backed by a benchmark.
- **Unless:** Do not add a second database for one awkward query — models converge and every extra component brings its own failure modes. At small volumes a read replica is the whole answer. An index that removes a hot full scan needs no defence.
- **Source:** Ch. 3 When to Use Which Model; Data Storage for Analytics; Ch. 4 Comparing B-Trees and LSM-Trees

### 27.10 Separate "temporarily stale" from "permanently wrong", and buy coordination only for the second
- **Why:** Staleness resolves itself by waiting; corruption does not, and needs detection and repair. Conflating them makes teams pay the availability cost of synchronous cross-shard coordination for cases where a delayed but eventually correct answer was always fine.
- **Applies:** Any change adding or removing distributed transactions, linearizable reads, or synchronous cross-service checks. Watch also for two channels between the same pair of components — a queue signalling data written elsewhere — where the fast path outruns the slow one.
- **Unless:** Constraints that must hold before an irreversible action genuinely need coordination up front, and a business with no apology or compensation process cannot rely on fixing violations afterwards.
- **Source:** Ch. 13 Timeliness and Integrity; Ch. 10 Cross-channel timing dependencies

### 27.11 Prefer the version of the change you can undo: append over overwrite, parallel derivation over in-place migration
- **Why:** Irreversibility is what makes systems hard to change. Serializable transactions do not protect against code that writes wrong values; the bad write commits and looks correct. An append-only history keeps the evidence and permits corrections, and building the new representation alongside the old — both derived from the same source — makes every cutover step reversible. And the claim that a derived store still matches its source stays unverified until something periodically re-derives and compares.
- **Applies:** Destructive updates and deletes in the system of record, schema and format migrations, backfills, replacing a serving path, and indexes/caches/replicas whose correctness the system merely assumes.
- **Unless:** Running both paths forever is its own tax — deleting the old one after the new is proven is the simplification. High-churn history can dominate storage, and verification should be sized to the value of the data.
- **Source:** Ch. 12 State, Streams, and Immutability; Ch. 13 Reprocessing data for application evolution; Trust, but Verify

### 27.12 Treat stored personal data as hazardous inventory, and make erasure reach the derived copies
- **Why:** Data never collected cannot leak, be stolen, be sold in a bankruptcy, or be demanded by a government. Immutability and derivation collide head-on with a right to deletion: a delete that stops at the system of record leaves the person alive in indexes, caches, warehouses, logs and models, and retrofitting the fix costs far more than keeping the fields out or encrypting them under a per-user key that can be destroyed.
- **Applies:** New personal fields, behavioural event logging, retention windows removed or lengthened, pipelines copying user data into analytics or training sets, and any new consumer of an existing personal dataset — reuse for a new purpose is a design change, not free.
- **Unless:** Data a requested feature genuinely needs, or that is retained for a stated lawful purpose, is not the target; legal holds and accounting records override erasure. The test is whether the value exceeds the total cost, not whether collection is possible.
- **Source:** Ch. 1 Data Systems, Law, and Society; Ch. 14 Privacy and Tracking; Data as Assets and Power

## Review heuristics

- For each new store, cache, index or view in the diff: which one is authoritative, and what rebuilds the others? If application code writes the same fact to two systems, that is the finding.
- Grep the diff for SELECT-then-UPDATE and for "check availability, then insert". Ask what happens when two requests run it at the same instant, and whether a constraint or atomic operation could replace it.
- Every new cross-service or cross-region call: what does the code do when there is no response at all, and is a second attempt safe? Look for a request ID that came from the client, not one generated at the boundary.
- Any comparison of timestamps, UUIDs, or IDs from different machines to decide order or a winner — including `created_at` sorting and last-write-wins upserts.
- Any lock or lease: does the protected resource itself reject a stale holder, or does correctness rest on the holder never being paused?
- Any change to a stored or transmitted shape: can the previous version of the code still read it, can the new code still read old records, and does read-modify-write preserve unknown fields?
- Any new personal field, log line, or dataset consumer: what deletes it, and does that deletion reach the derived copies?
