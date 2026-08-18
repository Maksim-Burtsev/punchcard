# 18. Just Enough Software Architecture — George Fairbanks

> Fairbanks treats architecture as risk management, not ceremony: design effort — and review effort — should rise and fall with the risk of failure, stopping the moment risk subsides. Qualities like security, latency, and modifiability live nowhere in particular; they emerge from structure and are kept alive by constraints, so a reviewer's job is to guard the constraints, demand that guarantees have locatable enforcement, and insist that intent be visible in the code itself rather than only in heads and documents. Comprehensibility is engineered the same way: parts hide the choices that may change, and every level of nesting stays a story someone can be dropped into. Models and arguments amplify reasoning but are not the system — risky claims need running evidence.

## Principles

### 18.1 Scale design rigor and demanded evidence to the risk of failure
- **Why:** Too little design where risk is high invites failure; too much where risk is low wastes time better spent coding. The same proportionality governs what proof a reviewer demands — measurement for risky claims, nothing extra for routine work.
- **Applies:** Every review: raise the bar for security, concurrency, scalability, or novel-domain changes; lower it for precedented, low-stakes tweaks.
- **Unless:** Never wave through a genuinely risky change because its diff is small, and never impose one-size-fits-all artifacts (mandatory diagrams, risk matrices) on trivial work.
- **Source:** Ch. 3 (Risk-Driven Model, 3.6 When to stop); 5.1; 4.4

### 18.2 For every guaranteed property, require locatable enforcement
- **Why:** The book's test for a hoisted property: either code actively manages it (a timeout, a supervisor, a regulator) or a deliberate structural constraint ensures it. A property nobody can point to is hope, not design.
- **Applies:** Changes claiming the system is now reliable, fast, secure, or crash-tolerant — ask where the enforcement lives.
- **Unless:** When the platform already hoists the property (GC, app-server concurrency), duplicating enforcement in application code is waste that may fight the platform.
- **Source:** 2.8 Architecture hoisting

### 18.3 Guard declared constraints: bending the style silently forfeits its qualities
- **Why:** A style's promised qualities (portability, reconfigurability, decoupling) derive directly from its constraints; one expedient exception — a layer calling upward, a filter sharing state, a second writer to single-writer data — keeps the name but loses the benefit, and destroys the ability to reason about the system. No constraints means no analysis.
- **Applies:** Diffs adding dependencies, communication paths, or escape hatches that cross a layered, pipeline, pub-sub, or single-writer rule; anything relaxing an enforced boundary.
- **Unless:** Constraints can be over-restrictive or obsolete; the remedy is a deliberate, visible revision of the constraint, not silent violation — and reviewers should not invent constraints no risk motivates.
- **Source:** 2.2; 14.1–14.3; 14.6; 14.11; 16.4

### 18.4 A quality claim must name its sacrifice and be falsifiable
- **Why:** There is no free lunch among quality attributes — every gain trades something away, and irrational choices survive because the rationale is never stated. A categorical label like "improves reliability" is equally unusable: only a scenario with stimulus, response, and measure lets anyone check whether the risk was actually mitigated and whether the tests exercise it. Claims nobody can object to hide risk.
- **Applies:** Changes justified by a quality attribute — caching, denormalization, abstraction layers, sync-vs-async, framework adoption; PR descriptions, ADRs, and diagrams whose boxes and arrows have no stated meaning. Check the sacrifice is named and does not invert this project's priority order.
- **Unless:** Routine implementation details with no quality-attribute impact need no rationale or scenario framing, and a rough sketch is fine when the question it answers is rough.
- **Source:** 5.4; 1.3; 16.2; 12.13; 3.3 (Describing risks); 12.11; 15.1

### 18.5 Distinguish problems to find from problems to prove; tests only cover the former
- **Why:** Any number of passing tests can miss a locking bug or an invariant violation, because "it never happens" claims must hold in every execution. Evidence for prove-type properties comes from structural constraints or analysis, not examples.
- **Applies:** Changes touching concurrency, protocol conformance, security invariants, or data integrity — anywhere the claim is universal.
- **Unless:** For find-type properties (this input yields this output), a direct test is exactly the right evidence and demanding proofs is overkill.
- **Source:** 3.5 (Problems to find and prove); 15.5

### 18.6 Put the burden of proof on deviations from the presumptive architecture
- **Why:** Dominant patterns (N-tier for IT, queues for messaging) dominate because they match the domain's recurring risks; developers who follow them almost always do fine, so the novel structure owes the justification, not the standard one.
- **Applies:** Bespoke messaging where the platform pattern is a queue, hand-rolled persistence beside the standard store, exotic topology for an ordinary workload.
- **Unless:** When the project's risks genuinely differ from the domain norm, conforming is itself the mistake — welcome a well-argued deviation.
- **Source:** 2.4 Presumptive architectures; 3.3 Prototypical risks

### 18.7 Require the architecture to be evident in the code itself
- **Why:** The model-code gap is inherent: boundaries, roles, and rationale the team debated are not expressed in source by default, and intent that lives only in heads or documents is lost. Packages should mirror components, wiring should be co-located or declarative, names should reveal role and intent — so a newcomer can recover the design from the diff.
- **Applies:** New modules, moved code, bootstrap and wiring changes, components assembled from slivers of scattered packages, dynamic configuration buried in imperative startup logic.
- **Unless:** This is about making existing intent visible, not documentation for its own sake; skip reification ceremony where there is no architectural intent to express.
- **Source:** 10.1; 10.3; 10.5–10.7; 9.7

### 18.8 Judge an interface by which secret it hides, not by whether it hides something
- **Why:** Encapsulation is not binary. An interface can conceal the implementation and still be ineffective because it leaks the implementor's own abstractions onto every caller — the timesheet form that made employees debit and credit accounts so the accounting department would not have to. The useful test is Parnas's: name the design secret, the choice between alternatives A and B that the interface lets you reverse later without the change rippling out to users. Getter-and-setter interfaces over internal data structures pass the "has an API" check and hide nothing. Effort here is risk-proportional too: pay for a strong API where exposing a data structure would be expensive to undo (published, external, cross-team, remotable), accept weak encapsulation where refactoring is cheap.
- **Applies:** New or widened public APIs, module and component boundaries, plug-in and extension points, data structures crossing a boundary. Ask what a caller now has to understand that belongs to the implementor, and which internal choice this interface still lets you change.
- **Unless:** An internal API used only by its authoring team, cheap to refactor, does not deserve crystal-ball design; keeping options open costs effort and complicates the design, so demand it only where the exposure is a real risk.
- **Source:** 11.4 Effective encapsulation (Parnas modules; judgment and risk); 1.1; 11.5

### 18.9 Ask whether each level of nesting still tells its own story
- **Why:** The book's comprehensibility test is that a developer dropped in at any level can make sense of what they find, treating everything below as a black box. Hierarchy alone does not deliver this: a system with one flat level, modules that are haphazard groupings, or boundaries that leak internals all defeat it. The guidelines are concrete — bounded element count per level (roughly 5 to 50), a coherent purpose per element, no unnecessary internals exposed — and levels themselves cost upkeep, so too few elements argues for collapsing a level, not adding one.
- **Applies:** New modules and packages, large decompositions, refactorings that add or remove a layer of nesting, components that have accumulated dozens of peers. Also placement questions: which existing level does this belong to, and does it make that level's story better or worse?
- **Unless:** Systems where the parts genuinely interact outside the hierarchy (shared power, heat, contention) resist clean nesting, and forcing it hides the coupling; also, the benefit is cognitive, so do not add bureaucratic levels a small system does not need.
- **Source:** 11.1 Story at many levels; 11.2 Hierarchy and partitioning; 11.3

### 18.10 Call out architectural bending: behavior bolted where it was expedient, not where it belongs
- **Why:** Systems erode into a big ball of mud one expedient placement at a time — a component fetching another's commands, a call path detouring around the intended owner, the same local patch duplicated where one shared fix belongs. Debt accumulates precisely because each bend looks harmless.
- **Applies:** Diffs where a component absorbs a responsibility that is not its own, cross-boundary calls bypass the declared connector, or one instance of a systemic issue gets a local patch siblings share.
- **Unless:** A deliberate, documented revision of the architecture is not bending; and for a genuinely one-off contained defect, the local fix is correct and generalizing is over-engineering.
- **Source:** 4.2.2; 2.6–2.7; 4.1 (architectural drift); 10.7 (connector types)

### 18.11 Trust the running system over the model for risky claims
- **Why:** Models amplify reasoning but are not the system: clean predictions fail against bursty load and real data's curveballs. The book settled its own latency risk by instrumenting a prototype, not by modeling harder.
- **Applies:** Performance, capacity, and compatibility claims backing a risky change — ask for a measurement, prototype, or demonstration; also walk one concrete scenario end-to-end through multi-component changes.
- **Unless:** Back-of-the-envelope reasoning is exactly right for low-stakes claims; demand running evidence only where failure would be expensive.
- **Source:** 15.5; 16.3; 4.2.3; 15.3 (animating scenarios)

### 18.12 At integration points, hunt for mismatched hidden assumptions and demand failure isolation
- **Why:** Seemingly compatible components fail to integrate over unstated assumptions about control, protocol and format, topology, and initialization order — and a crash-prone dependency needs containment (process isolation, adapters, heartbeats, clean restart), not a happy-path hookup. Surface compatibility while domain models conflict is the named trap.
- **Applies:** Diffs adding a library, vendor component, or dependency on another team's service; adapter code; changes to startup order. Cross-domain glue belongs in the connector, not smeared into a component.
- **Unless:** Mature dependencies with a track record here need no isolation harness; depth of scrutiny tracks how little is known and how bad failure would be.
- **Source:** 4.2 (COTS integration); 15.7 Architectural mismatch; 12.4 Connectors

## Review heuristics

- Ask "what risk does this change carry?" before deciding how much justification, testing, or measurement to demand — and stop when the risk is covered.
- For any "this guarantees X" claim, make the author point to the timeout, supervisor, DB constraint, or structural rule that enforces it.
- Trace new imports, calls, and shared state against the system's declared style: any upward layer dependency, filter back-channel, or bypass of a mandated path is a forfeited quality, not a shortcut.
- Rewrite the PR's quality claim as stimulus-response-measure; if you cannot, the claim is not reviewable and the tests cannot be checked against it.
- Check the diff's location against component responsibilities: would a newcomer reading only the source recover why this code lives here?
- On any new or widened API, ask two questions: what does this force the caller to know that is really the implementor's business, and what internal choice does it still let you reverse?
- Read the change at the level above it: does this module still have a coherent purpose and a readable number of neighbours, or has the level become a sea of parts?
- On concurrency, invariant, or protocol changes, refuse "the tests pass" as closing evidence — ask for the constraint or argument covering all executions.
