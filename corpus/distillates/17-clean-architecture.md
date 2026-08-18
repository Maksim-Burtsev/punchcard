# 17. Clean Architecture — Robert C. Martin

> Architecture is the art of keeping options open: the shape of a system should defer every detail decision — database, web, frameworks, transport — while protecting the business rules that are the reason the system exists. All value flows from one rule: source-code dependencies point inward, from volatile details toward stable policy. A reviewer's job is to defend that direction on every new import, because a system that ships features while becoming harder to change is losing value even as it appears to deliver it.

## Principles

### 17.1 Verify every new source dependency points from detail toward policy, never outward
- **Why:** Change impact travels backward along dependency edges; if entities or use cases name UI, DB, or framework types, every cosmetic technical change ripples into the most valuable code. Inverting the edge (policy owns the interface, detail implements it) confines churn to the periphery.
- **Applies:** Any diff adding an import, reference, inheritance, or type dependency between modules at different abstraction levels — especially new code in domain or use-case layers.
- **Unless:** The composition root (Main) is the designated dirtiest component and may know everything; depending on stable, boring concretions like the standard library is not a violation.
- **Source:** Ch. 11 (DIP), Ch. 22 (The Dependency Rule)

### 17.2 Keep business rules ignorant of the database, the web, and the framework — they are replaceable details
- **Why:** Three chapters each argue one mechanism is a detail behind a boundary; when domain code embeds SQL, HTTP types, ORM entities, or framework base classes, the slowest-changing code is welded to the fastest-changing, and every vendor change becomes a rewrite.
- **Applies:** Edits to domain or application-service code that add framework annotations, request/response types, schema knowledge, or wire formats.
- **Unless:** Adapters, gateways, controllers, and repositories exist to know these details — do not demand purity inside the layer whose job is the mechanism. And the data model is explicitly exempt: the structure given to data inside the application is architecturally significant and deserves real design attention; what is demoted to a detail is the storage engine and its tabular/SQL representation, not the shape of the data itself.
- **Source:** Ch. 30–32 (Database/Web/Frameworks Are Details), Ch. 20 (Business Rules)

### 17.3 Prefer changes that defer detail decisions; flag premature commitment to a technology
- **Why:** The book defines a good architecture as one that maximizes the number of decisions not yet made — the longer a detail choice is delayed, the more information exists when it is finally made. Threading a vendor-specific type through core interfaces converts a cheap deferral into rewrite risk.
- **Applies:** Greenfield skeletons, new module interfaces, and any diff that hard-wires storage layout, transport, or framework lifecycle into code above the adapter layer.
- **Unless:** Once operation genuinely demands a concrete choice, making it is correct; do not demand speculative abstraction layers with one implementation and no plausible second.
- **Source:** Ch. 15 (Keeping Options Open)

### 17.4 Separate code that changes for different actors, even inside one class or module
- **Why:** The book's SRP is about people, not functions: when one module answers to several stakeholders, a change requested by one silently breaks behavior another depends on, and unrelated teams collide in the same files.
- **Applies:** Diffs adding a method or responsibility to an existing module — ask which actor requests each behavior; also component grouping (things that change together stay together).
- **Unless:** A module with many methods is fine if they all answer to one actor; this is not the function-level "do one thing" rule.
- **Source:** Ch. 7 (SRP), Ch. 13 (Component Cohesion)

### 17.5 Keep the component graph acyclic, with edges running from volatile toward stable, and stable hubs abstract
- **Why:** A cycle merges its participants into one lump nobody can build, test, or release independently; a concrete component that everything depends on sits in the Zone of Pain, where it is both hard to change and impossible to extend.
- **Applies:** Every new inter-component edge — check for a path back to the depending component, check which side is more depended-upon, and check whether a widely imported module is accumulating concrete logic.
- **Unless:** Leaf, volatile feature code should be concrete and easy to change; mutual references inside one small module are normal. Breaking a cycle by extracting a new component is growth, not scope creep.
- **Source:** Ch. 14 (ADP), part of Ch. 14 (SDP, SAP)

### 17.6 Test whether duplication is true or accidental before unifying code
- **Why:** Two lookalikes that will change at different rates for different actors are not duplicates; merging them (a shared helper across use cases, a DB record reused as a view model) couples things that must evolve independently, and prying them apart later is far harder than tolerating a copy now.
- **Applies:** DRY-motivated refactors in review — extraction of helpers across use cases or layers, reuse of one data structure across a boundary.
- **Unless:** True duplication, where every change to one copy must be mirrored, should still be eliminated; this is a test to apply, not a license to copy-paste.
- **Source:** Ch. 16 (Independence — Duplication)

### 17.7 Require data crossing an architectural boundary to be a plain, dependency-free structure
- **Why:** Passing an entity, DB row, or framework request object across a boundary silently imports the outer circle's dependencies into the inner one and couples both sides to a representation that changes for different reasons.
- **Applies:** Use-case inputs/outputs, gateway signatures, service payloads, view models — any new or changed cross-layer interface.
- **Unless:** Within one component, passing rich domain objects is fine; do not force DTO ceremony on calls that never cross a boundary.
- **Source:** Ch. 22 (Which Data Crosses the Boundaries)

### 17.8 Treat "can the rules run without the web server, database, or UI" as the acceptance test of a change's architecture, and expect a Humble Object split at every hard-to-test edge
- **Why:** Testability is a proxy for boundary correctness: if a rule can only be exercised through infrastructure, its dependencies point the wrong way. The Humble Object recipe keeps the untestable sliver trivially thin and puts everything with branching logic where a unit test reaches it without booting a framework.
- **Applies:** New features whose only evidence of behavior is end-to-end or GUI-driven tests; logic accumulating inside views, handlers, callbacks, or IO adapters.
- **Unless:** A genuinely humble edge (pure pass-through) needs no extracted testable half and no unit tests; "it's UI" stops being an excuse the moment conditionals appear in it.
- **Source:** Ch. 21 (Testable Architectures), Ch. 23 (Presenters and Humble Objects)

### 17.9 Review tests as system components: they obey the Dependency Rule and must not couple to volatile structure
- **Why:** Tests are the outermost circle; suites that mirror class structure or drive business assertions through the GUI break en masse on trivial refactors, and fragile tests make developers afraid to change production code — rigidity by another route.
- **Applies:** New or modified suites, one-test-class-per-class patterns, production changes that force mass test edits; prefer a stable testing API.
- **Unless:** Small local unit tests during development are fine; the concern is suite-wide structural coupling, and a dedicated test-API layer is overkill for small stable modules.
- **Source:** Ch. 28 (The Test Boundary)

### 17.10 Price boundaries by risk: accept partial or deferred boundaries, flag the first backchannel across one, and never credit a service split as decoupling by itself
- **Why:** Full boundaries are expensive and retrofitting missing ones is also expensive, so the book endorses partial boundaries that decay only through small illicit dependencies reviewers fail to catch. Meanwhile services bound by shared record formats or cross-cutting features must deploy in lockstep — an expensive function call, not a boundary. The failure signature is a single cross-cutting feature (the book's example: adding parcel-style deliveries to a ride-hailing system) that forces every service to change at once, because a set of services carved up by function is exactly what a new feature cuts across. The positive prescription: real boundaries run *through* services, not between them — each service gets an internal component structure obeying the Dependency Rule, so the feature arrives as a new component loaded alongside the old ones rather than a coordinated edit everywhere.
- **Applies:** Diffs that bypass an interface or reach around a facade "just this once"; proposals to erect or skip boundaries; service extractions and fields added to payloads consumed by several services; any feature whose changelist touches most services in the fleet.
- **Unless:** Do not demand full reciprocal interfaces everywhere, and do not forbid service splits made for scalability or team ownership — just refuse the split as proof of decoupling, and ask where the boundaries inside each service run instead.
- **Source:** Ch. 24 (Partial Boundaries), Ch. 27 (Services: Great and Small)

### 17.11 Make the top-level structure scream the domain, and make the compiler enforce the boundaries
- **Why:** Package-by-layer hides what the system does and lets any layer quietly reach any other; package-by-component plus strict visibility turns architectural rules into compile errors instead of tribal knowledge that erodes under deadline pressure. Making everything public dissolves boundaries silently.
- **Applies:** New top-level packages or modules, restructuring diffs, and changes that widen visibility to satisfy an import.
- **Unless:** Adapter-layer internals are legitimately technical; in ecosystems without enforceable module visibility, insist on dependency direction rather than folder shape, and skip the machinery in tiny codebases.
- **Source:** Ch. 21 (Screaming Architecture), Ch. 34 (The Missing Chapter)

### 17.12 Ask whether new behavior arrives as a new implementation or as an edit inside existing policy
- **Why:** Extension without modification is the book's stated reason for studying architecture at all: if a modest new requirement forces edits inside high-level modules, the partitioning has already failed. It also fixes the ordering of everything else — components are arranged into a hierarchy of protection (interactor most protected, controller above presenters, presenters above views) by one rule: if A must be protected from changes in B, then B depends on A. The same reasoning drives the later argument that a service should absorb a new feature as an added component.
- **Applies:** Diffs that add a branch, switch arm, enum case, or feature flag inside a use-case or policy module to support a new variant — a new report format, payment method, notification channel, importer, tenant, or provider — instead of adding an implementation behind an existing interface.
- **Unless:** With two variants and no plausible third, a branch is cheaper than a plugin point; the extension seam belongs at the level that actually varies, not preemptively at every level.
- **Source:** Ch. 8 (OCP), Ch. 27 (Component-Based Services)

## Review heuristics

- For every new import in the diff, ask which side is more volatile; the arrow must point at the stabler, more policy-like side — flag domain/use-case files importing DB, HTTP, ORM, or framework types.
- Trace each new inter-component edge for a path back to its source; any cycle must be broken with an inverted interface or an extracted component before merge.
- Look at what types cross layer interfaces: an entity, ORM row, or framework request object in a use-case signature is a boundary leak.
- Ask whether the changed business rule can be unit-tested with no server, DB, or UI running; if all evidence is end-to-end, the dependencies point the wrong way.
- On any DRY refactor, ask whether the two merged pieces change for the same actor at the same rate; if not, the duplication was accidental and should stay.
- When a diff adds a variant, check where the new code landed: a new branch inside a policy module means the module is being modified rather than extended — ask what interface the variant could have implemented instead, and which side the dependency should point from.
- If one feature's changelist touches nearly every service or module, say so out loud: that is the decomposition failing under a cross-cutting concern, not a large feature.
- Flag new shared mutable state — a cache, counter, registry, or field mutated from more than one path — since races, deadlocks, and lost updates all originate there; ask whether the computation can move into a pure component and leave only a small, transactional mutable core.
- Watch for the first "just this once" dependency that bypasses an existing interface or facade — partial boundaries die by exactly these edges, and review is where the line holds.
