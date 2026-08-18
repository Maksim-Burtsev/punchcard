# 13. Implementation Patterns — Kent Beck

> Beck treats every line of code as an economic decision: software cost is dominated by maintenance, and maintenance cost is dominated by reading and changing code, so the highest-leverage property of any change is how clearly it communicates to the next programmer. Good structure keeps the consequences of future changes local and cheap; bad structure exports cost invisibly to distant code and later dates. A reviewer applying this book is not checking style — they are auditing whether the diff makes the next change cheaper or more expensive, and whether that bet is calibrated to the code's real audience.

## Principles

### 13.1 Judge names and decomposition by whether a caller can tell the story without reading the bodies
- **Why:** Code is read far more often than written, so programmer-to-programmer communication is the largest lever on total cost. Methods named for intent and composed of steps at one abstraction level let readers stop at the level they need.
- **Applies:** Any new public method or entry point; long methods mixing high-level steps with bit-twiddling; names encoding algorithm, scope, or type instead of purpose.
- **Unless:** Fragmenting into a dust of tiny methods scatters the idea as badly as one lump; compose structure from working code, not up-front speculation.
- **Source:** Chapter 3 (Values: Communication); Chapter 8 (Composed Method, Intention-Revealing Name)

### 13.2 Require that one idea be expressed the same way everywhere it appears, and that sibling statements sit at one level
- **Why:** Symmetry is conceptual, not graphical: once a reader understands one half of it, the other half comes free. A statement pitched lower than its neighbours breaks that — the reader must drop into mechanics to reconstruct why the step is there. The mismatch is the defect by itself, with or without duplication: a raw counter bump wedged between two intention-named calls is wrong even though it occurs exactly once, and renaming it after its purpose, not its implementation, is the fix.
- **Applies:** Statement sequences mixing named intentions with inline mechanics; paired operations (add/remove, open/close, encode/decode) where only one side follows the house convention; sibling methods, fields, or branches that solve the same shape of problem in visibly different shapes; a new case written unlike the cases beside it; fields in one object with unrelated lifetimes.
- **Unless:** Two things that merely resemble each other should not be forced into one form, and real asymmetry in the domain should stay visible rather than be smoothed away. Making copies symmetrical is also the first move toward unifying them — sometimes the whole move (13.5).
- **Source:** Chapter 3 (Principles: Symmetry)

### 13.3 Prefer a statement of the facts over a procedure that computes them
- **Why:** Imperative code obliges the reader to simulate control and data flow to answer questions that are plain facts. Where there is no genuine sequencing or branching, a declaration answers at a glance and forecloses hidden special cases — the reader can trust it without auditing a method body. The price is generality, and for facts that is the right trade. Beck's case is JUnit: a suite-building method has to be read to learn which tests run; an annotation listing the classes simply says so.
- **Applies:** Setup, wiring, registration, and configuration written as build-it-up routines; routes, schemas, permissions, test suites, or fixtures assembled by loops and conditionals over what is really a static list; variables declared far from where they first get a value; fields assigned by a constructor step that a declaration initializer would state directly.
- **Unless:** Values that genuinely depend on runtime conditions, or are expensive enough to defer, belong in imperative or lazy initialization; and do not invent a mini-language to declare what three plain lines already state.
- **Source:** Chapter 3 (Principles: Declarative Expression); Chapter 6 (Initialization, Eager Initialization)

### 13.4 Reject changes whose effects ripple beyond the code being edited, and keep what changes together together
- **Why:** Cost explodes when a change in one place forces or silently breaks changes in distant places; code with local consequences can also be understood piecemeal, without loading the whole system. Logic and the data it operates on change at the same moment, so separating them makes every future change non-local — the same argument, run over time, says things that change at different rates do not belong side by side.
- **Applies:** Diffs that touch shared state, widen coupling, or edit code with many distant dependents; computations added to one module over data fetched from another; feature envy fed by abundant getters; new fields that do not live and die with their object; volatile rules threaded into otherwise stable code.
- **Unless:** Some changes are genuinely cross-cutting; then ask whether the structure could make the next such change local, rather than blocking this one. Splitting by rate of change is speculative until two parts have demonstrably diverged.
- **Source:** Chapter 3 (Principles: Local Consequences, Logic and Data Together, Rate of Change); Chapter 6 (Indirect Access, Common State)

### 13.5 Flag repetition in every form, including parallel structures that must change in lockstep
- **Why:** Every copy converts one local change into several coordinated ones. Parallel class hierarchies are the pernicious case: adding a variant means editing two structures, a coupling with no copied text to search for.
- **Applies:** Additions that repeat an existing branch, mirror an existing hierarchy, or paste-and-edit logic from elsewhere.
- **Unless:** Duplication is a cost, not a sin; where no clean unification is visible, making the copies symmetrical (13.2) beats forcing a premature abstraction.
- **Source:** Chapter 3 (Principles: Minimize Repetition); Chapter 5 (Subclass)

### 13.6 Make every abstraction pay for itself with a need the change has right now
- **Why:** Flexibility is the value most abused to justify bad design: each interface layer is another thing to learn, debug, and maintain, and speculative generality usually prepares for the wrong change while obstructing the real one. Shared abstractions should cover the intersection of several real uses, never the union of imagined ones.
- **Applies:** Interfaces with one implementation, config knobs for values that never vary, pluggable seams with no second plug, hooks justified by future-proofing prose, shared-module features serving one client.
- **Unless:** Published boundaries the author cannot later change (frameworks, public APIs) justify buying flexibility up front; genuinely common needs that every client would otherwise reimplement belong in the shared layer.
- **Source:** Chapter 3 (Values: Flexibility); Chapter 10 (Conclusion)

### 13.7 Demand a clean line between immutable values and stateful objects, preferring values
- **Why:** A value set fully in its constructor eliminates whole classes of reader questions — nothing changes behind your back, and call order stops carrying hidden meaning. Half-mutable objects are the worst of both worlds: complex interfaces with no safety guarantees.
- **Applies:** New domain types (money, transactions, coordinates, requests); setters added to a type that conceptually never changes after creation; interfaces where call sequence is an implicit contract.
- **Unless:** Genuinely evolving entities are properly stateful; allocation-cost objections against values need a profiler, not folklore.
- **Source:** Chapter 5 (Value Object)

### 13.8 When a conditional structure recurs or a switch grows with every feature, require dispatch instead of another branch
- **Why:** Each added path lowers the odds the whole program is correct, and a duplicated type-switch means every new variant edits several places in shared code, risking existing behavior. A message turns the choice point into an extension point.
- **Applies:** Diffs adding a case to an existing type-switch, copying a branch structure into a second method, or branching on fast-changing criteria; behavior that must change at runtime wants delegation over subclassing.
- **Unless:** A single, local, stable conditional is simpler than dispatch smeared across classes; do not demand polymorphism where there is no variation.
- **Source:** Chapter 5 (Conditional, Delegation); Chapter 7 (Choosing Message)

### 13.9 Verify the main flow reads straight through, with exceptions reserved for failures that cross call-stack levels
- **Why:** Nested precondition conditionals bury the important path and breed defects; exceptions used as ordinary control flow put adjacent logic in distant methods. At a boundary, a raw low-level failure confuses the catcher — wrap it in the layer's vocabulary while preserving the cause.
- **Applies:** Deeply nested null and validity checks that guard clauses would flatten; exceptions thrown and caught in the same routine; infrastructure exceptions escaping a module's public surface; rethrows that discard the original cause.
- **Unless:** Some hostile-environment systems have no dominant main flow; within one layer, wrapping is pure ceremony; single-exit dogma must not be turned against guard clauses.
- **Source:** Chapter 7 (Main Flow, Guard Clause, Exception, Exception Propagation)

### 13.10 Read declared types and collection choices as documentation, and hold them to it
- **Why:** Declaring against the most general sufficient interface confines implementation knowledge to one place, while the structure's contract — ordering, uniqueness, keyed access — states the domain invariant; the wrong choice either loses information silently or advertises a guarantee the code does not keep. And any mutable owned collection handed across a boundary silently transfers write access to the owner's invariants.
- **Applies:** Signatures and fields crossing module boundaries; new collection-shaped state; structure-type swaps; getters returning owned collections to outside callers.
- **Unless:** Never weaken a type below what the caller needs (stable order means List, not Collection); locals gain little from generalization; defensive copies are waste when receiver and owner share a module and mutation is the protocol.
- **Source:** Chapter 9 (Collections: Interfaces, List/Set/Map, Unmodifiable Collections)

### 13.11 Treat any widening of a public surface as a purchased promise, and price boundary changes by downstream breakage
- **Why:** Every revealed operation is a maintenance commitment — leave it unchanged, fix all callers, or notify them; revealing later is cheap, retracting is expensive. Where the maintainer cannot update client code, the economics inverts outright: the deployment cost of an incompatible change dwarfs the cost of tolerating more complex internals. So breaks must be staged — deprecate before removing, keep delegating overloads, split interface and implementation releases — and interfaces clients implement must not grow new methods, since each one breaks every implementor.
- **Applies:** New public methods, exposed fields, internals promoted for testing or convenience; removals, renames, signature or behavior changes on frameworks, libraries, plugin APIs, wire formats; choosing interface versus superclass for a new extension point; setters and boolean parameters on published surfaces that hard-code today's representation into every call site.
- **Unless:** A too-narrow interface makes every client work harder — balance the costs rather than minimizing exposure dogmatically, and let some private methods legitimately graduate. Inside an application where all callers update in the same change, compatibility shims are pure debt; parallel old/new paths without a retirement plan are worse than either alone.
- **Source:** Chapter 8 (Method Visibility); Chapter 5 (Interface); Chapter 10 (Encouraging Compatible Change; Incompatible Upgrades; Abstraction: Interface and Superclass; Methods)

### 13.12 Calibrate rigor to audience and evidence: performance claims need profiles, design investment needs consumers
- **Why:** The book's own benchmarks debunk tuning folklore — real wins are algorithmic — so unmeasured optimization buys complexity with imaginary benefit. Likewise its own timing framework keeps duplication and constants because it serves one book: internal single-purpose code and widely consumed code deserve different design philosophies, and both extremes as dogma are wrong.
- **Applies:** Any change justified by a faster rationale without measurements; deciding whether a finding is worth demanding — the same defect can be acceptable in a throwaway script and blocking in a shared library.
- **Unless:** When a profile accompanies the change, judge the fix on the data (and check the swap keeps semantics). Audience never excuses correctness, data-loss, or trust-boundary defects, and internal stops applying once other teams depend on the code.
- **Source:** Appendix A (Performance Measurement: Conclusion); Chapter 10

## Review heuristics

- For each edited unit, ask what else must change when this code changes next; a diff that widens that set needs a justification, one that shrinks it is the point.
- Read every new name from the call site: if you must open the body to know what it does, or the name leaks the algorithm, flag it.
- Read a changed sequence as a list and check the parts are pitched alike: an inline mechanic sitting among intention-named calls, or one side of a pair following a different convention from the other, is a finding on its own — no second copy required.
- On any setup, wiring, registration, or configuration block, ask what question a reader would bring to it and whether they must trace execution to answer. If the code is really a fixed list of facts, ask for a declaration instead of a routine that builds one.
- On any new public method, interface member, getter, or exposed field: name the client that needs it today, and price the promise being made.
- On any new conditional, search for the same branch structure elsewhere; if a future variant would edit two or more places, ask for dispatch or at least a note of the coupling.
- On any returned or stored collection: does the declared type state the real invariant, and can an outsider mutate the owner through it?
- Strike the words flexible, future-proof, and faster from the description and see what justification remains; demand a concrete present need or a profile to fill the gap.
