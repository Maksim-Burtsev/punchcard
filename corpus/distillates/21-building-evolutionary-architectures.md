# 21. Building Evolutionary Architectures — Neal Ford, Rebecca Parsons, Patrick Kua, Pramod Sadalage

> Architecture is not a set of decisions made once and defended in prose; it is a set of properties that decay silently unless something executable re-checks them on every commit. Nobody can predict what the system will need, so the goal of a change is not to fit a forecast but to leave the next change cheap: weak coupling across boundaries, contracts that tolerate skew, data that can migrate forward, decisions that can be undone. Coupling here is not only structural: how the work is divided between teams constrains what the code can become, so ownership boundaries and communication paths are read as part of the architecture rather than as scheduling detail. The two questions this book puts to any diff are "what runs to prove this property still holds?" and "what does this make harder to change later?" — with the extra warning that governance itself can be overbuilt until it stalls delivery.

## Principles

### 21.1 Demand a runnable check for every architectural rule the change relies on, not a paragraph in a wiki
- **Why:** Rules enforced only by review boards and documentation stop being enforced the first busy week; a check that executes in the build is the only kind that still holds a year later. Encoding it also converts a reviewer's opinion into an artifact the team can argue with and change.
- **Applies:** Changes that introduce or depend on an invariant a human would otherwise police by eye — layer and bounded-context boundaries, allowed dependencies, latency budgets, referential integrity across services. Also to *where* the check fires: match detection speed to blast radius, since structural untidiness can wait for a nightly scan but a security or data-integrity breach cannot.
- **Unless:** Some rules honestly resist automation (legal sign-off, exploratory testing) and should be explicit manual gates rather than fake automated ones. Many checks only become worth writing after a real stress point appears; piling interlocking checks onto a small system, or instrumenting everything at runtime, costs more than the failures it prevents.
- **Source:** Ch. 2 Fitness Functions; Ch. 4 Automating Architectural Governance; Ch. 7 Fitness Function-Driven Architecture

### 21.2 Turn every quality adjective into a measure, a threshold, and a failure signal
- **Why:** "Fast", "scalable", "secure" cannot be violated because they cannot be evaluated. A dashboard governs nothing until someone fixes an acceptable range and wires breaching it to an alert or a red build; otherwise degradation is visible in principle and invisible in practice.
- **Applies:** Any change justified by a non-domain quality — performance, availability, scalability, accessibility, complexity limits. On a codebase already past a desirable limit, do not set an unreachable bar or delete the check: cascade it, warning above one threshold and escalating to a build failure later, narrowing the accepted value toward the target over time.
- **Unless:** A threshold may legitimately be a documented function of load or context rather than a constant, so do not insist on a single number. And a metric breach is a prompt to look, not a verdict — no metric separates complexity inherent in a hard problem from complexity caused by bad factoring.
- **Source:** Ch. 2 Fitness Functions; Ch. 4 Cyclomatic Complexity and Governance

### 21.3 Treat parts that cannot ship without each other as one deployable unit, and challenge claimed independence
- **Why:** The real deployment boundary — the quantum — is set by the full operational dependency set, not by the boxes on the diagram. A shared datastore, shared orchestrator, or lockstep frontend silently fuses "separate" services back into one unit, and until you know where that boundary really is, you cannot know the blast radius of a change.
- **Applies:** Changes that add cross-service dependencies, introduce a common data store or runtime component, or split and merge services.
- **Unless:** One large unit is sometimes the right answer; the measure is descriptive, not a mandate to decompose. The defect is claiming an independence you do not have, not choosing to deploy things together deliberately.
- **Source:** Ch. 5 Architectural Quanta and Granularity; Independently Deployable

### 21.4 Weaken the kind of agreement two parts share as the distance between them grows
- **Why:** Coupling has kinds, not just amounts: agreeing on a name is cheap, agreeing on meaning, position, algorithm, or execution order is expensive — and the same agreement that is harmless between neighboring classes is corrosive between separately deployed components. Naming the kind gives the author a refactoring direction instead of a vague complaint about tangling.
- **Applies:** Cross-module and cross-service agreements — magic values, positional argument conventions, required call ordering, timing assumptions, parsing or business rules duplicated on both sides of a wire.
- **Unless:** Strong coupling concentrated inside one boundary is normal and often clearer; maximize it within, minimize what crosses. Weigh degree too: a strong form binding two modules is a smaller problem than a weak form binding fifty.
- **Source:** Ch. 5 Connascence; Connascence Intersection with Bounded Context

### 21.5 Refuse to let a module's internals — especially its tables — become someone else's integration surface
- **Why:** Once several components read the same schema, that schema is an undocumented public contract and no owner can change storage without breaking strangers. Data coupling is harder to unwind than code coupling and is the single thing that most often blocks incremental change in legacy systems.
- **Applies:** New cross-application SQL, a service granted credentials on a database it does not own, reports bound straight to the operational store, imports of another module's private types.
- **Unless:** Service-per-table is not the cure either — it floods the system with chatter; a single owning writer plus read-only replicas or caches is usually the middle path. A tracked, explicit interim step toward separation beats blocking a feature on the full untangling.
- **Source:** Ch. 6 Shared Database Integration; Data Duplication; Ch. 8 Antipattern: Reporting Atop the System of Record

### 21.6 Break a shared interface or column in two phases — expand, then contract — never in one
- **Why:** Parallel change lets each dependent migrate on its own schedule, converting a flag-day break into an ordinary incremental step. The same logic covers data: schemas evolve with the code, applied by small forward-only migrations that are reviewed and versioned in the same repo, never by editing one already shipped.
- **Applies:** Breaking edits to shared columns, endpoints, payloads, or stored procedures with consumers the author's team does not control; any change to database structure or stored data shape.
- **Unless:** With demonstrably no other integrators, the transition machinery (dual writes, sync triggers, proxies) is pure cost — change it outright. The expand phase needs a planned end date and an owner, or coexistence becomes permanent duplication. Do not also demand reverse migrations: they double testing and cannot honestly undo destructive operations.
- **Source:** Ch. 6 Evolutionary Data — Evolving Schemas; Replacing Triggers and Stored Procedures

### 21.7 Allow new shared code across boundaries only when it is genuinely abstract and slow-changing
- **Why:** Effective reuse is abstraction times low volatility. A shared component that keeps changing pushes coordination cost onto every consumer and dissolves their independent deployability; at that point duplicating a small representation is the cheaper answer, and a shared asset whose owners cannot keep up with its dependents is a bottleneck, not an asset.
- **Applies:** Proposals to extract a shared library or canonical model across teams or services; adding a flag or parameter to an existing shared component to serve one new caller; changes queued behind another team's backlog.
- **Unless:** Duplication inside a single boundary is still a defect, and this is no licence to copy protocol handling, security primitives, or other stable logic better kept single. Cross-cutting operational concerns — monitoring, logging, auth — are exactly where consistency beats duplication and belong in a shared platform or sidecar layer.
- **Source:** Ch. 5 Reuse Patterns; Effective Reuse = Abstraction + Low Volatility; Ch. 8 Case Study: Reuse at PenultimateWidgets

### 21.8 Keep contracts to what is actually consumed, tolerate the rest, and version internally
- **Why:** Every field in a contract is a way the provider can break the consumer, so binding to a whole record to read one attribute manufactures fragility for free. Producers and consumers are never upgraded at the same instant, so accepting liberally, emitting conservatively, and resolving the caller's expected shape inside a stable endpoint is what makes independent deployment possible.
- **Applies:** API definitions, event payloads, message schemas, generated clients, and any interface with callers outside the deployment unit.
- **Unless:** Looser contracts move verification into application logic — sometimes strictness is worth its cost, and being liberal never means skipping validation on data you act on. Numbered versions are still right for genuinely breaking changes, but never let more than two live at once and always ask when the old one dies.
- **Source:** Ch. 5 Contracts; Ch. 7 Postel's Law; Version Services Internally

### 21.9 Judge the change by how expensive it makes the next change, not by how well it matches a prediction
- **Why:** Architects cannot forecast requirements, so evolvability beats predictive design: speculative generality usually solves the wrong problem and taxes every change until the imagined future arrives. The same restraint applies to insulation — a preemptive abstraction layer over every dependency is debt bought early, and modern tooling makes extracting the seam later cheap.
- **Applies:** New abstractions, plug-in points, config layers, and generalizations added ahead of a concrete second use case; introducing or wrapping third-party libraries, queues, and vendor SDKs.
- **Unless:** Genuinely one-way doors — public contracts, persistence choices, data formats — deserve real upfront thought, and evolvability is not an excuse to skip design where reversal is expensive. Do put a seam around a vendor product broad enough to shape the architecture, or whose types would otherwise appear in domain signatures.
- **Source:** Ch. 7 Prefer Evolvable over Predictable; Build Anticorruption Layers; Ch. 8 Antipattern: Vendor King

### 21.10 Ask how the change is undone in production, and give every toggle a removal date
- **Why:** Systems that evolve fail in ways nobody anticipated, so reversibility — staged rollout, canary routing, feature switches, running the new path beside the old and retiring it on observed evidence — is what makes aggressive change safe. But a stale flag is a live landmine: a dormant one reused by accident cost a trading firm hundreds of millions.
- **Applies:** Changes with production blast radius — behavioral switches, migrations, replacements of a live code path, interface upgrades with several consumers.
- **Unless:** Parallel paths cost real complexity (proxies, dual writes, comparison plumbing) and are not worth it for a single caller or a low-risk change. Toggles kept deliberately as product customization are legitimate but are permanent features that multiply test permutations, not free flexibility.
- **Source:** Ch. 3 Incremental Change; Ch. 7 Make Decisions Reversible; Ch. 8 Pitfall: Product Customization

### 21.11 Check the change against the qualities it was not meant to affect
- **Why:** Architecture characteristics defeat each other in combination even when each passes alone — a cache added for scalability can make data stale enough to break a security or correctness requirement. Verification that only looks at the changed concern systematically misses this whole class of failure.
- **Applies:** Changes touching caching, replication, async processing, retries, batching, or anything that trades one quality for another.
- **Unless:** Combinations are unbounded; pick a few important interactions deliberately rather than demanding combinatorial coverage. How hard an interaction is to check is itself information about how much that characteristic is worth to the team.
- **Source:** Ch. 2 Scope: Atomic Versus Holistic

### 21.12 Count the teams a change needs, and treat needing several as an architectural defect
- **Why:** Communication structure constrains design: a group can only produce boundaries it can talk across, so a seam that cuts through three org charts will keep acquiring coordination cost no matter how clean the diagram looks. Splitting teams by technical layer while splitting the system by domain guarantees this — every feature crosses every silo, and nobody can change what someone else owns. Coordination load also grows quadratically with the number of people who must agree, so the fix is fewer parties per change, not better meetings.
- **Applies:** Changes that need sign-off or parallel work from another team to ship; new seams whose two sides land in different owners; contract edits between services owned separately; work split along frontend/backend/DBA lines while the system is split by domain. The inverse move is the design tool: shape teams — cross-functional, owning a domain end to end — to look like the architecture you want, and the architecture follows.
- **Unless:** Some boundaries genuinely belong to another owner and cross-team agreement is the point, not the flaw — shared platform, security, and compliance surfaces exist to be coordinated. Reorganizing people is far more expensive than moving code, so this argues for placing new boundaries where ownership already is, not for demanding a reorg inside a review.
- **Source:** Ch. 1 Coupling and Team Impact; Ch. 7 Principles of Evolutionary Architecture — Conway's Law; Ch. 9 Organizational Factors — Don't Fight Conway's Law; Inverse Conway Maneuver; Team Coupling Characteristics

## Review heuristics

- For every architectural claim in the description ("stays decoupled", "still under budget", "services are independent"), find the check in the build that fails when it stops being true. No check, no claim.
- Follow the new dependency edges: does anything import upward, close a cycle, reach past a published interface, or touch a table owned by another component? Those are defects, not style notes.
- On any change to a shared interface, column, or payload, name the consumers and find the expand phase — plus who deletes the old path, and when.
- On new shared code, ask two questions: is it a real abstraction, and is it stable? A "no" to either means duplicate instead.
- Read a new migration as append-only: is an already-applied one being edited, and does the schema change land in the same review as the code that needs it?
- For anything risky, ask how it gets switched off in production, and whether the flag has an owner and an expiry.
- When the change adds caching, retries, replication, or async work, name the quality it might quietly break.
- Count the owners this change needs to ship: if a single feature has to be agreed by two or three teams, say where the boundary is in the wrong place, and whether the new seam could instead follow existing ownership.
