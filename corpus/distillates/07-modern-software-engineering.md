# 07. Modern Software Engineering — David Farley

> Farley frames software engineering as applied empiricism under uncertainty: every design is a guess until measured, and the only trustworthy yardsticks are quality of change (stability) and speed of change (throughput). A reviewer's job is therefore twofold — protect the team's ability to learn fast (small steps, fast feedback, cheap reversal) and protect its ability to manage complexity (modularity, cohesion, separation of concerns, guarded boundaries). Testability is his master instrument: code that resists isolated, deterministic testing is by that fact badly designed, whatever it does in production.

## Principles

### 07.1 Judge process and structure by measured stability and throughput, not by how disciplined they sound
- **Why:** Practices that feel rigorous (extra approval gates, sign-off ceremony) demonstrably worsen both dials; plausibility is not evidence.
- **Applies:** Changes adding gates, ceremony, or heavyweight structure justified by "safety" or "best practice" with no evidence they prevent defects.
- **Unless:** Controls with evidence behind them — automated tests, trunk-based CI — are backed by the same data; do not strip those.
- **Source:** Ch. 3, Fundamentals of an Engineering Approach

### 07.2 Treat design and performance claims as hypotheses to falsify, not assertions to accept
- **Why:** Instinct-driven claims are routinely wrong (parallel "optimizations" measured slower, method-call "overhead" unmeasurable); a cheap experiment beats debate from first principles.
- **Applies:** PRs justified by unbenchmarked performance arguments, complexity added "for speed", or technology choices argued from fashion or seniority — ask for the disconfirming test or measurement.
- **Unless:** The demand for evidence scales with the cost of the complexity being bought; do not stall trivial choices on proof obligations.
- **Source:** Ch. 1; Ch. 7–8, Empiricism and Being Experimental

### 07.3 Treat hard-to-test code as a design defect, never as a testing problem
- **Why:** Testability and design quality are the same signal: code easy to test in isolation is necessarily modular, cohesive, appropriately coupled, and information-hiding. Awkward setup, heavy mocking of internals, or dependence on real files, databases, networks, and wall clocks means the production design lacks seams.
- **Applies:** Any change adding logic, especially new modules and their tests; changes submitted untested because testing is "hard"; hard-wired construction of collaborators instead of injected ones.
- **Unless:** Thin adapters at physical edges are legitimately hard to unit test — shrink and marginalize them; never accept test-only backdoors that break encapsulation, and easy tests alone do not prove good design.
- **Source:** Ch. 5, Feedback in Design; Ch. 9 and Ch. 14, Testability

### 07.4 Prefer small, frequently integrated changes that keep the cost of the next change flat
- **Why:** Merging code is not merging behavior — long-isolated batches combine into wrong behavior no tool catches. Small steps cap the blast radius of a wrong assumption and keep decisions cheap to revisit as learning arrives.
- **Applies:** PR size and batching; long-lived branches; diffs bundling independent ideas; designs that hard-wire today's guess (frozen APIs, irreversible data-model commitments) when a reversible alternative exists.
- **Unless:** Do not fragment an atomic change (schema migration plus its adapter) into pieces that individually break invariants; each step must leave the system releasable.
- **Source:** Ch. 4, Working Iteratively; Ch. 5, CI vs. feature branching

### 07.5 Require a seam between essential domain complexity and accidental technical complexity
- **Why:** Business logic tangled with storage, transport, or framework plumbing is untestable in isolation and welds the domain to today's infrastructure; with a strict seam the author's exchange swapped its RDBMS in a morning. Mixed abstraction levels in one function are the tell.
- **Applies:** Domain flows that call SDKs, HTTP clients, ORMs, or brokers directly; new features inlining infrastructure into business rules — ask for a port named in domain terms.
- **Unless:** Trivial glue and throwaway scripts; language and standard-library types need no wrapping, and the port need cover only the subset actually used.
- **Source:** Ch. 11, Separation of Concerns; Ports & Adapters

### 07.6 Make boundaries between separately evolved units translate and validate what crosses them
- **Why:** A boundary only exists if what is known inside differs from what is exposed. Consuming a foreign representation raw couples you to another team's change schedule, and everything a component interprets in its inputs — payload shapes included — is part of its API, not just declared signatures.
- **Applies:** Inter-service messages, consumed events, webhook payloads, shared DTOs, anything crossing bounded contexts or pipelines; backward-compatibility review of interpreted content.
- **Unless:** Inside one cohesive module full translation is ceremony; the adapter can be thin — a defended perspective, not bulk. Data treated as opaque does not enlarge the contract.
- **Source:** Ch. 6; Ch. 9, Services and Modularity; Ch. 11, What Is an API?

### 07.7 Fence nondeterminism and concurrency at module edges instead of letting them smear through the code
- **Why:** Concurrency and coupling are the two genuinely hard problems, and nondeterminism cannot be reliably tested — a result that varies per run is opinion, not evidence. Sequencing entry into a module keeps it deterministic and testable.
- **Applies:** New threads, async flows, shared mutable state, wall-clock reads, retries, caches; flaky tests; where synchronization lives in the design.
- **Unless:** Not a ban — async messaging is a legitimate decoupling tool; also distrust reflexive parallelization, since measured coordination costs often make it slower than sequential code.
- **Source:** Ch. 9, Complexity and Determinism; Ch. 7 concurrency experiment

### 07.8 Reject future-proofing; testable, well-seamed code is the only insurance worth buying
- **Why:** Good incremental design organizes code so change stays easy; over-engineering tries to handle everything imaginable now. Speculative interfaces, unused config points, and framework layers close doors as effectively as tangled code.
- **Applies:** Interfaces with one implementation justified by "we may need it", configurable values that never vary, generality added ahead of any materialized second concern.
- **Unless:** A seam that falls out of separating today's concerns is fine even if it happens to enable futures; rejecting speculation never licenses ball-of-mud shortcuts.
- **Source:** Ch. 6, Incremental Design; Ch. 12, Fear of Over-Engineering

### 07.9 Stop DRY at deployment boundaries, and verify claimed independence is real
- **Why:** A shared library or canonical model spanning independently deployed services trades duplication cost for coupling cost, forcing lockstep upgrades. And a "microservice" that needs joint testing with neighbors is one system with distributed overhead — the middle ground is slower than the monolith it avoids.
- **Applies:** Cross-service shared code and common model packages; service contract changes; integration suites spanning services; proposals to split or merge deployable units.
- **Unless:** Within one repo and pipeline DRY remains excellent advice; a deliberate monolith tested and released as one unit is legitimate — there the demand shifts to keeping its single feedback loop fast.
- **Source:** Ch. 13, DRY Is Too Simplistic; Ch. 9 and Ch. 13, Deployability

### 07.10 Never weigh a diff by its line count; weigh the coupling and readability it produces
- **Why:** Decoupling almost always costs extra code at first, and optimizing for typing rather than thinking targets the wrong economy — independence and clarity have direct value that character counts do not measure.
- **Applies:** Pushback on extractions of methods, adapters, or modules framed purely as "more lines"; equally, defenses of a coupling-increasing change framed as "fewer lines".
- **Unless:** Extra code that adds indirection without reducing any real coupling is over-abstraction, and size is a fair complaint against it.
- **Source:** Ch. 13, Decoupling May Mean More Code

### 07.11 Keep failure inside the abstraction: model error outcomes in domain terms
- **Why:** Technical failures surfacing through domain interfaces — HTTP codes, driver exceptions — break the abstraction's continuity and couple every consumer to transport details; modeling failure as a domain result contains the leak in one place.
- **Applies:** Error paths crossing any seam — storage, remote calls, third-party libraries; return types and exception surfaces of domain interfaces.
- **Unless:** Transport errors reported by the transport layer itself are fine; some leaks (latency, resource limits) are unavoidable and should be consciously designed for, not denied.
- **Source:** Ch. 12, Leaky Abstractions

### 07.12 Admit new tools and frameworks only when they move a structural dial
- **Why:** Most industry change is ephemeral and some makes things worse — his Hibernate case required more code and read worse than the plain SQL it replaced. The test for adoption is improved modularity, separation of concerns, or feedback speed, not currency.
- **Applies:** Diffs introducing a dependency, framework, or architectural fashion — ask what structural property improves and whether the plain solution is smaller and clearer.
- **Unless:** Not technophobia: genuine paradigm steps earn their place precisely by moving those dials; age is no more a virtue than novelty.
- **Source:** Ch. 2, The Illusion of Progress; Ch. 3, An Industry of Change?

## Review heuristics

- Ask where the measurement points are: can the new logic be exercised deterministically, in isolation, without real IO, clocks, network, or a sibling service?
- Scan each changed function for mixed altitude — a raw SDK, SQL, or HTTP call sitting beside domain-level statements marks a missing port.
- Trace everything crossing a service, repo, or team boundary: is it translated into the receiver's own model and validated, or consumed raw? Do technical exceptions escape through domain interfaces?
- Hunt speculation: interfaces with one implementation, config that never varies, flexibility justified by imagined futures — and, symmetrically, arguments for or against the diff made in line counts.
- Check blast radius: does one logical change ripple through unrelated modules, and does any new concurrency, wall-clock read, or shared mutable state escape a fenced module edge?
- Ask whether the change could land as smaller, individually releasable and revertible steps, and what measured evidence backs any performance or "best practice" claim it rides on.
