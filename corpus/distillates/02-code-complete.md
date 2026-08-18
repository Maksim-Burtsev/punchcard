# 02. Code Complete — Steve McConnell

> Construction is an engineering discipline governed by evidence, not taste: complexity is the primary enemy, data beats dogma, and defects follow measurable patterns — they cluster in hotspot modules, peak in "trivial" one-line changes, hide at boundaries and interfaces, and grow ten to a hundred times costlier the longer they go undetected. A reviewer in this book's mold judges a diff by the mental load it imposes on the next reader, checks that secrets stay hidden and validation barricades stay intact, and never accepts green tests as a substitute for demonstrated understanding.

## Principles

### 02.1 Judge every design choice by how much of the system a reader must hold in mind to change it safely
- **Why:** Managing complexity is the book's Primary Technical Imperative: no one fits a whole program in their head, so each piece must be understandable in isolation. A design forcing you to understand distant parts to touch one part is failing at its main job.
- **Applies:** Any non-trivial change; especially clever-versus-plain trade-offs and new module decompositions.
- **Unless:** Essential domain complexity must live somewhere — target the accidental kind; and abstraction layers added for their own sake raise reader load rather than lower it.
- **Source:** Ch. 5 Design in Construction; Ch. 34.1 Conquer Complexity

### 02.2 Require each class or module to hide an identifiable secret, and reject units that hide nothing
- **Why:** Information hiding is one of the few design techniques with measured evidence behind it; asking "what should this hide?" settles interface disputes better than "what is convenient to expose?". A pure data bag, verb-named do-er, or god class adds surface and coupling without paying for itself.
- **Applies:** New classes and modules, interface changes, anything exposing raw representation (fields, formats, container types) to callers.
- **Unless:** Utility groupings and plain data carriers at a boundary designed as data are legitimate; the hiding mechanism can be as small as a named constant.
- **Source:** Ch. 5 Hide Secrets; Ch. 6.4 Reasons to Create a Class

### 02.3 Flag semantic coupling: callers depending on how a module happens to behave rather than what it promises
- **Why:** Ordering assumptions, skipped init because another call "already does it", control flags interpreted inside, and hidden setup by sibling routines all break silently when the callee changes — and no compiler or type checker catches it.
- **Applies:** Inter-module interactions in the diff; the tell is that understanding the caller required reading the callee's implementation.
- **Unless:** Documented contract behavior is fair to rely on; the fix for an unclear contract is better interface documentation, not banning the usage.
- **Source:** Ch. 5 Kinds of Coupling; Ch. 6.2 semantic encapsulation violations; Ch. 14.1

### 02.4 Enforce the barricade and one system-wide error strategy: validate at the trust boundary, assert the impossible inside, and never let errors vanish silently
- **Why:** Concentrating validation at an explicit boundary relieves the bulk of the code of checking duty and makes the assertion/error split unambiguous: assertions for impossible states (bugs), error handling for expected off-nominal conditions — loud in development, gentle in production. Robustness-versus-correctness is an architectural stance (safety code prefers no result to a wrong result; consumer code prefers degrading to dying), so ad hoc per-patch conventions produce a system nobody can reason about, and empty catch blocks or ignored return codes let errors propagate undetected.
- **Applies:** Input paths, new external interfaces, stringly-typed values flowing past the entry point; new asserts, catches, error returns, retries, fallbacks — compared against the codebase's established policy.
- **Unless:** High-reliability systems may legitimately both assert and handle; some data genuinely needs cleaning at more than one level — but checking everything everywhere makes code fat, slow, and itself buggy. If the codebase has no articulated strategy, the finding is the missing strategy, not the individual patch.
- **Source:** Ch. 3 architecture checklist; Ch. 8 Defensive Programming (8.2–8.8); Ch. 34.1

### 02.5 Demand decomposition on measured complexity signals — nesting, decision points, mixed responsibilities — never on line count
- **Why:** The book's data shows routines up to 100–200 lines are not more error-prone and mandated tiny routines gave no benefit, while nesting past three levels and roughly ten decision points do correlate with faults. This cuts both ways: it blocks bloat and blocks under-10-lines dogma.
- **Applies:** Length debates; routines crossing ~3–4 nesting levels or ~10 branches; flag parameters selecting between behaviors as proof a routine does two things.
- **Unless:** A long flat case statement can legitimately exceed the threshold; splitting only relocates decision points, so demand it only where it reduces what a reader juggles at once.
- **Source:** Ch. 7.4 How Long Can a Routine Be?; Ch. 19.4, 19.6

### 02.6 Read names as design findings: a routine that cannot be honestly named has a purpose problem
- **Why:** A name that would need "AndOpenOutputFile" appended reveals a hidden side effect to eliminate; wishy-washy verbs (Handle, Process, Perform) signal weakness of purpose. Trouble naming the thing means the thing is wrong, not the label.
- **Applies:** New public routines and classes; names whose meaning drifted because the change altered what the value holds.
- **Unless:** Not a license to bikeshed synonyms — if the responsibility is crisp and the name states it, move on; sometimes a rename is the whole fix.
- **Source:** Ch. 7.3 Good Routine Names; Ch. 11.1

### 02.7 Discipline every variable's lifecycle: narrowest scope, initialization next to first use, one purpose, no in-band hidden meanings
- **Why:** Span and live time measurably predict defects; a count that becomes an error flag at -1 forces every consumer to know a secret encoding; and code written for one pass will eventually be wrapped in a loop, so reset-on-every-iteration must be assumed, not hoped.
- **Applies:** New state, variables promoted to fields or globals, reused temporaries, sentinel encodings, counters and accumulators near loops.
- **Unless:** Constants and read-only configuration are fine at broad scope; idiomatic ecosystem-wide sentinels are lower risk than bespoke double meanings.
- **Source:** Ch. 10.3–10.4, 10.8; Ch. 13.3 Global Data

### 02.8 Move volatile knowledge out of control flow into data, and give every change-prone value a single point of control
- **Why:** Knowledge stored in tables and named constants makes a rate change a data edit instead of a logic edit with a retest of every branch; scattered literals and mixed constant/literal representations silently diverge when the definition changes.
- **Applies:** Growing if/else or case chains encoding business facts (rates, mappings, classifications); repeated literals; a named constant used in some places and a raw literal in others.
- **Unless:** A handful of stable cases reads clearer as direct logic; late binding (config files, runtime lookup) must be justified by an actual requirement, since flexibility beyond need is complexity.
- **Source:** Ch. 10.6 Binding Time; Ch. 12.7; Ch. 18 Table-Driven Methods

### 02.9 Price every defect at its detection delay: catching it at review time is the cheap end of a 10–100x cost curve
- **Why:** The book's hard data shows fix cost multiplies with the gap between when a defect is introduced and when it is found — up to 10–100x by post-release — and its named General Principle of Software Quality holds that improving quality reduces development cost, because debugging and rework consume about half of a traditional development cycle. Thorough review is not overhead taxing delivery; it is the cheapest point on the curve, and teams that shift detection earlier cut cost and schedule, not just defect counts.
- **Applies:** Pushback of the form "QA or production will catch it"; schedule pressure to shallow out review depth; triaging whether a real defect finding justifies blocking a merge — it almost always does, on economics alone.
- **Unless:** The multiplier is steepest for requirements and architecture defects; construction defects caught in system test run nearer 10x than 100x, so don't overclaim. Style and cosmetic findings carry no multiplier and cannot borrow this argument.
- **Source:** Ch. 3.1 Table 3-1 (hard data); Ch. 20.4–20.5 General Principle of Software Quality

### 02.10 Expect adversarial tests to dominate, and never let green tests substitute for review or understanding
- **Why:** Every single defect-detection technique modally misses a large share of defects — unit testing catches only ~30%, while formal code inspections catch ~60%, roughly double — and each finds different kinds, so removal rates above 95% come only from combining reviews with tests; green unit tests alone leave most defects standing. Mature organizations run about five breaking tests per confirming one; a happy-path-only suite has demonstrated the intent, not challenged it.
- **Applies:** Every non-trivial change: boundary triples (just below, at, just above), bad-data classes, compound extremes; test code itself reviewed at production rigor, since it often carries higher error density.
- **Unless:** Trivial pass-through code needs no adversarial suite; one representative per equivalence class beats a spray of values that reveal the same failure.
- **Source:** Ch. 20.3 Table 20-1; Ch. 21.1; Ch. 22.2–22.4, 22.6

### 02.11 Give tiny diffs full scrutiny — small changes are statistically the most error-prone
- **Why:** One-to-five-line changes peak in error rate precisely because everyone treats them casually: no desk check, no review, sometimes no run. One organization's one-line maintenance changes were wrong 55% of the time before it reviewed them, and 2% after.
- **Applies:** Hotfixes, one-line tweaks, "trivial" config or boolean flips, anything labeled too small to test.
- **Unless:** This raises rigor for small changes, never lowers it for large ones; scale depth to risk class — interface, schema, and boolean-logic edits are the high-risk bucket.
- **Source:** Ch. 21.1 (Freedman and Weinberg 1990); Ch. 24.5 Refactoring Safely (Yourdon 1986, Weinberg 1983)

### 02.12 Treat bug fixes as diagnosis: reject symptom patches, require a reproducing test and a sibling sweep, and escalate hotspots to redesign
- **Why:** First-attempt fixes are wrong more than half the time, and defects cluster hard — roughly 80% in 20% of routines. A special-case guard keyed to the failing input proves the author never understood the defect; organizations that rewrote their error-prone classes cut field defects tenfold.
- **Applies:** Every fix — ask whether it explains the failure mechanism or merely suppresses the observed instance; the Nth patch into the same repeatedly-fixed module argues for restructuring, not another patch.
- **Unless:** A documented, tracked mitigation shipped under pressure is legitimate if labeled as such; redesign demands need clustering evidence (bug history, complexity), not vibes.
- **Source:** Ch. 22.4; Ch. 23.3 Fixing a Defect

## Review heuristics

- Could you understand this diff without opening the implementation of what it calls? If not, name the semantic coupling as the finding.
- Locate the barricade: where exactly does raw input become validated, domain-typed data, and does anything inside re-check or — worse — trust too early?
- Count what the diff adds — decision points, nesting levels, collaborators touched — against the tests it ships; five new branches with one test is provably under-verified.
- Check first/at/just-past on every new comparison, loop bound, and index; ask the author for the endpoint argument, not a flipped operator that made tests pass.
- Grep for siblings: the same literal, the same pattern, the same defect elsewhere in the codebase — fixes and constants are wrong when they land in one of several copies.
- Apply full scrutiny inversely to size: the one-line hotfix gets the same evidence bar as the thousand-line feature.
- When asked to wave a defect through "because it'll get caught later", answer in cost multiples: later detection is the expensive end of the curve, and review is the cheap one.
