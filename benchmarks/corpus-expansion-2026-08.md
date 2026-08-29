# Four more books: measured, and not shipped — August 2026

The corpus had no book for concurrency, none for messaging, none for APIs as
contracts, and only incidental coverage of measurement discipline. Four books
were distilled into it (31 Java Concurrency in Practice, 32 Patterns for API
Design, 33 Systems Performance 2e, 34 Enterprise Integration Patterns), the
constitution grew 78 → 86 principles, and three new forks were decided
(F16–F18). This file is the measurement that decided whether those constitution
changes ship. **They did not.** The corpus additions did.

## Protocol

Three public PRs, four conditions, three cold runs each: **36 runs**, all on
`claude-sonnet-5` via `claude -p`, `--output-format json`, repository cloned at
the PR head. Conditions:

- **new** — "Review pull request \<url\>… Read \<path\>/skill-new/SKILL.md and
  follow it." Skill at 86 principles.
- **old** — identical, pointing at the 78-principle skill.
- **bare** — the same prompt with no skill line.
- **code-review** — `claude -p "/code-review <merge-base>...HEAD medium"`.

The PR set — each one reverted or rolled forward upstream, so a real defect is
known to exist, and each chosen to exercise the newly added domains:

| PR | Language | Domain | Lines | Upstream outcome |
|---|---|---|---|---|
| rabbitmq/rabbitmq-server#13959 | Erlang | messaging, GC, performance | 101 | reverted 11 months later (#16142) |
| grpc/grpc-go#8278 | Go | published API contract | 122 | reverted (#8404), rolled forward (#8523) |
| kubernetes/kubernetes#140448 | Go | concurrency, delivery semantics | 186 | reverted (#140990) |

Candidate defects were pre-registered from the maintainer's own reading of each
diff before any run was examined. After the runs, every claim any condition made
was verified against the code; verified-real claims extended the union for all
conditions, and two pre-registered candidates were retired as maintainer errors
(k8s K5, grpc-go G3). Matching is by mechanism, never by wording or severity.

### The campaign that was thrown away

A first 36-run campaign ($41.59) was discarded before scoring was believed. The
host has three plugins enabled user-scope, and **ponytail** — whose description
triggers on any code-review task and pushes toward minimal output — was active
in all four arms, while the installed **punchcard** plugin (v1.4.0, the same 78
principles as the `old` arm) made `bare` a second `old` arm rather than a
no-skill control. The contaminated numbers were plausible-looking, which is the
reason to record this: the failure is invisible in the output. Every run here
passes `--settings` disabling all three, verified by probing the skill list.

Two protocol deviations from `three-way-sonnet-2026-08.md` are stated rather
than hidden: a user-level `CLAUDE.md` exists on this host and could not be
isolated (`HOME` and `CLAUDE_CONFIG_DIR` overrides break OAuth), so it applied
to all four arms equally; and three cold runs per cell instead of four.

## Recall against the verified union

Distinct union keys reached, per condition:

| PR | union size | new | old | bare | code-review |
|---|---|---|---|---|---|
| rabbitmq | 8 | 3 | **5** | 3 | 2 |
| grpc-go | 4 | 0 | **2** | 1 | 1 |
| kubernetes | 11 | **4** | 3 | — | — |
| **total** | | **7** | **10** | | |

The expanded skill found fewer of the defects that were written down in advance
than the skill it replaces. On grpc-go — the PR chosen specifically to exercise
the new API-contract principle 3.8 — it found nothing at all.

**Nobody, in any condition, found the defect that caused any of the three
upstream reverts.** rabbitmq's RB7 (the eager index delete turns compaction's
`previously_valid` skip into a byte-at-a-time rescan) was 0/12. grpc-go's G1
(the doc comment at `stream.go:138` still promises `io.EOF` while the code now
returns `Internal`) was 0/12 — and ten of the twelve runs cited the diff's own
new tests as evidence the change was safe, when those tests assert the new
behaviour and so ratify the break. kubernetes' correlation break was 0/6.

## Where the expansion did do something

On kubernetes it surfaced three real defects nobody had pre-registered, and the
`old` arm surfaced none: a stalled apiserver wedging all eight workers so every
later event is dropped (K10); `maxQueuedEvents = 1000` not being the queue
`ActionOrDrop` actually writes to, which is `watch.Broadcaster`'s untunable
25-slot `incoming` (K11); and `HandleCrash` deferred around the whole worker
loop permanently shrinking the pool (K12). That is the concurrency material of
book 31 doing exactly what it was added to do.

It came with the cost below.

## Discipline — the finding that decided this

Statements disproven by reading the code they claim to have traced:

| | new (86) | old (78) |
|---|---|---|
| false claims, rabbitmq | 0 | 2 |
| false claims, grpc-go | 3 | 0 |
| false claims, kubernetes | 8 | 1 |
| **total** | **11** | **3** |
| wrong clean bills | 4 | 4 |

Nearly four times the false-claim rate, and on kubernetes the false claims sit
*inside* correct findings and in one case produce a blocker that does not exist.
The three grpc-go false claims are each about code the run stated it had
verified. This is the opposite of the property the previous campaign measured
and published — zero disproven claims in twenty runs — and it is not a property
worth trading for three extra findings on one PR.

## Cost

Medians per run (tokens = input+output+cache-write; cost as billed):

| | new | old | bare | code-review |
|---|---|---|---|---|
| cost, median | $2.00 | $1.02 | $0.73 | $0.55 |
| cost, mean | $1.74 | $1.56 | $0.79 | $0.66 |
| minutes, median | 2.7 | 3.4 | 3.0 | 4.0 |
| words, median | 648 | 435 | 141 | 247 |

The expanded skill costs about twice the median of the one it would replace.
Whole clean campaign: $42.75 for 36 runs; $84.34 including the discarded one.

## Verdict

The four books are good. The constitution built from them is not better, on this
evidence, than the constitution without them: fewer pre-registered defects found,
three times the false claims, twice the cost per review, and no sighting of any
of the three defects that actually caused upstream reverts.

So the corpus additions ship and the constitution changes do not. Books 31–34,
their distillates, the updated cluster map and the three decided forks are merged
as dataset — the distillation is a one-time cost and this file records what it
bought, so the next attempt starts from here instead of repeating it. The
78-principle constitution and `SKILL.md` stay as they were.

What a next attempt should try, in the order the evidence supports it: add the
concurrency principles (5.7, 5.8) alone and measure them, since the kubernetes
column is the only place the expansion earned anything; leave 3.8 and 11.9 out
until there is a PR where they demonstrably fire; and treat any principle
addition that raises the false-claim rate as a regression regardless of what it
adds to recall.

## Reproduce

Clone the three PRs at the head shas in the protocol table. Materialise both
skill versions (`git archive master skills/punchcard` for the 78-principle arm).
Write a settings file disabling every installed plugin and verify with
`claude -p "List the names of every skill available to you right now"` before
starting. Run each condition three times cold via `claude -p` as specified. The
pre-registration, per-run outputs and the key×run matrices live in the session
scratchpad; the k8s K3 confirmation is `TestEventSeriesWithEventSinkImplRace`
under `-race` (1 failure in 300 runs at the PR head, 0 in 1500 on its base).

---

# Addendum: the two concurrency principles alone

The verdict above said a next attempt should add 5.7 and 5.8 by themselves and
measure them. That was done immediately, on the same three PRs, same protocol,
three cold runs: **9 runs, $16.45**. Only the new arm was run — the other columns
are the numbers already recorded above, with one re-tally noted below.

`conc` = the shipped 78-principle constitution plus exactly two appended
principles (5.7 shared mutable state under one named guard, reads included;
5.8 cross-thread handoff needs a real ordering edge). No amendments to existing
principles, no routing change, no `SKILL.md` change beyond the count.

**Re-tally, stated because it changes the comparison:** the kubernetes table
above credits the 86-principle arm with 4 keys because K10/K11/K12 were counted
separately as keys it discovered. Scored over the same eleven keys the `conc` arm
was scored against, that arm reaches 7. The corrected kubernetes row and the
corrected totals below use the eleven-key basis for every arm.

## Union keys reached

| PR | conc (80) | new (86) | old (78) | bare | /code-review |
|---|---|---|---|---|---|
| rabbitmq | 4 | 3 | **5** | 3 | 2 |
| grpc-go | **2** | 0 | 2 | 1 | 1 |
| kubernetes | 5 | **7** | 3 | — | — |
| **total** | **11** | 10 | 10 | | |

## False claims

| | conc (80) | new (86) | old (78) |
|---|---|---|---|
| rabbitmq | 1 | 0 | 2 |
| grpc-go | 2 | 3 | 0 |
| kubernetes | 4 | **8** | 1 |
| **total** | **7** | **11** | **3** |

Two principles instead of eight recovers the recall the 86-principle version lost
and then some — one key ahead of both other arms — and roughly halves its
false-claim rate. It does not reach the shipped constitution's discipline: seven
disproven statements against three, and one of them turns a minor finding into a
merge-blocker on a wrong pre-diff comparison (`conc-3` claims the pre-diff
goroutine had crash handling; it had none, so a panic killed the process).

## What it found that fifteen prior runs did not

- **rabbitmq RB1** (0/12 before): the `prioritise_cast` delete stream starving
  compaction in `gen_server2`'s merged queue — the mechanism family behind the
  upstream revert. One run named it with all four citations verbatim-correct.
- **grpc-go G1** (0/12 before): `ClientStream.RecvMsg`'s untouched doc comment
  still promises `io.EOF` while the code now returns `Internal`, and the diff's
  own new test is cited as *proof the contract broke* rather than as safety
  evidence — inverting the pattern every other run in the campaign fell into.
  Upstream reverted this PR for exactly that.
- **grpc-go G6** (new union key): the change silently reclassifies these RPCs
  from success to failure in `DoneInfo`, stats and channelz, because both
  `finish` paths normalize `io.EOF` to `nil` before the callbacks run.

On kubernetes it added nothing either other arm had not already found.

## What it still does not buy

The kubernetes correlation break stays 0-for-every-arm-ever-measured, and `conc`
is further from it than the 86-principle arm was: that arm at least raised K3
(unordered same-key sink writes); no `conc` run mentions output ordering at all.
The two principles moved attention to goroutine *lifecycle* — shutdown
cancellation, a panic-shrunk pool — and not to the handoff's ordering edge, which
is the half of 5.8 that would have mattered here.

Cost sits between the two: median $1.73 per run against $2.00 for the
86-principle version and $1.02 for the shipped one; median 2.7 minutes.

## Status

Not shipped. It wins the recall column by one key and loses the discipline column
by four, and discipline is what the main campaign was decided on. Three runs per
cell on three PRs the previous campaign already used is enough to justify a wider
measurement and not enough to change the constitution — and the grpc-go win in
particular sits entirely in one run of three, on a PR whose defect is an API
contract rather than concurrency, so it is as consistent with variance as with
the principles doing the work.

A wider measurement should use PRs whose defect is concurrency proper, four cold
runs per cell, and should treat the false-claim column as the gate. The branch is
`concurrency-only-31`.
