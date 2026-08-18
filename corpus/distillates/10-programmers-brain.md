# 10. The Programmer's Brain — Felienne Hermans

> Code comprehension is a cognitive process bounded by hard limits: working memory holds roughly two to six chunks, long-term memory supplies the patterns that let experts read fast, and readers silently autocorrect what they see toward what they expect. A diff is therefore not judged by whether it works or whether its author can follow it, but by the load it imposes on a reader without the author's context. Most review-worthy defects in this view are not logic errors — they are misleading names, defeated chunking, scattered wiring, and confidently wrong assumptions that reading alone cannot catch.

## Principles

### 10.1 Budget the change against the reader's working memory
- **Why:** Working memory holds two to six chunks; code that forces mental tracing of many interdependent mutable values pushes every reader into external state-tracking, a measurable comprehension failure rather than a taste issue.
- **Applies:** Calculation-heavy code, loops where several variables update each other, dense control flow, signatures and conditionals a reader must hold in mind at call sites.
- **Unless:** The limit is chunks, not tokens — domain-familiar groupings count as one chunk, so do not mechanically count parameters or lines.
- **Source:** Ch. 4 (why complex code is hard); Ch. 9 (long parameter lists, complex switches)

### 10.2 Charge only for extraneous load, never for intrinsic load
- **Why:** Intrinsic load comes from the problem itself; extraneous load comes from the author's presentation choices. Only the second is the author's responsibility, and it is exactly what review can remove cheaply before merge.
- **Applies:** Deciding whether a "this is too complicated" comment is fair on any non-trivial diff.
- **Unless:** Extraneous is relative to the readers — a construct the whole team reads fluently is not extraneous load because one reviewer dislikes it.
- **Source:** Ch. 4, types of cognitive load

### 10.3 Prefer structure the team can chunk over clever novelty
- **Why:** Experts read fast only when code matches schemas already in long-term memory; an unrecognizable structure reduces everyone to line-by-line reading, and known patterns measurably cut maintenance time.
- **Applies:** New modules, reworked control flow, dense constructs (nested comprehensions, chained lambdas) inside already-complex code, choices between a codebase idiom and an ad-hoc invention.
- **Unless:** Do not force a formal pattern where none fits, and do not expand idioms the team genuinely reads fluently — gratuitous pattern use adds its own load.
- **Source:** Ch. 2, the power of chunking; Ch. 4, replacing unfamiliar constructs

### 10.4 Reject names and cues that lie, mislead, or invite autocorrect
- **Why:** Readers chunk on the name and never inspect the body; the brain literally overwrites what the eyes saw with what memory expects. A getter that mutates, a plural returning one item, near-twin identifiers, or a stale comment steer readers into confident wrong models that survive review.
- **Applies:** Every new or renamed identifier, especially public surfaces; pairs of similar names in one scope; copy-paste siblings whose subtle difference readers will wrongly generalize away; comments and structural beacons left behind by refactors.
- **Unless:** Do not litigate honest-but-imperfect names or pure style (case, harmless abbreviations); the target is active contradiction and confusability, not aesthetics.
- **Source:** Ch. 1, the "mian" effect; Ch. 9, linguistic antipatterns and code clones

### 10.5 Keep one vocabulary and one name mold per concept
- **Why:** Consistent molds let long-term memory retrieve related code; a synonym for an established concept forces readers to carry a translation table in short-term memory. Consistent-and-mediocre beats good-but-inconsistent.
- **Applies:** Renames, new identifiers, and new modules in a codebase with recognizable conventions.
- **Unless:** Antipatterns outrank conformance — never propagate a name that lies about behavior for consistency's sake, and a genuinely new concept deserves a new name.
- **Source:** Ch. 8, naming perspectives and name molds

### 10.6 Verify each variable plays one recognizable role
- **Why:** The role framework (stepper, flag, gatherer, most-wanted holder, and so on) gives readers ready-made chunks; a variable that shifts roles mid-function or hides its role behind a generic name denies them that shortcut, and role awareness measurably improves comprehension.
- **Applies:** Loops, accumulators, search routines, state-carrying fields, and any generically named variable (data, temp, val) living beyond a few lines.
- **Unless:** Short-lived genuine temporaries are a legitimate role needing no ceremony; the goal is legible behavior, not encoding types into names.
- **Source:** Ch. 5, roles of variables

### 10.7 Treat delocalization and hidden dependencies as a tax
- **Why:** Every call-site hop and every piece of undiscoverable wiring forces the reader to hold navigation state in short-term memory while comprehending — the book's "lack of information" failure mode. Searching is a separate activity that steals working memory from understanding.
- **Applies:** Refactors extracting many single-use helpers, deep call chains, cross-file callbacks, reflection, DI wiring, ambient configuration, logic split across layers for symmetry.
- **Unless:** Deduplication, genuine reuse, and principled module boundaries justify indirection — the smell is undiscoverability and fragmentation with vague names, not modularity itself.
- **Source:** Ch. 1, lack of information; Ch. 12, hidden dependencies; Ch. 13, limiting activities

### 10.8 Hunt misconceptions: signpost negative transfer, pin assumptions with tests
- **Why:** The deepest bugs are wrong beliefs held with confidence — a familiar convention with changed semantics, or an unverified "this is never negative." Experts especially fail to suspect themselves, and a corrected misconception still lingers and resurfaces.
- **Applies:** Wrappers and ports mimicking a well-known interface with different semantics; fixes and features whose correctness rests on unverified properties of code outside the diff.
- **Unless:** Faithful reuse of a convention with matching semantics is a virtue, and properties already enforced by types or existing tests need no extra pinning.
- **Source:** Ch. 7, transfer and misconceptions

### 10.9 Demand plan knowledge, not code narration
- **Why:** Code encodes what it says, not why it hangs together; intent, rationale, and rejected alternatives evaporate unless written down, while line-level comments restating the statement below actively burden chunking.
- **Applies:** Non-obvious design choices, workarounds, tricky algorithms, commit messages and PR descriptions for changes whose reasoning is invisible in the diff.
- **Unless:** Self-evident code needs no comment at all; the standard is intent capture, not comment volume.
- **Source:** Ch. 9, comments smell; Ch. 11, storing the mental model; Ch. 13, text vs. plan knowledge

### 10.10 Judge design changes as cognitive-dimension trade-offs tied to a named activity
- **Why:** Dimensions conflict — types cut error-proneness but raise viscosity, abstraction aids reuse but harms exploration — so strictness and flexibility are never unconditional goods; a searched-through library and a rapidly changing app need opposite optimizations.
- **Applies:** Architecture-level review of type machinery, abstraction layers, extension points, stricter contracts; naming that maps to the business domain versus generic mechanics.
- **Unless:** Not license for relativism — the reviewer must name the dominant activity and the specific dimension traded, and correctness at trust boundaries is not tradable.
- **Source:** Ch. 12, cognitive dimensions and design maneuvers

### 10.11 Spend extra rigor on conventions that are still young
- **Why:** Identifier quality is fixed early and does not improve as a codebase ages, and newcomers imitate existing code rather than reading guidelines: the first patterns become the permanent patterns.
- **Applies:** Early commits of new projects, new modules, and the first instance of any pattern others will copy — names, molds, test shape.
- **Unless:** In a mature codebase this cuts the other way — wholesale convention-improvement churn rarely pays; invest where imitation is still ahead.
- **Source:** Ch. 8, lasting impact of initial naming

## Review heuristics

- In the diff's densest function, count the interdependent mutable values a reader must track at once; if it exceeds a handful without structure, ask for decomposition — but first check the load is presentational, not intrinsic to the problem.
- Read every new or changed name against its body: getter that mutates, boolean-sounding non-boolean, plural returning one, near-twin of an existing identifier, or a synonym for a concept the codebase already names.
- For each variable outliving a few lines, try to state its role in one word (stepper, gatherer, flag); if you cannot, or the role shifts mid-function, request a rename or a split.
- Trace one feature flow end to end and count file-hops plus invisible wiring (callbacks, DI, config); ask whether each hop pays for itself with a discovery path.
- List the assumptions the change makes about code outside the diff, and check each is pinned by a type, assertion, or test — especially where the code mimics a familiar API with different semantics.
- Check comments and the PR description carry why and rejected alternatives, not a restatement of the code; flag both stale beacons and line-level narration.
