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
