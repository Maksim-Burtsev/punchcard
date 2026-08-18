# 22. Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis — Adam Tornhill

> Code quality is not a property of code in isolation; it is a property of code plus how it changes. The version history is evidence: which files churn, which files move together, where complexity is trending, how old the code is, and how many people touch it. A reviewer armed with that evidence spends objections where they will actually be paid back, and sees couplings — and missing edits — that no compiler or static analyzer can show.

## Principles

### 22.1 Weigh a finding by how often the touched code actually changes, not by how ugly it looks.
- **Why:** Bad code only costs money when someone must read and modify it, and change frequency follows a power law — most of a codebase is a long tail nobody edits. The same review effort buys far more where churn and complexity meet.
- **Applies:** Deciding which of several flaws in a diff to block on, and how hard to push, whenever change history for the files is available.
- **Unless:** Not a licence to ship sloppy new code — you cannot know yet whether it lands in the hot part. Low churn is also not proof of quality: quarantined code and dead code both look stable.
- **Source:** Ch. 1–2 (Why Technical Debt Isn't Technical; Identify Code with High Interest Rates)

### 22.2 Judge complexity by direction of travel against the file's own baseline, not against a fixed threshold.
- **Why:** Absolute limits fire constantly in legacy code and desensitize everyone. A file whose complexity climbs steadily while its size barely moves is being patched with ever-deeper conditionals — and a change adding a tenth or more on top of an already sizable unit is the pattern that precedes a bloated class.
- **Applies:** Incremental changes to long-lived files; compare against the pre-branch state or the lowest point of the last few weeks so a refactor-then-regrow cycle is not masked.
- **Unless:** Reformats and in-flight refactorings perturb the trend; a single spike is a prompt to look, not a verdict, and growth can be genuine new behavior.
- **Source:** Ch. 2 (Complexity Trends); Ch. 10 (Identify Steep Increases in Complexity)

### 22.3 Treat unexplained co-change as the finding: files edited together with no visible relationship are coupled in practice.
- **Why:** Change coupling is real coupling even when no import connects the two sides — a leaked abstraction, a clone, or one concept split across the wrong boundary. Surprise is the expensive part: the next maintainer edits one side and forgets the other. By the same logic, duplication is only worth removing when the copies demonstrably change together.
- **Applies:** Reading the shape of a diff — which files and functions had to move together for one logical change; also judging near-identical blocks.
- **Unless:** Tests changing with their subject, or implementations with their interface, is expected and its absence would be the warning. Single co-changes, renames, and formatting sweeps prove nothing.
- **Source:** Ch. 3 (Coupling in Time; The Dirty Secret of Copy-Paste)

### 22.4 Prefer moving related code next to each other over extracting a shared abstraction from superficial similarity.
- **Why:** Proximity — same function, same file, same package — makes coupling visible at near-zero risk, and readers treat adjacent code as one concept. An abstraction pulled from two things that model different domain concepts inherits conflicting reasons to change and degenerates into flags and branches.
- **Applies:** Where new functions land in an existing file, refactors that stop short of full extraction, and every proposed shared helper or base class.
- **Unless:** Proximity is a mitigation, not a fix, when a whole cluster always co-changes — that wants its own module. Do not demand a large file be reshuffled as a drive-by; it destroys the diff.
- **Source:** Ch. 4 (Follow the Principle of Proximity)

### 22.5 Require congested code to be split in small steps behind the original interface, with a temporary safety net first.
- **Why:** Congested code is exactly the code other people are editing right now, so a long-lived refactoring branch guarantees a merge catch-up game. Splitting responsibilities out while the original signatures delegate keeps each step shippable in hours. And such code usually has token coverage, so black-box end-to-end tests are what make the first move safe.
- **Applies:** Restructuring work on hotspots under active parallel development; extractions and rewrites of legacy modules.
- **Unless:** The delegating facade and the provisional tests are both scaffolding — name them so, and the follow-up that removes them has to be real. On code nobody else touches, the ceremony is overhead.
- **Source:** Ch. 4 (Refactor Congested Code with the Splinter Pattern; Build Temporary Tests as a Safety Net)

### 22.6 Hold test code to the same standard as production code, and read a heavy setup as a report on the design.
- **Why:** Maintenance cost does not care which side of the test boundary code sits on — in the book's case studies the worst hotspot in a real framework was a giant unit test. Setup length moves inversely with the readability of the subject, and mocks that mirror internals lock the suite to a mechanism instead of a behavior.
- **Applies:** Any diff that adds or edits tests; also using the tests as the entry point into an unfamiliar change.
- **Unless:** Mocks at real external boundaries are fine — the signal is excess, not presence. Over-abstracted tests lose their value as documentation, so judge them by readability, not DRY purity.
- **Source:** Ch. 3 (There Is No Such Thing as Just Test Code); Ch. 2 (Use the Setup Heuristic)

### 22.7 Read the age of the code being touched, and question a module that mixes churning files with files untouched for years.
- **Why:** Stable code is code nobody remembers, so editing it means working without the mental model that built it; it is also the solidified foundation the rest of the system leans on. Differing rates of change inside one boundary usually mean two concepts were packaged together — the settled half could become a black box.
- **Applies:** Diffs reaching into old subsystems; package structure, new module placement, proposals to extract a library.
- **Unless:** Age is a shallow signal — one trivial edit makes a file look young. Old is not automatically good either: confirm stable code is still reachable, since dead code stabilizes perfectly and deleting it beats extracting it.
- **Source:** Ch. 5 (The Principles of Code Age)

### 22.8 Look for the change that is missing: if a file's historical partners are absent from the diff, ask why.
- **Why:** A large share of defects are omissions — an unpatched clone, a consumer that never learns to handle a new event, a caller that ignores a newly raised error. Compilers, types, and tests cannot point at an edit that was never made; the co-change history is the only thing that can.
- **Applies:** Changes to code with known strong partners — duplicated implementations, mirrored platform variants, producer/consumer pairs across a protocol.
- **Unless:** The check must be overridable or the coupling can never be refactored away. Deliberate divergence is a legitimate answer, and repeated overrides mean the coupling is dissolving — or should be removed rather than dutifully honored.
- **Source:** Ch. 10 (Catch the Absence of Change)

### 22.9 Draw boundaries along responsibilities, features, and team seams — not technical layers — and count how many components one user-visible change had to touch.
- **Why:** Work arrives feature-shaped while layered structures split code by technical role, so every feature cuts across all of them; measured cross-layer co-change runs about a third of commits in stable systems and much higher in growing ones. Coordination is paid on each change and responsibility diffuses until nobody owns the outcome.
- **Applies:** New modules and packages, service decomposition, and any feature change that edits controller, service, repository, and mapper at once; also additions of use-case-specific fields onto a shared global model.
- **Unless:** Feature-oriented packaging has its own failure modes — gatekeepers, duplicated infrastructure, inconsistency — so argue the trade-off rather than enforcing it, and never on the evidence of one diff.
- **Source:** Ch. 8 (Layered Architectures and the Cost of Consistency; Discover Bounded Contexts Through Change Patterns)

### 22.10 Treat a change that ripples across services or repositories for one business capability as a design defect, and name the cause.
- **Why:** Distribution does not remove logical dependencies, it hides them — the coupled files sit in different repos, possibly different languages, so nothing static reveals the relationship while the coordination cost recurs forever. Chronically co-changing services are a distributed monolith paying network cost for monolith coupling.
- **Applies:** Diffs spanning deployable units; protocol and API-shape changes; predictable producer/consumer pairs such as a backend metric and the UI that renders it.
- **Unless:** Some cross-unit change is normal in early evolution, and some mirroring is deliberate. The remedy is often to move the related code together, transfer ownership, or collapse the services — not to add more indirection so the producer can avoid touching its consumer.
- **Source:** Ch. 9 (Detect Microservices Shotgun Surgery; Balance Monolithic UIs)

### 22.11 Count the people, not just the code: challenge new technology variety and fragmented ownership.
- **Why:** Defect risk correlates with the number of minor contributors to a component, and code everyone touches but nobody owns degrades with each smallest-tweak-that-works. Unrestricted technology choice compounds this by narrowing who can maintain each part, turning an ordinary departure into permanent knowledge loss.
- **Applies:** Prioritizing review depth; edits by someone with little prior footprint in a module; any change pulling in a new language, framework, build system, or datastore alongside existing ones.
- **Unless:** Never a judgment of individuals and never a productivity metric — measure people and the data dies. Deliberate polyglot boundaries and planned migrations are legitimate; a single gatekeeper reviewer is its own bottleneck.
- **Source:** Ch. 7 (Measure Coordination Needs); Ch. 9 (Measure Technical Sprawl); App. 1

### 22.12 Say it out loud when a change is acceptable only because the surrounding code is already bad.
- **Why:** Normalization of deviance is how teams drift: each exception looks small against what is already there, fifteen thousand lines becomes the new normal, and the next thousand feels free. Review is the last checkpoint where the drift is still visible and the debt can be taken on as an explicit decision instead of a habit.
- **Applies:** Reviews where the argument for approval is consistency with existing poor patterns; also new modules named util, misc, common, or core, whose emptiness of concept guarantees they become magnets.
- **Unless:** Blocking every small change until the neighborhood is cleaned is its own dysfunction. The goal is a recorded decision, not a refusal to ship; renaming an established generic module rarely belongs in the current diff.
- **Source:** Ch. 6 (Fight the Normalization of Deviance); Ch. 4 (Signal Incompleteness with Names)

## Review heuristics

- Before commenting, check the churn of the files touched: deep design argument for hotspots, light scrutiny for the long tail — and say which one you are in.
- Look at the file's complexity trend and how much this diff adds relative to its recent baseline, rather than to any fixed line or branch limit.
- Read the *set* of files in the diff: any pair with no visible relationship is suspected hidden coupling; any historical partner missing from the diff is a suspected omission.
- Count how many modules, layers, or deployable units one user-visible behavior required — and ask what the separation bought in exchange.
- Review the tests as code: long setup or mock-heavy wiring is a report about the design of the subject, not a test-quality nit.
- Check the age mix of what is being edited: a long-stable file being touched needs more justification and more test cover than a young churning one.
- For any new shared abstraction, ask what evidence exists that the two sides actually change together; if there is none, propose proximity instead.
