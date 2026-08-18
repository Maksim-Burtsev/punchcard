# 04. The Practice of Programming — Brian W. Kernighan & Rob Pike

> Programming is a craft whose first materials are simplicity, clarity, and generality: programs are read and changed by people, so a construction is judged by how easily a maintainer comprehends it, not by how little it types. The design lives in the data — get the layout right and the code falls into place; get it wrong and no local edit saves it. Complexity must be earned by measurement, contracts at boundaries must be explicit, and any deviation from the standard way of writing a standard thing is where the bugs hide.

## Principles

### 04.1 Judge code by ease of comprehension, and treat any deviation from established idiom as a bug signal
- **Why:** When the same computation is written the same way everywhere, variation marks a genuine difference; nonstandard forms of standard loops, allocations, and copies are where off-by-one and overflow bugs live. Clarity is not brevity or verbosity — it is whatever a maintainer decodes fastest, even if longer.
- **Applies:** Any diff with dense expressions, trick control flow, a homegrown variant of an operation the codebase already does one way, or new code that ignores surrounding conventions.
- **Unless:** Do not demand the surrounding legacy style be rewritten to taste — preserve the style of code you did not write; and do not confuse clarity with bloat (long names for tiny locals, spelled-out forms where an idiom is shorter).
- **Source:** Chapter 1: Style (1.1–1.3, 1.7)

### 04.2 Give every fact one authoritative source: name constants, derive derived values, generate duplicated representations
- **Why:** Raw literals hide their derivation and their relationships to each other, making change unsafe; hand-mirrored copies of one fact (enum and its message table, size and its format string) inevitably drift apart. Sizes should come from the language itself so code survives a type change untouched.
- **Applies:** Unexplained numeric literals, a limit repeated in two places, and any diff where editing one artifact silently obligates editing another by hand.
- **Unless:** 0 and 1 in ordinary roles need no names; for one or two stable facts a cross-referencing comment beats generation machinery, and generated files must be clearly marked and rebuilt automatically or they become the stale copy.
- **Source:** Chapter 1: Style (1.5); Chapter 9: Notation (programs that write programs)

### 04.3 Review the data structures before the code: the layout of the data is the design
- **Why:** Once the data structures are right, the algorithms fall into place — the book's Markov program survived rewrites in five languages because its data model was correct. Code shaped by the wrong data model cannot be fixed line by line.
- **Applies:** New modules and features, and any change that adds or reshapes persistent or shared representations; start the review there, not at the diff hunks.
- **Unless:** Some representation choices are genuinely interchangeable (list vs. growable array); do not force debate on choices that do not matter.
- **Source:** Chapter 3: Design and Implementation (intro, 3.9)

### 04.4 Push irregularity into the data so control flow stays regular; repetitive code is structure that belongs in a table
- **Why:** Code is harder to get right than data: a sentinel or uniform initialization deletes the first-iteration and last-element branches entirely, and a compact declarative spec (format string, handler table, tiny language) collapses thousands of copy-paste case lines into a driver plus data.
- **Applies:** Diffs adding empty-input or boundary special cases a sentinel would remove, and families of near-duplicate functions or long switch chains where each new case clones the last.
- **Unless:** Genuinely messy input formats legitimately need parse-level special cases; and never invent a notation for two or three cases — the spec language must stay smaller and clearer than the code it replaces.
- **Source:** Chapter 3 (3.4); Chapter 9: Notation (pack/unpack, little languages)

### 04.5 For anything others will call, demand explicit answers: what it promises, what it hides, who owns each resource, how errors reach the caller
- **Why:** The book's CSV prototype failed as a library precisely because these decisions were implicit and woven through the code; quick unexamined choices in a shared interface surface as trouble years later. Whatever clients can see becomes the interface de facto, freezing the implementation.
- **Applies:** New public APIs, module boundaries, and changes that alter an existing contract's ownership or error semantics; also any diff exposing internals (public fields, returned mutable state) clients could start depending on.
- **Unless:** A throwaway prototype or single-caller internal helper does not need this rigor — provided it is recognized as disposable and not silently promoted to shared code.
- **Source:** Chapter 4: Interfaces (4.2, 4.3, 4.5)

### 04.6 Reject interfaces that reach behind the caller's back: no hidden inter-call state, no secret mutation, resources released by the layer that acquired them
- **Why:** The book's strtok autopsy shows hidden statics and behind-the-back writes breeding bugs and precluding reentrant use; when a resource is opened in one module and closed in another, ownership goes ambiguous and leaks or double-frees follow.
- **Applies:** Module-level mutable state, functions that silently write into inputs, APIs returning references to internal buffers without documented lifetime, and any diff moving a free/close away from its matching acquire.
- **Unless:** State explicitly carried in an instance the caller creates is the fix, not the crime; documented ownership-transfer contracts are legitimate; internal caching invisible except in speed is fine.
- **Source:** Chapter 4: Interfaces (4.5, 4.6)

### 04.7 Detect errors at the lowest level, decide policy at the top: library code reports failure and never aborts, prints, or swallows
- **Why:** The callee cannot know whether quitting, retrying, or degrading is right — a word processor must not die where a one-shot tool may. Exceptions used for routine outcomes (end of input, not found) distort control flow; expected results belong in ordinary return values.
- **Applies:** Error paths in reusable modules: exits and panics below the entry point, in-library logging in place of propagation, distinct failures collapsed into one indistinguishable value, try/catch wrapped around normal flow.
- **Unless:** Top-level application code may legitimately abort, and small standalone tools may print-and-exit through a wrapper; after reporting, a library should leave itself clean and usable rather than attempt ambitious recovery.
- **Source:** Chapter 4: Interfaces (4.7)

### 04.8 Default to the simplest algorithm and data structure that handles the expected size; escalate only on measured evidence, and keep the simple version
- **Why:** Intuition about where time goes is unreliable — the book's engineers famously tuned the idle loop — and a better algorithm beat a hand-tuned routine by 5–10x. Arrays, lists, trees, and hash tables cover nearly all programs; hand-rolled sophistication is where bugs live, and the retained simple version doubles as the correctness oracle.
- **Applies:** Diffs justified by "faster": custom structures, caches, unrolled loops, unsafe variants of safe operations chosen for speed — require a profile and before/after numbers, and prefer the always-correct entry point.
- **Unless:** Simplicity never excuses a design that cannot handle the stated problem size or adversarial worst-case inputs; once profiling proves a bottleneck in long-lived code, aggressive optimization is exactly right.
- **Source:** Chapter 2 (2.3, 2.10); Chapter 7: Performance (7.1, 7.3, 7.7)

### 04.9 Require boundary and property tests as minimum evidence, and require every bug fix to arrive with a failing test plus a sweep for siblings
- **Why:** Most bugs live at the edges — empty, single, exactly-full, one-past-full — and probing them surfaces spec gaps before they ship as accidental behavior. The book's own argument-parsing blunder recurred lines apart and shipped twice; when exact output is hard to state, conservation, round-trip, and independent-implementation checks catch what eyeballing never will.
- **Applies:** Any loop, parser, buffer, or size-limited structure in the diff; bug-fix PRs (does the test fail on the old code? were matching call sites grepped?); test adequacy for generators, converters, and numeric code.
- **Unless:** A regression suite silently assumes the previous version was right — verify expected output independently; and exhaustive edge enumeration or elaborate scaffolds for trivial one-line corrections is wasted effort.
- **Source:** Chapter 5 (5.2); Chapter 6: Testing (6.1–6.3, 6.8)

### 04.10 Prefer one code path that runs everywhere over per-environment branches, and confine unavoidable dependencies behind a boundary module
- **Why:** A variant per environment grows with every new target, and each build-time conditional multiplies the number of programs you must test — code excluded from a configuration is invisible to the compiler and to tests, so fixes silently miss sibling branches. One small system-specific file per target kept the rest of the book's Sam editor identical everywhere.
- **Applies:** Diffs adding platform checks, build-time flags, or ifdef-style conditionals scattered across files; direct OS or third-party calls leaking past the module that should isolate them; data crossing machines as raw native structs instead of text or a defined canonical layout.
- **Unless:** A consciously chosen non-portable feature can be worth it when functionality clearly outweighs portability; isolated conditional defense and single-target throwaway code do not need the abstraction layer.
- **Source:** Chapter 8: Portability (program organization, isolation, data exchange)

### 04.11 If a change alters the observable behavior of an existing interface, require backward compatibility or a new name
- **Why:** The book's echo and sum stories: silently changing what a widely-used tool does breaks every dependent script, and the lasting harm is incompatible things answering to one name — the confusion persists for years after the improvement.
- **Applies:** Any change to public APIs, CLI behavior, serialized formats, or defaults that existing programs, scripts, or stored data depend on.
- **Unless:** Pure additions that leave the old specification intact need no new name; a genuine improvement with a documented migration and a way to recover old behavior can justify the break.
- **Source:** Chapter 8: Portability (portability and upgrade)

## Review heuristics

- Scan every loop, allocation, and copy for nonstandard forms of standard operations — that is where the off-by-ones hide; any deviation from the file's idiom needs a reason.
- Circle every numeric literal: unexplained, or repeated anywhere else (buffer size in a format string, limit in a test), it needs a single named source.
- For each new or changed public function, answer without reading the body: who frees what, is the returned data overwritten on the next call, and how does failure reach the caller. If the doc comment can't say, the interface isn't done.
- If the PR says "faster," ask for the profile and the before/after numbers; if it picks an unsafe variant of a safe operation, the burden of proof is on the fast path.
- Diff touched code but not the adjacent comments? Check each one still tells the truth — a comment contradicting its code poisons both.
- On a bug fix, confirm the new test fails on the unfixed code, and grep for the same pattern at sibling call sites before approving.
