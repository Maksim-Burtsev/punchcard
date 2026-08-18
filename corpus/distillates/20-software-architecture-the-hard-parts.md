# 20. Software Architecture: The Hard Parts — Neal Ford, Mark Richards, Pramod Sadalage, Zhamak Dehghani

> There are no best practices in architecture, only the least bad combination of competing forces for one organization at one moment. This book's contribution to review is a vocabulary for the hard parts nobody can copy from a blog post: how far apart to break things, who owns which data, and what a split actually costs once the network is in the middle. A change that presents only upsides has not been analyzed; a change that claims independence while sharing a database, a schema, or a synchronous call has not achieved it. And a structural rule that only lives in a reviewer's head is a rule the codebase will break before the next review.

## Principles

### 20.1 Judge a structural change by the trade-off it accepts, not by the pattern it names
- **Why:** The aim is the least bad option under this system's constraints, so a decision defended only by benefits — or by "everyone does X" — is an unexamined decision. Comparisons must be like-for-like and grounded in the actual context, which usually eliminates most options outright.
- **Applies:** Consequential, hard-to-reverse structure: a new service boundary, a shared datastore, a broker, a synchronous hop across a boundary, any new coupling point.
- **Unless:** Routine feature and bugfix diffs do not owe a trade-off essay, and a decision already made in context with its consequences recorded should not be relitigated on every read.
- **Source:** Ch. 1 (no best practices) and Ch. 15 (build your own trade-off analysis)

### 20.2 Turn a structural rule you would otherwise repeat in reviews into a check the build runs
- **Why:** Principles that live only in a diagram or a reviewer's memory erode: imports go where they please, layer directions get bypassed, components quietly swell — and review catches it days later, after the damage is committed. An automated check makes structural rules that are important but never urgent unskippable, at no per-commit cost to anyone. The scoping question is simple: if verifying the rule needs no domain knowledge, it belongs in an architecture check rather than a unit test. And a characteristic no machine can compare against a number is too vaguely defined to govern — decompose it into ones that can be measured.
- **Applies:** Any review where the same structural objection has come up before, and any diff that introduces or leans on a boundary rule: allowed dependency directions, component size or dependency ceilings, latency and startup budgets, cycle-freedom.
- **Unless:** A check needs an objective threshold and an owner; an unowned failing check gets deleted or muted within a month. Characteristics interact, so a set of single-concern checks can all pass while the combination regresses — security tightening that guts performance passes both individually. Some judgments, such as what counts as shared domain logic, stay manual on purpose.
- **Source:** Ch. 1, architecture governance and fitness functions; applied throughout, densely in Ch. 5

### 20.3 Treat any shared operational dependency as proof the services are one deployable unit
- **Why:** A quantum is independent deployability plus static coupling: services that all bootstrap through one database, broker, orchestrator, or tightly coupled UI cannot be deployed, scaled, or given different characteristics independently, whatever the diagram claims.
- **Applies:** Changes that add or extend a shared resource, or that describe a new component as an independent service.
- **Unless:** Sharing a database is a legitimate deliberate choice when the team accepts the single-quantum consequence; the defect is claiming independence you do not have.
- **Source:** Ch. 2, architecture quantum and static coupling

### 20.4 Read a new cross-service call on three axes at once, and flag the default corner
- **Why:** Communication (sync/async), consistency (atomic/eventual), and coordination (orchestrated/choreographed) are chosen together whether or not anyone noticed; picking one axis silently fixes the others, and the synchronous-atomic-orchestrated corner is the most expensive place to live.
- **Applies:** Any change introducing or altering inter-service communication or a distributed workflow.
- **Unless:** High coupling is sometimes the right purchase — transactional integrity really is easier with synchronous mediated calls. The question is whether the position was chosen.
- **Source:** Ch. 2, dynamic quantum coupling

### 20.5 Fix the component structure inside the monolith before extracting anything out of it
- **Why:** Services are built out of components, so an extraction inherits whatever internal structure it starts from — carving pieces off an unstructured codebase just adds a network to the mud. Two questions come first: is this codebase decomposable at all, judged by incoming and outgoing coupling, the balance of abstract to concrete, and how far components sit from the ideal line between the two; and if so, does it have recognizable components to refine and extract, or none, in which case you replicate the whole thing and chip pieces away instead. Components then have measurable smells worth naming in a diff: one holding more than roughly a tenth of the codebase's statements, or standing several standard deviations off the mean size; source files stranded in a namespace that also has children below it; the same trailing namespace segment repeated across unrelated components, hinting at duplicated domain logic; a component whose incoming plus outgoing dependencies pass the ceiling the team agreed on.
- **Applies:** Migration plans, any new service extracted from an existing codebase, and ordinary diffs that grow an already-large component or drop code into a non-leaf namespace.
- **Unless:** Statement counts are a proxy, not truth — a large component with no genuine sub-domains inside it should stay whole rather than be split on the metric alone. Repeated trailing names are often coincidence (validation, calculation helpers) and want an exclusion list, not a refactor. Every threshold here is a per-application choice, not a universal constant.
- **Source:** Ch. 4, is the codebase decomposable and which approach; Ch. 5, component-based decomposition patterns

### 20.6 Make the reason for a split a named driver, and weigh the forces pulling the other way in the same change
- **Why:** Size in lines or classes says nothing about whether something should be its own unit. Legitimate drivers — unrelated responsibilities, volatile code, differing scale, fault isolation, restricted access, known coming variants — each carry a payoff you can check afterward, and if the remainder can only be called "other" or "non-X", the cut went across cohesion instead of along it. The opposing forces then decide whether the split survives: transitive synchronous dependencies mean one part going down takes the others with it, every hop adds network and security latency to the user's wait, and parts that must be tested, released, or scaled together are a distributed monolith paying distribution costs for nothing.
- **Applies:** Any change carving new deployable units, modules, or packages out of an existing one; and any change adding a call from one service into another inside a single business transaction, or turning an existing asynchronous hop synchronous. Especially a remote fetch replacing a local join on a hot path.
- **Unless:** Extensibility is the weakest driver — use it only when further variants are genuinely known to be coming, and a domain term can sound awkward to outsiders while still being precise, so treat the naming test as a prompt to re-examine rather than proof. Some workflows genuinely need a blocking answer, background flows where nobody waits tolerate far more chatter, and asynchronous communication breaks the availability chain, so messaging-based splits are not condemned here.
- **Source:** Ch. 7, granularity disintegrators and integrators; Ch. 3, testability, deployability, availability; Ch. 10

### 20.7 Give every table exactly one writing service, and route all other access through that service
- **Why:** Writes define ownership. A second writer means nobody can change the schema safely and nobody is accountable for integrity rules; a direct cross-schema read re-couples a service to a schema it does not control, so a rename silently breaks callers nobody remembers. Named resolutions exist: split the table, appoint a delegate owner, pass the data on a message the workflow already sends, consolidate the services, or declare a shared data domain and accept its cost.
- **Applies:** New writes into a table the component did not own, cross-schema joins, synonyms, report queries against foreign tables, ORM mappings outside the module.
- **Unless:** Not a defect inside a single bounded context, where joins and foreign keys should stay. Synonyms are fine as temporary migration scaffolding, common-ownership tables (audit, event log) deserve one dedicated owner fed asynchronously, and an explicitly agreed shared data domain is a design, not a violation.
- **Source:** Ch. 6, step 3 (don't reach into other databases); Ch. 9, assigning data ownership

### 20.8 Shape a published contract independently of the storage schema, and carry only what the consumer needs
- **Why:** An abstracting contract is what makes a bounded context worth having: the owner renames a column and adapts internally while consumers keep compiling. A contract that mirrors the table — or one padded with fields "for later" — breaks consumers over data they never read, and the split bought nothing.
- **Applies:** New or changed APIs, events, and DTOs from a data-owning service, especially payloads auto-generated from entity classes.
- **Unless:** No gratuitous renaming for novelty's sake; internal single-team code, or a service whose data model is genuinely the published domain model, may keep names aligned. Large structures are legitimate for industry-standard documents or for carrying workflow state through a choreographed flow.
- **Source:** Ch. 6, change control; Ch. 13, contracts and stamp coupling

### 20.9 When one committed unit of work becomes writes in several services, require the failure story in the same change
- **Why:** Across service boundaries atomicity and isolation are gone: partial data becomes visible and actionable immediately, compensating updates can themselves fail, and other services may already have acted on what the compensation tries to undo. Prefer background state management and retry, which answers the caller fast, over making a user wait on a rollback they do not care about.
- **Applies:** Diffs that break an existing transactional operation apart, add a second service's write to a business request, or introduce compensating updates and rollback chains.
- **Unless:** Do not demand strict consistency the business does not need. But eventual consistency has a tolerance limit, and every deferred error needs a retry path and a human escalation, not just a log line.
- **Source:** Ch. 12, transactional sagas and state management; Ch. 9, ACID versus BASE

### 20.10 Name the owner of workflow state, and add a mediator once the error paths multiply
- **Why:** Transient state — what ran, what failed, what is retrying — always exists. Unowned, either a domain service quietly becomes a front controller or every status query fans out to rebuild a snapshot. Choreographed happy paths look simple, but each error branch adds links the normal path never needed and pushes workflow knowledge into services that should know only their own domain.
- **Applies:** New multi-step processes, and changes adding a failure branch, cancellation, retry, or reassignment to an existing one.
- **Unless:** An orchestrator is itself a coupling point, bottleneck, and single point of failure; for linear fire-and-forget flows with rare errors, choreography scales better and a mediator is over-building. State can also ride in the message at the cost of fatter contracts.
- **Source:** Ch. 11, orchestration versus choreography and workflow state management

### 20.11 Judge reuse by how fast the shared thing changes, not by how neatly it abstracts
- **Why:** Abstraction only identifies candidates; low rate of change is what makes them safe to depend on. Shared domain logic that changes often forces every consumer to retest and redeploy together — the exact coordination cost the split was meant to avoid — and a canonical service for a volatile core entity must satisfy everyone at once. So: version shared libraries, pin explicit versions instead of tracking the newest build, keep libraries functionally partitioned, and when the shared portion is large or volatile, ask whether these are really one service.
- **Applies:** New or growing shared libraries carrying domain rules; proposals to unify duplicated concepts into one canonical service; dependency declarations in multi-service builds.
- **Unless:** Cross-cutting infrastructure — logging, metrics, auth, discovery — belongs in a library or sidecar and is never a reason to merge services. A runtime shared service is right for polyglot estates or fast-changing behavior, accepting its latency, scaling, and availability costs. And very fine library granularity turns the dependency graph into the new problem.
- **Source:** Ch. 8, code reuse, shared library versioning, and shared service

### 20.12 Feed analytics and reporting through a domain-owned asynchronous channel, never off the operational write path
- **Why:** Central pipelines that extract and reshape data strip away domain context, so schema changes break ingestion and only domain experts could have spotted the privacy hazard in the combined result. Keeping the analytical side owned by the same team, coupled only asynchronously, preserves both the boundary and operational performance.
- **Applies:** Changes adding reporting extracts, analytics feeds, ML training exports, or dashboards over service-owned data.
- **Unless:** This assumes the organization can live with eventual consistency and carry the extra contract coordination; where analytical and operational views must agree at every instant, it does not apply.
- **Source:** Ch. 14, managing analytical data / data mesh

## Review heuristics

- Every new deployable unit or boundary in the diff: which named driver justifies it, and what does the change give up in return? Only-upside justifications are unfinished.
- Before applauding an extraction, look at the component it came from: what share of the codebase does it hold, does it have code sitting outside its leaf namespaces, and how many other components does it reach into or get reached from?
- Ask of every structural objection you are about to write: could a script decide this? If yes, say so and name the check — an objection repeated across reviews is a fitness function nobody got around to writing. If the rule needs domain knowledge to verify, it is a test instead.
- Trace each new cross-service call: does the caller block? Does it need the callee to be up? Must the two now be released or scaled together? If any yes, the split is being undone.
- Grep the diff for SQL, ORM mappings, synonyms, or batch jobs touching a schema the changed component does not own — reads included.
- For any new payload, event, or DTO: is it a copy of the table, and does it carry fields no consumer reads today?
- Where a business operation now spans two services, find the compensation and escalation path in the same diff; if it is absent, the change ships partial data with no cleanup.
- For every new shared library or canonical service holding domain logic: how often does it change, and are consumers pinned to versions or floating on the latest build?
