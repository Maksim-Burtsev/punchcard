# 16. Patterns of Enterprise Application Architecture — Martin Fowler

> Fowler sees enterprise software as a small set of recurring structural decisions — how layers depend on each other, where domain logic lives, how objects meet relational tables, what crosses a process boundary — each with named alternatives and explicit trade-offs. The reviewer's job is not to enforce one pattern but to check that the chosen pattern matches this system's actual complexity, and that expensive one-way doors (distribution, concurrency schemes, serialized blobs) are walked through deliberately. Complexity is a cost paid forever; the most valuable architectural move is making a big problem small.

## Principles

### 16.1 Keep layer dependencies one-way: presentation may know the domain, but domain and data-source code must know nothing about UI, HTTP, or rendering
- **Why:** The litmus test is adding a radically different front end — if that would duplicate logic, business rules have leaked into presentation. Reverse dependencies destroy testability, front-end swapping, and independent evolution.
- **Applies:** Diffs adding imports, callbacks, or parameter types from business/persistence modules into controllers, views, view models, or request/response types; business conditionals appearing in templates or handlers.
- **Unless:** Purely presentational decisions (formatting, layout, colors) belong in the view, and trivially simple systems with no real domain behavior gain little from the ceremony.
- **Source:** Chapter 1 (Layering); Model View Controller

### 16.2 Treat the domain-logic style as a three-way choice — transaction script, table module, or domain model — decided by the complexity of the rules and by the data structure the platform's tools are built around
- **Why:** This is the book's central decision. Procedural scripts are cheapest for simple logic but decay into copied, drifting conditionals; a domain model absorbs new cases by adding objects, at the price of learning curve and mapping. The table module sits between them — one class per table (or view) operating over a shared record set, with enough structure to find and remove duplication but without inheritance, polymorphism, or per-instance relationships. Its worth hinges almost entirely on whether the environment supplies a common record-set structure that the UI widgets and data-access tools already speak; where it does, Fowler makes it the default and finds essentially no remaining role for transaction scripts. Growing duplication across handlers is the signal to move up this scale, and the move is cheapest made early.
- **Applies:** New services or modules where the logic style is being set; diffs that copy a rule or validation into a second handler, or add yet another branch to per-use-case procedures; table-oriented domain classes being judged as if they were unrefactored scripts, or table-module code reaching for inheritance and strategies it cannot support.
- **Unless:** All three can legitimately coexist in one system; do not demand a rich object model for CRUD-ish logic, whose mapping and learning costs are not repaid there; and where no shared record-set structure exists in the platform, a table module is not worth adopting. The available tooling shapes this decision as much as the rules do — architecture often has to match the tools rather than the reverse.
- **Source:** Chapters 2, 8, and 9 (Transaction Script, Table Module, Domain Model, Record Set, Service Layer)

### 16.3 Keep the domain layer free of framework, container, and persistence machinery so it builds and tests as plain objects
- **Why:** Business behavior changes most often, so it must be the easiest code to change and test; framework types leaking in force every test through a container or database and make developers reason about two worlds at once.
- **Applies:** New imports of ORM, web, messaging, or container types into domain classes; domain tests that suddenly require a running database; email or messaging calls inside entities.
- **Unless:** Thin adapters and mappers at the edge legitimately depend on infrastructure — the rule protects the domain objects, not the layer that plugs them in.
- **Source:** Chapter 9 (Domain Model, Service Layer)

### 16.4 Confine SQL and persistence mechanics to a dedicated gateway or mapper layer, and pick the mapping pattern by how far the object model diverges from the schema
- **Why:** Embedded database code ties tests to a live database and hides queries from whoever tunes the schema. Table-mirroring records are fine while object and schema stay isomorphic; once they must evolve independently, only a mapper keeps each side ignorant of the other.
- **Applies:** Inline SQL or connection handling in domain or controller code; inheritance, strategies, or rich associations bolted onto classes that directly mirror tables; a second competing persistence style introduced for the same objects.
- **Unless:** One isolation layer is the target, not several — a gateway plus a mapper over the same tables is one representation too many; and full mapping frameworks should be bought, not hand-built.
- **Source:** Chapters 3 and 10 (Data Source Architectural Patterns, Active Record, Data Mapper)

### 16.5 Never issue repeated per-row queries where one query would do, and make lazy loading a deliberate choice, not a default
- **Why:** Call latency dominates, so one over-fetching query usually beats fifty precise ones; misapplied lazy loading produces ripple loading — many small queries — while blanket eager loading drags unbounded object graphs into memory.
- **Applies:** Loops issuing queries or remote calls per iteration; new lazy proxies or deferred collections; loads pulling whole graphs a screen never uses.
- **Unless:** Fields in the same row are essentially free — defer nothing there; expensive, rarely-touched associations are exactly where lazy loading pays.
- **Source:** Chapters 3 and 11 (Reading in Data, Lazy Load)

### 16.6 Reject performance-motivated complexity that arrives without measurement — except the few structural decisions that cannot be fixed later
- **Why:** Fowler reports designs repeatedly accepted or rejected on performance grounds that proved bogus once measured, and a configuration change can invalidate old numbers. But chatty remote interfaces and similar structural choices resist later optimization, so those rules need no re-proving per diff.
- **Applies:** Caches, denormalization, hand-rolled pooling, joins and prefetch machinery, or logic moved into stored procedures — anything justified by speed without profiling evidence from the real configuration.
- **Unless:** A demonstrated hot spot (a measured N+1, a profiled slow query) is exactly when the complex version is warranted; do not block it there.
- **Source:** Introduction (Thinking About Performance); Chapter 8 (Stored Procedures)

### 16.7 Do not distribute the parts of one application; where a process boundary is unavoidable, cross it with a coarse-grained facade carrying bulk data, holding no logic of its own
- **Why:** Inter-process calls are orders of magnitude slower than local ones, and remoteness forces awkward interfaces that hurt the design even after the performance is paid for. The litmus test: the application must run locally with the facades removed and no code copied.
- **Applies:** Changes that carve a component into a separately deployed service, add RPC between formerly local modules, expose fine-grained per-field remote calls, or put validation and workflow inside an API facade.
- **Unless:** Some boundaries are given (client/server, app/database, genuine integration between separate applications) — there the demand is the coarse-grained facade, not avoidance; and in-process designs should stay fine-grained, never coarsened for imagined future distribution.
- **Source:** Chapter 7 (Distribution Strategies); Remote Facade; Data Transfer Object

### 16.8 When a business transaction spans multiple requests, require explicit offline concurrency control: optimistic version checks by default, with the check covering what was read, not just what was written
- **Why:** System transactions cannot protect a multi-request edit, so without explicit control the code silently permits lost updates. Version numbers beat timestamps because clocks drift; and a result computed from a record the transaction never wrote can still commit stale, wrong data.
- **Applies:** Edit-then-save flows, wizards, long-running operations; review of version columns, update criteria, and whether the marker covers the data whose consistency actually matters; locking steps hand-coded per call site instead of centralized in shared code.
- **Unless:** Work fitting inside one system transaction needs none of this — let the transaction manager do its job; and pessimistic locks are right where conflicts are likely or losing an hour of user work is unacceptable.
- **Source:** Chapters 5 and 16 (Concurrency, Optimistic/Pessimistic Offline Lock, Implicit Lock)

### 16.9 Keep servers stateless where possible; when session state is unavoidable, place it deliberately and treat anything returned by the client as untrusted
- **Why:** Statelessness lets a few servers serve many idle users, and each placement fails differently: client state rides every request and is tamperable, server state dies with the process, database state must be fenced from committed record data.
- **Applies:** Changes adding per-session server memory, growing cookies or hidden fields, writing in-progress work into ordinary tables, or deriving authorization and pricing from round-tripped values without revalidation.
- **Unless:** Carts and multi-step edits are inherently stateful — reject unexamined placement, not state itself; a cache that can be lost without breaking correctness is not session state.
- **Source:** Chapters 6 and 17 (Session State, Client Session State)

### 16.10 Coordinate a business transaction's writes in one place that tracks changes and commits them together, and never let the same row load into two in-memory objects in a session
- **Why:** Saves scattered mid-flow cause chatty traffic, forgotten writes, and ad-hoc ordering; a single coordinator with a fixed write order also reduces deadlocks. Two objects for one record silently overwrite each other's updates.
- **Applies:** Diffs where callers save at multiple points, hand-manage write ordering, fire messages before the owning transaction commits, or add new load paths and caches for mutable persistent objects.
- **Unless:** Work fitting in one short transaction with a handful of objects needs no unit-of-work machinery; immutable values need no identity map, and the map must stay session-scoped, never shared across threads.
- **Source:** Chapter 11 (Unit of Work, Identity Map)

### 16.11 Build data-access and mapping infrastructure minimally: cover current needs, prefer an existing tool to a hand-rolled framework, and treat families of near-identical hand-written mappers as a design smell
- **Why:** It costs no more to extend a minimal query object later than to build a general one now; repetitive per-field mapping code multiplies maintenance cost, which is why serious mapping layers are metadata-driven and bought rather than built.
- **Applies:** PRs adding ORM-like layers, criteria builders, reflection- or config-driven dispatch; another near-identical mapper or serializer joining an existing family of them.
- **Unless:** A handful of simple explicit mappings is clearer than a reflection framework — do not demand metadata machinery for two or three cases; special cases belong in code, not in ever-richer metadata.
- **Source:** Chapter 3 (Using Metadata); Query Object; Repository

### 16.12 Decide where screen-flow logic lives by who drives the sequence: machine-controlled navigation belongs in a dedicated application controller, user-controlled browsing needs none
- **Why:** Screen ordering is a placement decision separate from both domain rules and view rendering. When definite rules govern which page follows which, and which view a given object state deserves, scattering that logic across input controllers means one flow change edits many files. Concentrating it — ideally with no dependency on the UI machinery, so it can be tested without a request and reused across front ends — keeps the sequencing in one place. Where a user may reach any screen in any order, the extra layer buys nothing.
- **Applies:** Diffs that put next-screen decisions, wizard step ordering, or state-dependent view selection inside handlers, templates, or domain objects; a single flow change touching several controllers; a flow layer that reads HTTP session data or forwards directly; genuine business rules migrating into flow decisions.
- **Unless:** A handful of request-specific conditionals in the flow layer is tolerable — only when they multiply should the domain model be reshaped to drive them; and simple browse-anywhere applications should not be asked for this layer at all. Different front ends often deserve different flows, so shared reuse is a convenience, not a requirement.
- **Source:** Chapters 4 and 14 (Application Controller, Model View Controller, Front Controller)

## Review heuristics

- Trace every new import crossing a layer boundary: anything in domain or data-source code that names a UI, request, framework, or wire-format type is a finding.
- Ask the second-front-end question of any logic in a template, controller, or API facade: would a CLI next to this web app have to duplicate it?
- Look inside every loop for a query, remote call, or per-row save — and ask where the resulting rows' objects live if the same key loads twice.
- For any multi-request edit flow, find the version check: is it a number (not a timestamp), does it run in the committing transaction, and does it cover what was read?
- When a diff's justification is performance or future scale, ask for the measurement; when the diff adds a process boundary, ask why the parts cannot stay in one process.
- Before calling table-oriented domain code an unrefactored script, check the platform: where the tools revolve around a shared record set, one class per table is a deliberate middle ground, not a missing domain model.
- When a diff decides which screen or view comes next, ask who controls the sequence; if the machine does and the decision appears in more than one handler, the flow logic wants a single home.
- On a third near-identical mapper, handler branch, or null check, flag the family, not the instance: duplication under change is the book's universal refactor signal.
