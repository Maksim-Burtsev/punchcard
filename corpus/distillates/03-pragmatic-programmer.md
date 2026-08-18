# 03. The Pragmatic Programmer — David Thomas & Andrew Hunt

> Software is never done being changed, so the only durable measure of a design decision is what it does to the cost of the next change. The reviewer's job is to hunt the things that silently raise that cost: knowledge stored twice, concerns smeared across modules, decisions welded shut, code that only works by accident, and small tolerated rot that licenses larger rot. When the future is unknowable, the book's answer is never speculative flexibility — it is replaceable, decoupled, honest code.

## Principles

### 03.1 Flag any single piece of knowledge that now lives in two places needing manual sync
- **Why:** Duplicated knowledge guarantees eventual contradiction — someone updates one copy and the failure surfaces far from the edit. This covers more than code: comments restating logic, stored fields derivable from other fields, a schema mirrored in a hand-written struct.
- **Applies:** Any diff introducing a second representation of the same fact — copied rules, derived values persisted beside their sources, how-comments echoing the code, doc/code intent drift.
- **Unless:** Textually identical code representing genuinely different knowledge (two coincidentally matching validations) must stay separate; a cache is fine when the module fully hides and maintains the duplication.
- **Source:** Topic 9, DRY — The Evils of Duplication

### 03.2 Judge every structural choice by whether it makes the system easier to change
- **Why:** The book treats decoupling, cohesion, and naming as special cases of one value: ease of change. Coupling that makes the next fix hesitant or expensive — like fetching a whole entity to read one field — is a defect even in working code.
- **Applies:** Every structural decision in a diff: where new code lives, what it depends on, what shape it exposes to callers.
- **Unless:** This is a weighing question, not a demand for generic machinery; when no one can name the coming change, plain replaceable code is the correct hedge.
- **Source:** Topic 8, The Essence of Good Design; The Essence of Agility

### 03.3 Require one concern's change to land in one module
- **Why:** In an orthogonal system changes stay local, bugs stay contained, and components can be swapped. A requirement change scattered across many files, or a UI tweak that edits the database layer, is direct evidence the boundaries are wrong.
- **Applies:** Judging where a diff lands relative to module boundaries; new couplings, modules exposing internals or reaching into other modules' implementations.
- **Unless:** A real requirements change may touch several modules legitimately — the test is one functional change per module, not one file per diff.
- **Source:** Topic 10, Orthogonality

### 03.4 Treat vendor, framework, and third-party commitments as decisions that must stay reversible
- **Why:** Critical decisions feel permanent but rarely are — databases get swapped, vendors get acquired. Direct third-party calls entangled through the codebase turn a business decision into a rewrite; an isolating seam turns it into a local change.
- **Applies:** Diffs that introduce or spread direct dependencies on external services, databases, or frameworks across many modules.
- **Unless:** A dependency already confined to one small area needs no extra wrapping; the goal is isolation, not a speculative multi-vendor framework.
- **Source:** Topic 11, Reversibility

### 03.5 Do not let a known broken window land unrepaired and unmarked
- **Why:** One tolerated piece of visible rot signals nobody cares and licenses the next shortcut; decay then compounds faster than any other force. Copying an existing bad pattern "to match surrounding code" is how entropy propagates.
- **Applies:** Diffs that silently replicate a known bad pattern or introduce a known hack without acknowledgment.
- **Unless:** Fixing everything now is not required — containment plus an honest marker (disabled path, explicit not-implemented, tracked issue) is the acceptable minimum; do not weaponize this to demand unrelated cleanups.
- **Source:** Topic 3, Software Entropy

### 03.6 Distinguish tracer code from prototype code; skeletons ship at production quality, prototypes never ship
- **Why:** A tracer slice is lean but permanent — it proves the architecture end to end and carries real error handling from day one. A prototype deliberately skips correctness and robustness, so promoting it imports every omission. Thin vertical slices also surface integration risk that layer-at-a-time work defers to the end.
- **Applies:** First vertical slices of new systems, walking skeletons, any PR whose tone says "we'll harden it later"; staging of feature work.
- **Unless:** A skeleton legitimately lacks features — demand full structural quality, not full functionality. Prototype shortcuts are fine in explicitly disposable code kept off the shipping path.
- **Source:** Topics 12–13, Tracer Bullets / Prototypes; Pragmatic Teams

### 03.7 Expect stated contracts at boundaries and loud, early failure when an impossible state appears
- **Why:** A routine that accepts anything and promises everything hides bugs until they surface far from the cause — a NaN propagating instead of a crash at the call site. Code that keeps running past a broken invariant produces suspect output and destroys the evidence needed to diagnose it.
- **Applies:** New public functions and interfaces; error paths, default switch branches, ignored return codes, swallowed exceptions in invariant-holding code.
- **Unless:** Expected recoverable conditions at trust boundaries (bad user input, network hiccups) deserve real handling, not assertions or crashes; with external resources held, terminate can mean supervised cleanup-and-restart.
- **Source:** Topics 23–25, Design by Contract / Dead Programs Tell No Lies / Assertive Programming

### 03.8 Reject code that works by coincidence — undocumented behavior, lucky ordering, unstated environment assumptions
- **Why:** Code that merely happens to work breaks when the accident it rests on changes — a library fix, a new environment, more cores. If the author cannot say why it works, nobody can know why it later fails.
- **Applies:** Calls depending on side effects the callee never promised, copy-pasted snippets from a different context, off-by-one tweaks papering over a missing model, implicit reliance on locale, clock, filesystem, or network behavior.
- **Unless:** When depending on the undocumented is unavoidable, a prominently documented (and ideally asserted) assumption is the book's accepted fallback — the sin is silence, not the dependence.
- **Source:** Topic 38, Programming by Coincidence

### 03.9 Reject speculative flexibility; demand small verifiable steps and cheap-to-replace code
- **Why:** Foresight has a short throw distance — extension points built for imagined futures encode guesses that will be wrong. Replaceable code hedges an uncertain future better than flexible code and improves cohesion as a side effect.
- **Applies:** New abstractions, plugin points, generic parameters, or config knobs justified by anticipated rather than present needs.
- **Unless:** Design for changes actually visible one or two steps ahead is fine; the test is demonstrated need versus fortune-telling.
- **Source:** Topic 27, Don't Outrun Your Headlights

### 03.10 For every bug fix, require a reproducing test first, a root cause, and a check for the same defect elsewhere
- **Why:** Without a failing reproduction there is no evidence the change fixes anything or stays fixed; writing it forces isolating the true cause instead of the visible symptom. A surprise bug means a wrong assumption — the same wrong assumption usually lives in sibling code. A bug found once must never need a human to find it again.
- **Applies:** Every diff labeled a bug fix, especially symptom-level patches like a guard at one call site of a shared function.
- **Unless:** Defects impractical to automate (timing, hardware) may skip the harness, but the review should still see root-cause reasoning, not a diff that merely silences the report.
- **Source:** Topic 20, Debugging; Tightening the Net (Find Bugs Once)

### 03.11 Keep volatile policy and environment values in configuration a general mechanism interprets, not in control flow
- **Why:** Business rules and deployment values change constantly; encoded as inline checks and hardcoded constants, every policy change becomes a code change. Implement the general case and express today's rule as data behind a thin API.
- **Applies:** Diffs embedding role lists, thresholds, pricing tiers, credentials, endpoints, or environment-specific constants directly in source; scattered direct reads of a raw config blob.
- **Unless:** Genuinely stable invariants need no configurability; making everything a knob is its own maintenance nightmare, and pushing contested design decisions into config is abdication. Secrets stay out of version control entirely.
- **Source:** Topic 32, Configuration; The Requirements Pit (Policy Is Metadata)

### 03.12 Hunt coupling symptoms: method-call train wrecks and globally reachable mutable state
- **Why:** A chain reaching through several objects' internals freezes their structure into every caller and scatters business rules where nothing can enforce them — tell the data's owner instead of asking and deciding outside. Global mutable state (singletons and ambient config included) is a hidden parameter to every function, with an unknowable blast radius; painful test setup is the early warning.
- **Applies:** Callers traversing more than one level of another module's structure; read-decide-write-back patterns on foreign state; new module-level mutable state, singletons, or scattered direct access to shared external resources.
- **Unless:** Chains over stable standard-library types and pipelines of pure data transformations are not train wrecks; immutable constants are not global data; the fix for shared resources is a narrow wrapper API, not elimination.
- **Source:** Topic 28, Decoupling (Tell, Don't Ask; The Evils of Globalization)

## Review heuristics

- Trace every fact the diff adds — a rule, format, constant, or intent — and confirm it exists in exactly one authoritative place, counting comments, docs, and derived stored fields as copies.
- For each functional change in the PR, count the modules it touched; more than one module per concern means a boundary is wrong.
- Ask of every new dependency, exposed shape, and hardcoded value: what does the next change here cost, and could this piece be deleted and replaced cheaply?
- On a bug fix, look for the test that failed before the fix, evidence of the root cause, and a sweep for the same wrong assumption in sibling code.
- Probe why the code works: any reliance on unpromised behavior, call order, or environment must be documented and asserted, or rejected.
- Check the failure posture: contracts stated at boundaries, impossible states crashing loudly and early, expected external errors handled for real — and no silent replication of a known bad pattern without a marker.
