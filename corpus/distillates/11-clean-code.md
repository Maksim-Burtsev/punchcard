# 11. Clean Code (2nd Edition) — Robert C. Martin

> Code is read an order of magnitude more often than it is written, so its dominant cost is comprehension, and cleanliness is a durability property, not aesthetics. Clean code is never a first emission: it is produced by a deliberate cleaning pass over working code, protected by tests that stay green throughout. The reviewer's job is to stand in for the first fresh reader — the author's intimacy with the solution makes the author systematically unreliable about clarity. The second edition adds its own counterweight: one-directional rules (split more, shorten more, comment less) without a stopping condition produce over-chopped, entangled, slower code, so judgment about the far edge is part of the discipline.

## Principles

### 11.1 Require every change to leave touched code slightly cleaner, and treat a diff that merely works as an unfinished draft
- **Why:** Mess compounds until it triggers doomed rewrites; small continuous cleanups are the only counter-mechanism. The cleaning pass itself surfaces small bugs and missing test cases, so skipping it ships both mess and defects.
- **Applies:** Any diff modifying existing code, and any submission still showing fumbling structure — dead experiments, duplicated cases, magic constants, ad hoc tricks.
- **Unless:** The bar is a livable house, not a show house: do not block a change over polish that adds no comprehension value, and never demand a rewrite of surrounding legacy in an unrelated diff.
- **Source:** Ch. 1 (The Boy Scout Rule; Livability); Ch. 2 (Clean That Code!)

### 11.2 Judge the diff's names as a system that carries the domain model
- **Why:** Good names let a reader infer the application's concepts from any fragment; disinformative or inconsistent names (four words for one concept, a list that is not a list) actively mislead every future reader at 10:1 read leverage.
- **Applies:** Every diff introducing or renaming modules, functions, or non-trivial variables — especially new public vocabulary and renames that follow a design insight.
- **Unless:** Short names are correct in tiny scopes; and a name is not a specification — a multi-clause megasyllabic method name signals missing contract documentation, not a naming win.
- **Source:** Ch. 4 (Meaningful Names); 2nd ed. dialogue (megasyllabic names)

### 11.3 Treat each comment as a claimed failure to express intent in code, but demand recorded whys and contracts where code cannot carry them
- **Why:** Comments drift into lies because nothing maintains them; most compensate for code that should be cleaned instead. Yet non-obvious rationale — a performance trick, a hidden precondition, an ordering constraint — costs the team repeated rediscovery if it lives only in the author's head.
- **Applies:** Diffs adding comments, commented-out code, or TODO markers; new or changed interfaces whose signatures leave input formats, ordering, side effects, or preconditions undefined.
- **Unless:** Intent, consequence warnings, unmodifiable-API clarifications, and public-API docs are legitimate; never use the rule to excuse a missing explanation code alone cannot give, and verify surviving comments against the code.
- **Source:** Ch. 5 (Comments); 2nd ed. dialogue (comments and contracts)

### 11.4 Require each function to hold one level of abstraction and read top-down; treat a large function as a missing class
- **Why:** Mixing policy with mechanism hides what matters and attracts further detail over time. A long function's locals are fields and its indented regions are methods — extraction turns geographic knowledge into navigable, named structure and often exposes invisible business rules.
- **Applies:** New or modified functions interleaving orchestration with arithmetic, formatting, or dispatch; additions to already-long functions; caller/callee ordering within a module.
- **Unless:** Some functions read better undecomposed; pure delegators and names restating one-line bodies are meaningless extractions.
- **Source:** Ch. 7 (Stepdown Rule); Ch. 10 (One Thing; Extract Method)

### 11.5 Demand honest signatures: commands or queries, never both, with no flags, output arguments, or predicate names hiding mutation
- **Why:** A name callers must not trust is a bug factory — a predicate-looking method that mutates state or imposes call ordering will be misused by every reader who believes it. Flag arguments openly declare two behaviors under one name; hidden side effects create temporal couplings that breed race and reentrancy bugs.
- **Applies:** Public API signatures in the diff: boolean behavior selectors, mutators returning computed answers, boolean-returning helpers, resource acquire/release pairing, any API whose correctness depends on call order.
- **Unless:** Pragmatic CQS violations like pop() are acceptable after weighing consequences; internal mutation invisible to callers is not a defect — containment, not elimination, is the ask.
- **Source:** Ch. 7 (Pure); Ch. 8 (CQS; Flag Arguments; Side Effects); 2nd ed. dialogue (predicate mutation)

### 11.6 Tolerate at most one type-dispatch switch per switchable type, buried at the edge where polymorphic objects are created
- **Why:** Tag dispatch replicates across every operation on the type family, so one new variant forces scattered, missable edits. A single switch behind a factory confines that knowledge to one place.
- **Applies:** Diffs adding a case to an existing switch, a second switch over the same tag, or a tag field plus if-chains where new variants are the expected axis of change.
- **Unless:** When the volatile axis is new operations over stable types, procedural dispatch is the better trade; a switch in a nanosecond-critical loop is acceptable.
- **Source:** Ch. 7 (Switch Statements); Ch. 12 (OO/Procedural Trade-off)

### 11.7 Make each type choose a side — object or data structure — and hold behavioral objects to Demeter
- **Why:** Objects hide data and make new types cheap; records expose data and make new operations cheap; a hybrid exposing both mutable state and significant behavior ripples on every kind of change. Chained navigation through other objects' internals couples the caller to the whole graph's structure.
- **Applies:** New classes, DTOs, and public APIs; call chains through behavioral objects; helpers that repeatedly interrogate another class to compute something that belongs on it.
- **Unless:** Plain data records at boundaries are legitimate — Demeter does not apply to them, and chaining through config trees is fine; beware the fix that bloats a facade with dozens of pass-throughs.
- **Source:** Ch. 12 (Data/Object Antisymmetry; Hybrids; Law of Demeter); Ch. 13 (feature envy)

### 11.8 Deduplicate only essential duplication — code that will change together for the same actor
- **Why:** Co-evolving copies rot when one is missed; but merging look-alikes owned by different stakeholders welds their futures together, and one actor's change silently corrupts the other's behavior.
- **Applies:** Diffs that copy-paste-modify existing logic, and diffs that extract a shared helper from similar sites — ask whether the sites change for the same reason at the same time.
- **Unless:** Tiny two-site duplicates are rarely worth an abstraction; never merge across actors just because the code looks identical today.
- **Source:** Ch. 8 (DRY; Accidental versus Essential Duplication)

### 11.9 Require error handling to be one thing, segregated from the happy path
- **Why:** Error codes woven into control flow drown the logic in guards and nesting; extracting the try body and the handler leaves one function about the work and one about the failures. Shared error-code enums also become dependency magnets nobody dares extend.
- **Applies:** Nested status-code checks, recovery logic mixed into business logic, try blocks with logic before or after them, additions to a system-wide error enum.
- **Unless:** In languages without exceptions, narrow and consistent value-plus-error returns are a reasonable convention; interface-based error types avoid the magnet problem.
- **Source:** Ch. 8 (Prefer Exceptions; Error Handling Is One Thing)

### 11.10 Read the tests as a design artifact held to production standards, and expect refactors to arrive green with coverage the cleaning exposed
- **Why:** Quick-and-dirty tests became one team's largest maintenance cost and took the production code down with them; a small production edit that rewrites dozens of tests marks a badly designed suite. Every restructuring in the book proceeds in small steps with tests passing, and the cleaning itself reveals missing cases and small bugs — without that suite, cleaning stops out of fear.
- **Applies:** Test diffs (setup obscuring intent, assertions on internals, production tables reused as expected values) and any diff claiming behavior is unchanged.
- **Unless:** Tests may waste CPU in ways production never would — inefficiency is fine, uncleanliness is not; multiple asserts verifying one logical fact are fine; do not litigate test-first versus test-after, only the coverage that lands.
- **Source:** Ch. 2 (The Cleaning Process); Ch. 9 (Make It Right); Ch. 15 (Clean Tests); 2nd ed. dialogue (fearless refactoring)

### 11.11 Judge comprehensibility from the fresh reader's seat, and treat over-decomposition as a defect equal to the thousand-line function
- **Why:** Both authors' code defeated the other despite each one's certainty it was clear — author intimacy is a systematically unreliable predictor of readability, and the reviewer is the first fresh reader available. Entangled extractions spread one mechanism across several interfaces the reader must mentally reassemble; a tidier two-loop refactor ran several times slower because an early exit was lost; implicit contracts satisfied four call levels away caused the hardest bugs.
- **Applies:** Any review requiring multiple passes or definition-hopping; refactorings advertised as cleanup by extraction; helpers that only work in a particular loop, order, or state; structural changes to hot paths or early-exit shapes.
- **Unless:** Inherently hard algorithms demand some effort regardless; do not swing to defending huge functions, and do not gate cold paths on profiling. Mechanical rules keep baseline value — they just must not outrank design judgment.
- **Source:** 2nd ed. dialogue appendix (A Tale of Two Programmers; entanglement; performance exchange; Closing Remarks)

## Review heuristics

- For each new or changed name, ask what a reader with zero context would predict it does — and whether that prediction is exactly right, including absence of mutation behind predicate names.
- For each comment, ask which rename or extraction would delete it; for each non-obvious interface, ask where the caller learns its preconditions, ordering, and side effects without reading the body.
- For each extraction, ask whether the pieces stand alone or can only be understood together — and whether a hot loop's early-exit or iteration structure survived the split.
- For duplication in either direction — a new copy or a new shared helper — ask which actor owns each site and whether they change together.
- For a diff claiming unchanged behavior, ask what evidence exists that tests stayed green in small steps, and what missing cases the cleanup exposed.
- For a switch or if-chain over a type tag, count how many other sites dispatch on the same tag and where a new variant would have to be edited.
