# 09. Code That Fits in Your Head — Mark Seemann

> Software engineering is the art of keeping code within the limits of human working memory: a reader can track about seven things at once, and any unit demanding more cannot be verified by reading. The reviewer's job is therefore to measure comprehension load — branches, variables, dependencies, hidden side effects — at every zoom level, and to insist on structures (parsing at boundaries, pure cores, honest signatures) that let each piece be understood without the rest. Process matters as much as structure: changes must arrive small, continuously integrable, and backed by tests treated as evidence rather than ritual.

## Principles

### 09.1 Hold every unit to a budget of about seven chunks, at every zoom level
- **Why:** Working memory tops out around seven items; code that tracks more branches, live variables, or activated objects at once cannot be checked by reading, so System-1 quietly guesses wrong about it. The fractal idea: each level of zoom — method, class, composition root — must be independently comprehensible.
- **Applies:** Any changed method or class: count pathways (cyclomatic complexity), constructor dependencies, and variables in play; a diff that pushes a unit past the budget should trigger decomposition before merge.
- **Unless:** The number is a guide, not a law — a team may set its own threshold, and a documented, justified exception is acceptable; rigid enforcement without judgment backfires.
- **Source:** Ch. 3 Tackling Complexity; Ch. 7 Decomposition; 7.2.6 Fractal Architecture; A.7–A.8

### 09.2 Demand a thin working vertical slice before any infrastructure or generality
- **Why:** Teams that build the database layer, framework, and abstractions first discover too late their usage assumptions were wrong; a deployed end-to-end slice produces feedback no upfront design can.
- **Applies:** New features and modules: ask what user-visible slice the change completes; flag single-implementation abstractions, home-grown frameworks, and layers added ahead of need.
- **Unless:** A seam introduced so the current slice is testable (a repository interface with a fake) is not speculative — it is part of the slice.
- **Source:** Ch. 4 Vertical Slice (4.1.2); Ch. 1 (1.1.3)

### 09.3 Parse boundary input once into always-valid domain types; keep DTOs separate
- **Why:** External data carries no guarantees, so it enters as a dumb transfer object and is converted exactly once into an immutable domain type whose constructor enforces its invariants. Validation returning a boolean discards the proof; a typed result carries it, and all downstream defensive checks disappear.
- **Applies:** API handlers, message consumers, config loading, persistence mappings: flag DTOs passed deep into business logic, domain types leaking into serialization, IsValid-style checks, and null/range checks buried in the core.
- **Unless:** DTOs are deliberately unencapsulated — forcing invariants onto them breaks deserialization; and in a trivial pass-through with no rules, a parallel type hierarchy is ceremony.
- **Source:** Ch. 4 (4.3.4); Ch. 5 Encapsulation (5.3); 7.2.5 Parse, Don't Validate; A.15

### 09.4 Review contracts against Postel's law: accept liberally, reject precisely, guarantee strongly
- **Why:** A method should accept any input it can meaningfully process — but no more — and fail fast with a specific, well-typed error the moment it cannot; a 400 with a reason is diagnosable, a generic crash is not. Weak demands plus strong guarantees are what let callers reason locally.
- **Applies:** Public entry points and signatures: check what the change accepts, what it rejects, and which error each invalid case produces; flag validation duplicating what a parse already proves.
- **Unless:** Do not demand unverifiable validation (e.g. proving an email is real) — checking beyond what the system can use adds cost without safety.
- **Source:** Ch. 5 (5.2, 5.2.4); A.16

### 09.5 Judge APIs by their signatures: types first, then names, then comments — and make misuse uncompilable
- **Why:** Types are compiler-checked and never stale; names rot slower than comments, comments slower than wikis. The test is X-ing out the method name — if types alone do not suggest the behavior, the design leaks. Poka-yoke designs (required constructor arguments, non-nullable types, unrepresentable illegal states) turn runtime defects into compile errors.
- **Applies:** New or changed public APIs and interfaces: nullable/Maybe returns to encode absence, distinct types where the compiler could catch swapped arguments, comments that should be well-named methods.
- **Unless:** Names still carry what types cannot, and "why" rationale legitimately lives in comments or commit messages; heavy type encodings can cost more than they protect in some languages.
- **Source:** 8.1.2 Poka-Yoke; 8.1.4–8.1.7 Hierarchy of Communication

### 09.6 Enforce Command Query Separation: return data or cause effects, never both
- **Why:** A side effect hidden inside a query means the signature lies — the reader budgets for fewer behaviors than actually occur. Strict CQS lets a reviewer reason about call sites without opening implementations.
- **Applies:** Every new or changed method; especially boolean-returning methods that also persist, send, or mutate — a TrySave dressed as a check.
- **Unless:** Local mutation inside a method returning a read-only result is fine; knotty cases like insert-and-return-ID deserve a deliberate, documented exception, not mechanical rejection.
- **Source:** 8.1.6; A.6; A.14

### 09.7 Keep decisions pure and push nondeterminism to a thin impure shell
- **Why:** Nested side-effectful objects accumulate hidden behaviors that overflow the reader's head; a pure function collapses to its result, composes by feeding output to input, and is reproducible without logging.
- **Applies:** Where business logic lives: handlers may query the clock, database, and RNG, but the decision over that gathered data should be a deterministic function.
- **Unless:** The shell is legitimately impure — do not demand purity of Main, controllers, or composition roots; the book asks for migration toward this style, not a rewrite.
- **Source:** Ch. 13 Composition (13.1.3); A.12 Functional Core, Imperative Shell

### 09.8 Keep cross-cutting concerns in Decorators, not woven into the logic they observe
- **Why:** Logging, caching, retries, and metrics change at a different rate than the code they wrap; injecting a logger into a repository couples persistence to observability, while a Decorator adds the concern without touching working code — and each concern stays independently removable.
- **Applies:** Any diff threading logging, caching, fault tolerance, or notifications through domain or data-access classes.
- **Unless:** Framework-provided facilities beat hand-rolled decorators; and log only impure actions — pure computation is reproducible from its inputs and needs no log line.
- **Source:** Ch. 13 (13.2, 13.2.3); A.9

### 09.9 Play devil's advocate against the tests: could an obviously wrong implementation pass?
- **Why:** Tests triangulate behavior; if a hard-coded or degenerate implementation survives the suite, the change is under-specified and can silently regress. Test sufficiency is risk assessment, and a defect that reached production is proof a test was missing — the fix ships with the reproducing test.
- **Applies:** Every behavioral change and every bug fix: mentally sabotage the implementation and check the new tests would object.
- **Unless:** Do not demand combinatorial boundary coverage, tests coupled to incidental details, or unit tests for humble objects that merely wrap un-automatable I/O without branching.
- **Source:** Ch. 6 Triangulation (6.2.2, 6.2.5); A.19

### 09.10 Scrutinize test edits harder than production edits; never move both in one change
- **Why:** Tests are the safety net and have none of their own: adding tests strengthens guarantees, but weakened assertions silently open regression doors, and refactoring tests and production together leaves nothing verifying the change.
- **Applies:** Any diff touching test files — prefer additive changes, keep test refactoring in commits with no production edits, and treat deleted or loosened assertions as blockers.
- **Unless:** Tooling-applied atomic renames are fine across both sides; multiple assertions per test are strengthened postconditions, not a smell; slow tests move to a second-stage suite rather than the trash.
- **Source:** Ch. 11 Editing Unit Tests; A.22

### 09.11 Hold the line at zero warnings; every suppression carries its reason
- **Why:** Compiler, linter, and analyzer warnings are free automated review, but only while the signal is clean — one warning among hundreds is invisible. A written justification preserves the "why" and invites challenge.
- **Applies:** Every diff in a checked codebase: new warnings, disabled rules, or bare suppressions block; documented suppressions (a library rule applied to test code) are legitimate.
- **Unless:** Analyzers produce false positives; principled, recorded exceptions are expected — the rules are defaults, not dogma.
- **Source:** Ch. 2 Checklists (2.2.3); Ch. 4 (4.2.3)

### 09.12 Reject change sets too large to review; big migrations go Strangler-style
- **Why:** A review is worthless as evidence if the reviewer cannot actually read the change — beyond roughly half a day's work, reviews drag or get waved through on sunk cost. Large restructurings stay integrable by running new alongside old, migrating callers incrementally, then deleting the old path; incomplete features hide behind a flag on the mainline, not on a long-lived branch.
- **Applies:** Every incoming diff (does it do one thing, build, pass, and add tests?); multi-day refactorings, interface replacements with many call sites, and behavior changes mixed with restructuring — which should be split and reviewed separately.
- **Unless:** Small changes with few callers can be edited in one step; do not nitpick cosmetics in reviewable changes; and the old path or the flag must actually get deleted at the end.
- **Source:** 9.2.4–9.2.6; Ch. 10 (10.1, 10.2); A.23–A.24

## Review heuristics

- For each changed method, count branches, live variables, and injected dependencies together; past about seven, ask for decomposition — and check the extracted pieces are each comprehensible alone.
- Trace every point where outside data enters the diff: is it parsed once into a validated domain type, or checked with a boolean and passed along raw?
- Scan new signatures for lies: query methods that mutate, persist, or send; nullable facts hidden behind non-nullable types; parameters the compiler cannot tell apart.
- Sabotage the change mentally — replace the implementation with a hard-coded constant and ask whether the accompanying tests would notice; for a bug fix, look for the test that reproduces the defect.
- In test-file diffs, hunt for weakened or deleted assertions and for test refactoring mixed with production changes in the same commit.
- Ask what user-visible slice the change completes; abstractions with one implementation, layers "for later", and new warnings or bare suppressions are all blockers.
