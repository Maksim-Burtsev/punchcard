# Finding stability across runs — August 2026

The [August calibration](calibration-2026-08.md) named run-to-run
variance as a known limit: two cold
runs of the same skill on the same diff could surface different findings.
This measurement quantifies that variance on the v3 output format, tests
one mechanical fix, and reports why the fix was rejected.

## Protocol

Two PRs with a known, hand-verified union of real findings:

- pallets/flask#5918 (head `a82e942`) — union of 6 root-cause keys,
  including two blocker-class regressions (blueprint hooks skipped on
  automatic `OPTIONS`; `flask routes` mutating live `Rule.methods`) and a
  key discovered during this measurement and verified by hand
  (`required_methods` merged before the automatic-options decision).
- psf/requests#7520 (head `50064fd`) — union of 4 keys, one blocker-class
  (an unterminated quote swallowing the rest of the Link header).

Five cold runs per PR per condition: fresh session, Opus (medium), the
prompt names only the skill and the target — no format or finding hints.
Findings were matched to keys by mechanism, never by wording or severity;
unmatched findings were verified once — real ones extended the union,
the rest would count as noise (none occurred, in either condition).

## Baseline — skill at v3.2 (`a82cc39`)

| Key | flask k/5 | | Key | requests k/5 |
|---|---|---|---|---|
| bp hooks skip on OPTIONS | **5/5** | | unterminated quote | **5/5** |
| routes mutates live rule | **5/5** | | quote rule duplicated | **5/5** |
| auto-OPTIONS state, no single source | **5/5** | | escape branches untested | **5/5** |
| Rule.methods introspection | 2/5 | | valueless param drops tail | 0/5 ¹ |
| try/except registration family | 2/5 | | | |
| required_methods flip | 2/5 | | | |

Mean recall vs union 0.70 / 0.75; mean pairwise Jaccard 0.66 / 1.00;
noise 0; verdict stable 10/10; ~103k / ~86k tokens per run.

¹ Contested scope: the behavior is identical on main and on the PR
(verified by executing both), so the gate legitimately drops it as not a
consequence of this change.

Every blocker-class key sits at 5/5. The n=2 anecdote that motivated this
work (a run missing the blueprint-hooks blocker) happened on the v3.1
skill and did not reproduce at n=5 on v3.2.

## The experiment — a mandatory contract sweep (`7ff8362`, reverted)

Hypothesis: the 2/5 tail keys are enumeration misses of one shape — the
diff changes a contract, the damage lives in a consumer the diff does not
touch — and a mandatory pre-judging step (enumerate changed contracts,
grep their consumers, record the search) would lift them without cost.

Result, same 5×2 protocol:

- The poster-child key rose (Rule.methods introspection 2/5 → 4/5, twice
  as a blocker), and the try/except family surfaced in 4/5 runs.
- But the fives fell: routes-mutation 5/5 → 4/5, no-single-source
  5/5 → 4/5, requests escape-tests 5/5 → 3/5; required_methods got worse
  (2/5 → 1/5). Requests, previously perfectly stable, dropped to
  Jaccard 0.80 with one verdict flip (the verified quote regression
  downgraded to DESIGN in one run). Tokens did not grow.

Diagnosis: runs render ~4 cards against a 6-key union regardless of what
they enumerate. The sweep reallocates the slot budget toward
contract-consumer findings; it does not expand it. That is the cap doing
its job — "aim for three to five, keep the worst consequences" — so the
tail variance is a property of the design, not an enumeration defect, and
no enumeration mechanism can remove it without inflating reviews. The
sweep was reverted (`b0599b2`).

## What stands

- Blocker-class findings are stable: 5/5 on every blocker key, both PRs,
  ten baseline runs, zero noise, zero fabricated claims.
- Which low-consequence findings fill the remaining card slots varies
  run to run. Two honest reviews of the same diff may differ in their
  tail; they agree on what blocks.
- Open direction (roadmap): a deep/ensemble mode — N merged finder passes
  for callers who want union coverage at N× cost. Rejected here because
  it masks the slot-budget property rather than changing it, and the
  single-run default is what ships.

## Search decoupled from render

The with/without measurement showed the reviewer reading "aim for three
to five" as a search budget — every flask run rendered exactly five cards
and one lost a blocker to a full set — and stopping at the repository
boundary while the consequence of a shared endpoint string lived inside
werkzeug. Two edits, measured with 17 cold runs (Opus, medium): the
finding count left the skill entirely (scope is the only limit; everything
that passes the gate renders), and step 3 became "follow every value to
its last consumer, inside this repository and outside it", with a second
round adding "every read of the value, and a collision pass when things
start sharing a key".

| Key | before (3 runs) | after |
|---|---|---|
| flask · blueprint hooks skip | 3/3 | 5/5 |
| flask · routes mutates live rule | 2/3 | **5/5** |
| flask · required_methods flip | 3/3 | 3/5 |
| flask · OPTIONS cross-redirect (inside werkzeug) | 0/3 | **0/5** |
| requests · unterminated quote | 3/3 | 3/3 |
| requests · escape branches untested | 2/3 | 0/3 |
| logrus · fix in dead code | 3/3 | 3/3 |
| fastify · errorHandler restored, untested | 2/3 | 0/3 |
| control · celery#10493 | — | 🟢 2/3, one run a verified QUESTION (the description claims a unit test the branch added and then deleted) |

Cards per run fell, not rose: flask 4–5 (was 5), requests 2 (was 3–4),
logrus 2 (was 2–3), fastify 0 (was 1). Noise: zero in 17 runs. Tokens
per run fell about a third: flask ~108k (was ~162k), requests ~80k
(~130k), logrus ~73k (~124k), fastify ~99k (~157k).

What the numbers say:

- **Decoupling held.** The blocker that a full card set had crowded out
  is back at 5/5, verdicts are stable, nothing was invented on the clean
  control, and the reviewer got cheaper rather than longer.
- **The dependency boundary was crossed, the consequence was still not
  found.** All five flask runs read werkzeug — for the mutated
  `Rule.methods` and the inert duplicate guard — but none grepped the
  package for every read of `endpoint` or ran the collision pass the
  text asks for, so `get_default_redirect` was never reached. One
  paragraph in a long skill does not change what a reviewer looks at
  once it has a design-shaped finding for the same value. Two wordings
  tried; this is where prompt text stops. The class stays uncovered and
  is now written down as such.
- **The tail got thinner.** Two keys that used to appear 2/3 now appear
  0/3: requests' untested escape branches and fastify's silently widened
  blast radius. Pre-existing faults moved correctly to out-of-scope
  lines (the scope rule working), but these two are consequences of the
  diff — 8.1-class coverage findings — and they were dropped, not
  demoted. Without a number to reach for, the reviewer stops at what it
  can demonstrate by running; a missing test has no runtime demonstration.

Kept, with that on the record: stable blockers, zero noise, a third
cheaper. Open: the coverage tail, and consequences that live inside a
dependency.

## The coverage tail, restored in part

Removing the finding count had dropped two 8.1-class findings from 2/3
to 0/3 — changed behavior with no test exercising it has no runtime
demonstration, and the reviewer had stopped at what it could run. One
edit to the Judge step: the mandatory check now names the test that goes
red on revert, covers changed behavior (a new branch, a widened effect, a
new code path) as well as new modules, and says outright that this
finding needs no runtime demonstration — the evidence is the named
missing case. Twelve cold runs (Opus, medium):

| Key | before | after |
|---|---|---|
| requests · escape branches untested | 0/3 | **3/3** |
| fastify · errorHandler restored, untested | 0/3 | 1/3 |
| flask · no test in the diff goes red on revert (new 8.1 card) | — | 3/3 |
| flask · blueprint hooks skip / routes mutates live rule | 5/5 / 5/5 | 3/3 / 3/3 |
| flask · OPTIONS cross-redirect inside werkzeug | 0/5 | 1/3 — the first time, on the step-3 wording already in place |
| requests · unterminated quote | 3/3 | 2/3 |
| control · celery#10493 | 🟢 2/3 | 🟢 2/3, one run a verified DESIGN (the smoke test never pins `worker_concurrency`, so it passes on any surviving child) |

Cards per run stayed at the baseline or one above (requests 2–3, fastify
0–1, flask 4, celery 0–1); noise zero in twelve; tokens flat (~73–104k).

Read honestly: the requests tail is back and flask now carries a
coverage card every run, but fastify's widened `errorHandler` surfaced
once in three — a coverage gap that hides behind a correct fix is still
easy to walk past. And the requests quote regression, found in every one
of fourteen earlier runs, was missed once here. One miss in three is
within what this protocol can see; it is recorded, not explained away.

## Beyond Python

The format and the judgment were calibrated on Python. Four cold runs on
other ecosystems, one PR each, checked that neither depends on it:

| PR | Language | Verdict | What it turned on |
|---|---|---|---|
| sirupsen/logrus#1574 | Go | 🟠 Ship after #1 | The fix lands in `LevelHooks.Fire`, which the logging path no longer calls — the reported bug reproduces identically on both branches |
| spf13/cobra#2486 | Go | 🟡 Ship with care | The padding cache is repaired on attach but left stale on the `RemoveCommand` detach path |
| fastify/fastify#6965 | JS | 🟡 Ship with care | The advisory's sibling entry point still reaches the not-found handler with its `preHandler` skipped |
| colinhacks/zod#6450 | TS | 🟡 Ship with care | Suppression and restoration of stack frames are gated on two different feature probes |

Every claim was demonstrated by execution — `go run` against two
worktrees, `node` against two bundles — not by reading. The annotation
marker came out in each language's own comment syntax, and no run
fabricated a Python-style REPL session where the ecosystem has none. The
zod run also checked the PR's own performance claim by measuring it
(~3x claimed, 4.6–5.9x observed on the failing-`safeParse` cases) rather
than repeating it.

Four PRs, one per shape, is a smoke test of portability — not evidence
that findings are as complete outside Python as within it.

## Reproduce

Clone the target, check out the PR head, open a fresh session with only
the skill and the target named, run five times, match by mechanism. The
per-run reviews and matching tables for both conditions are not committed;
this file records the protocol and the numbers.

## Independent search passes — August 2026

Two classes stayed uncovered after the coverage-tail work: a consequence
that terminates inside a dependency (flask's OPTIONS cross-redirect, found
1 run in 11, where Claude Code's built-in `/code-review` found it 3/3) and
the `except: pass` swallow on the same PR (1/3 against its 3/3). Reading
that reviewer's own prompt explains the gap: at medium effort it runs eight
independent finder angles, each in its own context, and one of them exists
only to ask what every *removed* line used to guarantee. Punchcard searched
once, in the context that also judges — and a reviewer that has already
written a finding about a value stops looking at that value.

Two variants were measured against that, both on Opus (medium), cold runs,
matched by mechanism.

### Variant A — prose only (rejected)

Step 3 gained a second reading of the diff ("for every line it deletes or
replaces, name the guarantee that line used to make and find where the new
code makes it again"), an explicit "a candidate does not close a trace",
and lost the endpoint/registry/cache-key paragraph the earlier sweep had
left behind.

| Key | master | A |
|---|---|---|
| flask · OPTIONS cross-redirect (target) | 1/11 | **0/3** |
| flask · blueprint hooks skip | 3/3 | 3/3 |
| flask · routes mutates live rule | 3/3 | 3/3 |
| flask · no single source | 0/3 | 3/3 |
| flask · no test goes red on revert | 3/3 | 3/3 |
| flask · required_methods flip | 3/5 | 1/3 |
| flask · `except: pass` swallow | 1/3 | 0/3 |
| requests · unterminated quote / duplication / escape tests | 3/3 · — · 3/3 | 3/3 · 3/3 · 3/3 |

Tokens flat (88–109k), noise zero, verdicts stable. The target key did not
move, and the reason was visible in the runs: they *did* follow the shared
endpoint into its consumers — `request.endpoint`, blueprint hooks — and
folded all of it into one card, then stopped looking at that value. Three
prose wordings have now failed on this key. Prose was the wrong instrument.

### Variant B — three independent passes (kept)

Step 3 became three readings of the same diff, dispatched as subagents that
do not see each other's notes — every value to its last consumer, every
removed guarantee to its new home, the test that goes red on revert — each
returning candidates only: file, line, mechanism, traced consequence. No
severity, no verdict, no card. Judgement stays in one place: the
constitution, the runtime demonstrations, the gate, the render. Without a
subagent tool the three passes run in sequence, each starting from the diff
rather than from what the last pass concluded.

| Key | master | A | B |
|---|---|---|---|
| flask · OPTIONS cross-redirect (target) | 1/11 | 0/3 | **3/3, blocker every time** |
| flask · blueprint hooks skip | 3/3 | 3/3 | 3/3 |
| flask · routes mutates live rule | 3/3 | 3/3 | 3/3 |
| flask · required_methods flip | 3/5 | 1/3 | 3/3 |
| flask · no single source | 0/3 | 3/3 | 2/3 |
| flask · no test goes red on revert | 3/3 | 3/3 | 3/3 |
| flask · `except: pass` swallow | 1/3 | 0/3 | 1/3 (once correctly dropped as answered in the PR description) |
| flask · sansio registers a view only `flask.Flask` supplies | — | — | 1/3 — **new key**, verified by hand |
| requests · unterminated quote | 3/3 | 3/3 | 2/2 |
| requests · quote rule duplicated | — | 3/3 | 2/2 |
| requests · escape branches untested | 3/3 | 3/3 | 2/2 |

The target key is taken, as the first or third card, with the redirect
demonstrated by running both trees. The class it belongs to — a
consequence that terminates inside a dependency — is no longer open. One
run found something no condition had found before, including the built-in
reviewer: the automatic-`OPTIONS` rule is registered in `sansio/app.py`,
the shared base Quart also subclasses, while the view function it points at
is installed only in `flask/app.py`. Confirmed by hand.

Discipline held where it matters. Noise: zero below-altitude sections in
nine reviews across both variants. Verdicts: stable across runs on both
PRs. The judge rejected finder candidates that did not survive checking —
two runs independently dropped a "weakened test" claim after reading the
assertions, one dropped the `except: pass` breadth because the PR
description already answers it. The clean control (celery#10493) came back
"Ship it." with zero cards and one correct out-of-scope line: three finders
looking for candidates do not talk a clean change into a finding.

**The cost is real and it is the argument against B.** Tokens per run rose
from ~100k to 152k/183k/191k on flask and from ~80k to 124k/131k on
requests — about 1.7×, above the 1.5× ceiling this measurement set for
itself in advance. Reviews got longer too, but only where the diff is
complex: flask went from ~950 words and four cards to ~1,600–2,050 words
and six, while requests stayed at three cards and ~950 words. The extra
length is findings, not padding — on flask, two of the extra cards are
blocker-class regressions that were being missed.

So the trade is stated, not hidden: three finder passes buy the last
uncovered blocker class and full union recall on both PRs, and they cost
roughly 70% more per review. That is a deliberate exceedance of the
pre-registered token rule, kept because what it bought is the class the
project had twice written down as out of reach.

### Wall-clock time

Nobody timed the earlier conditions on purpose; these figures are
reconstructed from file timestamps (the `/code-review` runs went through
`claude -p` with output redirected, so each has a start and an end) and
from subagent durations in this session. Two runs were in flight at any
time in every condition. Treat the minutes as the right order of
magnitude, not as a controlled measurement.

| PR | `/code-review` medium | Punchcard, single pass | Punchcard, three passes |
|---|---|---|---|
| flask#5918 | 4:07 · 4:21 · 5:40 → ~4.7 min | 7:25 · 5:45 · 7:04 → ~6.7 min | 13:45 · 10:23 · 14:50 → ~13 min |
| requests#7520 | 2:42 · 2:06 · 3:36 → ~2.8 min | 6:18 | 6:38 · 6:38 → ~6.6 min |
| logrus#1574 | 0:40 · 0:45 · 0:37 → ~0.7 min | — | — |
| fastify#6965 | 4:36 · 5:40 · 5:08 → ~5.1 min | — | — |
| celery#10493 (control) | — | ~14 min, one run | 8:43 |

The single-pass column is variant A, whose token count matched master
(88–109k), so it stands in for master here.

Where the time goes: the three finder passes run in parallel, so they do
not triple the clock — on requests they added twenty seconds. The judge
is the slow part, because it demonstrates every claim by running both
trees, and on a diff with six findings that is a lot of running. The
built-in reviewer executes nothing; forty seconds on logrus is what eight
reading angles cost when none of them starts an interpreter.

## Beyond Python, three passes — August 2026

The earlier cross-language runs were single-pass. Two cold runs with the
three-pass search, one each in Rust and Java, on PRs the projects
themselves later reverted or fixed — so the key is the project's, not ours:

| PR | Language | Ground truth | Verdict | The key, as rendered |
|---|---|---|---|---|
| tokio-rs/tokio#7757 | Rust | reverted by #8057: `spawn_blocking` hangs under load (#8056) | 🔴 Wrong shape | #1 BLOCKER — a stale `num_idle_threads` read stops the pool from growing and strands a task on an exiting thread |
| netty/netty#16837 | Java | fixed by #16949: `setAutoRead(false)` inside `channelRead` no longer honored (#16945) | 🟠 Ship after #1, #2 | #2 BLOCKER — `dequeueAll` no longer re-reads auto-read, so the backlog drains past the handler that just said stop |

Both keys came through the removed-guarantees pass; on netty the value
tracer reached the same line from the other side. Noise: zero. Two
honest limits recorded: the tokio judge rendered after one finder had
returned (the other two were still running when it was told to finish),
so that review rests on pass 2 plus the judge's own trace; and no JDK is
installed here, so every netty claim is traced by reading and the review
says so instead of pretending to have run `FlowControlHandlerTest`.
Tokens ~117k / ~156k; wall clock ~6 / ~8 minutes.

One run per language is a smoke test, as before — evidence the search
shape ports, not a recall figure.

## Faster — PR A

ROADMAP 9 asks for the same recall at `/code-review`'s speed. The
minutes go to the judge, not the finders — so the first PR changes what
the judge does with what finders bring back, and tried a cheaper model
for the finders. Cold runs on Opus (medium), the coordinator asked to
timestamp four points.

**S1 — finders on a cheaper model: rejected.** Three flask runs with the
three passes on Sonnet (two by instruction, one where the coordinator
chose it on its own after the instruction was removed):

| Key | Sonnet finders (3 runs) | 1.0.0 (three passes, Opus) |
|---|---|---|
| blueprint hooks skip (blocker) | **1/3** — found by the judge, not a finder | 5/5 across every measurement |
| OPTIONS cross-redirect | 0/3 | 3/3 |
| routes mutates live rule | 3/3 | 3/3 |
| required_methods flip | 0/3 | 3/3 |

Wall clock 5.2–7.3 minutes; the judge 76–88k; but the finders wrote
~60k each and found less, so the run cost more (~260k) than the run it
was meant to undercut. A finder that does not reach the dependency is
not cheaper, it is a different reviewer. The skill now says finders run
on the judge's own model, and why.

**S3 + S4 — finders bring their executed runs; the judge re-runs only
what decides a verdict; the constitution is read once, by the judge.**
Three valid flask runs, one requests, one control:

| | flask 1 | flask 2 | flask 3 | 1.0.0 flask ×3 |
|---|---|---|---|---|
| verdict | 🟠 after #1–#3 | 🔴 Wrong shape | 🟠 after #1–#4 | 🟠 · 🟠 · 🔴 |
| cards | 8 | 8 | 9 | 6 · 6 · 6 |
| hooks skip · routes · required_methods | ✓ · ✓ · ✓ | ✓ · ✓ · ✓ | ✓ · ✓ · ✓ | 3/3 each |
| OPTIONS cross-redirect | — | ✓ | ✓ | 3/3 |
| coverage card | ✓ | ✓ | ✓ | 3/3 |
| judge's own executions | 3 | 2 | 5 | every card |
| judge tokens | 94k | 90k | 85k | 152k · 183k · 191k |
| dispatch → written | 9:28 | 6:49 | 10:47 | ~13 min |

| | requests | celery control | 1.0.0 |
|---|---|---|---|
| verdict | 🟠 after #1 | 🟡 Ship with care | 🟠 · 🟢 (one earlier control was the same 🟡) |
| keys | quote blocker ✓, escape tests ✓, duplication → out of scope | one verified DESIGN: the smoke test passes on `main` too | 2/2 · 2/2 · 2/2 |
| judge tokens | 84k | 75k | 124k · 131k · ~140k |
| dispatch → written | 4:56 | 4:58 | 6:38 · 8:43 |

What the runs say. The judge's half of the review halved in tokens
(85–94k against 152–191k on flask, 75–84k against 124–140k on requests
and the control) and the clock fell from ~13 minutes to 7–11 on flask
and from ~7–9 to 5 on the smaller diffs — `/code-review` takes 4.7 and
2.8 on the same two PRs, so the gap is now 1.5–2× instead of 2.5×.
Recall held: every blocker on every run, cross-redirect 2/3 (gate ≥2/3),
the coverage card every time, the control still clean of noise. In
flask run 1 the judge distrusted all three finders on the `flask routes`
mutation, re-ran it, found its own invocation was wrong, and rendered
the finders' result — "re-run only what you doubt" working as written.

Two things on the record. Flask run 3 carries the first wrong sentence
in this whole measurement: its coverage card says `test_all_methods`
"was weakened", which two earlier judges and a finder had checked and
refuted (the new assertion pair is strictly stronger). The card's main
claim — no test covers the four regressions — stands; the sentence does
not. And the ≤6-minute target for flask was not reached: 6:49 once,
9–11 twice, because on a diff with four demonstrable blockers the judge
still runs four demonstrations. That is PR B's question, not this one's.

One harness lesson, now in the skill: a coordinator that dispatches
finders in the background and ends its turn to "wait" can sleep until
someone wakes it — one run sat four hours that way. Finders are awaited
synchronously; their return is what resumes the judge.

## Faster — PR B (rejected)

Hypothesis S2: the main-vs-PR demonstration stays mandatory for blockers
and for whatever the verdict turns on; design and question cards are
proven by the copied code, and the judge does not start an interpreter
to decorate a card that merges either way. Expected to take flask from
7–11 minutes to about 6, since the judge was making 2–5 runs of its own.

Three cold flask runs on Opus (medium), same protocol as PR A:

| | PR B run 1 | run 2 | run 3 | PR A (merged) |
|---|---|---|---|---|
| verdict | 🟠 after #1–#3 | 🟠 after #1, #2 | 🟠 after #1–#4 | 🟠 · 🔴 · 🟠 |
| cards | 7 | 6 | 7 | 8 · 8 · 9 |
| hooks · routes · required_methods | ✓ · ✓ · ✓ | ✓ · ✓ · 🟡 | ✓ · ✓ · ✓ | 3/3 each |
| OPTIONS cross-redirect | — | — | ✓ | 2/3 |
| judge's own executions | 3 | 5 | 3 | 3 · 2 · 5 |
| judge tokens | 82k | 92k | 88k | 94k · 90k · 85k |
| dispatch → written | 8:21 | 9:20 | 8:50 | 9:28 · 6:49 · 10:47 |

Nothing moved. Same minutes, same tokens, one fewer card, cross-redirect
down to 1/3 at n=3. The judge's runs were never going to the design
cards — they go to reproducing the blockers the finders had already
executed, and in two runs of three the first attempt at `flask routes`
was a wrong invocation that had to be redone. "A blocker carries the
run that shows the break" was read as "run it yourself", which is the
double work PR A had tried to remove, now made mandatory in prose.

Not merged. The ≤6-minute target is still open, and the next hypothesis
is the precise one this run points at: a finder's executed demonstration
satisfies the blocker's entry ticket; the judge re-runs a blocker only
when it doubts the finder's output, and says which output it doubted.
That is a one-sentence change and a separate measurement.

## Faster — the finder's run as the blocker's ticket (rejected)

PR B's diagnosis pointed at one sentence: the REPL-block rule says outputs
"must come from actually executing the code", and judges read that as
"execute it yourself", re-reproducing blockers their finders had already
run. The narrow edit (branch `finder-run-satisfies`, kept unmerged):
the Finding-format paragraph now says the execution may be a finder's —
paste its transcript; re-run only an output you doubt, and name which —
and step 5's re-run clause grew the same "say which output you doubted".

Three cold flask runs on Opus (medium). Two caveats first: the original
benchmark clones were garbage-collected with the session scratchpad, so
runs 1–2 worked in a fresh clone with no virtualenv and their finders
spent time building one; run 3 got ready venvs in both trees and is the
only clean comparison against PR B.

| | run 1 | run 2 | run 3 (venv ready) | PR B (rejected) | PR A (merged) |
|---|---|---|---|---|---|
| verdict | 🟠 #1–#4 | 🟠 #1–#3 | 🟠 #1–#4 | 🟠 ×3 | 🟠 · 🔴 · 🟠 |
| hooks · routes · required_methods | ✓ · ✓ · ✓ | ✓ · ✓ · ✓ | ✓ · ✓ · ✓ | 3/3 · 3/3 · 2/3+🟡 | 3/3 each |
| OPTIONS cross-redirect | ✓ | — | ✓ | 1/3 | 2/3 |
| judge's own executions | 2 | 3 | 2 | 3 · 5 · 3 | 3 · 2 · 5 |
| judge tokens | 93k | 129k | 109k | 82–92k | 85–94k |
| dispatch → written | 11:18 | 10:03 | 8:16 | 8:21–9:20 | 6:49–10:47 |

Pre-registered gate: flask ≤7:00 in two runs of three, or the judge's own
executions ≤1 on average. Neither happened — 0/3 and 2.3 — so the branch
stays unmerged by its own rule. Read honestly, the edit is hygiene, not
speed: every remaining judge run was a named doubt (a single-sourced
verdict-deciding claim re-run and confirmed; a wrong claim killed before
rendering), recall came back at full strength with cross-redirect 2/3,
and the one REPL block re-executed by hand matched its printed output.
But the minutes were never in those two runs. The clock's floor is the
finders themselves — 5:36–8:17 of wall time before the judge starts —
and no wording aimed at the judge can move it.

What would move it is out of scope for prose and recorded for later:
finders that share one warmed clone and environment instead of probing
it each (run 1–2 vs run 3 shows environment setup alone is worth two
minutes), or trimming what finders re-derive about the repository before
they start. Speed work on the judge is done; three hypotheses in, the
judge costs 85–110k and two named-doubt runs, and that is the shape of
the product.

## Faster — the judge prepares while the finders search (kept)

Two edits, measured together because both aim at the clock's real floor —
the finders' wall time — after three judge-side hypotheses closed that
side. First: the coordinator's wait is working time — while the finders
run, it reads the intent, matches the routing table and loads the
chapters, so the last finder's return starts judging, not preparation.
Second: pass 3 runs targeted experiments, not suites — a named test, at
most three executions, and the one revert-and-run that decides a verdict
belongs to the judge.

Five cold flask runs, one requests, one control, Opus (medium), ready
virtualenvs in every clone (the earlier environment-building confounder
removed):

| | flask ×5 | requests | celery control |
|---|---|---|---|
| dispatch → written | 6:56 · 8:33 · 5:54 · 7:05 · 5:59 — median **6:56** | **5:04** | **4:14** |
| before this change | 6:49–10:47 (PR A), 8:16–11:18 (later variants) | 6:38 | 8:43 |
| `/code-review` same PR | ~4.7 min | ~2.8 min | — |
| hooks · routes · required_methods | 5/5 · 5/5 · 5/5 | — | — |
| coverage card | 5/5 | ✓ | — |
| OPTIONS cross-redirect | 2/5 | — | — |
| judge's own executions | 2 · 4 · 1 · 7 · 2 | 1 | **0** |
| noise | 0 | 0 | 0 |

The pre-registered time gate — under 7:00 in two runs of three — was met
in three of five, with the two misses at 7:05 and 8:33. The control run
is the shape the design wants: two finders independently executed the
deciding demonstration, the judge doubted nothing, ran nothing, and the
review took 4:14 where 1.0.0 took 8:43.

One number is reported raw rather than smoothed: the werkzeug
cross-redirect key came up 2/5 here against 2/3 on the unchanged text —
neither edit touches passes 1 and 2, whose wording finds that key, and
across every variant measured this month the key has swung between 0/3
and 3/3. It remains the flakiest key in the rubric, not a regression
this change can explain — but 2/5 is what happened.

Judge-side conclusions from the rejected hypotheses held up here: the
judge re-ran only named doubts, and where two finders agreed it ran
nothing at all.

## Faster — adaptive depth (kept, pending merge)

ROADMAP 9's last lever: the clock's floor is the finders, and on a small
diff the fan-out buys nothing to protect — a reviewer can hold thirty
changed lines whole. The edit puts a triage at the top of step 3: up to
roughly a hundred changed lines, or a purely mechanical change set, and
the coordinator runs the three passes itself, inline, in sequence — the
same readings, the same rules, no dispatch. Escalation is one-way: a
small diff that proves bigger mid-pass (a value crossing into a
dependency, a guarantee with no visible home) gets the full pipeline
after all. Everything else fans out as before.

Measured on four small planted-flaw fixtures built for this purpose (the
originals were never committed) plus one large one, cold runs on Opus
(medium), ready virtualenvs, each run in its own copy of the fixture.
The pre-registered gate from the roadmap: small fixtures keep full
recall or the shortcut goes.

| Fixture (planted keys) | adaptive, recall | inline chosen | wall | tokens |
|---|---|---|---|---|
| retry swallows failure · timeout dropped · test weakened (3 keys, 30 lines) | 3/3 · 3/3 · 3/3 | 3/3 runs | 2:26–2:45 | 63–69k |
| price format duplicated · name lies · no test (3 keys, 16 lines) | 3/3 · 3/3 · 3/3 | 3/3 runs | 1:07–1:53 | 49–58k |
| limit off-by-one · test weakened in same diff (2 keys, 11 lines) | 3/3 · 3/3 | 3/3 runs | 1:16–2:03 | 57–62k |
| clean mechanical rename (control) | — | 2/2 runs | 1:23–1:48 | 55–60k |
| large: transfers feature, 124 insertions, 9 files | see below | **fan-out, 3 finders** | 6:55 | ~130k |

Every planted key was found in every adaptive run — most demonstrated by
executing both trees — and the verdicts were stable across runs. Noise:
zero below-altitude findings in eleven adaptive runs. One control run
rendered a card on the renamed `get` contradicting dict `get` semantics;
the unchanged baseline rendered the same card on the same diff with its
full fan-out, so the shortcut did not invent it.

The baseline for the same small fixtures, same protocol: with the
fan-out actually running (three finders), 4:11–5:46 and ~195–200k
tokens per run, same recall. Where the harness denied the baseline its
subagents and it fell back to sequential passes, it ran 1:49–4:42 at
59–82k — still behind the triaged runs, which skip the fallback's
re-reading along with the dispatch. So on small diffs adaptive depth is
roughly 2–3× faster and ~3× cheaper than the shipped pipeline at equal
recall, which closes the class of diffs where Punchcard was paying the
most for the least.

The large fixture is the other half of the gate: triage must not eat
the pipeline. Run solo, it dispatched all three finders, and the review
came back with two blockers the rubric had not even planted — a
negative transfer amount draining the destination (executed, including
`nan` corrupting the stored ledger) and the fee account creatable by a
customer — plus the planted audit-log split and float-money keys. The
escalation clause exists for the day triage misjudges; it was not
needed in these runs.

Two honest limits. The fixtures are synthetic and small-N (eleven
adaptive runs, five baseline); the real-PR rubric (flask, requests)
stays the recall benchmark for the pipeline itself, which this change
does not touch. And one harness observation from the baseline runs, on
the record: a coordinator that dispatches finders and ends its turn can
sleep until nudged, and finders could not always message the judge back
— the inline path removes that whole failure class from small reviews.
