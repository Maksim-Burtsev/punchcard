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
