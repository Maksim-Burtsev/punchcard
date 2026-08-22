<!-- uncomment when assets/logo.png lands (roadmap #6)
<p align="center">
  <img src="assets/logo.png" alt="Punchcard" width="280">
</p>
-->

# Punchcard

> Reviewing code since it came on cardboard.

**Architecture-level code review for Claude Code.** Punchcard is the reviewer
every team wishes it had: the veteran who started on punch cards, shipped
through every era of the industry, and read the classics before they were
classics. He doesn't care about your variable names. He cares whether the
design fits the problem — and he says so in seven findings or fewer.

## Why another review tool

Ask a stock agent for a code review and you get a wall of text: nitpicks
about naming, a paragraph praising your structure, and a different verdict
every run. Punchcard is built on three constraints instead:

- **Altitude lock.** Boundaries, dependency direction, data model, error
  paths, cost of the next change. Never naming, formatting, or anything a
  linter catches — that's someone else's job.
- **The gate.** Every finding must have a real consequence, cite a numbered
  principle, and change how the code works or evolves — not how it reads.
  Hard cap of seven findings. "Ship it." is a complete review.
- **A constitution, not a mood.** Every finding is grounded in a numbered
  principle before it survives the gate, so two runs argue from the same
  ground rather than from taste. The constitution is 78 principles in 11
  chapters, [synthesized](CORPUS.md) from 30 classic software engineering
  books and a register of the decided conflicts between their schools.

## Install

```
/plugin marketplace add Maksim-Burtsev/punchcard
/plugin install punchcard@punchcard   # plugin@marketplace
```

Or load it for one session without installing:

```
claude --plugin-dir path/to/punchcard
```

## Use

```
/punchcard                  # review working tree, or current branch vs default
/punchcard main..feature    # review a range
/punchcard <MR/PR url>      # review a PR/MR, render in the conversation
/punchcard:pr <url|number>  # review a PR/MR and post the review into it
```

`/punchcard:pr` posts the review as one PR review on GitHub (locations
permalinked to the reviewed sha, which GitHub expands into code cards) or
one MR note on GitLab — a single coherent report, never scattered inline
comments. Re-run it after a push and it updates that same review in
place rather than adding another — one Punchcard entry per PR, for the
life of the PR. No access to post? The review is rendered in the reply
instead, with one line saying why.

### In CI

A fresh runner has no plugins installed, so load Punchcard explicitly
with `--plugin-dir` pointing at a checkout of this repository.

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

## Measured

Every claim above was checked on real open-source pull requests, with
the per-run reviews matched to a hand-verified list of defects and every
factual claim re-executed against the code. Three reports in
[`benchmarks/`](benchmarks/):

- [Calibration](benchmarks/calibration-2026-08.md) — six PRs, four
  systematic faults found in the reviewer and fixed, the first clean
  "Ship it."
- [Stability](benchmarks/stability-2026-08.md) — ten cold runs on two
  PRs: every blocker-class finding at 5/5, zero noise; plus Go and
  JavaScript smoke runs.
- [With and without](benchmarks/with-without-2026-08.md) — the same four
  PRs reviewed by the bare model, by Punchcard, and by Claude Code's
  built-in `/code-review`, three cold runs each. The bare model finds the
  blockers too. What Punchcard changes: zero below-altitude noise against
  2.3 nit sections per bare review, a verdict every time, reviews 37%
  shorter (70% on a clean PR), a slightly thinner tail — at about 1.6×
  the tokens.

## Keeping it in the loop

There is no hook and no daemon: you decide when the reviewer is worth
three minutes. The cheapest way to make that automatic for the agents
working in a repository is to say so in `AGENTS.md` or `CLAUDE.md`:

```markdown
Before opening a pull request, run `/punchcard` on the branch and fix
every BLOCKER it reports.
```

## Punchcard and friends

[Ponytail](https://github.com/DietrichGebert/ponytail) governs what you
build — the laziest solution that works. Punchcard judges whether what you
built fits the problem. A bug-hunting review (Claude Code's built-in
`/code-review`) catches the off-by-ones. Run all three and you have a senior
team; Punchcard is the one with the corner office and the punch card in his
shirt pocket.

## License

MIT
