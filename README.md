<p align="center">
  <img src="assets/banner-card.png" alt="Punchcard — reviewing code since it came on cardboard" width="720">
</p>

<p align="center"><em>"There are two ways of constructing a software design: one way is to make it so simple that there are obviously no deficiencies, and the other way is to make it so complicated that there are no obvious deficiencies."</em><br>— C. A. R. Hoare, Turing Award lecture, 1980</p>

<p align="center">
  <a href="https://github.com/Maksim-Burtsev/punchcard/releases"><img src="https://img.shields.io/github/v/release/Maksim-Burtsev/punchcard?display_name=release&label=release&color=2ea44f" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license"></a>
  <a href="https://github.com/Maksim-Burtsev/punchcard#install"><img src="https://img.shields.io/badge/install-npx%20skills%20add-8A2BE2" alt="Install with npx skills add"></a>
</p>

<p align="center">Architecture-level code review <strong>for any coding agent</strong>.<br>
Three independent searches, one verdict, every blocker demonstrated by running the code.<br><br>
<strong>Benchmarked head-to-head with Claude Code's <code>/code-review</code> on real PRs: more blockers reported, the deepest caught by Punchcard alone, one verdict every single run — not a list when it feels like it. <a href="benchmarks/three-way-sonnet-2026-08.md">The numbers.</a></strong></p>

---

Point Punchcard at a working tree, a branch or a pull request and he reads
it the way the veteran who started on punch cards does: module boundaries,
dependency direction, the data model, the error paths, the cost of the next
change. Back comes the same review every time — one verdict, a summary
table, one card per finding, every claim shown on the code — inside
whatever coding agent you already work in.

## What he read

<p align="center">
  <img src="assets/corpus.png" alt="The thirty books of the corpus: cover collage, five shelves, in the order they are listed in CORPUS.md" width="100%">
</p>

Fifty years of the industry's best thinking, read cover to cover: thirty
books, five shelves, no others — distilled into 349 principles, then into
the 78 that decide a review. Every finding cites one, so he argues from
the canon, never from mood. Underneath the persona is a research question
asked in the open — what does a reviewer become when a specialist
bookshelf is condensed into one decided list of practices? — and the
benchmarks below are its measured answer so far.

- **I. The engineering canon** — Ousterhout, McConnell, Thomas & Hunt, Kernighan & Pike, Fowler, Feathers, Farley, Winters, Seemann, Hermans, Martin, the Gang of Four
- **II. Local design and responsibilities** — Beck, Wirfs-Brock & McKean, Evans, Fowler, Martin, Fairbanks
- **III. Architecture, change, technical debt** — Richards & Ford, Ford & Sadalage & Dehghani, Parsons & Kua, Tornhill, Spinellis
- **IV. Tests as proof of behavior** — Beck, Freeman & Pryce, Khorikov
- **V. Data, production, reliability, security** — Kleppmann, Nygard, Adkins et al., Johnsson & Deogun & Sawano

The shelf with ISBNs is [`CORPUS.md`](CORPUS.md); the distillations are in
[`corpus/distillates/`](corpus/distillates/), the decided forks in
[`corpus/conflicts.md`](corpus/conflicts.md), the constitution itself in
[`skills/punchcard/constitution/`](skills/punchcard/constitution/).

<details>
<summary><strong>One trace: book → principle → verdict</strong></summary>

Principle **1.4**, "Treat duplicated knowledge as a defect on sight", closes
with the line that makes it accountable:

```
**Sources:** (01, 02, 05, 13, 14, 18; F3)
```

That is Ousterhout, McConnell, Fowler's *Refactoring*, Beck's
*Implementation Patterns*, Wirfs-Brock & McKean and Fairbanks, plus fork
**F3** — "What makes duplication a finding" — where their disagreement was
decided rather than averaged.

On psf/requests#7520 that principle is finding #2 in the demo below: the
quoted-string scanner now exists twice, so the blocker in #1 has to be fixed
twice. The [stability benchmark](benchmarks/stability-2026-08.md) records it as
*quote rule duplicated*, **5/5** cold runs.

</details>

## How it reviews

Search and judgement are different jobs, so they run in different places.
Three finders read the same diff independently and return candidates, not
findings:

| Pass | Reads the diff as | Returns |
|---|---|---|
| 1 | every changed value, traced to its last consumer — inside the repository and inside the packages it calls | where the value lands wrong |
| 2 | every guarantee a deleted line used to make | the place the new code makes it again, or doesn't |
| 3 | every changed behavior | the test that goes red when it is reverted, or the missing case |

One judge then holds the candidates against the constitution, runs `main`
and the PR on the input that matters, and renders what survives: verdict,
summary table, one card per finding.

## See it

<p align="center">
  <img src="assets/demo.gif" alt="A Punchcard review of psf/requests#7520: verdict, summary table, and three finding cards — the regression run through main and the PR, the duplicated scanner side by side, the branches no test covers" width="900">
</p>

> A real review of [psf/requests#7520](https://github.com/psf/requests/pull/7520) — [the full text](assets/demo-review.md), as the skill rendered it.

## The verdicts

| Verdict | Meaning |
|---|---|
| 🟢 **Ship it.** | Nothing passed the gate. Merge, and here is what was verified. |
| 🟡 **Ship with care.** | Mergeable as is; the findings are worth closing, ideally in this PR. |
| 🟠 **Ship after #1…#N.** | The numbered findings are mandatory before merge; the rest can follow. |
| 🔴 **Wrong shape. Talk before more code.** | The design doesn't fit the problem. Stop. |

The verdict is followed by one sentence saying what to do right now, then a
summary table, then the findings. A finding looks like this:

---

### 🔴 2 · Charge failures vanish silently

`billing/api.py:48` · A failed charge leaves the order marked paid, and
nobody learns until month-end reconciliation.

The diff swallows every exception from the charge call, in `submit_order` at
`billing/api.py:48`:

```python
try:
    charge(order.total)
except Exception:
    pass          # ← a declined card is indistinguishable from a paid one
```

The order is then marked paid unconditionally, two lines later at
`billing/api.py:52`:

```python
order.status = "paid"
```

> 🔧 **Fix:** let the charge failure reach the caller — the endpoint's error
> handler already returns 502 and leaves the order unpaid.

---

## Install

```
npx skills add Maksim-Burtsev/punchcard
```

Any agent: this installs the skill into every harness it finds on the
machine. Everything below is the same skill, installed by hand.

<details>
<summary><strong>Claude Code</strong> — as a plugin, with <code>/punchcard</code>, <code>/punchcard:pr</code> and <code>/punchcard:brief</code></summary>

```
/plugin marketplace add Maksim-Burtsev/punchcard
/plugin install punchcard@punchcard   # plugin@marketplace
```

Or load it for one session without installing:

```
claude --plugin-dir path/to/punchcard
```

</details>

<details>
<summary><strong>Codex · Cursor · Gemini CLI · Copilot · OpenCode · Amp · Zed · Cline · Pi</strong></summary>

```
npx skills add Maksim-Burtsev/punchcard -a codex     # or cursor, gemini-cli, copilot, …
```

Or drop it in by hand — the skill is one self-contained directory:

```
cp -r skills/punchcard .agents/skills/
```

Invoke it as `$punchcard <target>` in Codex, `/punchcard <target>`
elsewhere; add the word `post` next to the target to have the review posted
into the PR/MR.

</details>

<details>
<summary><strong>Kiro · Windsurf · Goose · Droid · Hermes · Junie</strong></summary>

```
npx skills add Maksim-Burtsev/punchcard -a <agent>
```

</details>

<details>
<summary><strong>Aider</strong></summary>

```
/read-only skills/punchcard/SKILL.md
```

</details>

A small, single-concern diff skips the fan-out entirely: the reviewer runs
the same three passes itself, in sequence — same readings, same rules, a
fraction of the cost. The full three-finder pipeline runs when the diff is
large, or small but deep — rewired control flow, behavior moved between
layers, tests edited alongside a semantic change. Where the harness has no
subagents, the three passes run one after another in the same session —
the same review, only slower.

## Use

```
/punchcard                  # review working tree, or current branch vs default
/punchcard main..feature    # review a range
/punchcard <MR/PR url>      # review a PR/MR, render in the conversation
/punchcard:pr <url|number>  # review a PR/MR and post the review into it
/punchcard:brief <url|number|branch>  # orient before reviewing: claim, map, invariants, the hunks
```

The slash form is how Claude Code names a skill. Codex spells it
`$punchcard <target>`, and every other harness has its own way in — asking for
a Punchcard review of the target in plain words works everywhere. Where there
is no `:pr` command, put the word `post` next to the target instead.

Posting puts one PR review on GitHub (locations permalinked to the reviewed sha,
which GitHub expands into code cards) or one MR note on GitLab. Re-run it after a
push and it updates that same review in place — one entry per PR, for the life of
the PR. No access to post? The review is rendered in the reply, with the reason.

### The brief

`/punchcard:brief` is the other half of the reviewer's day: not what is
wrong with a change, but what it is. A diff is the delta of the text; the
reviewer needs the delta of the behavior, and rebuilding one from the other
is the hour the brief buys back. Four sections, always in this order —
**The claim** (what the description promises, and its class), **The map** (a
before/after drawing of the flow that changed, in plain ASCII, every node a
name from the code), **The invariants** (a before/after table of what holds
now), **The decision** (the hunks where behavior is chosen, copied from the
diff at their real lines). No findings and no verdict: that is `/punchcard`'s
job, and the brief is what to read before it. Two renders exactly as the
skill produced them, a one-line change and a six-hundred-line feature:
[assets/demo-brief.md](assets/demo-brief.md). The measurement behind it:
[the brief benchmark](benchmarks/brief-2026-09.md).

<details>
<summary><strong>In CI</strong> — GitHub Actions and GitLab CI</summary>

A fresh runner has nothing installed, so load Punchcard explicitly from a
checkout of this repository — below with `--plugin-dir`, in another harness
with whatever it reads skills from.

GitHub Actions, review every PR ([claude-code-action](https://github.com/anthropics/claude-code-action)):

```yaml
permissions:
  pull-requests: write   # note: fork PRs get a read-only token
steps:
  - uses: actions/checkout@v4
  - uses: actions/checkout@v4
    with:
      repository: Maksim-Burtsev/punchcard
      path: .punchcard
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
      prompt: "/punchcard:pr ${{ github.event.pull_request.html_url }}"
      claude_args: '--plugin-dir ./.punchcard --allowedTools "Bash(gh:*),Bash(git:*),Read,Grep,Glob"'
```

GitLab CI:

```yaml
punchcard:
  script:
    - git clone --depth 1 https://github.com/Maksim-Burtsev/punchcard /tmp/punchcard
    - claude -p "/punchcard:pr $CI_MERGE_REQUEST_IID" \
        --plugin-dir /tmp/punchcard \
        --allowedTools "Bash(glab:*),Bash(git:*),Read,Grep,Glob"
  variables:
    GITLAB_TOKEN: $CI_JOB_TOKEN
```

</details>

## Measured

Nothing on this page is a vibe: four benchmark reports, more than 150 cold
runs, fifteen-plus pull requests across a dozen repositories in six
languages. Every per-run review is matched by mechanism to a hand-verified
list of defects, and every factual claim re-executed against the code —
the reviewer's own claims included.

| Report | What it shows | Headline number |
|---|---|---|
| [Calibration](benchmarks/calibration-2026-08.md) | six PRs, four systematic faults found in the reviewer and fixed | the first clean "Ship it." |
| [Stability](benchmarks/stability-2026-08.md) | cold runs on two PRs plus a clean control, every edit measured before it stayed; Go, JS, Rust and Java smoke runs | every blocker-class finding stable, zero noise, the dependency-deep miss taken 3/3 |
| [With and without](benchmarks/with-without-2026-08.md) | the same four PRs by the bare model, by Punchcard, and by `/code-review`, three cold runs each, on Opus | zero below-altitude noise against 2.3 nit sections per bare review, reviews 37% shorter |
| [Three ways on Sonnet 5](benchmarks/three-way-sonnet-2026-08.md) | five PRs — three from repos no benchmark ever touched — by the bare model, Punchcard, and `/code-review`, with determinism and tokens measured for every condition | the most blockers reported, the deepest one caught by Punchcard alone, zero disproven claims, a verdict every time, median cost at bare-prompt level |
| [The brief](benchmarks/brief-2026-09.md) | twelve PRs in three languages briefed cold by URL, 38 Sonnet 5 runs in two rounds, scored against decision lists written before any run was read | decisions recalled 85/86, map at the right altitude 20/21, zero findings in 21 runs, 72/83 hunk anchors resolving in the file at head, median $0.39 a brief |

<details>
<summary><strong>Built, measured, rejected</strong> — the features that didn't survive their own numbers</summary>

A reviewer that only ever adds features is a wrapper. These were built,
measured against real work, and removed — each with the number that killed
it on the record:

- **Auto mode** — a Stop hook that reviewed on every turn. No automatic
  trigger fits the workflow; one line in `AGENTS.md` does the job exactly
  ([ROADMAP](ROADMAP.md), item 5).
- **Cheaper finder models** — measured and rejected: they lost a blocker
  that had never been missed ([CHANGELOG](CHANGELOG.md), 1.1.0).
- **A mandatory contract-enumeration sweep** — lifted the tail keys and
  dropped the stable fives; reverted, with the diagnosis written down
  ([stability report](benchmarks/stability-2026-08.md)).
- **The finding count** — "aim for three to five" was being read as a
  search budget and crowded out a blocker; removed, and the review got
  cheaper, not longer ([stability report](benchmarks/stability-2026-08.md)).
- **Inline PR comments** — split design-level cards across Files Changed
  and broke the verdict's reading order in live tests; one coherent review
  per PR instead ([ROADMAP](ROADMAP.md), item 7).

</details>

The cost, measured: a typical review runs at the price of a bare prompt.
A deep diff runs the full pipeline — and even there, the heaviest PR of
the latest campaign cost half of what `/code-review` spent on it. The
extra tokens buy one thing: every claim proven by running both trees.

## Keeping it in the loop

There is no hook and no daemon: you decide when a change deserves the
reviewer. The cheapest way to make that automatic for the agents
working in a repository is to say so in `AGENTS.md` or `CLAUDE.md`:

```markdown
Before opening a pull request, run the punchcard skill on the branch and
fix every BLOCKER it reports.
```

## Punchcard and friends

A bug hunter and Punchcard look for different defects. Claude Code's
`/code-review`, the one the benchmarks measure against, hunts runtime bugs
and returns a flat list — sometimes with the blocker, sometimes without it,
never with a decision. Punchcard judges the shape of the change and always
renders one. Measured from both sides on the same PRs, each catches things
the other doesn't; the deepest catch of the latest campaign — [a merged fix
whose emitted schema accepts exactly what its own parser
rejects](assets/zod-catch.md) — was Punchcard's alone. So run both,
whatever your harness calls its bug reviewer.

## Contributing

Issues and pull requests are welcome — a review that missed something, a
false positive, a harness where the install stumbles. A reproducible diff
(or PR link) is the perfect bug report.

## License

MIT
