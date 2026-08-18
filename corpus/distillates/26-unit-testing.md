# 26. Unit Testing: Principles, Practices, and Patterns — Vladimir Khorikov

> Tests are code, and code is a liability: a suite earns its keep only when the protection it buys exceeds what it costs to maintain, and most suites fail that test by accumulating brittle, low-value cases. The decisive quality of a test is whether it survives refactoring — which it does only when it asserts the observable result a client cares about, never the internal steps taken to produce it. That requirement pushes back into the production design: business decisions must be separable from I/O, and the only communications worth pinning down with mocks are the ones outside systems can actually see. A reviewer therefore reads a diff's tests as a report on the design, and reads new indirection, new seams, and new public surface as evidence of what the tests could not reach honestly.

## Principles

### 26.1 Judge each test by expected value minus lifetime upkeep, and argue for deleting the ones that don't clear the bar
- **Why:** Every test must be refactored alongside production code, run on each change, read by anyone reconstructing behavior, and triaged when it cries wolf. Tests on trivial constructors, getters, and pass-through wrappers charge all of that while protecting nothing.
- **Applies:** Any diff adding or keeping tests, especially large batches added to satisfy a policy or a coverage gate.
- **Unless:** Not an argument for a bare suite — the goal is selectivity. Code that merely looks simple but carries business meaning (a branch-free price calculation, an invariant check) still deserves a test.
- **Source:** Ch. 1 (1.2, 1.3); Ch. 7 (7.3)

### 26.2 Treat coverage as a warning light for gaps, never as a target the change must hit
- **Why:** Coverage counts lines executed, not outcomes verified, so it is trivially gamed by inlining code or dropping assertions and blind to paths inside called libraries. Low numbers are real evidence; high numbers prove almost nothing.
- **Applies:** Changes driven by a coverage gate, or changes defended against a drop in the number.
- **Unless:** A sharp coverage fall in core domain logic, or a suite that barely touches the domain at all, is a genuine gap worth raising.
- **Source:** Ch. 1 (1.3)

### 26.3 Assert the end result the code produces, not the internal steps it takes
- **Why:** Tests coupled to call sequences, collaborator composition, intermediate values, or generated SQL text go red on refactorings that change nothing observable. Those false alarms erode trust until real failures are ignored or the tests are disabled.
- **Applies:** Unit tests over domain models; assertions on private structure, on which in-process collaborator was called, or on the exact shape of an artifact when only its effect matters.
- **Unless:** Some churn is cheap and unavoidable — a signature change that breaks compilation is trivially fixed. An interaction that genuinely leaves the system (a message actually sent outward) is a legitimate assertion target.
- **Source:** Ch. 4 (4.1.2–4.1.4); Ch. 7 (7.4.3)

### 26.4 Mock only dependencies that other systems can observe, and place the mock at the outermost adapter
- **Why:** A message bus or SMTP server forms a contract with the outside world, so its call pattern is behavior worth freezing. A database your application alone owns is an implementation detail — pinning how you talk to it produces failures on harmless refactorings and proves nothing about outcomes.
- **Applies:** Any new test double, and any seam introduced to enable one; integration tests over persistence.
- **Unless:** A database shared with other applications splits — its externally visible tables behave as unmanaged and warrant mocks. If a managed dependency truly cannot run in the test environment, skip the integration test rather than mocking it.
- **Source:** Ch. 5 (5.3.2–5.3.3); Ch. 8 (8.2); Ch. 9 (9.1.1)

### 26.5 Never assert that a stubbed query was called; verify only the answer computed from it
- **Why:** A call made purely to obtain input is a step toward the outcome, not the outcome. Asserting it overspecifies the test so that any change in how data is gathered breaks a test that should only care whether the result is right.
- **Applies:** Doubles configured to return canned data that are then also asked to confirm the call or its count.
- **Unless:** One double can legitimately do both — stub an answer on one method, verify a genuinely outward side effect on another.
- **Source:** Ch. 5 (5.1.3, 5.1.5)

### 26.6 Split any unit that both decides and performs side effects into a collaborator-free decision maker and a thin part that carries the decision out
- **Why:** Business logic and communication with the outside world are each complex enough alone; fused, they multiply and force every test to drag infrastructure along. Once decisions are pure, they are checked by feeding inputs and inspecting returned values — the cheapest, least brittle evidence available.
- **Applies:** Any change adding branching or business rules to code that also touches a database, filesystem, bus, clock, or UI framework — controllers, handlers, services, jobs.
- **Unless:** Full purity costs extra up-front reads and more code. Don't demand it in trivial or low-stakes code, or where the round trips are a real performance problem; mostly-separated with some state mutation in the domain is acceptable.
- **Source:** Ch. 6 (6.3.2); Ch. 7 (7.1.2)

### 26.7 Require code to be either deep or wide, never both
- **Why:** Testing cost scales with the number of collaborators to set up; testing value scales with complexity and domain significance. Code high on both axes is expensive to test yet too risky to leave untested — the quadrant where nearly all testing pain originates.
- **Applies:** New or grown classes and methods: count branching points, then count mutable and out-of-process dependencies.
- **Unless:** One or two in-process collaborators do not make a domain class overcomplicated, and immutable values are not collaborators at all — a method with many value parameters is not wide.
- **Source:** Ch. 7 (7.1.1)

### 26.8 Keep hidden inputs and outputs out of decision-making code: no static clocks, ambient config, or direct queries inside the domain
- **Why:** A method whose real inputs are invisible in its signature cannot be reasoned about locally, and every test of it must reproduce ambient state. A static time source in particular is shared mutable state that silently couples tests to one another.
- **Applies:** Domain classes and algorithms; new calls to `now()`, random, environment, or a global cache introduced inside business logic; repositories or gateways injected into entities.
- **Unless:** Shell and adapter code exists to touch ambient state — the rule targets the decision layer. Where DI containers cope poorly with values, resolving a time service once at the operation's entry point and passing the value down is a fair compromise.
- **Source:** Ch. 6 (6.3.1, 6.5.1); Ch. 11 (11.6)

### 26.9 Reject any widening of the public surface whose only new caller is a test
- **Why:** A test granted special access couples itself to implementation details, so behavior-preserving refactoring still breaks it — destroying exactly the property the book ranks highest. And a private routine too complex to reach through the public API is not a testing problem; it is a missing class.
- **Applies:** Private methods, fields, setters, or constructors made public/internal/virtual in a diff; test-only accessors; a small public method delegating to a large private one full of business rules.
- **Unless:** A member that is genuinely part of a contract with an outside consumer (an ORM restoring an entity) is observable behavior, not an implementation detail. Trivial private helpers should not be extracted just because they are private.
- **Source:** Ch. 11 (11.1, 11.2)

### 26.10 Refuse production code that exists only to accommodate tests
- **Why:** Test-mode branches, environment flags, and debug hooks raise the maintenance cost of shipping code and create paths that can activate in production — a class of bug the test suite itself will never catch. A single-implementation interface added speculatively is the same instinct in milder form.
- **Applies:** Constructor parameters or config named for test or staging, conditionals keyed on "is test environment", new interfaces alongside repositories, gateways, or domain classes.
- **Unless:** An interface exists legitimately when it lets tests substitute an *unmanaged* dependency — a message bus, a mail server — since that is the only thing ever mocked. Managed dependencies stay concrete classes, injected explicitly and never hidden behind a one-implementation interface. The same limit applies to adapters: wrapping a third-party library pays off where the library reaches something outside systems observe, not over an ORM on a private database or a date/time API.
- **Source:** Ch. 8 (8.4.1–8.4.2); Ch. 9 (9.2.4); Ch. 11 (11.4)

### 26.11 Demand hard-coded expectations from an independent source, never a recomputation of the code under test
- **Why:** A test that mirrors the algorithm is a copy of the production code and cannot tell a real regression from a legitimate refactoring; when it fails, the team simply pastes in the new algorithm.
- **Applies:** Tests over calculations, transformations, and formatting — especially parameterized tests whose expected column is an expression over the inputs.
- **Unless:** The expected value must come from somewhere other than the SUT — a domain expert, a specification, the legacy implementation being replaced. For genuinely trivial operations the distinction barely matters.
- **Source:** Ch. 11 (11.3)

### 26.12 Cover edge cases with fast in-memory tests, and spend integration tests on one longest happy path per scenario plus what unit tests cannot reach
- **Why:** Integration tests buy more regression protection and refactoring tolerance but cost far more to run and keep alive, so they must clear a higher value bar. The longest successful path maximizes the external interactions a single expensive test exercises.
- **Applies:** The shape of a change's coverage across levels; test suites aimed at repositories or thin data-mapping adapters in isolation; database-backed test infrastructure.
- **Unless:** A thin CRUD application legitimately ends up with roughly equal numbers of both, and an API over one database may lean on end-to-end tests since they run fast there. An error path that fails loudly and corrupts nothing needs no integration test.
- **Source:** Ch. 8 (8.1.2–8.1.3); Ch. 10 (10.5.2)

## Review heuristics

- For each new test double, ask which side of the boundary it stands on: unmanaged dependency the outside world observes (mock is fine, at the outermost adapter) or managed/in-process (use the real thing and assert final state).
- Scan every changed public modifier — `private` → `public`, non-virtual → virtual, a new setter — and check whether the only new caller is a test.
- Count branching points and mutable/out-of-process dependencies per changed class; flag anything high on both, and ask for the decision/side-effect split.
- Read expected values in tests: if any is computed from the inputs by the same logic the SUT uses, the test is a mirror and proves nothing.
- Grep the diff for `now()`, random, environment reads, and global caches added inside domain code; ask for them to be lifted into the signature.
- Check where the arrange section is bloated or a wall of doubles exists just to construct the subject — push back on the production design, not on the test.
- For schema changes: ordered migrations in the repository, the production engine in tests, and a separate transaction per arrange/act/assert section.
