# Three ways on Sonnet 5, on PRs the skill has never seen — August 2026

The [with/without measurement](with-without-2026-08.md) ran on Opus, on four
PRs — two of which the skill had been calibrated against — and left two gaps
open: no determinism or token numbers for `/code-review`. This measurement
closes both, on a model the skill was never tuned on, with three of five PRs
from repositories no Punchcard benchmark had ever touched.

## Protocol

Five public PRs, three conditions, four cold runs each: **60 runs**, all on
`claude-sonnet-5` via `claude -p` (CLI 2.1.245), `--output-format json` for
exact token/cost/time capture, repository cloned at the PR head,
dependencies pre-installed. No user-level CLAUDE.md existed on the host, so
no configuration voice leaked into any condition. Conditions:

- **bare** — "Review pull request \<url\>. The repository is cloned at
  \<path\>, checked out at the PR head. Do not run the project's full test
  suite." Nothing else.
- **punchcard** — the same, plus "Read skills/punchcard/SKILL.md and follow
  it." Skill at `adaptive-depth` (post-1.2.0).
- **code-review** — `claude -p "/code-review <merge-base>...HEAD medium"`
  from inside the clone.

The PR set — two anchors with a known union, three fresh, three languages:

| PR | Language | Why it's in |
|---|---|---|
| psf/requests#7520 | Python | anchor: hand-verified union from the stability report |
| fastify/fastify#6965 | JS | anchor: de-facto clean control (its two union keys were found 0/18 times historically) |
| encode/starlette#3466 | Python | fresh: routing-index redesign, closed by maintainers |
| caddyserver/caddy#7952 | Go | fresh: security hardening, open |
| colinhacks/zod#6461 | TS | fresh: JSON Schema intersection folding, merged |

Candidate defects for the fresh PRs were pre-registered from my own reading
of the diffs before any run was examined (`pre-union` file, committed to the
session record, not the repo). After the runs, every claim any condition
made was verified against the code — by executing both trees where
possible — and verified-real claims extended the union for all conditions.
Matching is by mechanism, never by wording or severity.

Three bare runs (out of 60 total) ended mid-flight — the `-p` session
closed while its own background subagents were still working, leaving
narration instead of a review — and were re-run cold. One re-run fetched
the PR's true head (one commit ahead of the pinned clone) on its own; caddy
carries no union keys, so nothing scored differently.

## The verified union

**requests** (from the anchor rubric, re-verified by execution): U1 an
unterminated quote swallows every later Link entry — main recovers them,
the PR collapses them into one corrupted field (**blocker**); U2 the
quote/escape state machine exists twice; U3 the escape branch has no test.
The backslash-never-unescaped claim three conditions raised is *identical
on main and on the PR* (executed both) — pre-existing, outside the union,
and a review that frames it as a regression is making a false claim.

**starlette**: SA1 a `Route`/`Mount` subclass overriding `matches()`
silently 404s — the index consults only the declared `path`
(**blocker-class**, executed repros in three independent runs); SA2 the
index caches the mutable `.path` while matching uses the immutable
`path_regex`, so in-place route mutation strands the route (executed);
SA3 `is_stale` does an O(N) list-equality per request — twice on the
redirect path — undercutting the index's own purpose. Tail: SA5 the
param-led-Mount fallback branch has no request-level test (verified: the
only such Mount in the suite is exercised via `url_path_for` only).

**zod** (each verified by my own execution): **ZB1 the nested-property fold
pools unrelated members, so the emitted JSON Schema *accepts* objects the
parser rejects — the exact unsoundness class the PR exists to fix, one
level deeper, and a regression against main (blocker)**; ZD2 `assignProps`
aliases the `allOf` array across occurrences, so an `override` on one
occurrence corrupts a sibling and silently defeats the fold; ZD3 the fold
is target-dependent — a record intersection folds on draft-4 and declines
on 2020-12/draft-7; ZE4 chained `.and()` conversion goes cubic (measured
independently by three separate runs, ~187 s at N=1600).

**fastify**: both historic keys again found by nobody (0/12) — a clean
control in practice. **caddy**: no verifiable defect; the one contested
claim (an empty-basis `~1.TXT` alias bypass) cannot be proven off-Windows —
one bare run called it "confirmed" anyway, one honestly said PLAUSIBLE, one
punchcard run traced the same class and declined it for lack of evidence,
and `/code-review` asserted the opposite ("never a false negative") with
the same lack of evidence. The PR author has since pushed "fail closed on
extended short names", which is consistent with the class being real.

## Recall — the honest headline first

Mean recall against the union, and mean pairwise Jaccard within a
condition (empty sets on the two control PRs count as perfect agreement):

| PR | bare R / J | punchcard R / J | code-review R / J |
|---|---|---|---|
| requests | 0.50 / 0.25 | 0.58 / 0.33 | 0.25 / 0.17 |
| starlette | 0.50 / 0.67 | 0.33 / 0.50 | **0.75** / 0.58 |
| zod | 0.00 / 1.00 | 0.19 / 0.17 | 0.25 / 0.33 |
| fastify (control) | 0 keys found, all | same | same |
| caddy (control) | — / 1.00 | — / 1.00 | — / 1.00 |

**Nobody wins recall, and nobody is stable on the tail.** On Sonnet 5 the
tail-variance property the stability report established for Punchcard
holds for all three conditions. What separates them is *which* defects
they can see at all, and what they do when they see nothing.

## Blockers

Three verified blocker-class keys existed. Runs that reported them:

| Blocker | bare | punchcard | code-review |
|---|---|---|---|
| requests · unterminated quote | 2/4 | **3/4** | 1/4 |
| starlette · subclass `matches()` silent 404 | **4/4** | 3/4 | **4/4** |
| zod · emitted schema accepts what the parser rejects | 0/4 | **1/4** | 0/4 |
| total | 6/12 | **7/12** | 5/12 |

The zod row is the class divider. ZB1 is invisible to a diff-reading bug
hunt: finding it required treating the parser's semantics as the contract
and executing the emitted schema against the parser on an input the tests
never construct. One punchcard run did exactly that; zero of eight
bare/code-review runs came near it. The same pattern produced ZD2
(punchcard only) on one side and ZD3/ZE4 (code-review strongest) on the
other.

## Found by only one condition, across all 20 of its runs

| Only punchcard | Only code-review | Only bare |
|---|---|---|
| zod: the ZB1 soundness blocker | zod: target-dependent fold (ZD3) | — |
| zod: override-aliasing defeats the fold (ZD2) | zod: repo-CLAUDE.md convention violations (JSDoc rules, three-axes reporting) — legitimate per that repo's own contract | |
| starlette: param-led Mount branch untested (SA5) | | |

On Opus, `/code-review` never saw the duplicated-scanner key; on Sonnet it
reports it in 2 of 4 requests runs. The design-blindness claim from the
with/without report does **not** carry to Sonnet unchanged — what carries
is narrower and sharper: the *executed-semantic-contract* class (ZB1, ZD2)
appeared only under the skill, in the runs where its verdicts were worst
elsewhere.

## Discipline — where the daylight actually is

**Wrong clean bills.** Runs that asserted the change clean while a
verified blocker existed in it: bare **4** (every zod run: "no correctness
bug found"), code-review **3** (two requests runs — one of them stating
the unterminated-quote case "parses correctly", disproven by execution —
plus one zod run), punchcard **2** (two zod runs rendered 🟢). Nobody is
immune; punchcard is least exposed, and its two misses are the two runs
that stayed inline where the diff deserved the pipeline.

**False factual claims** (statements disproven by execution): bare 2 — the
starlette re-run's "`is_stale` correctly detects mutations" (it cannot:
the snapshot list holds the same route objects, so the comparison is
`a == a`) and caddy's "confirmed" on an unverifiable bypass; code-review
1 (the requests clean bill above); punchcard 0 — every punchcard claim
checked in this campaign survived re-execution, including its two deep zod
repros, both reproduced here from its own written commands.

**Verdicts.** punchcard 20/20 open with the four-state ladder and a
one-sentence instruction. bare: 2/20 carry anything verdict-shaped;
code-review: 0/20 by design. On the clean control both punchcard(4/4 🟢
with a revert-executed proof) and the others agree in substance — but only
one of the three tells you *to merge*.

**Noise.** Below-altitude sections: zero in all 60 runs, all three
conditions. The 2.3-sections-per-review noise that separated conditions on
Opus does not exist on Sonnet 5 — that differentiator is gone, and this
report says so rather than repeating it.

**Severity honesty.** Two punchcard wobbles: one requests run rendered the
blocker as 🟡 DESIGN, and one rendered the out-of-gate backslash key as a
🔴 blocker (its demonstration was accurate; the altitude call was not).
Recorded as the price of the tail variance already on file.

## Cost

Medians per run (tokens = all models, input+output+cache-write; cost as
billed; minutes wall):

| | bare | punchcard | code-review |
|---|---|---|---|
| tokens, median | 74k | 71k | 53k |
| tokens, mean | 103k | 137k | 154k |
| cost, mean | $0.71 | $1.28 | $1.03 |
| minutes, median | 2.7 | 3.6 | 2.3 |
| words, median | 190 | 316 | 194 |

Two inversions against the Opus-era numbers, both worth stating plainly:

- **Punchcard is no longer the expensive one by default.** Adaptive depth
  keeps its median (71k) at bare's level; the mean is pulled up by the
  four large-diff runs that fan out (starlette/zod, 206–464k) — the
  documented price of executed proofs on diffs that need them.
  `/code-review`'s mean is the highest: its fan-out on the zod monorepo
  billed 347–670k per run (median 495k), 7× punchcard's median.
- **Punchcard reviews are now the longest, not 37% shorter** — Sonnet's
  bare reviews are terse (190 words median). The card format spends its
  words on executed evidence; whether that is worth it is a taste the
  reader can judge from the transcripts.

Adaptive-depth triage wobbled once: the same caddy diff ran inline twice
(~65k) and fanned out once (201k) — the 229-line diff is 180 lines of
tests, straddling the threshold. Whole campaign: $60.41 for 63 runs.

## The summary table

| | bare Sonnet 5 | Punchcard | `/code-review` |
|---|---|---|---|
| mean recall (4 keyed PRs) | 0.25 | 0.28 | 0.31 |
| blockers reported | 6/12 | **7/12** | 5/12 |
| the zod soundness blocker | 0/4 | **1/4** | 0/4 |
| classes only it saw | — | executed-semantic-contract (ZB1, ZD2), test-seam (SA5) | target-matrix gap (ZD3), repo-convention contract |
| wrong clean bills | 4 | **2** | 3 |
| false claims (disproven by execution) | 2 | **0** | 1 |
| explicit verdict | 2/20 | **20/20** | 0/20 |
| noise sections | 0 | 0 | 0 |
| tokens median / mean | 74k / 103k | 71k / 137k | 53k / 154k |
| worst-case run | 270k | 464k | **670k** |
| minutes median | 2.7 | 3.6 | 2.3 |

## Verdict on the verdict, second edition

On a strong model, all three conditions find most blockers most of the
time, none reliably, and the old noise gap is gone. What the skill is
provably buying on Sonnet 5, on PRs it never saw, is: the only sighting of
the one defect in this campaign that makes a merged fix unsound (and the
only condition with zero disproven claims in 20 runs), a mandatory
executed-proof discipline that produced those sightings, a verdict every
single time, and a median cost at bare-prompt level. What it is provably
not buying: recall superiority, tail stability, or brevity. Run
`/code-review` beside it for the target-matrix and convention classes it
sees and Punchcard doesn't. This file exists so the README's claims can be
no larger than these numbers.

## Reproduce

Clone each PR at the head shas in the protocol table, install deps, and
run each condition four times cold via `claude -p` as specified above. The
per-run outputs and the key×run matrix live in the session scratchpad; the
verification probes for U1/U5, SA1/SA2/SA5, ZB1/ZD2/ZD3 are two-tree
executions written down in the scoring record.
