# 05. Refactoring: Improving the Design of Existing Code — Martin Fowler

> Fowler treats design as something you improve continuously through small, behavior-preserving steps, not something fixed up front. A restructuring is only real if tests prove behavior held before and after, and each change wears exactly one hat: reshape structure or change behavior, never both. The reviewer's job is to read where responsibilities live — behavior belongs with the data it uses, variation belongs in polymorphism, and every layer of indirection must pay rent — while resisting both speculative flexibility and speculative performance.

## Principles

### 05.1 Require self-checking tests and small steps before trusting any structural rework
- **Why:** Self-verifying tests plus frequent runs are what make restructuring safe; even a trivial extraction can silently change behavior, and a big-bang rewrite reviewed on faith hides regressions no reviewer can catch.
- **Applies:** Any diff that moves, renames, extracts, or reshapes existing code paths, and any PR claiming to be a pure refactoring.
- **Unless:** Mechanical tool- or compiler-checked renames; the standard is proportionate evidence per step, not exhaustive coverage.
- **Source:** Ch. 1 (The First Step in Refactoring); Ch. 4; Ch. 13

### 05.2 Reject diffs that mix behavior change with restructuring; one change, one hat
- **Why:** A mixed diff is unreviewable — you cannot tell which part of the delta was supposed to be behavior-neutral, so regressions hide inside the restructuring noise.
- **Applies:** Medium-to-large diffs interleaving renames, moves, and extractions with new logic or bug fixes.
- **Unless:** Tiny changes where separation is ceremony; a small preparatory refactor cleanly followed by the feature is the recommended workflow.
- **Source:** Ch. 2 (The Two Hats)

### 05.3 Enforce the Rule of Three on duplication: tolerate a second copy, block the third
- **Why:** Duplication's cost lands on the next edit — fix one copy, miss the sibling, and the system quietly diverges; identical members in sibling classes belong pulled up into one place.
- **Applies:** Copy-paste-modify within a class, across siblings, across unrelated classes, and repeated conditional structures.
- **Unless:** Code deliberately kept separate because the copies change for different reasons; a second occurrence is still tolerable.
- **Source:** Ch. 1; Ch. 3 (Duplicated Code); Ch. 11 (Pull Up Method, Form Template Method)

### 05.4 Move behavior to the data it uses; flag methods that mostly read another object's state
- **Why:** Feature envy — computing from chains of another object's getters — couples the caller to that object's internals and guarantees shotgun edits when the data changes; moving the method localizes future change.
- **Applies:** New or moved methods invoking several accessors on one collaborator; clients navigating getter chains across module boundaries.
- **Unless:** Patterns that deliberately separate behavior from data to isolate variation (Strategy, Visitor); roughly even interaction splits barely matter.
- **Source:** Ch. 3 (Feature Envy, Message Chains); Ch. 7 (Move Method, Hide Delegate)

### 05.5 Judge module boundaries by change axes: one kind of change should touch one module
- **Why:** Divergent change and shotgun surgery are the two failure modes of misplaced responsibility; when edits scatter, changes become hard to find and easy to miss, which is where regressions breed.
- **Applies:** Where a PR lands — one concern touching many modules, or one class repeatedly reopened for unrelated concerns.
- **Unless:** A one-time wide mechanical change (rename, API migration); the smell is a recurring pattern, not a single broad diff.
- **Source:** Ch. 3 (Divergent Change, Shotgun Surgery)

### 05.6 Push type-code switches into polymorphism when the same discrimination recurs or variants grow
- **Why:** Type-based conditionals get copied wherever the type matters, so each new variant means hunting every switch; putting varying behavior with the type makes adding a kind additive, and a factory keeps clients from picking subclasses themselves.
- **Applies:** Diffs adding a case to an existing type-switch, adding an enum-plus-if dispatch, or growing a boolean mode flag on a class.
- **Unless:** A few stable cases confined to one method — a hierarchy there is overkill; type codes carrying only data can stay values; behavior that changes mid-life needs delegation, not subclassing.
- **Source:** Ch. 1; Ch. 3 (Switch Statements); Ch. 8-9; Ch. 12 (Extract Hierarchy)

### 05.7 Reject speculative generality and make every indirection pay rent
- **Why:** Flexibility for imagined futures costs complexity everywhere while the predictions are usually wrong; each unused hop — middleman classes, pass-through methods, single-child abstractions, over-wide visibility — is pure tracing cost and should be inlined or hidden.
- **Applies:** Abstract classes with one concrete child, unused parameters, config for values that never vary, forwarding-only wrappers, and diffs widening visibility without a justifying caller.
- **Unless:** Indirection that currently isolates a real axis of change, shares real logic, or properly encapsulates a collaborator; invest up front only when no refactoring path to the future design exists.
- **Source:** Ch. 2 (Indirection and Refactoring); Ch. 3 (Speculative Generality, Middle Man, Lazy Class); Ch. 10 (Hide Method)

### 05.8 Distinguish public from published interfaces; only published ones need compatibility shims
- **Why:** An interface whose consumers you cannot edit is qualitatively different — breaking it strands them, so the old entry point should delegate to the new one and be marked deprecated; but treating in-repo APIs as published freezes structure prematurely.
- **Applies:** Any signature, module API, wire-format, or schema change; judging whether a compatibility layer is needed and whether it delegates rather than duplicates.
- **Unless:** All callers are reachable in this codebase — then rename and reshape freely; demanding shims there is itself the anti-pattern.
- **Source:** Ch. 2 (Problems with Refactoring: Changing Interfaces)

### 05.9 Refuse structure-degrading changes justified by unmeasured performance
- **Why:** Programs spend most time in a small fraction of code and intuition about hot spots is reliably wrong; well-factored code is easier to tune later, so trading clarity for guessed speed loses on both axes.
- **Applies:** Diffs and review comments justified by "this will be faster" with no profile attached; tangled structure defended as optimization.
- **Unless:** Hard real-time budgets per component, or changes backed by profiler evidence against a demonstrated hot spot.
- **Source:** Ch. 2 (Refactoring and Performance)

### 05.10 Treat what-comments as deodorant: demand extraction and intention-revealing names instead
- **Why:** Code is read far more than written; comments delimiting sections of a long method mark exactly the seams where a well-named unit should exist, and a good name closes the gap between what code does and how.
- **Applies:** Long methods sectioned by explanatory comments; names describing mechanism instead of purpose; thickly commented logic.
- **Unless:** Comments explaining why a decision was made or flagging genuine uncertainty — those are explicitly valuable.
- **Source:** Ch. 1 (renaming amountFor); Ch. 3 (Long Method, Comments)

### 05.11 Turn data clumps and overworked primitives into named types with the behavior moved in
- **Why:** Values that always travel together (start/end, amount/currency) are an object waiting to be born; naming it collapses parameter lists, and duplicated manipulation across callers becomes methods in one home. Data-bag classes manipulated in detail from outside spread their logic into every client.
- **Applies:** Growing parameter lists, repeated argument groups, domain concepts as bare strings and ints accumulating behavior, getter-setter-only classes with mature logic living in clients.
- **Unless:** One-off pairs; DTOs at serialization or trust boundaries as a starting point; values with no behavior yet; and passing the whole object is wrong when the method should not depend on that type.
- **Source:** Ch. 3 (Data Clumps, Primitive Obsession, Data Class); Ch. 8, 10 (Introduce Parameter Object, Replace Data Value with Object)

### 05.12 Objects control their own state: no mutable collection handouts, no mutating queries, no setters for construction-only fields
- **Why:** A getter returning the live collection lets any client corrupt the owner behind its back; a query that mutates is a trap for every caller; a setter on a never-changing field advertises mutability the design does not intend. Each removes the ability to enforce invariants at one point.
- **Applies:** Public protocol changes: collection-exposing accessors, methods that both answer and modify, and value-like classes (money, ranges, ids) gaining setters.
- **Unless:** Private helpers within one class; non-observable caching inside a query; fields that legitimately vary over the object's life — though collections still prefer add/remove over wholesale replacement.
- **Source:** Ch. 8 (Encapsulate Collection); Ch. 10 (Separate Query from Modifier, Remove Setting Method)

## Review heuristics

- If the PR says "refactor", check that tests existed and passed before the change and that no behavior delta hides in the diff; if it mixes restructuring with a fix or feature, ask for the hats to be separated.
- Count copies: a third occurrence of a rule, calculation, or conditional structure blocks the diff until it lives in one place.
- For every new or moved method, ask whose data it reads most — if the answer is another class, it probably belongs there.
- A new case added to an existing switch on type/kind/status, or a new boolean mode flag, is a prompt to ask for polymorphic dispatch, not a rubber stamp.
- Strip anything justified only by the future: unused parameters, single-implementation abstractions, "for later" hooks, and performance hacks without profiler numbers.
- Scan public surfaces for leaks: returned mutable collections, getter chains through delegates, query methods that write state, setters on construction-only fields, and forced downcasts at call sites.
