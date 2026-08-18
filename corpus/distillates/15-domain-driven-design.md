# 15. Domain-Driven Design — Eric Evans

> Code is the most durable carrier of a team's understanding of the business, so a diff is never just a technical event: it either sharpens the shared model or quietly corrupts it. The reviewer's job is to check that business knowledge lives in explicitly named domain objects, that the code literally mirrors the vocabulary experts use, and that consistency and translation boundaries — aggregates and bounded contexts — are declared rather than implied. Complexity that keeps re-accumulating in one spot is not bad luck; it is a missing concept asking to be named.

## Principles

### 15.1 Require code names to match the language the team and domain experts actually speak
- **Why:** Translation between developer dialect and domain dialect is always lossy; it hides conceptual rifts between modules and produces software that does not fit the business. When model and code drift apart, the fix is renaming and restructuring the code, not a mapping people carry in their heads.
- **Applies:** Any diff introducing or renaming classes, methods, modules, or fields that represent domain concepts, and any diff where the same idea now has one name in discussion and another in code.
- **Unless:** Purely technical identifiers (infrastructure, framework glue) live outside the domain language, and the same term may legitimately mean different things across bounded contexts.
- **Source:** Ch. 2 (Ubiquitous Language), Ch. 3 (Model-Driven Design)

### 15.2 Keep business rules in named domain objects, out of controllers, scripts, and UI
- **Why:** A policy hidden as a guard clause in an application method cannot be verified by experts, found by future readers, or reused; the application layer should coordinate and delegate, never decide. Superficial UI or plumbing edits must not be able to silently change business behavior.
- **Applies:** Diffs adding validation, limits, pricing, eligibility, or policy logic to services, controllers, handlers, batch jobs, or UI code in a system complex enough to justify a domain layer; SQL or widget calls appearing inside domain classes.
- **Unless:** Simple data-entry apps with few rules may deliberately skip layering — but as an all-or-nothing choice for the whole app, not a per-diff exception. Task-progress and session state legitimately belong to the application layer.
- **Source:** Ch. 4 (Layered Architecture, Smart UI), Ch. 9 (Specification)

### 15.3 Enforce aggregate boundaries: one root per consistency cluster, invariants held at commit
- **Why:** The root can only guarantee invariants if it mediates all access; a retained reference to an interior object lets callers blind-side the checks, and undeclared consistency boundaries force a choice between silently broken rules under concurrency and unusable over-broad locking.
- **Applies:** Changes touching persistence, transactions, or multi-object invariants: ask which aggregate owns the rule and whether the commit enforces it. Flag queries for non-root objects, lasting references to interiors, and deletion that leaves part of a cluster behind.
- **Unless:** Rules spanning aggregates should be eventually consistent via explicit mechanisms, not crammed into one transaction; transient inconsistency mid-operation is expected; value-object copies may be handed out freely.
- **Source:** Ch. 6 (Aggregates, Purchase Order Integrity)

### 15.4 Make every domain type commit to being an entity, a value, or a stateless service, and push heavy math into immutable values
- **Why:** Mistaken identity corrupts data, and gratuitous identity adds tracking machinery for distinctions nobody needs. An immutable value's operations are pure functions — replaceable, composable, testable in isolation — which is where the book puts its most intricate calculations. But some domain operations are activities, not things: cramming one into an entity or value either warps that object's definition or breeds meaningless "doer" objects, so a standalone operation is a legitimate third answer, not a modelling failure.
- **Applies:** New domain types, ID generation, equality logic, deduplication; computation-heavy branches added to long-lived stateful objects; money, quantity, and measurement math; methods that mutate their arguments; operations that coordinate several objects and fit none of them.
- **Unless:** Identity is contextual — judge against this application's needs, not the real world. Objects with a genuine lifecycle stay mutable entities; do not shred the model into primitive-obsessed micro-values. An operation with no natural owner belongs in a domain service named for the activity in the team's own vocabulary — the book's example is transferring funds between accounts — provided it carries real domain meaning, takes and returns model types rather than primitives or foreign structures, keeps no state of its own across calls, and does not become a habit that drains the surrounding entities and values of their behavior.
- **Source:** Ch. 5 (Entities, Value Objects, Services), Ch. 10 (Side-Effect-Free Functions)

### 15.5 Treat recurring special cases and awkward contracts as a missing concept; name it instead of patching again
- **Why:** Complexity that keeps re-accumulating in the same spot is usually a concept present only implicitly — in naming conventions, string matching, or the team's speech. Making it an explicit object collapses the special-case code and lets rules grow without swamping their host.
- **Applies:** Diffs adding another branch to an already-branchy method, a fourth compensating patch to the same area, boolean flags, convention-based inference, or scripts silently accreting business rules; vocabulary the team uses but the code lacks.
- **Unless:** A genuine one-off script is fine; not every noun deserves an object; a large remodel is a costed decision, not an automatic review demand — and some weird rules are real requirements, so verify with domain intent first.
- **Source:** Ch. 3, Ch. 8-10 (Making Implicit Concepts Explicit)

### 15.6 Forbid model reuse across context boundaries; demand narrow, tested translation layers instead
- **Why:** Stretching one class over two contexts' meanings produces false cognates, corrupt data, and teams stepping on each other. Concentrating translation in one small boundary object keeps both models clean, and the contact point is precisely where tests pay off most.
- **Applies:** Diffs patching extra fields onto another context's class "because it almost fits", importing a foreign subsystem's internal types, scattering format conversion through business code, or serializing internal entities directly onto wires and files other systems consume.
- **Unless:** Within one well-integrated context, unifying duplicates is exactly right; conforming wholesale to a dominant external model is a valid strategic choice; a full anticorruption layer for everything can bankrupt the project.
- **Source:** Ch. 14 (Bounded Context, Anticorruption Layer, Published Language)

### 15.7 Demand supple interfaces: names that state intent, queries split from commands, and every remaining command's effect stated and pinned
- **Why:** If a caller must read the implementation to use a component, encapsulation buys nothing; hidden side effects force tracing every delegation chain, and two implementations of one interface can differ in exactly the effects nobody wrote down. Splitting off pure functions is not enough — a residue of state-changing commands always remains, and what makes them safe is a stated post-condition plus class and aggregate invariants, written as automated tests wherever the language cannot express them. Intent-revealing names and stated effects are a pair; either alone leaves the caller guessing. Closed operations chain like arithmetic without growing the reader's mental load, and each nonessential dependency in a signature caps the complexity a developer can handle.
- **Applies:** New or renamed public APIs; methods that both mutate state and return domain data; a new or changed command whose effect on state is described nowhere and locked down by no test; delegation chains where the outer operation's guarantees were never restated; new calculation APIs on value types; diffs that widen signatures or thread new types through the most complex class in a module.
- **Unless:** Commands cannot be eliminated — do not block simple well-named mutators or demand ceremony for single-caller code; an effect that follows obviously from a coherent model needs no ceremonial restatement, and a genuinely surprising post-condition may be the real requirement rather than a bug; a fundamental association clarifies rather than burdens; do not fake decoupling by stripping interfaces to primitives.
- **Source:** Ch. 10 (Supple Design: Intention-Revealing Interfaces, Side-Effect-Free Functions, Assertions)

### 15.8 Spend design effort in proportion to distance from the core domain
- **Why:** The business value lives in a small distinctive core; when cleverness drains into infrastructure and generic subdomains, the mission-critical model degrades. Speculative flexibility and premature sophistication are the usual cover stories for that drain.
- **Applies:** Prioritizing review depth; questioning where sophistication lands; generic concerns (dates, money, auth glue) creeping into core modules or business terms leaking into utility packages; a simple obviously-correct implementation behind a stated contract beats a clever one.
- **Unless:** Supporting code still must work; a proprietary algorithm that is itself the differentiator belongs in the core even though it looks like mechanism; the naive version must still satisfy its stated contract, with known gaps documented at the interface.
- **Source:** Ch. 15 (Core Domain, Generic Subdomains), Ch. 10 intro

### 15.9 Review object lifecycle paths as domain design: atomic creation, identity-preserving reconstitution, repositories only for roots
- **Why:** A client that assembles an object graph must know its internals, and a half-constructed object escaping is a defect factory. Reloading is not creating — a fresh ID on hydration severs continuity, and balking at bad stored state is not an option. Client-built queries let rules migrate into query strings and punch through aggregate boundaries.
- **Applies:** Constructors and factories for multi-object structures (succeed completely or fail loudly); deserialization, ORM hydration, import, and migration code; new repositories or query paths; save helpers that hide commits — transaction scope belongs to the caller.
- **Unless:** Simple classes with trivial construction need no factory; new-object creation should still fail fast on broken invariants — leniency is only for data that already exists; specialized hard-coded queries alongside a generic mechanism are expected.
- **Source:** Ch. 6 (Factories, Reconstitution, Repositories)

## Review heuristics

- Read the diff's new names aloud next to the ticket or spec: any concept the business names that the code calls something else, or calls nothing at all?
- Grep the changed controllers, handlers, and jobs for `if` statements that decide business outcomes rather than orchestrate — each one is a rule that belongs in a named domain object.
- For every mutation of related objects, ask which aggregate root owns the invariant and whether anything outside the boundary holds a reference past this operation.
- When a diff adds another branch, flag, or compensating patch to a spot that has been patched before, ask what concept would make the branches collapse.
- Before demanding that a loose operation become an entity or value, ask whether it is an activity: a verb the business says, spanning several objects, holding no state — that is a domain service, and forcing it into a noun makes the model worse.
- For each new command in the diff, ask what it guarantees when it returns and where that guarantee is written; if the answer is nowhere and no test exercises it, the effect exists only in the implementation.
- At every integration point, find where translation happens: it should be one narrow, named, tested object — not conversions sprinkled through domain code, and never a foreign type imported into the model.
- Check where the cleverness in this diff landed: sophistication in generic plumbing plus a neglected core is the book's definition of a failing project.
