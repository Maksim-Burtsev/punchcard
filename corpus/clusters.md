# Clusters

Eleven review lenses distilled from the 30-book corpus. Each lists the scope question and the
principles the corpus agrees on, with book numbers.

## Complexity and Module Design

Does this change lower or raise long-term complexity — are modules deep, does each abstraction pay
rent, and is decomposition driven by measured load rather than line count?

- Complexity is reader load, and the reader is the instrument. Reviewer confusion is the finding, not a debate to win (01, 02, 09, 11, 13, 18).
- Every abstraction, layer, hook and knob must be paid for by a need present in this change. Speculative generality is a defect (01, 05, 07, 09, 12, 13, 14).
- A module earns its boundary by hiding a nameable secret — an internal choice you can still reverse without rippling to callers (01, 02, 12, 13, 18).
- Over-decomposition ranks equal with under-decomposition: pass-throughs, middlemen, single-child abstractions, forwarding wrappers (01, 05, 11, 13, 14).
- Duplicated *knowledge* is the real duplication defect; the coupling exists even when no text was copied (01, 02, 05, 13, 14, 18).
- Decomposition is driven by measured signals — branches, nesting, live variables, injected dependencies, mixed abstraction levels — never by line count (01, 02, 09, 11).
- Complexity belongs on the implementer's side: exported knobs, required call ordering, caller-side pre/post-processing multiply who must cope (01, 07, 12, 13, 14).
- Names and doc comments probe the decomposition; a unit that resists a short honest name is conflating roles (01, 02, 05, 11, 13, 14).
- Structure may not be degraded for unmeasured performance; a profile is the price of the trade (05, 07, 11, 13, 18).
- Where the codebase already solves this class of problem, conformance beats an equally good novel solution (01, 14, 18).

## Naming, Readability and Reader Load

Can a reader without the author's context understand this diff, or is reader confusion reporting a
decomposition defect?

- The reader without the author's context is the measure; the author's certainty is not evidence (01, 02, 10, 11, 13).
- An entity that resists a short honest name is reporting a decomposition defect, not a wording problem (01, 02, 13, 15).
- Names and signatures that lie are the highest-severity readability defect — readers chunk on the name and never open the body (01, 09, 10, 11, 15).
- Reader load is measured in chunks held at once, never in lines, in either direction (01, 02, 09, 10, 11).
- One concept, one name, one idiom across the codebase; a second way of doing what the project already does costs more than it gains (01, 04, 10, 13, 23).
- Comments carry what code cannot — intent, rationale, units, ordering, preconditions; a stale comment is a defect on the diff that left it (01, 04, 10, 11, 23).
- Durability ranks the carriers: types > names > comments > external docs (01, 09, 13).
- Navigation cost is reviewable: count files opened and invisible hops needed to believe the diff is correct (01, 10, 13, 23).
- Deviation from the established idiom for a standard operation is a bug signal, not a taste matter (04, 10, 23).

## Dependencies, Boundaries and Coupling

Which way do new dependencies point, what does each boundary publish, and how strong is the coupling
relative to the distance it spans?

- Dependency edges point from volatile detail toward stable policy; unavoidable externals are confined to the one module whose job is that mechanism (04, 16, 17, 21, 23, 25).
- Coupling is judged relative to distance: tight agreement inside one module is normal, the same agreement across a deployable or team boundary is corrosive (12, 17, 19, 21).
- What crosses a boundary is narrow and representation-free: no entities, ORM rows, framework request objects, or fields the consumer never reads (04, 12, 16, 17, 21, 25).
- A boundary publishes an explicit contract or it is unfinished: promises, ownership, and how failure reaches the caller (03, 04, 19).
- Observable behavior of widely used code is a de facto contract — ordering, timing, error text, defaults included (04, 08, 21, 23).
- Ambient access is a hidden dependency: globals, singletons, service locators, clocks, config reads. Hand collaborators in; one composition root knows everything (03, 04, 17, 23, 25).
- A process boundary is the most expensive coupling available, and carving out a service is not by itself decoupling (16, 17, 19, 21).
- Indirection is bought: a new interface, factory, wrapper or config surface needs a concrete second case (03, 12, 16, 17, 19, 21).
- The dependency graph stays acyclic and one-directional (12, 17, 21, 23).
- Structural rules only a reviewer enforces erode; prefer compiler-enforced visibility and build checks, while knowing where tooling goes blind (08, 17, 19, 21, 23).

## Domain Model and Types That Constrain

Does the code make invalid states impossible rather than merely checked?

- A concept whose valid values are narrower than its declared type belongs in a named type that enforces the rule, including values that always travel together (05, 09, 13, 15, 25, 30).
- Construction is the enforcement point: valid the moment it exists, or loud failure (09, 13, 15, 25, 30).
- Enforce once at the boundary in the type, then delete the downstream guards; repeated interior re-checking is a design defect (09, 14, 30).
- Encode the constraint where the compiler sees it: types, then names, then comments (09, 11, 13, 15, 30).
- An invariant survives only with exactly one door to the state: immutable values, no setters on construction-only fields, no live interior references (05, 13, 15, 24, 30).
- Behavior belongs beside the data whose invariant it protects (05, 11, 13, 14, 25).
- Business rules live in named domain objects, not controllers, jobs or templates; domain types do not import ORM or wire types (09, 15, 16, 25, 30).
- Names carry the model — the vocabulary domain experts actually speak, and the role the object really plays (11, 13, 14, 15).
- A recurring special case is a missing concept, not a missing branch (05, 11, 13, 15, 24, 30).
- A type earns existence from a distinction the application behaves differently on; a wrapper with no invariant is ceremony (13, 14, 24, 25, 30).

## Data, State and Consistency

Which store is authoritative, who may write it, and what happens under concurrency, replication and
schema change?

- Every fact has one authoritative home; every other copy is derived and owes a stated freshness and a re-derivation path (02, 04, 05, 16, 20, 21, 27).
- Exactly one component writes a store; everyone else goes through its interface, reads included (15, 16, 20, 21, 30).
- State is mutated only through a door that can enforce the invariant (04, 05, 15, 16, 30).
- Concurrency control is explicit and never rests on clocks: version checks, atomic operations or constraints, covering what was read (15, 16, 27).
- Declare the consistency boundary; an eventually-consistent rule needs a named reconciliation and a human escalation path (15, 20, 21, 27).
- Storage shape, domain shape and published contract are three different shapes (15, 16, 20, 21, 30).
- Stored or transmitted shape changes assume old and new code run simultaneously: expand then contract, forward-only versioned migrations shipped with their code (04, 05, 21, 27).
- Prefer the version you can undo: append over overwrite, new representation built beside the old (05, 21, 27).
- State arriving from outside the process is untrusted input, revalidated at the boundary before anything derives authorization, pricing or a write from it (02, 16, 30).

## Failure, Errors and Resilience

How does this code represent, propagate and survive failure?

- Errors are detected where they occur, policy is decided where the context exists; catch-log-continue and ignored return codes are findings (02, 04, 14, 19).
- Error handling is one codebase-wide strategy; a second convention owes a migration or a rejection, and a missing strategy is itself the finding (01, 02, 04, 14, 30).
- Validation belongs at an explicit, locatable trust boundary, expressed in a type where possible (02, 14, 18, 29, 30).
- Every wait crossing a process, host or pool boundary is bounded, and a timeout counts only if the caller's behavior on expiry is defined (18, 19, 28, 29, 30).
- Anything that grows with traffic ships its own bound: limited result sets, capped retries with backoff and jitter, a purge for every accumulator (28, 29, 30).
- A remote call has three outcomes — success, failure, unknown — so a retry is unsafe until idempotency is established end to end (19, 27, 28, 29).
- Failure is contained by structure: partitioned pools and queues, isolation at integration points, bounded blast radius (18, 19, 28, 29, 30).
- Behavior when a dependency is unavailable is designed, named and owner-agreed; reduced guarantees are visible, not served as fresh (14, 28, 29, 30).
- An operator must be able to tell busy from stuck from outside the process — real-work health signals, structured records, correlation ids, never the payload (28, 29, 30).
- Failure paths get adversarial evidence or are presumed broken (02, 04, 18, 28, 29, 30).

## Security and Trust Boundaries

What does this change trust, what does it validate once at the edge, and what must now be correct?

- Untrusted data is parsed once at the trust region's edge into a value carrying its own proof (02, 09, 14, 30).
- Every claimed security property has locatable enforcement a reviewer can point at (02, 18, 29, 30).
- An invariant holds only with exactly one door to the state; check-then-act split across callers or machines is a hole (14, 16, 27, 30).
- Failure paths around authorization, policy, quota and credentials are designed; silent swallowing is a finding on its own (02, 14, 29, 30).
- Anything that leaves the system's control and returns is untrusted: round-tripped state, hidden fields, configuration, cross-boundary values (16, 27, 29, 30).
- The failure output is an attack surface: no echoed input, no interpolated objects, and stored personal fields are inventory someone must be able to erase (09, 27, 29, 30).
- Rigor scales with consequence, not diff size; a one-line config flip gets the same bar as a feature (02, 14, 18, 29).
- Universal claims cannot be closed by passing tests; they need a structural constraint or an argument over all executions (02, 09, 18, 27).
- Code that only runs on a bad day does not work: break-glass, fallback and restore paths must be exercised (02, 14, 18, 29).
- Configuration, deployment inputs and framework defaults are load-bearing code with none of code's review (18, 29, 30).

## Tests as Evidence

What evidence arrives with this change, and what does the difficulty of writing it report about the
production design?

- Every behavioral change arrives with a test that would fail without it; a bug fix carries the smallest reproducing test (02, 06, 08, 09, 24).
- Tests assert observable results through the public protocol; assertions on private state or internal call sequences go red on changes that alter nothing (05, 08, 09, 11, 24, 25, 26).
- Difficulty writing the test is a verdict on the production code; fixing only the test hides the signal (06, 07, 08, 24, 25, 26).
- Ambient and self-constructed dependencies are flagged on sight (06, 07, 09, 24, 25, 26).
- Code that both decides and performs I/O splits into a collaborator-free decision and a thin performer (07, 09, 25, 26).
- Test code is reviewed at production rigor: one named behavior, no logic, obvious canned values, a failure message that locates the fault (02, 08, 09, 11, 24, 25).
- Green is not evidence: would an obviously wrong implementation still pass? (02, 08, 09, 26).
- Restructuring and behavior change never travel together, and test edits get harder scrutiny than production edits (05, 06, 09, 11, 24).
- "Verified manually" and "the nightly suite covers it" are not evidence for a localized logic change (06, 08, 26).
- Production indirection ahead of a demonstrated second case is a guess, even when the word used is testability (05, 07, 09, 24, 26).

## Change, Refactoring and Legacy

Does this change make the next change cheaper?

- The durable measure of a diff is what it does to the cost of the next change (01, 03, 05, 07, 21, 22).
- One hat per edit: restructuring and behavior change never share a diff (05, 06, 07, 08, 09, 24).
- Behavior-preserving rework needs behavior evidence that existed and passed beforehand (05, 06, 08, 09, 22, 24).
- Difficulty testing a unit in isolation is a verdict on the design, never a testing problem (06, 07, 08, 09, 24).
- Structure ahead of a concrete second case is rejected; prefer replaceable code over flexible code (01, 03, 05, 07, 09, 21, 24).
- Where a diff lands is evidence about the boundaries: one concern's change should touch one module (01, 03, 05, 07, 21, 22).
- Duplication's cost is the coupled edit — the copy someone forgets (03, 05, 21, 22, 24).
- Large restructurings arrive as small, individually releasable, individually revertible steps on the mainline (07, 08, 09, 21, 22, 24).
- Every migration and toggle needs a named owner, a removal plan and an end (08, 09, 21, 24).
- A deliberate shortcut is acceptable only when stated; silence is what normalizes decay (01, 03, 06, 08, 21, 22).

## Architecture at Scale and Distribution

For decisions expensive to reverse, what trade-off is accepted and how is it undone?

- Scrutiny scales with the cost of undoing a decision, not with diff size (16, 18, 19, 20).
- A justification listing only upsides is unfinished: name the sacrifice and who pays (16, 18, 19, 20).
- Claimed independence is checked against the operational dependency set, not the diagram (17, 19, 20, 21).
- Every call leaving the process is slow, unreliable and has an unknown outcome: bounded wait, bounded result, defined hang behavior, idempotency story (16, 19, 27, 28).
- Writes define ownership; a module's internal storage must never become someone else's integration surface (20, 21, 27).
- A cross-boundary contract is shaped independently of the schema and carries only what consumers read (17, 19, 20, 21, 27).
- Old and new versions run simultaneously in both directions: expand, then contract, with an owner and an end date (21, 27, 28).
- A boundary rule that lives in reviewer memory erodes; put it in the build with a threshold and an owner (19, 20, 21).
- When one capability's changelist touches most services, the decomposition is failing — say so instead of reviewing the pieces (17, 20, 21, 22).
- Reuse across a deployment boundary is licensed by low volatility, not by neat abstraction (20, 21, 22).
- Once one unit of work spans services, atomicity is gone: ship the failure story — retry path, escalation, the gaps where data is lost (19, 20, 27).

## The Review Act Itself

How should the reviewer spend attention and demand proof?

- Calibrate rigor to consequence, never to diff size; "too small to review" is when one-line changes fail most (02, 08, 18, 19, 22).
- Demand evidence proportional to the cost of the claim; an unfalsifiable claim is itself the finding (01, 07, 18, 19).
- Every behavioral promise ships with the artifact that fails when the promise breaks (02, 08, 09, 18, 23).
- Green tests are not closing evidence — sabotage them: would a degenerate implementation pass? (02, 08, 09, 18).
- Mechanical rules belong in the build; a structural violation caught by hand twice is a request for a check (08, 09, 19, 22, 23).
- Version history is admissible evidence: repeated fixes in one region, complexity trend, an absent co-change partner (02, 22, 23).
- A fix runs from symptom to fault and then sweeps the siblings; containment is legitimate only when labeled (02, 09, 18, 22, 23).
- Change sets stay small enough to actually be read, and each step releasable (07, 08, 09, 23).
- The reviewer's confusion is data about future maintainers, but must be pinned to the exact point where the trace broke (01, 02, 08, 10).
- Review the whole project element at production rigor, against the architecture the code already follows (08, 10, 18, 22, 23).
- Debt is recorded, never normalized; review is the last checkpoint where the drift is visible (01, 02, 18, 22).
