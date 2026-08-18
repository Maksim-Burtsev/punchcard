# 23. Code Reading: The Open Source Perspective — Diomidis Spinellis

> This book treats reading code, not writing it, as the central professional skill, and a reviewer is simply a reader with the authority to say no. Its claim is that even enormous systems stay tractable because a competent reader can locate the relevant parts, understand them in isolation, and then reason about their relationship to the rest — so the reviewer's job is to check that a change respects that reading discipline. It refuses to confine "code" to executable statements: build files, configuration, the directory tree, and the documentation are all machine-readable project elements that break systems when wrong. And it insists the reader use instruments — compiler, warnings, revision history, the architecture the code already follows — rather than trusting recall or personal taste.

## Principles

### 23.1 Bound what a reviewer must understand: a change should be verifiable from a small local region plus a named impact area.
- **Why:** Large systems are modified successfully by locating the relevant parts and understanding them in isolation. If verifying a diff means opening an ever-widening fan of files, the change is either badly placed or badly bounded.
- **Applies:** Feature work and modifications in large or unfamiliar codebases; any change whose correctness argument keeps pulling in more subsystems.
- **Unless:** Some changes are inherently cross-cutting (a shared interface rename, a protocol bump). And a small diff is not by itself evidence of good scoping — the impact area must be understood, not ignored.
- **Source:** Ch. 1 (Evolution); Ch. 11 (limiting the extent of code you must understand)

### 23.2 Demand a mechanical trace of affected call sites, and know where the machine stops helping.
- **Why:** The compiler and its cascade of errors and warnings is the practical instrument for discovering what an interface change touches, precisely because human impact analysis misses sites. Ask for the trace rather than trusting the author's recall.
- **Applies:** Signature changes, type changes, semantic changes behind an unchanged signature, porting between similar environments.
- **Unless:** The tooling is blindest where the risk is highest — dynamic dispatch, reflection, string-built calls, and semantics changed under a stable signature. "It builds" is not impact analysis for those.
- **Source:** Ch. 1 (Evolution); Ch. 2 (Functions and Global Variables); Ch. 10

### 23.3 Require the path from symptom to fault, and reject fixes applied where the failure merely showed up.
- **Why:** The maintenance reading strategy runs from manifestation back toward source, refusing detours. A patch at the manifestation point silences one output while leaving the defect and its other victims in place.
- **Applies:** Every defect fix, especially in systems where the failing output is far from the faulty logic.
- **Unless:** An urgent boundary mitigation or a containment guard is legitimate when labeled as containment and followed by the real fix — not when presented as the cure.
- **Source:** Ch. 1 (Maintenance)

### 23.4 Before calling code needlessly odd, find the non-functional constraint that shaped it.
- **Why:** Portability, space, timing, and even deliberate obscurity produce implementations with peculiar characteristics that look wrong read out of context; an apparent problem often turns out on closer inspection to be perfectly good code. Ask the author to record the constraint where the next reader will meet it.
- **Applies:** Review comments on unusual data layouts, hand-optimized routines, awkward interfaces, anything a naive rewrite seems to improve.
- **Unless:** This is not a shield for unexplained cleverness. If no constraint can be named, or it expired with the platform that imposed it, the odd code is just odd and the simplification stands.
- **Source:** Ch. 1 (Code as Literature)

### 23.5 Review the whole project element, not only the statements: build files, configuration, file placement, interface, documentation.
- **Why:** The book's inspection guidance widens "code" to every machine-readable part of a project. An omitted build dependency yields stale artifacts that behave unlike the code under review; a misfiled module hides itself from everyone navigating by structure. Prefer dependencies derived from the sources over hand-kept lists, and isolate platform variation in dedicated files the configuration step selects.
- **Applies:** Changes adding modules, dependencies, generated code, deployment knobs, or new configuration surfaces.
- **Unless:** Do not make this a checklist tax on trivial diffs, and do not ask for hand-listed edges the build system already discovers. One genuinely local platform difference is cheaper inline than a new abstraction layer.
- **Source:** Ch. 1 (Inspections); Ch. 6 (Project Organization, Build Process, Configuration)

### 23.6 Treat any correspondence between two declarations that nothing verifies as a defect.
- **Why:** Parallel arrays of codes and messages, allocation sizes written as separate literals, duplicated layouts and enum/table pairs all keep compiling after one side moves, then fail unpredictably much later. The worked example's own bug was an entry inserted in the wrong order into an unaligned table. Derive the dependent value from the thing it describes, or make drift loud.
- **Applies:** Registration into lookup tables, dispatch arrays, keyword lists and error catalogues; serialization layouts; sizes; structures mirrored by documentation.
- **Unless:** Where the language cannot express the derivation, a stated invariant plus an assertion or test that fails on divergence is acceptable. Cosmetic alignment is not an enforced invariant — do not mistake one for the other.
- **Source:** Ch. 4 (Matrices and Tables); Ch. 11 (Testing and Debugging)

### 23.7 Name the architecture, framework, or pattern the code already follows, and review the change against that — not against the design you would have chosen.
- **Why:** Implementers rarely document the architecture they reuse, considering it common knowledge, and patterns are frequently present with no reference to them anywhere in the source. Recognizing the form gives you a documented description to check against and a vocabulary for the review; a change written in a style foreign to its surroundings adds a second architecture to maintain.
- **Applies:** Non-trivial changes inside a subsystem that visibly follows a repository, pipeline, layered, boss/worker, state-machine, or framework structure.
- **Unless:** Real systems legitimately blend styles, patterns are a vocabulary and not a requirement, and conformity is not the goal — the point is to see where the change uses the architecture and where it abuses it. A deliberate, argued style change is fine when the old style is the actual problem.
- **Source:** Ch. 9 (Architecture Reuse, Design Patterns, Domain-Specific Architectures)

### 23.8 Keep boundaries physical and one-directional: a module is a file, directory, or prefixed group with a published interface, and no layer may learn who calls it.
- **Why:** Physical structure is the readable statement of the architecture. A layer stays replaceable only while it makes no assumption about its users, so usage dependencies must flow strictly downward. Anything needed in one file should be confined to it — broadly visible names collide with same-named names elsewhere, and visibility is enforced only at review time.
- **Applies:** New globals, types, macros and exported functions; new files and relocations; parameters or flags that encode caller identity.
- **Unless:** Results legitimately travel upward through callbacks, interrupts, and wakeups — the ban is on usage dependencies. Trees grow historically and one feature diff is not the place to fix inherited inconsistency; some state really is process-wide.
- **Source:** Ch. 9 (Layered Architectures, Slicing); Ch. 2 (Functions and Global Variables); Ch. 6 (Project Organization)

### 23.9 Read documentation and comments as unverified claims, and reconcile them with the code instead of believing them.
- **Why:** Nothing compiles or tests prose, so it drifts toward describing the system as intended rather than as built. When code and text disagree, decide which is wrong. An undocumented behavior is either a defensible omission, a careless one, or a hostile one — a support hook, an exposure, a back door — and only the classification says what to fix.
- **Applies:** Changes adding options, flags, protocol fields, or user-visible behavior; any hidden entry point found while reading; diffs where the description and the code diverge.
- **Unless:** Documentation still shortens comprehension and often reveals the true structure, so use it as a hypothesis rather than discarding it. Experimental or deliberately unsupported features may legitimately stay undocumented — the omission just has to be a decision.
- **Source:** Ch. 8 (Documentation Problems)

### 23.10 Read the change's history, not only the change: repeated fixes to one region indicate a design defect, and one mistake usually has siblings.
- **Why:** Repetitive or conflicting patches to the same code mark a fundamental deficiency that maintainers keep papering over, and similar fixes scattered across the tree indicate an error that is easy to make and probably still lurking in places nobody has visited. Reviewing only the diff at hand ships the siblings broken.
- **Applies:** Bug fixes in code that has been fixed before; duplicated idioms and copy-adapted code; hot spots visible in revision logs or trackers.
- **Unless:** Churn also just means the area is under active development. And the mandate is to check for other instances and decide, not to turn every fix into a repo-wide refactor.
- **Source:** Ch. 8 (Documentation as evidence); Ch. 6

### 23.11 Expect a proven baseline: the system built and run unchanged, warning-clean at the project's level, before and after the change.
- **Why:** Building and running the untouched system proves the sources and toolchain are sound, teaches the build the author will exercise repeatedly, and fixes a dependable starting point so later breakage cannot be blamed on pre-existing conditions. Warnings are the compiler's definitive analysis — implicit conversions, assignment where comparison was meant, shadowed declarations, missing cases, missing returns.
- **Applies:** Changes to unfamiliar or infrequently built systems; any bug report starting from an unreproduced failure; any language with a warning-capable compiler or lint.
- **Unless:** Redundant where CI already proves a green baseline per commit. The warning level should match local practice rather than being maximal on principle — code added purely to silence a warning can cost more readability than the warning did.
- **Source:** Ch. 10 (The Compiler as a Code-Reading Tool); Ch. 11 (Overview, Observations)

### 23.12 Prefer porting a proven implementation to writing a new one, and suspect exactly the fragments that were rewritten rather than copied.
- **Why:** In the worked example the author copies an existing algorithm nearly verbatim and rewrites one loop — and that loop is where the defect lands, because the original constant carried an implicit platform offset the reimplementation silently dropped. When the output came out wrong, the rewritten part was the suspect before debugging began.
- **Applies:** Changes reimplementing an algorithm, protocol, or formula that already exists in the tree or a dependency.
- **Unless:** Faithful transcription is not mindless transcription — epochs, units, offsets, and encodings the source assumed about its own environment are exactly what fails to carry over, and each needs a check against a value obtained independently of the code.
- **Source:** Ch. 11 (Code Reuse, Testing and Debugging)

## Review heuristics

- Count the files you had to open to convince yourself the diff is correct; if the count keeps growing, say so as a scoping objection, not as a nitpick.
- For every interface touched, ask how the call sites were found — and separately ask what dynamic dispatch, reflection, or unchanged-signature semantics the compiler could not have caught.
- On a bug fix, ask for the chain from symptom to fault, then grep for the same mistake elsewhere and check the revision log for previous fixes in the same region.
- Look outside the source files: build and dependency declarations, configuration, where new files were filed, and whether the documentation changed with the behavior it describes.
- Hunt for two declarations that must agree with nothing enforcing it — parallel tables, sizes as literals, code/message pairs, docs mirroring an enum — and ask for derivation or an assertion.
- Before proposing a rewrite of odd-looking code, name the constraint that produced it; if you cannot and the author cannot, the simplification is justified.
- Name the pattern or architectural style the surrounding code uses and check the change against it, including whether any lower layer just learned the identity of a caller.
