# 28. Release It! Design and Deploy Production-Ready Software — Michael T. Nygard

> Software does not fail in the way its specification describes; it fails at the seams, where one system waits on another that has stopped answering. Every integration point is a place where someone else's problem becomes yours, and the caller's behaviour on failure — not the callee's bug — is what decides whether a local fault stays local or takes down the site. So a review question is rarely "is this correct?" but "what does this do at 3 a.m. when the thing it calls hangs, floods, or lies?" Passing the functional test proves nothing about surviving a year in production under real load, real volumes, and real operators. And the arithmetic is not neutral: a system spends far more of its life being run than being built, so design and architecture choices are spending choices, and the one that saves a week of development by adding a recurring operational expense is usually the expensive one.

## Principles

### 28.1 Bound every wait that crosses a process, host, or pool boundary
- **Why:** A call with no time limit converts a slow neighbour into an exhausted thread pool, then into a dead tier while CPU sits idle. In the 5 a.m. firewall case the threads sat in a low-level socket read inside the database driver, on a connection the firewall had silently discarded. In the airline outage the block was one layer up: every thread on every application server waiting to check out a connection from a pool that a leak had drained — while the unbounded remote call with no timeout was what froze the kiosk and voice-response systems calling in.
- **Applies:** Sockets, HTTP, RPC, message request/reply, database calls, connection- and thread-pool checkouts, lock and queue waits — especially inside vendor client libraries where the socket is hidden and the timeout silently absent.
- **Unless:** A timeout is only real if the caller's handling of it is real; a rethrow into the void or an immediate retry into the same broken thing buys nothing and may amplify the load. Bounds set arbitrarily are their own defect — a pool too small produces contention that looks exactly like a slow dependency.
- **Source:** Stability Antipatterns — Integration Points, Blocked Threads; Stability Patterns — Use Timeouts; 9.1 Resource Pool Contention

### 28.2 Ask what the caller does while the new dependency hangs, and reject silence as the answer
- **Why:** Cracks jump between layers only where the caller behaves badly on failure. The read-through cache in the book was functionally textbook-correct and still took the whole site down when the inventory system stopped answering.
- **Applies:** Any change that adds a synchronous call across a system, service, or team boundary, including a cache or registry sitting in front of one.
- **Unless:** Nobody can enumerate every failure permutation, and exhaustive what-if analysis is impractical outside life-critical systems. Ask for one defined degraded behaviour, not a proof of coverage.
- **Source:** Introducing Stability — Cracks Propagate; Stability Antipatterns — Blocked Threads

### 28.3 Guard a failure-prone dependency with a circuit breaker, and prefer a fast refusal to a slow answer
- **Why:** A sick dependency gets sicker under continued load while callers stack up threads learning what they already know. Refusing immediately preserves capacity, lets the caller finish its transaction, and gives operators a leading indicator when trips are logged. Checking that required resources exist before starting expensive work saves the same capacity at the other end.
- **Applies:** Outbound calls across a process, host, or vendor boundary in request-handling paths; admission control when a queue is already past capacity; validation at the front of long transactions.
- **Unless:** The fallback is a product decision, not a technical one — a breaker that quietly degrades business-critical behaviour needs an owner's agreement. Trip thresholds tuned to ordinary latency jitter manufacture outages. And distinguish a resource failure from a bad-input failure: a user typo should not open somebody's circuit.
- **Source:** 5.2 Circuit Breaker; 5.5 Fail Fast; Stability Antipatterns — Slow Responses

### 28.4 Partition shared capacity so one consumer cannot drain what the rest of the system needs
- **Why:** Shared pools create invisible coupling — a defect or spike in one consumer silently degrades unrelated ones and makes their symptoms undiagnosable. A reserved slice keeps partial function alive and keeps a diagnostic or shutdown route open when everything else is saturated.
- **Applies:** New consumers of an existing shared thread pool, connection pool, queue, or service tier; and any service several independent clients depend on.
- **Unless:** Partitioning trades utilization for containment — every partition needs its own headroom, and slicing too finely strands capacity so nothing can absorb a burst. Consumers that are neither independent nor differently critical do not need separating.
- **Source:** 5.3 Bulkheads

### 28.5 Ship the purge with whatever the change accumulates
- **Why:** Any accumulator without a drain eventually overflows, and the fallback is a human logging into production to clean up — itself a leading source of outages. This is invisible in testing because no QA instance runs long enough under load, and it is the first work deferred past release because it demos badly.
- **Applies:** New tables, log and audit output, caches and in-memory maps, session state, temp files, message and event rows — anything whose growth is driven by traffic rather than by an operator.
- **Unless:** Retention mandated by law or by users is not sludge; move it off the production path rather than deleting it. Purge logic that ignores referential integrity or application invariants is worse than none, which is why it usually belongs in application code and not a DBA script.
- **Source:** 5.4 Steady State; Introducing Stability — Extending Your Life Span

### 28.6 Make the caller impose the limit on how much data comes back
- **Why:** Without a limit the other side dictates terms — a table expected to hold a thousand rows held ten million and crashed a hundred-instance farm in sequence. The sensible cardinalities are zero, one, and many; anything not provably one row can grow without warning, and test data is always small enough to hide it.
- **Applies:** SQL and ORM queries, association traversals, service and RPC responses returning collections, and any loop materializing rows into objects.
- **Unless:** Breaking out of the loop after N rows protects only the application and still wastes the database's work — the limit belongs in the request. And bounding forces a decision about the remainder: silently dropping rows where completeness matters is worse than the original bug, so paginate or stream.
- **Source:** Stability Antipatterns — Unbounded Result Sets

### 28.7 Compare what the caller can generate against what the callee can absorb, at production ratios
- **Why:** Front ends outnumber back ends ten to one, so thousands of request threads point at a service sized for dozens; a marketing push or a new code path floods it. Development and QA hide this entirely because there everything looks like one or two boxes. The same many-to-one shape makes a shared lock manager, coordinator, or hot row the thing that serializes an entire tier.
- **Applies:** Changes adding a call from a large tier to a smaller one, changing the frequency or mix of an existing call, raising pool sizes on the calling side, or introducing cluster coordination and cross-instance chatter.
- **Unless:** Symmetric capacity is a waste of capital — sizing a back end for a five-year peak is explicitly rejected; the answer is throttling, back-pressure, and reserved partitions. That is an argument for a cheaper mechanism, not for skipping the problem; weigh it against 28.11. Shared-nothing is not always available either, and point-to-point messaging is fine at two or three nodes.
- **Source:** Stability Antipatterns — Unbalanced Capacities, Scaling Effects; Stability Patterns — Handshaking

### 28.8 Demand evidence from hostile dependencies and production-shaped topology, not stubs on one box
- **Why:** Integration failures do not arrive as tidy errors inside the protocol; they arrive as hangs, half-closed sockets, dribbled bytes, and garbage where structure was promised — and a mock constrained to an interface can only produce interface-shaped failures. Likewise, most surprises come from the shape of the deployment: two components colocated in test share a directory and hide a dependency, and a single instance hides everything that only appears with peers.
- **Applies:** Test evidence for changes at any external boundary, and for anything sensitive to instance count — clustering, session handling, caching, failover, load balancers, firewalls.
- **Unless:** You cannot prove the negative — a clean harness run is not a clean bill of health, and this verifies survivability, not correctness. A full simulator for a trivial internal call is over-investment, and a one-for-one production replica is rarely affordable: one instance versus several is the distinction that matters. But "we cannot afford it" is a claim about a number, and the book puts the number the other way for network gear — the downtime caused by a firewall or load balancer that exists only in production costs more than buying a smaller model of the same device for QA. Never ship failure simulation inside the production application.
- **Source:** 5.7 Test Harness; 14.1 Does QA Match Production?, Just Buy the Gear; You Play the Way You Practice sidebar

### 28.9 Publish enough internal state that an operator can tell busy from stuck
- **Why:** A process is opaque by default, and what is not deliberately exposed cannot be diagnosed during an incident; retrofitting visibility costs far more than building it in. During the airline outage the health check stayed green because it hit a status page served by an idle pool while every business thread was blocked — health must be an actual transaction observed from outside.
- **Applies:** New components, integration points, background jobs, caches and pools; health and readiness checks; and the logging that accompanies them.
- **Unless:** Metrics with no defined normal range are noise, and collection that perturbs the hot path is a regression rather than transparency. Reserve error severity for conditions needing operator action, carry a correlation id, keep debug output and secrets out of production logs — and do not rely on logging alone, since under memory pressure the framework may record nothing. Alert thresholds and vendor agents belong outside the application.
- **Source:** Chapter 17 Transparency; 17.4 Logging; Stability Antipatterns — Blocked Threads

### 28.10 Let each side of an interface deploy alone, and each instance start, stop, and be tuned without a human at a screen
- **Why:** A change both endpoints must adopt at the same instant couples their release calendars and forces downtime with no rollback. Expanding the schema first, naming new versions of assets and endpoints, and cleaning up after the old version is gone lets two versions coexist. Operators, meanwhile, work across many instances under time pressure: a UI-only procedure gets skipped in favour of a kill signal, and a knob that only takes effect at boot is not an operational control.
- **Applies:** Migrations, wire protocols, file formats, asset URLs, peer discovery; plus bootstrap order, listener binding, drain-on-shutdown, feature toggles, pool sizes, and configuration layout.
- **Unless:** The compatibility window is debt — bridging triggers and dual code paths rot if cleanup is never scheduled, and a strictly internal interface with one co-deployed caller needs no ceremony. Do not turn every start-up hiccup into a hard exit or let drain run unbounded, do not expose dangerous mutations broadly just because they are scriptable, and do not push genuinely internal wiring into operator-facing config — that is just more ways to break the system.
- **Source:** 18.4 Releases Shouldn't Hurt; 18.3 Adaptable Enterprise Architecture; 14.2 Configuration Files; 14.3 Start-up and Shutdown; 14.4 Administrative Interfaces

### 28.11 Price a change across the system's operating life, not against the project's budget
- **Why:** Between forty and ninety percent of what a system costs to develop is spent after the first release, and downtime bills at the same rate whether or not it was planned — at ten thousand dollars an hour, a four-hour maintenance window is forty thousand dollars that no budget line records. Nygard's worked example: five thousand dollars of build-and-release automation avoids two hundred thousand dollars of release downtime, and the yearly gap between 98% and 99.99% availability exceeds seventeen million. Buying a one-time saving with a recurring operational expense is rational only for a team measured on a fixed date and a fixed budget, and irrational for whoever pays to run the thing. Stability, transparency, and deployment work is cheap to do during development and expensive to keep not doing.
- **Applies:** Any review argument that a timeout strategy, a purge job, instrumentation, a production-shaped test environment, or a zero-downtime release path is not worth the effort; and any estimate that counts build cost while leaving operations, incidents, and release windows out of the comparison.
- **Unless:** The test is net return over the system's life, not maximum spend — a change should release more money than it consumes, so gold-plating that no operator or customer ever benefits from fails the same test. Where the recurring cost is genuinely small, the cheap mechanism wins; the point is to run the arithmetic rather than to assume either side of it.
- **Source:** 1.5 Pragmatic Architecture (technical and financial viewpoints fused); 14.1 Just Buy the Gear; Chapter 15 Design Summary; 18.1 Adaptable Software; 18.4 Deployments Cost Too Much, Zero Downtime Deployments

## Review heuristics

- Find every call in the diff that leaves the process and check it names a timeout — including pool checkouts and calls made through a vendor library where the socket is invisible.
- For each query or response returning a collection, ask where the row limit is; if the answer is the size of the data, it is unbounded.
- For anything the change writes that is never deleted — rows, log files, cache entries, session objects — ask which shipped mechanism removes it and when.
- Trace the new dependency's failure path: what the user sees, what the thread does, and whether the failure is distinguishable from a bad input.
- Check whether the change shares a pool, cache, lock, or single row with consumers it has nothing to do with, and what happens to them when it misbehaves.
- Ask what an operator on the pager can see about this component from outside the process, and whether the health signal would go red if the work path were blocked.
- For interface or schema changes, ask whether old and new code can run at the same time during rollout, and whether rollback needs a second deploy.
- When something is deferred as too costly, ask what it costs to keep not having it — incident hours, manual release steps, a maintenance window — and compare that recurring figure to the one-time build, not to zero.
