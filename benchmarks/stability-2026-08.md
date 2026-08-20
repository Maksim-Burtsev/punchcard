# Finding stability across runs — August 2026

The August calibration named run-to-run variance as a known limit: two cold
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

## Reproduce

Clone the target, check out the PR head, open a fresh session with only
the skill and the target named, run five times, match by mechanism. The
per-run reviews and matching tables for both conditions are not committed;
this file records the protocol and the numbers.
