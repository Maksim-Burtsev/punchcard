# 14. Object Design: Roles, Responsibilities, and Collaborations — Rebecca Wirfs-Brock, Alan McKean

> Wirfs-Brock and McKean see software as a community of responsible collaborators: every object plays a nameable role, owes services to its clients, and relies on neighbors under decided terms of trust. Design quality is judged by who is responsible for what, who trusts whom, and whether collaborations still read as a coherent story — not by class diagrams or real-world resemblance. For a reviewer this means checking each diff against the roles it touches: does it keep responsibility where the knowledge lives, does it respect the system's trust regions and control style, and does its rigor match the consequences of failure.

## Principles

### 14.1 Verify each class in the diff plays one nameable role
- **Why:** Objects are responsible members of a community; a class whose responsibilities do not add up to a role is where designs muddle. Duties only slightly off-purpose are the most insidious, dragging the object into contexts it should not depend on.
- **Applies:** New classes, and changes that graft duties onto a convenient existing class because the caller already holds it.
- **Unless:** Private supporting responsibilities needed to fulfill the public ones legitimately live inside; an object blending stereotypes (holding the data it serves with) is still one role if it serves the same clients for one purpose.
- **Source:** Ch. 1 (roles and role stereotypes); Ch. 4 (testing candidate quality)

### 14.2 Keep behavior beside the knowledge it uses; steer toward delegated control
- **Why:** The book maps a continuum: centralized control breeds passive data bags and a controller every change ripples through; fully dispersed control smears one behavior across many weak objects. Delegated control — substantial pools of responsibility with occasional helpers — is the balance.
- **Applies:** Growing manager/service/controller classes, callers that pull several fields from another object to derive a result the owner could answer, and diffs fragmenting one behavior across new micro-classes.
- **Unless:** Orchestrating a multi-object workflow (sequencing, error reporting) legitimately lives in a coordinator; framework-imposed control styles are followed, not fought; a tiny helper with a single client should merge back into its caller.
- **Source:** Ch. 1 (architectural control styles); Ch. 4 (distribute system intelligence); Ch. 6

### 14.3 Give every fact exactly one owning home
- **Why:** Copied knowledge invites inconsistency; maintainability comes from eliminating potential discrepancies. The remedies are a dedicated holder others query, folding the fact into the object it fits best, or collapsing the objects that all need it.
- **Applies:** Diffs that cache, copy, or denormalize data; fields mirroring data held elsewhere; an object storing another object's attribute instead of asking for it.
- **Unless:** Deliberate replication the system explicitly requires (availability, performance) with a designed sync strategy; over-consolidation into one giant owner is the opposite failure.
- **Source:** Ch. 4 (keep information about one thing in one place)

### 14.4 Model only distinctions this application behaves differently on
- **Why:** Resembling the real world or the spec is explicitly not the goal; objects should be only as smart as the application needs. A distinction with no behavioral difference in this system earns no separate type.
- **Applies:** New domain types, subclasses, hierarchies, and enums — for each, ask what behavior here distinguishes it.
- **Unless:** Variants that genuinely carry different responsibilities, or a distinction that is a real trust or access boundary, earn their place; keep a general role only when several concrete cases actually share responsibilities.
- **Source:** Ch. 1 (domain objects); Ch. 3 (looking for common ground); Ch. 4

### 14.5 Hold names to the role they promise
- **Why:** Names shape what responsibilities an object accumulates: a record-style name condemns an object to passivity where a role-style name can grow; a name tied to an early phase lies later; two meanings for one name confuse every reader; names should not leak implementation.
- **Applies:** New public types, roles, and interfaces; renames; a diff whose code no longer matches what the class name promises.
- **Unless:** Not a style tool for locals and private helpers; do not demand ever-longer names — salient facts only, and domain-standard abbreviations are fine.
- **Source:** Ch. 3 (What's in a Name?)

### 14.6 Decide trust per boundary: validate once at the region's edge
- **Why:** Co-designed neighbors may trust each other; paranoid checking everywhere multiplies the places a rule must change, costs performance, and can itself introduce bugs. At boundaries that must be reliable, an explicit contract — preconditions obligating the client, postconditions obligating the provider — replaces symmetric defensive checking.
- **Applies:** Diffs adding input checks, null guards, or revalidation of already-validated data; API surfaces between subsystems; integrations with external or vendor code.
- **Unless:** Genuine trust boundaries (untrusted input, plugins, cross-process callers) keep their defenses; widening a trust region or removing an edge check needs explicit justification, because violated trust fails badly.
- **Source:** Ch. 4 (don't overlap responsibilities); Ch. 5 (trust among collaborators); Ch. 8 (trust regions, formal contracts)

### 14.7 Treat exception handling as designed policy, not scattered reflex
- **Why:** Reacting to expected-but-abnormal situations is a design activity on par with assigning responsibilities: distinguish exceptions (recoverable, must be handled) from errors, route each raise to a handler positioned to decide — logging alone is not handling — and recast exceptions crossing an abstraction boundary into the higher level's terms.
- **Applies:** Any diff adding catch blocks, retries, new thrown types, or error paths; walk the partial-completion scenario and confirm intermediates release what they acquired.
- **Unless:** Balking — honestly reporting failure to the requester — is legitimate; do not demand recovery in every frame (cleanup yes, deciding no) or a wide exception hierarchy — separate classes only where handlers genuinely diverge.
- **Source:** Ch. 2 (designing for reliability); Ch. 5 (reliable collaborations); Ch. 8

### 14.8 Scale rigor to the consequences of failure, and name what you fudge
- **Why:** Criticality grades from loss of comfort to loss of life, and both under- and over-hardening are defects; hardening one object while its collaborators stay brittle improves nothing. Every method under-attends to something — fatal only when the neglected concern is load-bearing and the omission is silent.
- **Applies:** Changes touching error handling, retries, recovery, or robustness; changes that skip validation, error paths, or concurrency handling with no acknowledgment.
- **Unless:** Unattended services, glue code, and consumer-facing paths warrant reliability work even at low apparent stakes; omitting a concern the project truly does not need is fine when it is named.
- **Source:** Ch. 8 (consequences of failure, increasing reliability); final chapter (fudging)

### 14.9 Keep neighborhoods private: one narrow entry, coarse cross-town requests
- **Why:** Exposing a subsystem's members defeats the goal of containable change; distant collaboration must be packaged into few meaningful requests, since a client forced through a chatty setter-getter sequence is carrying knowledge the provider should own. Digging through an object's parts couples the client to structure that will change.
- **Applies:** New exports from a package, a second public path into a subsystem, call sequences that configure a collaborator before one real operation, and multi-hop navigation into another component's structure.
- **Unless:** Inside a co-designed neighborhood, fine-grained chatter is normal — do not force ceremony onto local helpers; Demeter is a guideline, not a law, and deliberately public structure may be navigated. The entry point stays a delegating facade, never a decision-making controller.
- **Source:** Ch. 5 (collaboration options, facade, Law of Demeter case study)

### 14.10 Accept flexibility only for named, planned variations
- **Why:** Flexibility is never free — extra code on both sides of a configurable interface, learning curve, extension conventions ("flexibility disease") — and it is only one design option, rarely the actual requirement. The process is hot spots first, mechanisms second.
- **Applies:** Diffs introducing interfaces, strategy hooks, config options, plugin points, or generalized abstractions — ask for the concrete required variations behind each.
- **Unless:** Where requirements name configurability or the environment has a history of change, well-placed flexion points preserve integrity; the failure mode there is unplanned hacks, not planned hooks.
- **Source:** Ch. 9 (degrees of flexibility); final chapter (hot spots and planned variations)

### 14.11 Prefer the codebase's established solution over an equally good novel one
- **Why:** A design's quality is largely its predictability: one problem solved one way should be solved the same way elsewhere, because repeated collaboration patterns are what make a large system comprehensible. A working but alien solution adds a second way of doing the same thing.
- **Applies:** Any change solving a problem the codebase already solves — error handling, dispatch, resource management, layering direction.
- **Unless:** Consistency with a bad pattern entrenches it; deliberate, argued divergence is fine — silent divergence is not.
- **Source:** Ch. 2 (predictable, consistent, comprehensible design)

## Review heuristics

- For each touched class, state its role in one sentence; if the diff's additions do not fit that sentence, they belong somewhere else.
- Where a caller reads several fields of another object and computes a result, ask why the owner cannot answer the question itself.
- Trace every new raise to a handler that actually decides or recovers, and check that each intermediate step releases what it acquired; catch-log-continue is a finding.
- For each added check, name the trust boundary it guards; the same check on both sides of one collaboration means picking a single owner.
- For each new interface, hook, or config knob, ask for the existing or explicitly planned variations that justify it; none named means it comes out.
- Before accepting a novel approach, check how the codebase already solves this class of problem and require either conformance or an argued reason to diverge.
