# With Punchcard and without — August 2026

The question a team asks before installing a reviewer: what does it change
compared to just asking the agent to review? This measurement answers it
on the same model, the same PRs, the same number of runs.

## Protocol

Four public PRs with a hand-verified union of real findings, carried over
from the [stability measurement](stability-2026-08.md) and the
cross-language smoke runs:

| PR | Language | Union | Blocker-class keys |
|---|---|---|---|
| pallets/flask#5918 | Python | 7 | 4 |
| psf/requests#7520 | Python | 4 | 1 |
| sirupsen/logrus#1574 | Go | 4 | 1 |
| fastify/fastify#6965 | JS | 4 | 1 |

Three conditions, three cold runs each per PR, 36 runs in all, every run
on Opus (medium) with the repository cloned at the PR head. The first two
are compared next; the third, `/code-review`, in its own section below:

- **without** — the prompt is "Review pull request <url>", plus where the
  clone is and a request not to run the test suite. Nothing else.
- **with** — the same, plus "read SKILL.md and follow it".

Findings were matched to the union by mechanism, never by wording or
severity. Claims outside the union were checked against the code; real
ones extended the union for both conditions (one did — see below).
Noise was counted as sections of the review that sit below Punchcard's
altitude: naming, comment wording, nits, praise, changelog reminders,
"performance: no measurable change", "docs need no change", backport
planning.

## Recall — what each condition found

Mean recall against the union, and hit rates on the blocker-class keys:

| PR | without | with | Blocker keys, without → with |
|---|---|---|---|
| flask#5918 | 0.76 | 0.62 | hooks-skip 3/3 → 3/3 · routes-mutation 3/3 → 2/3 · required_methods 2/3 → 3/3 · cross-redirect 1/3 → 0/3 |
| requests#7520 | 0.92 | 0.92 | unterminated quote 3/3 → 3/3 |
| logrus#1574 | 0.75 | 0.58 | fix in dead code 3/3 → 3/3 |
| fastify#6965 | 0.25 | 0.25 | preHandler bypass 0/3 → 0/3 |

Read this honestly: **the stock agent on this model finds the blockers
too.** Every headline defect — blueprint hooks silently skipped, the
routing table mutated by a display command, a Link header swallowed by
one stray quote, a fix landing in a function the logging path never
calls — was found by both conditions in nearly every run. On the tail,
the stock agent lists more: it writes seven to ten numbered items where
Punchcard's cap holds it to three to five, and on flask and logrus that
costs Punchcard two tail keys per run on average. One run with Punchcard
also missed a blocker (flask's routes-mutation, 2/3) that the stock agent
caught 3/3. Recall is not where Punchcard wins.

Two discoveries belong to luck, in both conditions. One stock run on
flask found a blocker nobody had — with every automatic-OPTIONS rule
sharing one endpoint, Werkzeug's default-redirect logic cross-talks
between unrelated routes, and `OPTIONS /posts/page/1` now 308s to
`/users/` — verified here by running both trees, found by 1 of 6 runs.
And fastify's security-relevant sibling bypass (a malformed URL reaches
the not-found handler with its `preHandler` skipped), found once in the
earlier smoke run, was found by 0 of 6 runs here. At three runs, rare
findings are a coin toss for everyone.

## Where the difference is

**Noise.** Eleven of twelve stock reviews carry sections below the
altitude — 28 in total, 2.3 per review: "Nits", "Minor", "What's good",
"Drop the Go version note", "The comment documents the mechanism but not
the precondition", "Performance: no measurable change", "Docs need no
change", "Backport", a shadowed loop variable, a missing HTAB in a
separator regex. Punchcard: zero in twelve. Not low — zero.

**Verdict.** Every Punchcard review opens with one of four statuses and a
sentence saying what blocks. Stock reviews carry a verdict when they feel
like it — "needs changes", "request changes", "approve", or a section
called "The bug, confirmed" with no decision anywhere — and on the PR
where nothing blocks, one run approves, one requests changes, one does
both.

**Length.** Stock reviews average 1,365 words; Punchcard's 857 — 37%
shorter overall, and on the PR that needed the least said (fastify),
397 words against 1,344: 70% shorter, because a cap plus a gate means a
clean change gets a short review rather than a long search for something
to say.

**Evidence discipline.** Both conditions demonstrated claims by running
code — this is the model, not the skill. What the skill adds is the
refusal to say things it did not run: no stock review was caught in a
false claim among those checked, but several state test behavior by
inference ("this passes on main as well") where Punchcard is bound to
execute or stay silent.

## Against `/code-review`

Claude Code ships a reviewer: `/code-review`, a correctness bug-hunter
that reports findings as a list with file and line. For a Claude Code
user that is the real baseline, so the same four PRs got three more cold
runs each: `claude -p "/code-review <base>...<head> medium"` from inside
the clone, output captured to a file. (One caveat: `--bare` drops the
login, so these runs inherited the host's global configuration; the
prose carries that voice, the findings do not appear to.)

| PR | `/code-review` recall | Punchcard recall | Found only by `/code-review` | Found only by Punchcard |
|---|---|---|---|---|
| flask#5918 | 0.67 | 0.62 | OPTIONS cross-redirect **3/3** (Punchcard 0/3); the `except: pass` swallow 3/3 (1/3) | no-single-source 3/3 (0/3); `Rule.methods` introspection 2/3 (0/3) |
| requests#7520 | 0.33 | 0.92 | — | the unterminated-quote **blocker 3/3 (`/code-review` 1/3)**; valueless-param tail 3/3 (0/3); escape tests 2/3 (0/3) |
| logrus#1574 | 0.25 | 0.58 | — | test at the wrong altitude 2/3 (0/3); `errors.Join` identity 1/3 (0/3); two loops disagree 1/3 (0/3) |
| fastify#6965 | 0.08 | 0.25 | — | `errorHandler` restored untested 2/3 (0/3) |

Blocker-class keys by condition, three runs each:

| Blocker | bare model | Punchcard | `/code-review` |
|---|---|---|---|
| flask · blueprint hooks skip | 3/3 | 3/3 | 3/3 |
| flask · routes mutates live rule | 3/3 | 2/3 | 3/3 |
| flask · required_methods flip | 2/3 | 3/3 | 2/3 |
| flask · OPTIONS cross-redirect | 1/3 | 0/3 | **3/3** |
| requests · unterminated quote | 3/3 | 3/3 | 1/3 |
| logrus · fix in dead code | 3/3 | 3/3 | 3/3 |
| fastify · preHandler bypass | 0/3 | 0/3 | 0/3 |

Two reviewers, two shapes. `/code-review` is the better bug-hunter on
one axis: the flask cross-redirect — a pure runtime-behavior defect
buried in Werkzeug's routing internals — it found three times out of
three where Punchcard found it never and the bare model once. Everything
design-shaped it does not see at all: duplicated knowledge, a contract
with no single source, a test pinning the wrong seam, a widened blast
radius without a test — zero across twelve runs, because those are not
bugs and it is not looking for them. And it is not reliable on the
regression that matters most in requests: the unterminated-quote
blocker, which both other conditions found 3/3, it found once.

Form: `/code-review` output is a flat list, no verdict, 140–330 words —
the shortest of the three — with essentially no below-altitude noise
(it is correctness-scoped by design). Two of its fastify runs reported
no findings and instead listed what they had verified as clean; one of
those clean bills is wrong — it asserts the lazily built validation
memo "still lands on the child", while the code's `== null` guard
inherits a parent map that already exists, which the Punchcard run
demonstrated by execution. Token cost was not captured for this
condition (`-p` prints no usage).

So the README's claim holds, with numbers: run both. `/code-review` for
the runtime defect a design reviewer is not hunting; Punchcard for the
shape of the change and a decision about it. Neither replaces the other,
and on this evidence neither replaces a bare strong model for raw
recall — they replace it for discipline and for the class of defect each
is built to see.

## The cost

Punchcard reviews cost more: roughly 140k tokens per run against 88k
for the stock prompt, about 1.6×. The skill reads its constitution
chapters and runs more experiments before rendering. A team choosing it
is paying 60% more per review for a review that is 37% shorter, carries
no noise, always renders a decision, and finds the same blockers —
occasionally one fewer on the tail.

## Verdict on the verdict

Punchcard is not a better bug-finder than the agent it runs on. It is
the same finder with a gate, a cap, a fixed verdict ladder, and a ban on
saying what it has not shown. On a strong model that is what you get:
less text, no nits, a decision every time, the blockers intact, and a
slightly thinner tail — for more tokens. Whether that trade is worth
making is the team's call; this file is so it can be made with numbers.

## Reproduce

Clone each PR at its head, open a fresh session, and run each condition
three times. The rubric of verified mechanisms is in the stability
report's protocol; the per-run reviews are not committed.
