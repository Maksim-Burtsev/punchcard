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
- **A constitution, not a mood.** Findings cite principles from a written
  constitution, so two runs argue from the same ground. Today it's ten
  bedrock principles (v0); the [roadmap](ROADMAP.md) replaces them with a
  synthesis distilled from ~30 classic software engineering books.

## Install

```
/plugin marketplace add Maksim-Burtsev/punchcard
/plugin install punchcard@punchcard   # plugin@marketplace
```

## Use

```
/punchcard                  # review working tree, or current branch vs default
/punchcard main..feature    # review a range
/punchcard <MR/PR url>      # review a PR/MR, render in the conversation
/punchcard:pr <url|number>  # review a PR/MR and post the review into it
```

`/punchcard:pr` posts one PR review on GitHub — the full review as the
body (permalinked to the reviewed sha), plus inline comments on findings
whose lines are part of the diff — or one MR note on GitLab. No access
to post? The review is rendered in the reply instead, with one line
saying why.

### In CI

GitHub Actions, review every PR ([claude-code-action](https://github.com/anthropics/claude-code-action)):

```yaml
permissions:
  pull-requests: write   # note: fork PRs get a read-only token
steps:
  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
      prompt: "/punchcard:pr ${{ github.event.pull_request.html_url }}"
      claude_args: '--allowedTools "Bash(gh:*),Read,Grep,Glob"'
```

GitLab CI:

```yaml
punchcard:
  script:
    - claude -p "/punchcard:pr $CI_MERGE_REQUEST_IID" \
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

## Auto mode

Drop an empty `.punchcard-auto` file into a repository's root and Punchcard
reviews the agents working in it. When an agent finishes a turn leaving
uncommitted changes, a Stop hook blocks the handoff and makes it review its
own work first: BLOCKER findings get fixed, DESIGN and QUESTION findings get
reported, and the loop is bounded — two rounds per session, then the work
ships as reviewed. Agents running in a loop end up applying fifty years of
engineering judgment to their own output before you ever see it.

```
touch .punchcard-auto   # opt in, per repository
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
