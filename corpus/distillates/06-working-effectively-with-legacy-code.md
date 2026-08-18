# 06. Working Effectively with Legacy Code — Michael C. Feathers

> Legacy code is simply code without tests: however clean it looks, nobody can prove a change made it better or worse. The book's entire discipline follows from that definition — get the touched behavior into a test harness first, change it second, and accept temporary ugliness as the price of admission. For a reviewer this inverts the usual aesthetics-first instinct: the question is never "is this elegant?" but "what pins the behavior this diff can disturb, and could this code be exercised in isolation if we had to?"

## Principles

### 06.1 Judge a diff by the tests around its change points, not by how clean the code looks
- **Why:** Code without tests cannot be changed verifiably; a covering test acts as a vise that pins existing behavior while one piece changes. Every merge into a weak area should leave strictly more code under test than before.
- **Applies:** Any edit to existing logic in poorly covered modules; evaluating whether a PR carries evidence for the behavior it adds or alters.
- **Unless:** The Legacy Code Dilemma — conservative, catalogued dependency-breaking moves done without tests are acceptable as a bridge, provided tests land right behind them. Baby steps, not full-module coverage per PR.
- **Source:** Preface; Chapter 2 (The Legacy Code Change Algorithm)

### 06.2 Require characterization tests that pin what the code actually does before a "behavior-preserving" refactor
- **Why:** In legacy systems, actual behavior outranks intended behavior — users depend on it, bugs included. Tests recording current behavior turn later differences into detectable failures; nothing else does.
- **Applies:** Changes that modify, move, or extract existing untested logic, especially the specific branches and conversions the change touches.
- **Unless:** Surprising behavior found while characterizing gets escalated, not silently canonized; brand-new code deserves specification-first tests instead.
- **Source:** Chapter 13 (Characterization Tests)

### 06.3 Reject "verified manually" or "the nightly suite covers it" as evidence for a localized logic change
- **Why:** Application-level tests localize errors poorly and run too slowly to be run often — feedback overnight instead of in a minute. Unit tests exist precisely to close that gap.
- **Applies:** Changes to intricate internal logic whose only claimed coverage is scenario, integration, or manual testing.
- **Unless:** Higher-level tests remain valuable for cross-class interactions; the demand is for fast local tests in addition, not instead.
- **Source:** Chapter 2 (What Is Unit Testing?; Higher-Level Testing)

### 06.4 Check that new code leaves seams and flag hard-wired globals, singletons, and heavyweight collaborators
- **Why:** A call that constructs and uses its collaborator inline has no enabling point and can never be sensed or substituted in isolation. Most singletons exist to avoid passing a variable, and the hidden coupling they spread is why classes cannot be instantiated in a harness.
- **Applies:** New constructors and signatures; anything taking a live DB connection, socket, framework object, or reaching for static state when it needs only an interface or the data itself.
- **Unless:** Don't demand speculative injection points for stable, side-effect-free stdlib calls; introduce a seam where a dependency actually blocks testing or change, not as a blanket style rule.
- **Source:** Chapters 3–4 (Sensing and Separation; The Seam Model); Chapter 9

### 06.5 When surrounding code cannot yet be tested, require new behavior as a separately tested sprout or wrap
- **Why:** Sprout Method/Class and Wrap Method/Class give the new code tests and a clean interface immediately while the old code changes by roughly one line — risk stays contained in the new unit.
- **Applies:** Features, fixes, and cross-cutting behavior (logging, notification, checks) landing in untested or poorly understood areas.
- **Unless:** Sprouting admits the host stays untested and can leave it oddly gutted — it implies follow-up, not a final design. When the host is already under test, refactor and integrate normally.
- **Source:** Chapter 6 (Sprout Method/Class, Wrap Method/Class)

### 06.6 Insist that refactoring and behavior change travel in separate, single-goal edits
- **Why:** Safety comes from knowing exactly which edits alter behavior; a diff that reorganizes and changes logic at once makes regressions unattributable by reviewer or tests. In untested moves, verbatim-preserved signatures and rote mechanical steps are what keep errors out.
- **Applies:** Any diff in weakly tested code that both restructures and changes functionality; "cleanup plus fix" commits; manual extractions from monster methods.
- **Unless:** Incidental formatting inside a functional change is harmless; with solid tests and automated tooling, signature changes within a refactor are fine.
- **Source:** Chapter 23 (Hyperaware Editing; Single-Goal Editing; Preserve Signatures)

### 06.7 Prefer test coverage over encapsulation and elegance in legacy areas — but book the scar as debt
- **Why:** The dependency-breaking catalog deliberately makes design worse first: widened visibility, awkward parameters, and delegate shells are surgical incisions that make everything beneath them testable. A reviewer who blocks every ugly seam blocks the only safe exit from legacy code.
- **Applies:** Changes whose stated purpose is getting code under test: protected-for-testing members, clumsy extracted interfaces, exposed constructors.
- **Unless:** Never a license for permanent mess or for leaky design in new code; covert tricks like reflection into privates stay banned because they anesthetize the team to decay. Each scar needs a follow-up plan.
- **Source:** Chapter 11 (Effects and Encapsulation); Chapter 25 (introduction)

### 06.8 Treat untestability as a verdict on the design, not on the tests
- **Why:** A class that cannot be instantiated without an onion of nested objects, or whose construction fires hidden I/O, is exhibiting tangled dependencies and overloaded responsibility. The urge to test a private method directly is the same signal: the class does too much — extract the logic into its own class with a public face.
- **Applies:** New classes and constructors; diffs adding reflection-based test helpers or making members public purely for tests.
- **Unless:** Testing through existing public methods is preferred when practical; a temporary protected-for-testing relaxation is a fair trade when a full split is too risky right now.
- **Source:** Chapter 9 (The Onion Parameter); Chapter 10 (The Hidden Method)

### 06.9 Trace where a change's effects propagate, and accept pinch-point tests as scaffolding, not a destination
- **Why:** Regressions hide in the three propagation channels — return values, mutated parameters, and shared state. A pinch point, the narrow interface all those effects flow through, covers a cluster of changes with few tests and marks a natural encapsulation boundary.
- **Applies:** Changes to widely called code or shared mutable structures; deciding where test evidence for a multi-class change may legitimately sit.
- **Unless:** Purely local changes fenced by private fields and immutable state need no deep tracing — that fencing is the point. Pinch-point tests left in place permanently rot into slow, unlocalizable mini-integration suites.
- **Source:** Chapters 11–12 (Reasoning About Effects; Interception Points)

### 06.10 Block changes that grow an already-large class or method in the name of a "safer" small edit
- **Why:** Minimizing structural change to avoid risk is exactly how systems rot: methods swell, teams get rusty at restructuring, and fear compounds. Repeated edits to one giant class are unnamed responsibilities asking for extraction — small, low-coupling extractions, not big-bang decomposition.
- **Applies:** Diffs appending logic to the longest method or heaviest class in a module; ask for the class's purpose in one sentence and whether the addition belongs to it.
- **Unless:** Mid-hotfix, a sprouted tested addition with a follow-up extraction beats forcing the split now; awkward intermediate extractions are expected to be redone, not treated as defects.
- **Source:** Chapter 1 (Risky Change); Chapter 20; Chapter 22

### 06.11 Keep third-party APIs behind thin team-owned wrappers and core logic out of the glue
- **Why:** Promiscuous library use becomes an irreversible commitment and every hard-coded vendor call is a lost seam. Nearly every system has core logic that can be peeled away from send/receive/sleep plumbing; buried in it, that logic is untestable and unreadable.
- **Applies:** New or widening dependencies on vendor, platform, or framework types, especially sealed classes that cannot be faked; handlers where business rules interleave with I/O calls.
- **Unless:** Don't wrap stable stdlib or single-call-site usage; some layers are legitimately all glue — the requirement is that glue stays thin and dumb, not that every file contain pure logic.
- **Source:** Chapters 14–15; Chapter 25 (Adapt Parameter)

## Review heuristics

- For every modified line of existing logic, find the test that would fail if the change is wrong; if the only answer is a slow suite or manual verification, ask for a fast local test or a characterization test first.
- Scan new constructors and signatures for things that are hard to instantiate: live connections, singletons, statics, whole framework objects where an interface or plain data would do.
- Check that no edit mixes restructuring with behavior change; in untested areas, verify moved code kept signatures verbatim and each commit had one goal.
- When new behavior lands in an untested host, expect it as a sprouted or wrapped unit with its own tests, not lines woven into the existing method.
- Before blocking an ugly seam (widened visibility, odd parameter, clumsy interface), ask whether it exists to get code under test — if yes, ask for the follow-up plan instead of a rewrite.
- Flag any diff that makes the module's biggest class or longest method bigger, and any test helper that reaches into privates via reflection or access tricks.
