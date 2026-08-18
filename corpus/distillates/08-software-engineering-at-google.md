# 08. Software Engineering at Google — Titus Winters, Tom Manshreck, Hyrum Wright

> Software engineering is programming integrated over time: a change is judged not by whether it works today but by whether the codebase can still absorb change in ten years, at ten times the scale. Every observable behavior becomes a contract, every unenforced promise decays, and every cost that grows linearly with the number of engineers or callers eventually becomes unpayable. The reviewer's job is to protect sustainability — the capability to respond to change — using automated evidence rather than trust, and to spend human judgment only where machines cannot.

## Principles

### 08.1 Treat every observable behavior of widely used code as a de facto contract
- **Why:** Hyrum's Law: with enough users, someone depends on ordering, timing, error text, and undocumented internals regardless of the documented contract, so "non-breaking per the spec" is an estimate, not a fact.
- **Applies:** Changes to shared libraries, APIs, serialized formats, RPC responses, platform-facing behavior; new code that needlessly exposes incidental behavior callers could latch onto.
- **Unless:** All consumers are visible and fixable in the same change; the law can only be mitigated, never eradicated, so do not demand impossible guarantees.
- **Source:** Ch. 1 (Hyrum's Law, hash-ordering example); Ch. 21 (limits of SemVer); Ch. 25 (Borg's implicit contracts)

### 08.2 Calibrate review rigor to the code's expected lifespan
- **Why:** The difference between "works" and "maintainable" only matters once code must survive changes in its environment, and lifespans vary by a factor of 100,000 — the same standards cannot apply across that whole spectrum.
- **Applies:** Deciding how hard to push on tests, consistency, documentation, and upgrade-readiness for any change; distinguishing production modules from spikes and quarantined experiments.
- **Unless:** The short lifespan must be enforced or genuinely credible — "temporary" code that can reach production is long-lived code and gets no discount.
- **Source:** Ch. 1 (Time and Change); Ch. 3 (readability exemptions for experimental code)

### 08.3 Accept only CI-visible automated tests as evidence that a behavior is protected
- **Why:** The Beyoncé Rule — if you liked it, you should have put a CI test on it — because no one can hand-verify hidden usages at scale; untested behavior is fair game to break, and "we'll be careful" is not an invariant.
- **Applies:** Any behavioral change or promise in a diff: new features need tests, bug fixes need the regression test that would have caught the bug, claimed guarantees need an enforcing check.
- **Unless:** Bespoke test rigs outside common CI do not count as protection; throwaway code may skip heavy test investment per 08.2; pure refactorings that force test edits implicate the tests, not missing coverage.
- **Source:** Ch. 1 (Policies That Scale Well, compiler-upgrade example); Ch. 9, Ch. 11

### 08.4 Reject changes whose cost grows with the number of consumers; the owner internalizes migration work
- **Why:** The Churn Rule: policies that make every caller adapt scale linearly with the organization and become unaffordable, while centralizing the work in expert hands scales sublinearly.
- **Applies:** Deprecations, interface changes, config and protocol migrations, any process a change institutionalizes that imposes per-team work.
- **Unless:** Small codebases where one atomic change fixes every caller; the danger is baking non-scaling habits in as the organization grows, not the one-off itself.
- **Source:** Ch. 1 (Scale and Efficiency; Policies That Don't Scale)

### 08.5 Enforce one version: no forks, vendored copies, or parallel implementations of existing code
- **Why:** A second copy partitions the codebase — diamond dependencies break builds or runtimes, security fixes must chase every fork, and boundary-crossing formats ossify into permanent compatibility burdens. Code is a liability; the functionality is the asset.
- **Applies:** Changes that vendor a tweaked library, pin a divergent version, copy internal utilities, or add a parallel system duplicating what an existing one does without a migration and removal plan.
- **Unless:** A temporary second version during a staged migration, with new uses of the old path mechanically blocked and switchover underway; provably narrow, justified forks for short-lived work.
- **Source:** Ch. 16 (One Version); Ch. 18, Ch. 21 (diamond dependencies); Ch. 15 (code is a liability)

### 08.6 Treat a new dependency as a signed long-term contract, and distrust version numbers as evidence
- **Why:** Security disclosures and platform shifts will force upgrades regardless of intent, and SemVer is the provider's lossy self-attestation — under Hyrum's Law only the consumer's own passing tests evidence compatibility.
- **Applies:** Any change importing a new third-party library into shared or long-lived code; dependency bumps justified solely by "it's a minor version"; ask who maintains it and who performs the forced upgrade.
- **Unless:** Genuine throwaway code may import freely; reimplementing well-solved infrastructure is usually worse than depending on a reputable provider.
- **Source:** Ch. 21 (Considerations When Importing; The Limitations of SemVer)

### 08.7 A deprecation without a migration path and backsliding prevention is incomplete
- **Why:** Warnings alone accumulate into alert fatigue and move no one; without mechanically blocking new uses, migration becomes whack-a-mole and both systems get maintained forever — hope is not a strategy.
- **Applies:** Changes marking anything deprecated, removing dangerous idioms, or introducing a replacement: check for a concrete named replacement, enforcement at the point of new use, and a removal plan.
- **Unless:** Dead code with verifiably zero users can just be deleted; low-value cleanups do not merit the machinery — churn without recurrence prevention is not worth doing at all.
- **Source:** Ch. 15 (Deprecation Warnings; Preventing backsliding); Ch. 22 (Cleanup)

### 08.8 Test state through public APIs against real implementations or owner-maintained fakes, not mock choreography
- **Why:** Interaction tests prove the code tried, not that it worked, and weld tests to implementation structure; per-test mocks encode each author's guess about a contract they did not write and drift from reality, while a test needing many stubs exposes a design smell in the unit itself.
- **Applies:** Any test using verify-style assertions, widened visibility, or setup dominated by stubbed returns; production code whose hard-wired construction forecloses substitution — require seams.
- **Unless:** Doubles are right when the real thing is slow, nondeterministic, or side-effecting; interaction verification is legitimate when the interaction is the contract (send email, cache hit-count).
- **Source:** Ch. 12 (Test via Public APIs; Test State, Not Interactions); Ch. 13 (Test Doubles)

### 08.9 Hold tests to an obviousness bar: one named behavior each, no logic, DAMP over DRY
- **Why:** Tests have no tests of their own, so they must be verifiably correct on inspection — even one string concatenation can conceal the exact bug the test exists to catch, and clever shared helpers make failures undiagnosable.
- **Applies:** All test code in a diff, including shared fixtures and assertion helpers; failure output must name the behavior that broke, in given/when/then terms.
- **Unless:** Do not flag repeated literals in tests as a smell; separately tested test infrastructure and data builders with overridable defaults are fine.
- **Source:** Ch. 12 (Writing Clear Tests; Don't Put Logic in Tests; DAMP, Not DRY)

### 08.10 Demand the smallest hermetic, deterministic test that covers the risk; treat sleeps and flakiness as defects
- **Why:** A suite's value rests on speed and trust — tests lose all value as flakiness nears one percent, sleep-based waits silently tax every run, and a nonhermetic failure implicates the world instead of the change. But unit tests structurally miss config, load, and emergent cross-component behavior, so evidence must match the risk.
- **Applies:** New or modified tests and CI gates: question whole-stack SUTs, live third-party backends in presubmit, time-based synchronization, and green unit suites offered as proof for deployment-config or cross-service changes.
- **Unless:** Some emergent properties genuinely need production-like scope; a bounded timeout as a safety net around event-driven waiting is fine — the objection is sleeps as the mechanism.
- **Source:** Ch. 11 (Test Size; Flaky Tests Are Expensive); Ch. 14 (Larger Testing); Ch. 23 (Hermetic Testing; Takeout case)

### 08.11 Favor small shardable changes landing on trunk, with incomplete work flag-guarded
- **Why:** Small changes get thorough reviews, cheap bisection, and safe rollback — downstream code depends on new code almost immediately — while long-lived branches compound merge risk and months of hidden work carries compounded design error and a bus factor of one. Flags let a feature be toggled off without an emergency respin.
- **Applies:** Large batched diffs, plans to develop on a branch for weeks, wide refactors that should shard into independently correct pieces, risky features landing on a continuously released trunk.
- **Unless:** Semantically atomic changes (interface plus implementation, lockstep protocol) must land together; measure size by reasoning effort, not line count — never auto-reject on a number.
- **Source:** Ch. 2 (Hiding Considered Harmful); Ch. 9 (Write Small Changes); Ch. 16 (trunk-based); Ch. 22 (Sharding); Ch. 24 (flag-guarding)

### 08.12 Approve improvement over perfection; block only on concrete items; automate everything mechanical
- **Why:** Review ratchets code health upward — holding out for the reviewer's preferred design stalls progress, vague disapproval corrodes trust, and human enforcement of formatter-checkable rules is inconsistent and wasteful. A reviewer's own confusion, though, is a real defect: one confused reviewer predicts many confused maintainers.
- **Applies:** Review conduct itself: defer to the author among defensible approaches, tie every blocking comment to something fixable, push mechanical findings into formatters and analyzers, require restructuring or comments when the code needs oral explanation.
- **Unless:** Deference ends at actual deficiency; judgment calls (complexity, appropriateness) must not be reduced to numeric auto-reject thresholds; checks that are only probably right stay advisory, not blocking.
- **Source:** Ch. 9 (Code Correctness; Comprehension; Automate Where Possible); Ch. 19 (review tooling principles); Ch. 20 (Static Analysis)

## Review heuristics

- For any change to shared code, ask what incidental behavior (ordering, timing, error text, log format) shifts — not just whether the documented contract holds — and whether affected dependents' tests actually ran.
- For every claimed guarantee or bug fix, point to the CI-visible test that fails if the claim breaks; a fix without its regression test leaves the hole open.
- On any new dependency, fork, or vendored copy: is the same thing already in the tree, who owns the eventual forced upgrade, and is the version pinned with a hash in source control?
- On any deprecation or removal: name the replacement, the mechanism blocking new uses, and (for odd-looking deletions) evidence the author knew why the code was there.
- In tests: flag verify-style interaction assertions, stub-heavy setup, logic or loops in test bodies, sleeps as synchronization, and live external backends at the pre-merge gate.
- Ask whether this diff could have landed as smaller independent pieces, and whether unfinished paths are behind a flag rather than waiting on a branch.
