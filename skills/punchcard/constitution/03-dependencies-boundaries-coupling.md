# 3. Dependencies, Boundaries and Coupling

This chapter answers three questions about a diff's edges: which way does each new dependency point,
what does each boundary publish and carry, and is the strength of the agreement two parts share
proportionate to the distance between them. It judges the wiring — imports, injection, payloads,
published surfaces, process hops — not the logic inside a unit.

### 3.1 Point every new dependency edge from volatile detail toward stable policy, and never let it return

**Finding:** Three triggers, all readable from the import list and signatures. First, a policy-side
file — domain, use case, application service — that now names a mechanism: an ORM entity, HTTP
request or response type, driver, message client, vendor SDK, framework base class or annotation.
Second, a lower layer learning who calls it: a parameter, flag, enum arm or branch that encodes
caller identity, so the callee can no longer be reused or replaced without knowing its users. Third,
an edge that closes: a new import with a path back to the importing module, mutual imports between
two packages, or a back-reference added so a child can reach its owner. Widening visibility (private
to protected, package-private to public, exporting a symbol) purely to satisfy one of these imports
is the same finding at an earlier stage — the boundary is being dissolved rather than crossed.

**Unless:** The composition root is the designated dirtiest place and may know everything. The
adapter, gateway, repository or controller layer exists to know the mechanism; do not demand purity
from the code whose job is the mechanism. An ORM- or framework-shaped type reaching an application
service inside one deployment unit is not this finding while object and schema stay isomorphic and
the call stays in-process; the trigger is independent evolution, or the type crossing a process
boundary as bytes — serialization is the trigger whoever owns the consumer, not publication or team
lines (F17) — and 5.5 owns that case, so raise it there rather than here (F4). Depending on stable,
boring concretions — the standard library, a language-level value type — is not a violation. Mutual
references inside one module are normal, and results traveling upward through callbacks, events or
return values are not usage dependencies. Breaking a cycle by extracting a component is in scope for
the diff, not scope creep.
Note the remedy: the fix for a leaked external type is confining it to the one module that owns that
mechanism, which is not the same as wrapping it in an interface — see 3.2 before asking for one.

**Sources:** (03, 04, 12, 16, 17, 21, 23, 25, 34; F1, F17)

### 3.2 Make indirection pay rent: a seam needs a consumer that already exists, not a forecast

**Finding:** An interface with one implementation, a factory that makes one product, a wrapper or
adapter whose methods forward one-to-one, a configuration knob with one value, a policy layer over a
single call site, or a parameter with one caller — introduced in this diff ahead of any second
consumer. The tell is that the new type adds a navigation hop and removes no knowledge from anyone:
the caller still names the same concepts, and the layer beneath repeats the abstraction above it.
Testability is not an exemption; a seam whose only consumer is a test that does not actually
substitute across it is the same speculative indirection under a friendlier name.

**Unless:** A seam is earned when a concrete second consumer already exists in the tree, or when the
boundary is genuinely one-way — remote, published outside this build, cross-team, or a wire or
stored format — because there the cost of extracting it later is not symmetric. Existing seams are
not in scope: this is a rule against adding indirection, not a licence to strip a boundary someone
is already using. Where the mechanism is genuinely broad enough to shape the architecture, the
argument is about confinement (3.1), and confinement is achieved by keeping the calls in one module,
which requires no new interface. Extraction is cheap later; do not block a diff for lacking a
flexibility no present code needs.

**Sources:** (01, 03, 05, 12, 13, 14, 16, 17, 19, 21, 24, 26, 34; F1)

### 3.3 Hand collaborators in; treat anything the code reaches for by itself as an undeclared dependency

**Finding:** Code below the process boundary that reads its own surroundings — a singleton, service
locator, static registry, module-level mutable state, environment or configuration read, system
clock, random source, or a collaborator the object constructs for itself inside a method or
constructor. Each one is a parameter that does not appear in the signature, so the reader cannot see
what the unit depends on and the wiring cannot be changed without editing the unit. Related trigger:
a caller reaching through two or more levels of another object's structure to fetch data and decide
outside it, which welds that structure into every caller.

**Unless:** One composition root at the process boundary legitimately reads the real environment and
knows everything; that is where these reads belong, not nowhere. Immutable constants are not global
state, and chains over stable value or standard-library types, or pipelines of pure transformations,
are not structure reaching. Some state genuinely is process-wide. Threading a value through six
layers purely to remove one static can cost more than the static did — say so rather than demanding
the plumbing. And handing the concrete collaborator in satisfies this rule on its own: asking for an
interface on top of the injection is a separate demand that must clear 3.2.

**Sources:** (03, 04, 17, 23, 25; F1)

### 3.4 Weaken the kind of agreement two parts share as the distance between them grows

**Finding:** Name the kind of coupling the diff adds, not its amount. Agreeing on a name is cheap
because tooling can fix every site at once; agreeing on meaning (a magic value, a sentinel, a status
string both sides interpret), on position (a positional convention in an argument list, tuple or
record), on execution order (setters or init calls that only work in one sequence), on timing, or on
a replicated algorithm (a rule computed identically on both sides of a wire so the results must
match) is expensive because one side can move silently. The finding fires when one of those stronger
forms now spans a module, deployable, repository or team boundary. State the kind in the comment —
it hands the author a direction rather than a complaint about tangling.

**Unless:** Strong coupling concentrated inside one encapsulation boundary is normal and often
clearer than the indirection that would weaken it; maximize agreement within a boundary and minimize
what crosses. Weigh degree against kind: a strong form binding two modules is a smaller problem than
a weak form binding fifty. Some contracts genuinely require order or exact values — a protocol, a
cryptographic sequence — and the ask there is that it be explicit and single-sourced, not weakened.
Reserve the deep argument for shapes that are expensive to undo or for code that is hot or brand
new; on cold, cheaply reversed code this is a note, and say which it is.

**Sources:** (12, 17, 19, 21, 32, 34; F2)

### 3.5 Let a boundary carry only what its consumer reads, in a shape the consumer's side owns

**Finding:** A cross-boundary signature, payload, event or view model carrying a type the consumer
must decode more of than it uses: an entity graph fetched to read one field, a whole record bound to
branch on one attribute, a payload padded with fields nobody consumes, or an interface exposing
indices, internal collections, mutable internals or storage layout. Widening a widely implemented
interface to serve one privileged caller is the same defect from the other side — every implementor
now owes a method one client wanted. A contract that mirrors the storage schema field-for-field is a
finding when the two must evolve independently, because then a rename on the owner's side breaks
strangers. In a serialized payload two elements are findings on sight, whoever owns the consumer: a
storage-internal identifier the consumer never resolves — surrogate key, sequence number, enum
ordinal, version column, foreign key — and a field whose reader the author cannot name today. Both
are pure ratchet: unknown callers bind to whatever is observable, and removal is near impossible.

**Unless:** Inside one deployable, a type shaped like its table is legitimate on two conditions
together: object and schema stay isomorphic, and the call stays in-process or inside one build
artifact. CRUD-ish code owes no mapping ceremony, and demanding DTO ceremony on a call that never
leaves the process is itself the finding. Passing rich domain objects between components of one module is fine. The carve-out ends at
serialization: once the shape crosses a process boundary as bytes, the surrogate keys, version
columns, foreign keys and framework annotations riding along are the finding regardless of who owns
the consumer or which release train it ships on, because the ratchet is Hyrum's law and not ownership
(F17). Hold the anti-ceremony finding alive on the other side, or this becomes a licence for mapper
families: the remedy is one wire type carrying the fields a named consumer reads — a record and a
constructor is the whole ask — not a DTO hierarchy and not a translation layer over shapes that are
genuinely identical. In-process, the trigger for separating the shapes stays concrete: this diff
already shows the two evolving apart. High-throughput paths legitimately carry full data, and a
deletion notice legitimately carries only a key; there is no mechanical right payload, only one
nobody can name a reader for.

**Sources:** (04, 12, 16, 17, 19, 20, 21, 25, 32, 34; F4, F17)

### 3.6 Publish a contract at every boundary, and count observable behavior as part of it

**Finding:** A new or changed cross-module surface that leaves its promises implicit: what it
guarantees, what it hides, who owns each resource it returns or accepts, whether returned data
survives the next call, whether absence is legal, and how failure reaches the caller. If the
interface-level comment or type cannot answer those without reading the body, the boundary is
unfinished. Second trigger, on the other side of an existing surface: a diff that shifts observable
behavior nobody documented — iteration order, default value, error text, timing, log format, an
exposed field or returned mutable structure — with no account of who was relying on it. With enough
callers, someone depends on all of it, so the documented contract is an estimate rather than a fact.

**Unless:** A single-caller internal helper or an acknowledged throwaway needs none of this, provided
it is not being quietly promoted to shared code. Pure additions that leave the old specification
intact need no ceremony. On breaking changes, gate on the atomicity of the consumer set rather than
on the word public: when the build can prove every consumer moved in this change, the one-shot
reshape is correct and a compatibility shim is itself the finding. The moment one consumer sits
outside that unit — another repository, another deploy cadence, persisted data, a wire format, a
published package — the unversioned in-place break is the finding instead, and the staged path needs
a named owner and an end date.

**Sources:** (03, 04, 08, 19, 21, 23, 32, 34; F12)

### 3.7 Treat a process boundary as the most expensive coupling available, and refuse a split as proof of decoupling

**Finding:** A diff that carves out, extracts or newly depends on a separately deployed unit while
the two halves remain fused: a shared database or schema, a shared entity library, a common
migration or release train, a synchronous hop whose caller cannot proceed without it, or a
cross-cutting feature that must be edited on both sides at once. Independent deployability is
claimed by the description and refuted by the operational dependency set. Two edges are findings on
their own: a component reading or writing tables it does not own, which turns someone's storage into
an undocumented integration surface, and a formerly local join or lookup that has become a remote
fetch on a hot path.

**Unless:** Deliberately deploying things together is not the defect — claiming an independence you
do not have is. A monolith or modular monolith is one unit by design and shares a store at no extra
cost; a few services that are really one bounded context may legitimately share data if the team
accepts the consequence. Ownership legitimately decides where a boundary goes, and placing a new
seam along existing ownership lines is sound; it does not by itself argue for making that seam a
process boundary. Where a split does earn independence, the argument belongs with the other
distribution costs rather than here — this rule's scope is the coupling claim, not the granularity
decision.

**Sources:** (16, 17, 19, 20, 21, 34; F9)

### 3.8 Never change what an element means without changing what it looks like

**Finding:** A live element whose meaning moves under an unchanged name, type and version: changed
units, sign convention, currency or timezone, a changed set of included components (a price that
quietly became tax-inclusive), a changed inclusion or filtering rule for a collection, changed
cardinality, an enum arm reinterpreted, a default that now stands for something else, or the
computation behind the field rewritten. Every schema check, contract test and deserializer passes and
the consumer misreads the value in production, so the tell is on the producing side: a changed
formula, constant or query behind a field the payload still names the same way, shipped with no
version signal and no consumer-impact note. Three neighbours are the same finding — a mandatory new
field or a removed operation released as a compatible change, a version identifier duplicated across
URL, header and payload so two places can disagree, and a contract-affecting change carrying no
version marker anywhere. The mirror defect sits on the reading side: deserialization that fails on an
unknown field, which breaks the day the producer adds one.

**Unless:** Producer and consumer co-owned on one release train, with tests that exercise the existing
consumer, may evolve meaning ad hoc — the trigger is a consumer that deploys on someone else's
schedule, or persisted data written before this diff. A genuine bug fix restoring the documented
meaning is not a reinterpretation. Additive optional fields are exactly the tolerance a tolerant
reader buys and are not this finding, but tolerance never extends to values the consumer acts on: a
number or enum arm consumed with no range check is the finding from the other side. Per-element
versioning explodes governance cost — one identifier in one place is the ask. Where the payload's
shape is at issue rather than its meaning, 3.5 owns it; where the drifting thing is undocumented
observable behavior rather than a specified field, 3.6 does.

**Sources:** (32, 34)
