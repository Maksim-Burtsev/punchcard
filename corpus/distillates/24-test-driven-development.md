# 24. Test-Driven Development: By Example — Kent Beck

> Design is not decided up front and then typed in; it arrives one concrete example at a time, under pressure from failing tests and from duplication. So a change is judged by the evidence that came with it: which test failed before it, which dependency it removed, and whether the code could be exercised in isolation at all. Difficulty writing a small test is never a testing problem — it is the design reporting a defect in itself. Tests are also the working document a future maintainer reads, so their data, assertions and size are part of the change, not packaging around it.

## Principles

### 24.1 Require every behavioral change to arrive with a test that failed before it
- **Why:** Production code exists only to make a failing test pass; that rule is what keeps scope controlled, makes intent legible, and guarantees each new line is actually exercised. Near-total coverage is a by-product of the discipline, not a separate effort.
- **Applies:** Domain, model and business logic — anywhere a wrong answer would matter.
- **Unless:** Debug aids like a `toString` written for a better failure message, and small private helpers created during a refactoring already covered by existing tests. Some properties — security, subtle concurrency — cannot be demonstrated by tests at all, so a green suite there proves little.
- **Source:** Preface; Part I (Money); Chapter 16, Change

### 24.2 Read duplication as a report of a dependency, and judge the fix by whether the dependency is gone
- **Why:** Duplication is the symptom, dependency is the disease: while two places must be edited together, neither the test nor the requirement can change independently. Removing duplication is rare among software fixes in that it eliminates coupling rather than relocating it — which is how design actually emerges.
- **Applies:** Any diff where the same expression, constant or fact appears twice — including between a test and the code it drives, and between code and its configuration data.
- **Unless:** Short-lived duplication is a legitimate step: copy first to get green, remove immediately after. Do not demand deduplication in the same step that establishes behavior, and do not merge code that is only coincidentally similar.
- **Source:** Sidebar: Dependency and Duplication; Chapter 34, Refactoring

### 24.3 Refuse structure that no test or duplication currently demands
- **Why:** A class, interface, parameter or extension point introduced ahead of evidence encodes a guess about variation that has not happened, and it must be maintained until someone dares unwind it. Generalize on the second real example, not the first imagined one.
- **Applies:** New abstraction layers, interfaces with one implementation, strategy/factory indirection, options and parameters added "for flexibility".
- **Unless:** This is not permission to leave known duplication standing — a genuine second case must be generalized at once. A metaphor or seam chosen deliberately because it makes the whole problem simpler, or needed to substitute a collaborator in tests, is exactly right.
- **Source:** Chapter 31, Green Bar Patterns; The Root of all Evil; Makin' Objects

### 24.4 Insist that one defect produce exactly one red test, and that each test restore what it touched
- **Why:** Shared state turns one break into ten failures and, worse, produces suites that pass only in a particular order — a suite that lies. Cleanup repeated inside each test body is duplication that will eventually be forgotten in one place; it belongs in the teardown hook.
- **Applies:** Fixtures, shared or static test data, and any external resource a test acquires.
- **Unless:** Performance is the honest reason people share fixtures; the trade is acceptable only when fresh state is genuinely too slow, and the usual fix is cheaper setup rather than shared setup. A pure computation touching nothing needs no teardown; conversely, setup that can fail may skip teardown entirely, so critical cleanup needs its own guarantee.
- **Source:** Set the Table; Chapter 28, Isolated Test; Chapter 32, External Fixture

### 24.5 Treat "hard to test in isolation" as a verdict on the production code, and reject ambient globals and singletons
- **Why:** Isolating a test forces the problem into small orthogonal pieces — that is how cohesive, loosely coupled components get produced rather than merely praised. A singleton is a global variable with a pattern name: it hides every user's dependencies and blocks substituting a stand-in without mutating shared state. Passing the dependency explicitly almost always touches fewer call sites than feared.
- **Applies:** Changes adding a dependency on a database, network, clock, file system or other costly or ambient resource; new static mutable state or service locators.
- **Unless:** Process-wide immutable configuration and stateless utilities carry no such hazard, and pre-existing singletons are not automatically in scope. A fake carries its own risk of diverging from the real thing — pair it with a suite runnable against both. Not every test should be pushed down: one application-level starter test is often the right first test.
- **Source:** Chapter 33, Singleton; Chapter 30, Mock Object; Chapter 28, Isolated Test

### 24.6 Drive the unit through its public protocol, and make each assertion state the exact expected result
- **Why:** A test that reads private fields is welded to today's representation and hides the observable query the caller actually needs. An assertion that merely rules out zero passes for almost every wrong answer, so it costs maintenance and proves nothing.
- **Applies:** New or modified tests and assertions for code the team owns.
- **Unless:** When no public design idea presents itself, checking the variable and moving on beats stalling. Legacy code being pinned down before refactoring is not the place to enforce this. Timestamps, generated ids and floating-point results have no single expected value — assert the property or tolerance instead of inventing one.
- **Source:** Chapter 32, xUnit Patterns — Assertion

### 24.7 Read tests as documents: expectations should show their derivation, and distinct roles need distinct values
- **Why:** A later maintainer reconstructs intent from the tests, and a computed expectation that displays its own arithmetic teaches more than an opaque literal. Reusing one number for two roles destroys the test's ability to catch swapped arguments.
- **Applies:** Test data, fixture values and assertion style in any new or changed test.
- **Unless:** Not a licence for bulk — use the smallest data that drives the same design decisions. Prefer existing meaningful constants, and use realistic captured data for parallel testing, trace-driven systems, and refactorings that must reproduce identical output.
- **Source:** Chapter 28, Test Data and Evident Data

### 24.8 Treat tests coupled to internals as scaffolding, and delete tests only when nothing is lost
- **Why:** A test asserting which class was returned can legitimately lever a design step forward, but it freezes the internals and is meant to die once the behavior is covered from outside. Symmetrically, a test protecting a distinction that no longer exists is inertia — but confidence and communication are the two things tests buy, and a duplicate that narrates a different scenario still supplies one of them.
- **Applies:** Tests that cast, reach into fields, or assert implementation shape; diffs that remove tests, especially with the justification "already covered".
- **Unless:** Keep a suspicious duplicate whenever deleting it would cost even a little confidence, and demonstrate redundancy from current logic rather than from surface similarity. Never accept a test deleted or commented out to make the suite green.
- **Source:** Make It; Abstraction, Finally; Chapter 35, Mastering TDD

### 24.9 Require a defect fix to carry the smallest test that reproduces it
- **Why:** A regression test is simply the test that would have been written first with perfect foresight, so each one names a category missing from the team's test list. When the system must be restructured before the failure can be pinned down small, that difficulty is the design feedback — the bug surfaced at the level the design forced it to.
- **Applies:** Any change presented as a bug fix, and any fix whose only evidence is an end-to-end scenario.
- **Unless:** Application-level regression tests stay valuable as the channel through which users report what is wrong; the small test complements them. Integration, performance, stress and usability failures are genuinely emergent and are not expected to reduce to a unit test.
- **Source:** Chapter 29, Regression Test

### 24.10 Make the second appearance of a type or mode check into polymorphism, and pass policy in rather than teaching the core object about it
- **Why:** An explicit test on a runtime class puts a language-level fact where a domain fact belongs, and it spreads: sibling methods start asking the same question and the answers must be kept consistent by hand. Core objects stay flexible, testable and comprehensible exactly to the degree they know nothing of rates, configuration or infrastructure — otherwise every new operation swells the central type.
- **Applies:** Conditionals over runtime types, downcasts before dispatch, repeated null/mode checks across one class's methods, and decisions about where a new operation on a core entity should live.
- **Unless:** A class check is a fine temporary green-bar step before the polymorphic move, and a single conditional duplicating nothing needs no object. The placement of a collaborator is a working hypothesis — move the responsibility back if the collaborator earns nothing. Dispatching reflectively on a method name does beat carrying the switch, but it is a last resort: it costs the ability to trace or statically check who calls what, so accept it only to collapse a set of subclasses that each hold a single method, and only when no ordinary polymorphic move is available.
- **Source:** Apples and Oranges; Addition, Finally; Chapter 33, Pluggable Object / Null Object

### 24.11 Make objects that are handed around immutable, with equality defined
- **Why:** Once a reference is shared, later mutation silently invalidates conclusions the other holder already drew, with no notification. Copying everywhere is expensive and change notification makes control flow unfollowable; removing change removes the aliasing hazard entirely. Such objects are compared by content, so equality must be written.
- **Applies:** Types crossing module boundaries, cached, used as keys, or shared across threads — money, measurements, coordinates, identifiers.
- **Unless:** Objects whose identity is the point — accounts, sessions, entities with a lifecycle — are not values. Allocation cost is real but should be answered from a profile and an actual complaint, not in advance.
- **Source:** Chapter 33, Value Object

### 24.12 Treat step size as a dial: shrink it on unfamiliar ground, and stage a representation change rather than swapping it at once
- **Why:** The quantity actually being managed is the distance between a decision and the feedback that judges it, and the whole discipline is techniques for controlling that distance. Tiny steps are not the goal — being able to take them is, so that a hard or unfamiliar problem can be crossed with the suite confirming each foot of ground while a familiar one is crossed in strides. When a piece of work turns out to need several changes before anything can go green, the move is to set it aside for a smaller one covering the broken part and reintroduce it after. A one-shot format change makes every intermediate state broken and offers no point where equivalence could be confirmed; running old and new side by side, then migrating writers, readers, and finally deleting the old, keeps the system observably unchanged at each step so a failure localizes to the step that caused it.
- **Applies:** Large single-commit rewrites and mixed diffs; changing a field's type or shape, a stored format, a method parameter, or a published signature; any change in a subsystem the author is meeting for the first time.
- **Unless:** There is no correct step size for all time, and demanding small increments from someone who is confident and right is just friction. A small fully internal representation with every caller inside the same change can simply be changed. Watch for half-finished migrations: duplicated representation that outlives the change becomes a permanent consistency hazard.
- **Source:** Preface; Chapter 34, Refactoring — Migrate Data / Add Parameter; Chapter 30, Child Test; Chapter 35, Mastering TDD

## Review heuristics

- For each behavioral change in the diff, name the test that would have failed without it. If none exists, that is the finding.
- Look for the same fact in two places — code and test, code and config, two branches — and ask which dependency it is reporting; a change that tidied the repetition without removing the coupling is not done.
- Check new abstractions against the examples in the diff: an interface with one implementation, a parameter with one caller, or a factory for one product is a guess, not a design.
- Read the test setup as evidence about the production code: a hundred lines of fixture means the objects are too large, setup that resists factoring means they are too entangled, and a test that breaks for unrelated reasons means undeclared coupling. Fixing only the test hides the signal.
- Scan assertions for vagueness (not-null, not-zero), for reads of private state, and for one constant reused in two roles.
- Judge coverage by risk of being wrong, not by completeness: expect tests for the branches, loops and polymorphism this change introduces, and none for third-party code — except a test pinning surprising library behavior you depend on.
- Check that anything acquired in setup is released in teardown, and that no test depends on another having run first.
- Ask whether the change arrived in increments the suite could confirm one at a time, and calibrate that question to the risk: an unfamiliar subsystem, a format migration or a rewrite should show intermediate green points, while routine work on well-known code needs no such ceremony.
