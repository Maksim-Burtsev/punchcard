# 01. A Philosophy of Software Design — John Ousterhout

> Complexity is the single enemy of software, and it arrives incrementally — as hundreds of individually defensible dependencies and obscurities that no later fix can remove one at a time. A reviewer's job is therefore not to verify that the code works but to judge whether the change lowers or raises the system's long-term complexity. The central instruments are depth (simple interfaces over powerful implementations), information hiding, and obviousness as measured by the reader — never by the author.

## Principles

### 01.1 Hold a zero-tolerance line on incremental complexity
- **Why:** Complexity accumulates from small kludges each accepted "just this once"; once deposited it is nearly impossible to remove because no single fix visibly helps. After any change, the design should look as if the feature had been planned from the start.
- **Applies:** Every diff, especially deadline-driven fixes, "temporary" workarounds, and minimal patches that bolt a special case onto existing structure.
- **Unless:** Real constraints (hard deadline, refactor breaking many teams) can justify a tactical fix — but the debt must be named and scheduled, not normalized; nor should reviews demand full redesigns, only steady 10-20% investment.
- **Source:** Ch. 2-3; Ch. 16.1 (Stay strategic)

### 01.2 Judge every module by its depth, not its size
- **Why:** An interface is the complexity a module imposes on everyone else; a shallow element whose interface is as complex as what it does costs more to learn than it saves. "Smaller classes and methods are better" is false — classitis multiplies interfaces.
- **Applies:** Any new or extended public API, wrapper, helper, or service; any split of a class or method driven purely by line count.
- **Unless:** Genuinely simple data holders exist legitimately; depth is a cost/benefit judgment, not a ban on small units.
- **Source:** Ch. 4 (Modules Should Be Deep; 4.5-4.6)

### 01.3 Confine each design decision to one module; reject temporal decomposition
- **Why:** When a format, protocol, or representation is known in two places, every change to it must be made in both — and back-door leakage invisible in any interface is the most dangerous kind. Structuring modules around execution order (read-then-parse) reliably scatters one piece of knowledge across stages.
- **Applies:** Serialization, protocols, data formats, getters returning internal collections, pipelines and multi-stage handlers, any pair of files that must always be edited together.
- **Unless:** Do not hide what callers genuinely need (error signals, performance-critical tuning); phase separation is fine when phases use disjoint information.
- **Source:** Ch. 5 (Information Hiding; 5.3, 5.9); 9.1

### 01.4 Make interfaces somewhat general-purpose, not caller-shaped
- **Why:** An API that encodes the specific use case that motivated it comes out shallower, leaks upper-layer concepts downward, and welds the two modules' evolution together. Slightly general interfaces are simpler and have fewer methods.
- **Applies:** New APIs written "for" one caller; a lower-level method named after a UI or business action; a method invoked from exactly one place.
- **Unless:** Stop before speculative generality — if using the API for today's need requires lots of extra caller code, it is over-generalized.
- **Source:** Ch. 6; 9.4

### 01.5 Flag any layer that repeats the abstraction beneath it
- **Why:** Pass-through methods, thin wrappers, and variables threaded through code that never uses them add interface surface and dependencies while contributing nothing — the signature of an unclear division of responsibility. On hot paths, stacked shallow layers are a performance and design defect at once.
- **Applies:** Wrapper classes, delegation-heavy facades, decorators, same-signature methods across adjacent layers, parameters passed through untouched (consider a context object).
- **Unless:** Dispatchers and multiple implementations of one interface legitimately repeat signatures; occasionally a decorator really is cleanest.
- **Source:** Ch. 7; Ch. 20.3-20.4

### 01.6 Pull complexity down into the implementation, not out to callers
- **Why:** A module has far more users than implementers, so a hard implementation behind a simple interface reduces total system complexity, while exported knobs, required pre-steps, and punted decisions multiply the people who must cope with the problem.
- **Applies:** New configuration parameters (ask whether the module could compute the value), APIs demanding caller pre/post-processing, missing sensible defaults.
- **Unless:** Only pull down complexity closely related to the module's purpose; dragging in unrelated concerns (UI knowledge into a text class) is leakage, and parameters users truly know better than the module should stay exposed.
- **Source:** Ch. 8; 5.7

### 01.7 Decide split-vs-merge by resulting complexity, never by unit size
- **Why:** Subdivision itself costs: more interfaces, glue, distance between related logic, duplication. A long method with a simple interface is fine; having to flip between conjoined units to understand either is the real red flag.
- **Applies:** Refactors that split by line count, one-line extracted helpers, merges of unrelated concerns into one object.
- **Unless:** Do merge to eliminate duplication or shared-format knowledge; do split to peel a genuinely independent subtask or general-purpose mechanism away from special-purpose policy.
- **Source:** Ch. 9

### 01.8 Define errors and special cases out of existence
- **Why:** Handlers are the expensive part of errors — they multiply across callers, are rarely exercised, and cause catastrophic failures; likewise, state flags plus scattered if-checks make every touching site a bug source. Redefining semantics so the condition is not exceptional deletes all that code at once (e.g. an always-present empty selection).
- **Applies:** New thrown exceptions, error enums, special return values, per-call-site try/catch, boolean exists/initialized/mode flags with conditional handling in several places, "reject anything suspicious" internal validation.
- **Unless:** Never mask errors the caller must act on (lost messages, data-loss risk) — that makes robust callers impossible; crashing is wrong for conditions the system exists to survive; user-visible concepts may still exist at the UI layer.
- **Source:** Ch. 10 (10.9-10.10)

### 01.9 Expect evidence that alternatives were considered
- **Why:** First designs are rarely best; cheaply comparing radically different options exposes weaknesses in usability, generality, and efficiency before implementation locks them in, and often yields a hybrid better than either.
- **Applies:** New module boundaries, public APIs, major data-structure choices — ask "what else did you consider and why did it lose?"
- **Unless:** Skip for trivial or well-trodden decisions; the exploration should take hours, not become a waterfall phase.
- **Source:** Ch. 11 (Design it Twice)

### 01.10 Use names and doc comments as a probe of the design
- **Why:** The informal part of an interface — behavior, units, boundary inclusivity, side effects, preconditions — is usually larger than the formal part; without it the abstraction does not exist and callers must read implementations. An entity that resists a short precise name or a short complete comment is conflating roles: the decomposition, not the wording, is wrong.
- **Applies:** New or changed public classes and methods, non-obvious fields (units, invariants, null meaning), cross-module contracts, every identifier the diff introduces.
- **Unless:** Never demand comments that restate the code — those are worthless; short generic names (i, j) are fine in tiny visible scopes.
- **Source:** Ch. 12-15

### 01.11 Treat reader confusion as the finding, not a debate
- **Why:** Obviousness is judged by readers, not writers; a first reader's confusion predicts future misunderstandings and bugs, and review is the only reliable measurement of it. The author must fix the code, not argue the reviewer into understanding.
- **Applies:** Any review discussion; behavior violating reader expectations (constructors spawning threads, control flow hidden behind dispatch); generic Pair/tuple returns whose getKey/getValue say nothing; declaration types mismatching allocated types.
- **Unless:** The first remedy is less information to hold (simpler design, fewer special cases); comments are the fallback, and code fully local and unmistakable can keep its shortcuts.
- **Source:** Ch. 18; 13.8

### 01.12 Enforce codebase-wide consistency of names and conventions
- **Why:** Consistency lets readers' reflexive assumptions be safe; one identifier meaning two different things (the book's worst bug: disk block vs file block) makes assumptions silently wrong, and a "better" second idiom coexisting with the old one costs more than it gains.
- **Applies:** Identifiers overlapping existing project vocabulary (indices, IDs, offsets, units); any diff introducing a second way to do what the project already does — error style, layering, naming scheme.
- **Unless:** A convention change is fine when the author migrates every old occurrence; and do not force one name onto genuinely different concepts — distinguish variants with prefixes (src/dst) instead.
- **Source:** Ch. 14 (14.4); Ch. 17

## Review heuristics

- For each new public element, compare interface size to functionality: could a caller misuse it, and is it simpler than what it hides?
- Search the diff for knowledge that now lives in two places: duplicated parsing, shared formats, getters exposing raw internal collections, classes that must change together.
- Trace any new parameter, exception, or required call-order upward: could the module compute the value, absorb the case, or redefine semantics so callers do nothing?
- Look for same-signature methods across layers and variables passed through untouched — pass-throughs mean responsibility is misplaced.
- Read every new name and doc comment cold: if you cannot state precisely what it does without the implementation, report the design, not the wording.
- Grep for the project's existing idiom before accepting a new one; a second convention needs a full migration or a rejection.
