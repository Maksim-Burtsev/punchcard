# 19. Fundamentals of Software Architecture — Mark Richards & Neal Ford

> Architecture is the set of decisions that are expensive to reverse, and every one of them is a trade-off — a design presented as a pure win simply has an undiscovered cost. The book gives a reviewer vocabulary rather than rules: connascence for coupling strength, the architecture quantum for what really deploys together, the fallacies of distributed computing for what a network call actually costs, and fitness functions for turning an architectural rule into something the build can enforce. It insists that *why* outlives *how*, so unrecorded reasoning is itself a defect. And it is relentlessly anti-absolutist: its third law holds that architecture decisions are rarely binary and instead sit on a spectrum between extremes, characteristics must be few and prioritized, granularity is a dial with failure modes at both ends, and metrics are blunt instruments that raise questions rather than settle them.

## Principles

### 19.1 Refuse a justification that lists only upsides — make the author name the cost and who pays it
- **Why:** The First Law says everything in architecture is a trade-off; its corollary says an option with no visible downside means the downside has not been found yet. Approving on stated benefits alone defers the cost to production.
- **Applies:** Changes that pick between structural alternatives — sync vs async, shared library vs shared service, splitting or merging a component, adding a broker, cache, or layer.
- **Unless:** Local, cheaply reversed edits; and a tally of pluses and minuses is not a verdict — the criteria are unweighted until this system's context weights them (the Out of Context antipattern).
- **Source:** Ch. 1 Laws of Software Architecture; Ch. 2 Analyzing Trade-Offs; Ch. 27

### 19.2 Ask why the change is shaped this way, and require the answer to land somewhere durable
- **Why:** The Second Law puts *why* above *how*: a later maintainer can usually reconstruct how an unfamiliar structure works but never the context and the rejected alternatives. Without a record, teams relitigate settled questions or silently reverse a decision whose original driver still holds.
- **Applies:** Changes that establish a rule other code must follow — a new boundary, a communication style, a data-ownership shift, a dependency with lock-in, or a swap that carries a performance or security property.
- **Unless:** Not every commit needs a decision record; design choices inside a module are the developer's own. One authoritative place beats copies scattered across chats and emails.
- **Source:** Ch. 1; Ch. 21 Architectural Decisions; Ch. 27

### 19.3 Treat an either/or framing as the defect itself, and ask what lives between the two extremes
- **Why:** The Third Law, new in this edition, says most architecture decisions are not binary but sit on a spectrum between extremes — which is why the field's central distinctions (architecture versus design, orchestration versus choreography, topics versus queues) resist clean definitions: the criteria themselves are a messy range, not a switch. A proposal shaped as A-or-B has usually never examined the middle, and the middle is where the answer normally lands. The law also supplies a test for what deserves architectural attention: a decision is architectural when *every* option carries significant trade-offs.
- **Applies:** Any change argued as one thing versus another — sync versus async, shared library versus shared service, orchestrate versus choreograph, split versus keep, full payload versus key only, build versus buy — and any recommendation whose defence is that the alternative is obviously wrong.
- **Unless:** A few decisions really are binary (a vendor-fixed protocol, an on/off flag), and "it's a spectrum" is not permission to skip deciding — a middle position still has to name its point on the range and the trade-offs there, or it becomes Covering Your Assets. Where no option carries a significant trade-off, this is design, not architecture: pick one and move on.
- **Source:** Ch. 1 Laws of Software Architecture; Ch. 27 The Spectrum Between Extremes; Preface

### 19.4 Say plainly when a change widens the unit that must deploy, scale, and fail together
- **Why:** The architecture quantum is the yardstick: two services sharing a database, a schema, or an entity library are statically coupled into one deployable whether or not the diagram says so, and a blocking call across the boundary fuses their availability and scalability dynamically. The weaker side's characteristics become both sides' characteristics.
- **Applies:** A new table read by a second service, a shared entity JAR/DLL, a common schema pulled into another deployable, or a new request/response hop between separately deployed services.
- **Unless:** A monolith or modular monolith is one quantum by design — sharing a store there costs nothing extra. A few closely related services that are really one bounded context can legitimately share data; and request-reply messaging that still waits is not decoupling.
- **Source:** Ch. 7 Architectural Quanta, Static and Dynamic Coupling; Ch. 15; Ch. 18 Data Isolation

### 19.5 Name the kind of coupling introduced, and weaken it as the distance it spans grows
- **Why:** Connascence ranks coupling by how hard it is to refactor: name-based agreement is cheap because tooling fixes it everywhere, while agreement on meaning, position, timing, or a replicated algorithm breaks silently when one side moves. The same shared assumption is a mild smell inside a package and a cross-team outage across code bases.
- **Applies:** Magic values, positional parameter contracts, wire formats, client/server pairs that must compute matching results, setter sequences that only work in one order — especially when a second consumer appears or the logic crosses a boundary.
- **Unless:** Maximize connascence *inside* an encapsulation boundary — strong coupling within one small module is often clearer than the indirection that would weaken it. This is about weakening what crosses, not forbidding contracts or duplicating everything.
- **Source:** Ch. 3 Connascence and its properties; Ch. 7

### 19.6 Ask for the structural rule to be encoded as a check that fails the build, not policed by reviewers
- **Why:** Code review catches boundary erosion a week late, after casual auto-imports have done the damage. Fitness functions — cycle detection, allowed-layer assertions, dependency ceilings, latency budgets — are executable governance for things that are important but never urgent, and they turn a subjective boundary argument into a repeatable verdict.
- **Applies:** Newly declared or newly load-bearing invariants, and any structural violation this review just caught by hand for the second time.
- **Unless:** Do not impose checks the team cannot explain — they get disabled at the first red build. Metrics get gamed (coverage rules breed assertion-free tests), and some qualities resist automation entirely.
- **Source:** Ch. 6 Governance and Fitness Functions; Ch. 11; Ch. 26

### 19.7 Treat every new remote call as unreliable, slow, insecure, and invisible until proven otherwise
- **Why:** The fallacies of distributed computing are the book's checklist for distributed change: the network fails, latency is never zero (and the tail is what breaks a chain), bandwidth is finite so an oversized payload is stamp coupling at request-rate scale, each endpoint is its own trust boundary, and compensating updates are assumed to always succeed until they don't.
- **Applies:** Any diff that turns a local call into a remote one, adds a service hop, exposes an endpoint, or coordinates updates across services with a rollback path.
- **Unless:** None of it applies in-process — timeouts, correlation IDs, and circuit breakers around a method call are ceremony. Do not stack retries on non-idempotent operations, and an ACID transaction in one service needs no compensation logic.
- **Source:** Ch. 9 Fallacies of Distributed Computing #1–#11

### 19.8 Reject components named for entities, and apply the conjunction test to what the component now owns
- **Why:** A name built from an entity plus Manager/Handler/Processor describes nothing, so every piece of functionality touching that entity drifts into it — the Entity Trap produces anemic CRUD wrappers with no real cohesion. Write one sentence for what the component is responsible for after the change; if it needs "and" or a run of commas, the work belongs elsewhere.
- **Applies:** New top-level components, modules, namespaces, or directories, and existing ones a change is expanding — especially requirements that arrive attached to a workflow step rather than a component.
- **Unless:** Genuinely data-centric components (reporting, ETL, a pipeline filter) may legitimately track the data shape. Do not split just to lower a line count — each split adds a communication path — and do not chase perfect boundaries early.
- **Source:** Ch. 8 The Entity Trap; Analyzing Roles and Responsibilities

### 19.9 Challenge structure added for a capability nobody prioritized, and ask which capability it trades against
- **Why:** Every characteristic costs design, implementation, and maintenance, and they interact — hardening security usually costs performance — so the goal is the fewest characteristics that make the system succeed, not support for everything. Umbrella goals hide the same problem: "agility" decomposes into deployability, modularity, and testability, and optimizing the convenient constituent while claiming the goal is the named antipattern.
- **Applies:** Plug-in frameworks, extra indirection, configuration surfaces, and abstraction added for future flexibility; also any change whose benefit is an umbrella word rather than a number.
- **Unless:** Implicit needs — availability, security, data integrity — are real even when unwritten, so do not strike structure merely because no requirement names it. And do not demand every constituent be solved in one change; ask which parts remain open.
- **Source:** Ch. 4 Least Worst Architecture; Ch. 5 Limiting and Prioritizing Characteristics

### 19.10 Read granularity as a dial with failure modes at both ends
- **Why:** Grains of Sand is services split past usefulness, where a workflow becomes chatter; Swarm of Gnats is one business action exploded into per-attribute events nobody can follow. The same tension governs payloads: a fat event couples every consumer to fields it never reads, a key-only event sends them all back to the database and cannot say what changed, and for an update the workable payload is neither end but the middle — the fields that changed plus the prior values the store no longer holds. A cross-service transaction or pervasive compensation is usually the boundaries telling you they are wrong.
- **Applies:** Splitting or merging a service or component, adding event types to a flow, changing an event contract, or introducing a saga or distributed transaction.
- **Unless:** Coarse is correct when the pieces always deploy, scale, and fail together. There is no mechanical right payload — high-throughput paths legitimately carry full data, delete notifications legitimately carry a key — and a saga is right when two areas need different characteristics yet must stay consistent.
- **Source:** Ch. 15 Event Payload, Swarm of Gnats; Ch. 18 Granularity, Transactions and Sagas

### 19.11 Require an asynchronous path to say where failures go and where data can be lost
- **Why:** When work leaves the caller's thread there is no one left to receive the error: without a delegate that repairs, escalates, or queues for a human, the business process stalls silently while its siblings proceed. Data vanishes in three specific gaps — producer to broker, broker to a consumer that dies mid-work, consumer to its datastore — closed by durable queues, acknowledged sends, and acknowledging only after the commit.
- **Applies:** New queue consumers, background workers, fire-and-forget publication of work that must complete, and broker or producer configuration changes on paths carrying data that must not be dropped.
- **Unless:** Each guarantee costs latency and throughput — disposable telemetry does not warrant the full set, and streaming brokers work differently. Repair-and-resubmit reorders messages, so it is wrong where ordering carries meaning.
- **Source:** Ch. 15 Error Handling (Workflow Event pattern); Preventing Data Loss

### 19.12 Scale scrutiny to how expensive the change is to undo, not to how many lines it touches
- **Why:** Architecture and design are the two ends of one spectrum, and most decisions land somewhere between them; what positions a change is its strategic reach, the effort to change or build it, and how significant its trade-offs are. A three-line change to a data-ownership boundary or a transport protocol sits far toward the architecture end; a large but reversible refactor inside one module sits at the design end and needs none of the ceremony.
- **Applies:** Triaging which parts of a diff deserve deep argument, wider consensus, or a recorded decision — and rating risk as impact times likelihood, with technology the team does not know pinned at the top.
- **Unless:** Reversibility is not a reason to wave through small irreversible-looking edits, and high impact with genuinely low likelihood is not a blocker. Deferring a reversible decision until information arrives is sound; deferring with no plan to decide is Covering Your Assets.
- **Source:** Ch. 2 Architecture Versus Design; Ch. 22 Analyzing Architecture Risk; Ch. 21 antipatterns

## Review heuristics

- For each structural choice in the diff, write the cost next to the benefit; if the cost line is empty, keep reading rather than approve.
- Trace every new dependency edge and ask how far it travels — same class, same module, same deployable, or across the network — and demand the coupling weaken with each boundary it crosses.
- Grep the diff for what merges two deployables into one: a shared table, a shared entity library, a common schema, or a new blocking call between services.
- Count remote calls added, and for each one check the timeout, the failure path, the payload's unread fields, and whether the endpoint authenticates.
- Say in one sentence what each touched component is responsible for now; "and" in that sentence, or an entity-plus-role name, is the finding.
- When a proposal offers exactly two options, make the framing the finding: ask what sits between them, and which point on that range this change is actually choosing.
- When the review enforces a structural rule by hand, ask what automated check would have caught it — and treat a bad metric reading as a question for the author, never a verdict.
