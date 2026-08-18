# 30. Secure by Design — Dan Bergh Johnsson, Daniel Deogun, Daniel Sawano

> Security is not a feature bolted onto a design; it is a byproduct of modeling the domain precisely. Most breaches this book cares about are not exotic exploits but ordinary sloppiness — a quantity typed as `int`, a state flipped by a setter, a payload echoed into a log — that lets the system quietly do the wrong thing while every component reports success. The reviewer's job is therefore to ask what the code makes impossible, not what it checks: a type that cannot hold an invalid value, an object that cannot exist half-built, an operation that cannot be reached in the wrong state. Where the design leaves a rule to be re-checked by every caller, the rule is advisory, and one forgetful caller is enough.

## Principles

### 30.1 Replace bare primitives carrying domain meaning with types whose constructor enforces the concept's real rules
- **Why:** A primitive accepts the machine's whole range, so every rule about the concept must be re-verified by every caller. A type that cannot be constructed in an invalid state moves the rule to one enforced place and kills whole classes of injection and business-integrity defects as a side effect of being precise.
- **Applies:** Parameters, fields, return values, and API arguments for quantities, amounts, identifiers, codes, addresses — anything whose valid values are narrower than its declared type.
- **Unless:** The value genuinely spans the full primitive range, or the code is pure pass-through plumbing that never interprets it. A wrapper with no invariant is ceremony. Do not redefine a well-known external term (ISBN, email) to fit local needs — introduce a new term instead.
- **Source:** Ch. 1.4, 2.2, 5.1

### 30.2 Demand that a domain type enforce the whole concept: real bounds, and any qualifier needed to interpret it
- **Why:** A well-named wrapper with only a non-null check gives false confidence — readers assume constraints that are not there. Missing bounds is where business-integrity breaches live: a negative quantity yields a negative payable and nothing technically fails. And when a currency, unit, or tenant travels separately from the value it qualifies, nonsense operations succeed and produce plausible wrong results.
- **Applies:** New value objects and entity fields for quantities, money, measurements, counts, durations, and retry or batch limits; call sites where a value and its context arrive from two different sources.
- **Unless:** Do not fabricate a limit to satisfy the rule — an unknown bound is a question for a domain expert, not a number to guess. Keep types small by default; widen only when context is genuinely being transmitted out-of-band. Rules that truly vary by context belong in the context, not in a shared type.
- **Source:** Ch. 2.3, 12.6, 12.8

### 30.3 Order input checks by ascending cost — origin, size, characters, format, then meaning — and put the meaning check in the domain model
- **Why:** Cheap early checks bound the work an attacker can force; the expensive, fragile parts are the parsers and regex engines, and an unbounded string reaching a backtracking pattern can halt the application. A length gate is not redundant with the pattern check, it is what makes the pattern check safe. Only the domain knows whether data makes sense right now.
- **Applies:** Every entry point taking external data — HTTP handlers, batch imports, message consumers, uploaded documents, runtime-fetched configuration.
- **Unless:** Ordering is the point, not exhaustiveness: a stack of guards each restating the same rule is duplication, and a lexical pre-scan should ignore order and meaning rather than re-implement the parser. Size and origin checks are often gateway concerns, and origin proves little on its own. A tolerant reader ignores unknown-but-harmless fields rather than rejecting them.
- **Source:** Ch. 1.5, 4.3, 8.2.5

### 30.4 Reject malformed input; never repair it, and never echo it back into messages or logs
- **Why:** A repair filter creates a derivative the validator never saw in its original form, and stripping dangerous characters mostly produces false safety while hiding bad data from the source that should fix it. Echoing hands the attacker control of your output, which is later read by a log viewer or analytics tool that may interpret the stored string as code — the danger lives in a second system the throw site cannot reason about.
- **Applies:** Validation failure paths, generic error responses, and any diagnostic logging of rejected input.
- **Unless:** Deliberate one-time canonicalization (decoding to a known encoding, Unicode normalization) followed by validation is legitimate. Failure analysis still needs something: log a stable reason, a field name, a length or hash. Where legacy data is genuinely messy, widen the contract explicitly rather than scrubbing silently.
- **Source:** Ch. 9.4

### 30.5 Require objects to be fully valid the moment they exist, and to expose only the transitions the business allows
- **Why:** No-arg construction plus setters is a convention nothing enforces, so half-initialized objects leak into the system and each new attribute is forgotten at some call site. An unrestricted setter is an unprotected field regardless of the access modifier — it permits transitions the business forbids, such as an order flipping from paid back to unpaid.
- **Applies:** Entities and aggregates holding business state; constructors, builders where constraints span several optional fields, and any newly added accessor pair.
- **Unless:** Persistence frameworks may need a non-public no-arg constructor mapped by field, not by setter. Accessors that actually encapsulate logic are fine, and a final field holding an immutable value can be exposed directly. If construction genuinely needs several client interactions, model initialization as an explicit state instead of a long-lived builder.
- **Source:** Ch. 6.2, 6.3.1, 7.1

### 30.6 Never let a mutable reference to internal state escape, and make the aggregate root the only door to its internals
- **Why:** An invariant spanning several objects holds only if exactly one door exists for state changes. A returned collection lets a caller append directly instead of calling the coordinating method, and an unmodifiable list of mutable items still permits the classic attack of editing a price already sitting in a basket.
- **Applies:** Getters returning collections, dates, buffers, or child entities; constructors storing an externally supplied mutable reference; repository access to aggregate internals.
- **Unless:** Prefer moving the computation into the entity over exposing anything at all. Passing an internal reference transiently is acceptable; holding it is not. Immediate consistency across separate aggregates is over-reach, and a defensive copy can mislead callers who expect their edits to persist.
- **Source:** Ch. 3.2.2–3.2.3, 6.3.2–6.3.3

### 30.7 Gather scattered "may this happen now" guards into an explicit state object, and split an entity whose state graph has grown unmanageable
- **Why:** State rules grown as if-statements inside service methods cannot be audited or tested — you must grep the codebase to learn the rules, and one forgotten branch (shipping an unpaid order) is a direct business loss. A single class juggling fifteen states hides paths that quietly violate the rules; several phase-specific entities of four or five states each can be reasoned about.
- **Applies:** Entities whose allowed operations depend on their phase; any change that adds one more conditional guard around an entity call.
- **Unless:** Two states with always-legal transitions need no state object. Do not split an entity below roughly ten states, nor where a later phase can return to an earlier one or many points spawn the successor. A genuinely tangled graph needs remodeling with domain experts, not chaining.
- **Source:** Ch. 7.2, 7.4

### 30.8 Give sensitive values a read-once type, and keep business data out of exceptions, logs, and error payloads
- **Why:** Credentials and personal data leak through logs, exception payloads, and session persistence long after the code that created them; a single-read type that refuses serialization and string output turns silent leaks into loud, testable failures. Interpolating a whole object invokes a reflective string conversion, so every field added later is silently added to the log too.
- **Applies:** Credentials and sensitive fields with exactly one legitimate consumer; every log or audit statement touching domain objects, entities, DTOs, or exception payloads.
- **Unless:** Read-once detects misuse rather than preventing it, so it complements storage and transport protection instead of replacing it. Debuggability still matters: log named fields via explicit accessors, and attach technical correlators — request ids, resource names — rather than nothing.
- **Source:** Ch. 5.2, 9.1.3, 12.3

### 30.9 Separate domain failures from technical failures by type, and model expected outcomes as return values rather than exceptions
- **Why:** When both kinds share one generic type, the only discriminator left is the message text, and the first reword lets a domain exception escape into the generic handler that logs everything — which is how internals and business data reach logs and users. Routing routine outcomes through exceptions makes them control flow that infrastructure handlers also catch.
- **Applies:** Any layer that both raises domain rule violations and wraps infrastructure faults; services whose operations have a small known set of non-success outcomes — insufficient funds, quota exceeded, not found.
- **Unless:** Genuine invariant violations and bugs should still throw. A small marker hierarchy is the point, not one exception class per rule. A result type only pays off if it is convenient — a home-grown wrapper every caller unwraps with an ignored branch is worse than what it replaced.
- **Source:** Ch. 9.1–9.2

### 30.10 Treat availability as a security property: explicit timeouts, isolation, and a domain-agreed degraded answer
- **Why:** An unavailable system fails the same goal as a leaked one, and the default timeout on many network APIs is infinite, so one unresponsive dependency propagates into hung callers. What a circuit breaker returns when open — empty list or explicit failure — is a business decision a developer cannot make alone.
- **Applies:** Integration points, shared pools and queues, deployment topology, and any change adding a synchronous dependency.
- **Unless:** Watch for hidden dependencies that defeat the partition — separate services on one database, broker, or host are not bulkheaded. Per-process limits do nothing if the same work runs in unbounded parallel. Do not add breakers as decoration where a timeout suffices; each is state and a new failure mode.
- **Source:** Ch. 9.3

### 30.11 Do not let one configuration setting be the defense — stack unlike mechanisms, and test the behavior rather than the setting
- **Why:** Configuration is invisible in review, easy to drop, and changes silently on a library upgrade with no compile or runtime error; a fence with the doors unlocked protects only until the fence is breached. The design the book asks for stacks defenses of different kinds at one risk: the setting that restricts the component, a cheap input-side check that rejects what the business never needs before it reaches that component, and an operational constraint that caps the damage if both are bypassed — not the same validator written three times. Each layer shrinks what an attacker can reach through the ones still standing. And a test that observes the effect — headers present, only intended methods answering, transport enforced — survives both a bad merge and a version bump, while a test asserting a setter round-trips a constant proves nothing.
- **Applies:** Web container settings, transport security, parser features, authentication integration, and any framework default the system's safety rests on; also feature toggles, which are branches in production behavior.
- **Unless:** Layers are code to maintain — reserve them for boundaries where failure is costly, and prefer a blast-radius limit over a third redundant validator. Toggle combinations are the exception to trimming: verify all of them, since choosing a risk-ranked subset assumes you can already rank the flaws you have not found. Keep that tractable by deleting toggles, not by testing fewer combinations.
- **Source:** Ch. 1.5.4–1.5.7, 8.3, 8.6

### 30.12 Require explicit translation at every context or service boundary, and rename a term whose meaning has diverged
- **Why:** Data crossing a semantic boundary implicitly adopts the receiver's meaning, which is exactly where weaknesses open. A shared type reused across two contexts forces each side to respect the other's invariants, so a change correct in one silently violates a rule in the other. Keeping the old name to avoid breaking a consumer is how every system stays individually correct while the whole gives things away.
- **Applies:** Shared model libraries, cross-service DTOs and event names, monolith splits, published APIs, and any change to the semantics of an existing field.
- **Unless:** Inside a single bounded context, translation layers are pure overhead and one strict shared model is the goal. The rename is a means to force a conversation, so it belongs with a migration, not a silent deploy. Transfer types carry the protocol's constraints, not the domain's — convert on entry so validation still happens.
- **Source:** Ch. 3.4, 5.1.5, 11.5–11.7, 13.2

### 30.13 Read repeated null, range, and format checks deep inside a module as a design defect, not as diligence
- **Why:** Deep re-checking means the code does not trust its own design, so nobody can tell which promise holds where; over time the checks drift apart, and inconsistent rules across paths are what an attacker probes. Such checks usually cope by doing nothing, so bad data is neither rejected nor reported. The fix is a validated type plus a stated contract at the entry point, not another guard.
- **Applies:** Private helpers and loops re-validating arguments a public method already checked; optional wrappers around values the domain says are mandatory; also duplicated validation extracted into a shared util package.
- **Unless:** Validation at a genuine trust boundary is required, and this principle depends on it existing. An optional type expressing a real domain fact is correct modeling. Merge duplicated knowledge, not duplicated text: identical code for unrelated concepts is coincidence, and merging it ties the concepts together.
- **Source:** Ch. 12.4–12.5

## Review heuristics

- Scan the diff's new signatures for `String`, `int`, and `long` carrying domain meaning — especially two or more same-typed neighbours in one parameter list, which callers can swap silently and the compiler cannot catch.
- For every new bounded field, ask for both a lower and an upper bound stated from how the business works, and for the qualifier (currency, unit, tenant) that must travel with the value.
- Follow untrusted input from entry to its first parser, regex, or deserializer: is there a size gate before it, and does the failure path avoid echoing the value into a message or log?
- Look at every new getter and log statement for escaping mutable state and for whole objects being interpolated — the field added next release is the one that leaks.
- When a change adds a guard, enumerate the other routes to the same resource; when it adds a state check, ask whether the same rule is already duplicated as an if-statement elsewhere.
- Check the tests for what they omit: boundary values on both sides, malformed input, absurdly large input, and dependency timeouts. Missing extreme-input and failure-path tests mean that behavior was never designed, only assumed.
