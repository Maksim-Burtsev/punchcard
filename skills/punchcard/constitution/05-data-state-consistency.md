# 5. Data, State and Consistency

This chapter answers the questions a reviewer asks about anything the change stores, copies, or
shares: which store is authoritative, which component is allowed to write it, what makes the second
concurrent request fail, and whether the new stored or transmitted shape survives old and new code
running at the same time. State that left the system's control and re-enters the process — a hidden
field, a cookie or token payload, a cached blob, a configuration value — is not covered here: see
7.2, which owns both revalidating it at the boundary and the read-modify-write-through-a-partial-model
defect.

### 5.1 Give every fact one authoritative home and make every other copy openly derived
**Finding:** The diff writes the same fact to a second place — a cache, a denormalized column, a
search or analytics store, a duplicated field on another entity, a second service's table — without
naming which side wins on disagreement, how the copy is refreshed, and how stale it may be. Two
independent writes to two stores in one code path are a finding on sight: they have no agreed order
and can land reversed permanently. A derivation that reads the wall clock, calls an external
service, or emits side effects is a further finding, because it can never be replayed to rebuild the
copy. Ask what re-derives the copy and what would ever detect that it no longer matches its source.
**Unless:** Both writes commit inside one transaction against one store (the outbox shape) is fine.
So is a value recomputed on read whose staleness is bounded and harmless, and an index that removes
a hot scan. Deliberate projection — a copy that intentionally carries less — is not drift, provided
the diff says so. A read-your-own-write path still needs a synchronous route even when the general
copy is asynchronous.
**Sources:** (02, 04, 05, 16, 20, 21, 27; F3)

### 5.2 Let exactly one component write a store, and route every other access through its interface
**Finding:** The change writes rows, sends migrations, or maps ORM entities against a schema its
component does not own — and equally, reads them: a cross-schema join, a synonym, a report query,
or a batch job against a foreign table. Once a second component reads a schema directly, that schema
has become an undocumented published contract and its owner can no longer change storage. The same
finding fires when process state — retry attempts, step reached, compensation pending, lock or lease
records — is written into a business entity's row instead of getting its own named owner and
storage; one field serving both business meaning and workflow bookkeeping is the defect.
**Unless:** Inside one bounded context and one deployment unit, joins and foreign keys are correct
and this does not apply. A single owning writer plus read-only replicas or caches is the normal
middle path, not a violation. Common-ownership tables (audit trails, event logs) are legitimate with
one dedicated owner fed asynchronously, as is an explicitly agreed shared data domain. Synonyms and
dual access are acceptable as migration scaffolding when the diff names who removes them and when.
**Sources:** (15, 16, 20, 21, 30; F9, F10)

### 5.3 Make the store refuse the second concurrent writer, and never let a clock decide
**Finding:** The diff reads a row (or checks whether something exists, or sums a set) and then writes
based on what it read, with nothing between the two that a competing request would trip over.
Answer one mechanical question from the diff: what makes the second concurrent request fail? If the
answer is not a uniqueness or check constraint, an atomic engine operation, or a conditional write
on a version, this is a lost update or write skew that will pass review, tests and snapshot
isolation and appear only under load. Two further findings of the same family: a version check that
covers only the fields written and not the data that was read to decide, and ordering or conflict
resolution based on timestamps, last-write-wins, or a lease the holder assumes is still valid — a
paused process writes as if still in charge, so only the resource itself can refuse it.
**Unless:** A row private to the request needs none of this, nor does a race whose worst outcome is
duplicated work rather than lost or wrong data. Monotonic clocks for local durations, single-node
sequences, and last-write-wins on insert-once keys or disposable cache entries are legitimate. Where
writes already go to one store with conditional writes, that store can carry the lease and a
separate lock service adds nothing.
**Sources:** (15, 16, 27, 30; F10)

### 5.4 State the consistency boundary the change assumes, and ship the failure story when it is eventual
**Finding:** The change introduces or crosses a consistency boundary without saying so. Two
directions. Where a write now spans two stores or two services, the diff must classify the
invariant: if a violation would be permanently wrong or precedes an irreversible action, the
boundary is misplaced and single ownership is the remedy; if a business process can compensate,
eventual consistency is fine and the finding narrows to what is missing — a retry path, a
reconciliation that runs, and a human escalation for what neither fixes. A log line is not an
escalation. In the other direction, a local transaction that touches several aggregates inside one
store is not a defect, and splitting it into eventual consistency needs a named driver; citing an
aggregate boundary to justify a write that now crosses two stores is the finding.
**Unless:** Do not demand strict consistency the business does not need, and do not demand
coordination for commutative data (counters, add-only sets) or for a constraint local to one shard.
Transient inconsistency during an operation is expected. Staleness that resolves itself by waiting
is not corruption and must not be priced as if it were.
**Sources:** (15, 20, 21, 27; F10)

### 5.5 Treat storage shape, domain shape and published contract as three shapes when they must diverge
**Finding:** A payload, event or DTO leaving the component is a copy of the table — generated from
the entity class, carrying columns and foreign keys no consumer reads, or renaming itself whenever
the schema does. That is the finding, because the consumer is now coupled to storage it cannot see.
The mirror case is a storage or framework type appearing above the adapter layer: flag it when
object and schema demonstrably need to evolve independently, or when the type crosses a published,
remote or cross-team boundary.
**Unless:** Table-mirroring records and ORM-shaped constructors are legitimate while object and
schema stay isomorphic; a mapper earns its ceremony only once they diverge. Inside one deployment
unit, a shape shared between storage and the wire is not by itself a defect. CRUD-ish code does not
owe a translation layer, and a distinction the application never behaves differently on earns no
separate shape.
**Sources:** (15, 16, 20, 21, 30; F4, F12)

### 5.6 Change stored and transmitted shapes assuming old and new code run at the same instant
**Finding:** The diff changes a persisted record, event, message or API payload in place: a column
dropped or repurposed, a field's meaning changed under its existing name, a format only the new code
can parse, an already-applied migration edited rather than superseded. Deployments roll node by
node and stored records outlive the code that wrote them, so the finding is the missing expand
phase — write both, read either, then contract, with a named owner and an end date for the old path.
Also flag a migration that lands in a different change from the code that needs it, and a
destructive in-place rewrite of the system of record where an append or a parallel representation
would have kept the previous state recoverable.
**Unless:** Where the build can prove every producer and consumer moves in this same change — one
deployment unit, no persisted data in the old shape, no external readers — the one-shot reshape is
correct and the transition machinery (dual writes, sync triggers, proxies) is itself the finding. Do
not demand reverse migrations; they double testing and cannot honestly undo destructive steps. Once
a version genuinely has no traffic and no stored records, deleting it is the point.
**Sources:** (04, 05, 21, 27; F12)

### 5.7 Reach shared mutable state under one named guard, reads included
**Finding:** The diff touches a field reachable from more than one thread — a request handler and a
background job, a timer, a framework callback, a pool worker — and not every access site takes the
same guard. A bare read beside a guarded write is the finding and not an optimization: the reader can
see a stale or torn value, and a field taken under one lock here and a different lock or a lone
atomic there is guarded by nothing. The same finding fires where two variables are tied by one
invariant — bound and value, value and version, a count and the collection it counts — and each was
made individually thread-safe: between the two updates every observer sees the invariant broken, and
a composite of thread-safe parts stops being thread-safe the moment a constraint spans them. Flag the
in-process check-then-act window too — contains-then-add, null-check-then-create, size-then-index —
where nothing makes the pair one indivisible step. The guard nobody wrote down is a finding of its
own, because an unrecorded policy is what the next diff breaks silently; and the diff that first
gives existing state a second thread — a scheduled task, a listener, a handler that reads it — makes
every one of that state's existing access sites a finding at once.
**Unless:** Genuinely independent variables may each delegate to their own thread-safe holder; that
is the baseline design, not a violation. A compound action handed whole to a primitive that is atomic
itself — a compare-and-set, a put-if-absent — needs nothing around it, and a race whose worst outcome
is cheap duplicated idempotent work may be accepted knowingly, provided the diff says so. State that
is never shared, immutable, or structurally confined to one thread needs no guard at all, and what
makes those escapes real is 5.8's. Where the contended state lives in a store rather than in memory,
5.3 owns it.
**Sources:** (31)

### 5.8 Give every cross-thread handoff a real ordering edge, and take the cheap escape before the lock
**Finding:** The diff hands an object or a value from one thread to another — a field set here and
read by a worker, a listener, a cached instance, a lazily built singleton — with nothing between the
write and the read but a plain assignment. That is not publication. The reader is allowed to see the
reference before the state the constructor set: a live pointer to a half-built object, which is worse
than a stale null because it reads as valid and the damage surfaces far from here. Name the edge from
the diff, and it has to be one of a lock both sides take, an atomic, a thread start or join, or a
concurrent structure whose handoff its own contract documents. Two shapes fail this by construction —
a lazily initialized shared field checked without the lock before taking it, and visibility borrowed
from unrelated synchronization that happens to sit nearby, which is statement-order luck that
evaporates at the next refactor.
**Unless:** The escapes outrank the choreography, and taking one is the better answer rather than a
weaker one: do not share the state, or make it immutable — an immutable object survives any
publication, correct or not — or confine it structurally to one thread, in locals or a per-thread
holder. Confinement asserted in a comment instead of enforced by scope is the finding restated, not
an escape. Where the handoff is real, a proven concurrent building block — a blocking queue, a latch,
a concurrent map — beats hand-rolled flag-and-wait; eager initialization and a small synchronized
accessor are cheap enough that a clever lazy path owes a measurement; and novel lock-free code needs
a cited published algorithm.
**Sources:** (31)
