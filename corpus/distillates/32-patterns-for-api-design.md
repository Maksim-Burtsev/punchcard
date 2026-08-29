# 32. Patterns for API Design — Zimmermann, Stocker, Lübke, Zdun, Pautasso

> A published interface is a promise made to strangers: once clients you cannot see or notify depend on it, every element is contract — regardless of documentation disclaimers — and removal or reinterpretation breaks someone. So the contract deserves a different review standard than implementation code: it is its own designed layer, not a serialization of what the backend happens to have, and every field, operation, and version added is a ratchet that only tightens. There are no universal answers on granularity, coupling, or specification depth — only trade-offs; what a reviewer can demand is that each one was made consciously, with the rejected alternative and the accepted cost named.

## Principles

### 32.1 Design the contract as its own layer; never put internals on the wire
- **Why:** Exposing what the implementation already has — entities serialized field-for-field, storage keys, pass-through query access, generic string/key-value bags, one `execute(command)` envelope — is the fastest interface to build and the most coupled: every leaked detail becomes shared knowledge that forbids the implementation from changing, and structural knowledge hidden in opaque strings or generic payloads does not disappear, it just becomes implicit coupling that no schema can validate. A decade of the generic Land Register API proved syntactically stable and "difficult to learn, understand, implement, and test."
- **Applies:** DTOs mirroring entity classes or table rows; ORM objects dumped to the wire; database primary keys, enum ordinals, or sequential ids in payloads; `map[string,string]`-style parameters, JSON-in-a-string fields, catch-all `properties` bags; stringly-typed action discriminators replacing typed operations.
- **Unless:** Following the domain model closely aids understandability — the goal is a deliberate view onto the domain, not a gratuitously different vocabulary; genuinely uninterpreted pass-through data may stay opaque; a published query language over a designed schema is valid — the sin is exposing the internal representation, not query power.
- **Source:** Ch. 1 (information hiding); Ch. 5 (Information Holder Resource); Ch. 6 (Data Element, Id Element); Ch. 10 (Terravis: generic vs. task-specific APIs)

### 32.2 Challenge every element added, because removal is near impossible
- **Why:** Adding to a contract is always easier than retracting: unknown clients may depend on anything observable, so surface only ratchets upward — and per Hyrum's law it does not matter what the docs say. Terravis shipped a version header "not to be used in business logic"; partners built on it anyway. Every exposed field is also attack surface, test matrix, and documentation forever, and data not transferred cannot be stolen.
- **Applies:** Fields added "while we're here" or "someone might want it"; whole entities returned where the use case needs three attributes; "diagnostic only" or "ignore this" fields; sensitive data included because it was cheap to serialize; embedded data with stricter protection needs than its container.
- **Unless:** Withholding data clients genuinely need forces chatty follow-up calls — parsimony must not starve the use case; client-driven field selection is the pressure valve when needs truly diverge, at its own validation and testing cost.
- **Source:** Ch. 1 (data parsimony); Ch. 6-7 (Data Element, Embedded Entity, Wish List); Ch. 10 (Terravis retrospective, Hyrum's law)

### 32.3 Scope operations on business capabilities and tasks, not entity tables
- **Why:** One CRUD surface per entity reproduces an anemic model on the wire: any authorized client mutates provider data arbitrarily, data quality becomes a distributed responsibility, one user story takes many calls, and the data layout is baked into every client. Partitioning by task and role instead of by consumer group means a change touches only the clients that actually use it.
- **Applies:** New endpoint-per-table additions; interfaces whose only verbs are create/read/update/delete; a business action (approve, cancel, quote) expressible only as client-orchestrated field updates; one god interface spanning unrelated domains because the same consumer needs both; a generic update where a named action fits.
- **Unless:** Some domains genuinely are data-shaped (archives, inventories, reference stores) — a data holder is fine as a conscious, justified choice; maximal fragmentation multiplies artifacts to version and manage.
- **Source:** Ch. 3, 5 (Processing Resource vs. Information Holder Resource); Ch. 10 (Terravis interface segregation)

### 32.4 Declare each operation's effect on state, and keep the declaration honest
- **Why:** Whether an operation reads, writes, transitions, or purely computes determines what may safely be done with it — caching, replication, retries, scaling — and an operation that lies about its side effects sabotages all of it. Explicit state machines let the provider reject stale or invalid transitions instead of silently accepting fraudulent sequences; writes routed only through the data's owning module keep consistency and audit responsibility in one place.
- **Applies:** A "get" that mutates state or advances a workflow; lifecycle operations (approve, close, restart) with no transition validation; status as free-form strings mutated from many places; module A directly writing data module B owns; write operations committing partially or leaving state inconsistent on failure.
- **Unless:** Infrastructure writes (access logs) don't count; a creation may read minimally (duplicate-key checks); transactional mechanics stay hidden from the contract even where transactional behavior is documented.
- **Source:** Ch. 5 (Operation Responsibilities; State Transition Operation); Ch. 10 (Terravis CQRS, SACAC write restrictions)

### 32.5 Design every write for a network that loses, duplicates, and reorders
- **Why:** Remote calls fail eventually, and senders retry — so "set x to y" survives a duplicate while "increase x by y" corrupts data. Where true idempotence is unreachable, unique ids and timestamps per submitted item allow de-duplication, and acknowledgments stop clients from resending forever or giving up too early.
- **Applies:** Write operations or event consumers with increment/append/toggle semantics; retry logic wrapped around non-idempotent calls; submissions lacking a unique id; client code invoking a remote dependency with no timeout or failure branch; providers assuming exactly-once, in-order delivery.
- **Unless:** Some transitions are inherently non-idempotent (each start request legitimately spawns an instance); multi-entity writes make idempotence genuinely hard — demand a conscious design, not perfection; some resilience rightly lives in infrastructure, but the contract must tolerate what infrastructure cannot hide.
- **Source:** Ch. 1 (distribution fallacies); Ch. 5 (State Creation Operation, State Transition Operation)

### 32.6 Decide granularity and embed-versus-link per relationship, by access profile and lifecycle
- **Why:** Chatty and bloated are both failure modes: many narrow calls multiply round trips and coordination state, one mega-response ships data most callers never use and snapshots it stale. Data with different lifetimes pulls the choice further — embedding long-lived master data inside short-lived operational records welds together things that evolve at different speeds and under different ownership, while copies of shared reference data diverge silently the day the source changes.
- **Applies:** Loops issuing a remote call per item; references forcing N follow-up calls on a hot path; responses transitively inlining whole object graphs; long-lived entities denormalized into transactional payloads; lookup tables and enum lists another system owns pasted into a client; hard delete added to widely referenced data (archive-state it instead).
- **Unless:** No universal winner exists — the client access profile decides, hybrids are legitimate, and sometimes only measurement settles it; caching immutable reference data is fine when it has a consistency story.
- **Source:** Ch. 1 (granularity trade-off); Ch. 5 (Operational/Master/Reference Data Holder); Ch. 7 (Embedded Entity, Linked Information Holder)

### 32.7 Bound what any single call can return or consume
- **Why:** Response size grows with data, not design intent, so an unlimited query is a latent out-of-memory incident and a free denial-of-service vector; test data is always small enough to hide it. On the inbound side, a few overusing clients ruin the service for everyone, and adding hardware is rarely the economical answer.
- **Applies:** Collection returns with no limit parameter or no maximum on the client-supplied one; implementations loading everything then slicing (the cap is cosmetic); offset paging over mutable data (rows shift across page boundaries — use cursors); expensive operations invocable without throttle; limit enforcement returning bare denial with no remaining-allowance signal.
- **Unless:** Structurally capped inputs and provably small sets need no machinery; for trusted in-house callers the guardrail may cost more than the risk; note that limit tracking makes the provider stateful.
- **Source:** Ch. 7 (Pagination); Ch. 9 (Rate Limit); Ch. 10 (Terravis retrofitted pagination)

### 32.8 Never change what an element means without changing what it looks like
- **Why:** The deadliest evolution bug is a message old clients still parse but now misinterpret — a price that silently became tax-inclusive passes every schema check and fails in production. An explicit version identifier, in exactly one place, lets recipients reject what they cannot correctly interpret; a structured scheme makes compatibility impact machine-readable and forces the author to classify the change as breaking or not.
- **Applies:** Changed units, sign conventions, included components, or interpretation of an existing field under an unchanged name and version; a mandatory new field or removed operation shipped as a minor release; version strings duplicated across URL, header, and payload; contract-affecting changes with no version signal at all.
- **Unless:** Co-owned client and provider on one release train can evolve ad hoc under shared tests; genuine bug fixes restoring the documented meaning; per-element versioning explodes governance cost.
- **Source:** Ch. 8 (Version Identifier, Semantic Versioning, Two in Production forces)

### 32.9 Cap live versions, and give every retirement a labeled start and a dated end
- **Why:** Providers rush versions out and forget decommissioning; every version kept in production is permanent maintenance, test, and support cost, while a cliff-drop breaks all clients at once. A small sliding window (two in production) plus announced deprecation dates turns surprise outages into plannable migrations and keeps a rollback path; an explicitly commitment-free preview lets users experiment without adding a supported version.
- **Applies:** A v3 added while v1 and v2 are served indefinitely; the old version removed in the same change that ships its incompatible successor; public elements deleted with no deprecation period; deprecation markers with no removal date; experimental endpoints indistinguishable from supported ones.
- **Unless:** Aggressive schedules presume the provider holds the power — clients who cannot upgrade are owed longer windows; usage data showing a feature is genuinely unused justifies swift removal; security emergencies compress timelines.
- **Source:** Ch. 8 (Two in Production, Aggressive Obsolescence, Limited Lifetime Guarantee, Experimental Preview)

### 32.10 Make errors say whose fault it was and what to do next — and nothing more
- **Why:** A caller needs to know whether to fix its request or retry later; one generic failure collapsing validation errors and provider faults makes robust clients impossible. Machine-readable codes plus human-readable text let programs branch and people debug; the code/text pair also forces the designer to actually enumerate the failure conditions. The ceiling is disclosure: details that reveal internals or account existence hand attackers half the answer.
- **Applies:** Handlers returning one generic error for bad input and internal failure alike; clients string-matching on error prose; error bodies built from exception text or stack traces; login failures distinguishing "no such user" from "wrong password"; batch endpoints reporting one status for N independent items; raw transport codes doubling as the application error channel.
- **Unless:** Protocol-level codes suffice when exactly one protocol stack is in play — but keep them consistent with the payload, not contradicting it; internal logs keep the detail the response omits.
- **Source:** Ch. 1 (DX clarity); Ch. 6 (Error Report); Ch. 10 (Terravis, SACAC retrospectives)

### 32.11 Identify every caller, and treat any widening of the audience as a fresh security decision
- **Why:** Rate limits, quotas, billing, and abuse response all presuppose knowing who is calling; a per-client revocable key also decouples API access from account administration, unlike a human's credentials reused by automation. And visibility — internal, partner, public — is a designed property carrying different security, capacity, and stability obligations: an internal interface reaching a wider audience "should not just happen" as scope creep, because decisions made under internal assumptions must be remade.
- **Applies:** New shared or public operations with anonymous callers; automation authenticating with a person's full-privilege account; keys or tokens in URLs and query strings (they leak into logs); internal endpoints exposed through a gateway or public docs; auth or network restrictions loosened on an existing service.
- **Unless:** Doing nothing is legitimate on controlled private networks and low-risk systems; a plain key is only identification — delegation and high-stakes access call for a real auth protocol; planned graduation of an internal interface is healthy when its obligations are consciously accepted.
- **Source:** Ch. 6 (API Key); Ch. 3 (API Visibility); Ch. 10 (Terravis solution-internal APIs)

### 32.12 Document the behavioral contract, and make every quality promise measurable — or decline to promise
- **Why:** Message shapes alone leave clients guessing at exactly what matters — sequencing, pre/postconditions, idempotency, error cases — and guesses harden into assumptions that later break; a description trailing the code sends them reverse-engineering the provider. Freeform quality prose ("fast", "highly available") breeds disputes: a real objective names threshold, percentage, window, and measurement method, while promises nobody asked for are pure liability.
- **Applies:** Public operations whose docs list only parameters and types; observable behavior changed without touching the spec; SLA-sounding claims with no measurable definition; retry/timeout/alert thresholds with no traceable objective behind them; significant contract choices shipped with no recorded rationale or rejected alternative.
- **Unless:** Depth scales with consumer distance and criticality — one team owning both sides can carry tacit knowledge, prototypes may skip formality; elaborate descriptions drift and can leak internals; some qualities (security) resist honest formalization.
- **Source:** Ch. 9 (API Description, Service Level Agreement); Ch. 3 (why-statement ADRs)

## Review heuristics

- For every new or widened field in a published payload, ask which consumer needs it today; "for debugging", "internal only", or "might be useful" means it is contract with no purpose — flag it.
- Grep the boundary for internals on the wire: entity/ORM types serialized directly, database keys or sequential ids in responses, string-typed bags where structure exists on both sides.
- For each mutating operation, ask what happens when the request arrives twice or out of order, and whether the caller can distinguish "fix your input" from "retry later" on failure.
- Every collection return names its cap and every shared operation its throttle; if the limit equals the size of the data, it is unbounded.
- Diff the meaning of existing fields, not just the schema: changed units, semantics, or interpretation under an unchanged name and version is a silent breaking change.
- When a new version or endpoint appears, ask which old one retires and on what date; when one disappears, ask where its deprecation window was.
- Check that read-looking operations do not write, and that no module in the diff mutates data another module owns.
- New correlation, tenant, auth, or locale handling shaped differently from sibling operations — or copy-pasted per handler instead of living in the shared layer — is scattered context; flag it.
