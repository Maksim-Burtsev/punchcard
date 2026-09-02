# Roadmap

- [x] **1. Walking skeleton** — plugin structure, `/punchcard` command, skill
  v0 with a ten-principle stub constitution, smoke-tested on a planted-flaw
  diff.
- [x] **2. The corpus** — 30 deliberately chosen books (see
  [CORPUS.md](CORPUS.md)): the persona's worldview, not an industry survey.
  Sources live in `books/` (gitignored — the corpus never ships; only the
  synthesis does). All 30 collected and machine-verified for completeness
  and text extraction; `scripts/extract_corpus.py` turns them into chunked
  plain text under `books/.text/`.
- [x] **3. The synthesis** — done in three PRs: 30 distillates
  (`corpus/distillates/`, 349 principles), 11 clusters and a register of 15
  explicitly decided forks (`corpus/clusters.md`, `corpus/conflicts.md`),
  and the constitution — 11 chapters, 78 principles (`skills/punchcard/constitution/`) —
  now wired into the skill: a 15-principle core plus per-diff chapter
  routing. `CORPUS.md` serves as the bibliography. Smoke-tested on three
  planted-flaw fixtures: 30/30 flaws caught across six runs, zero style
  baits taken.
- [~] **4. GitLab/GitHub inline** — dropped by decision: the local diff
  review covers the actual workflow, and a posting integration is a second
  product to maintain.
- [~] **5. Auto mode** — built as a Stop hook, then removed. No automatic
  trigger fits: `Stop` fires on every turn including plain questions, a
  commit hook re-reviews the same growing branch once per commit (fifty
  commits, fifty reviews), and PR creation comes after the work is done.
  When to call a reviewer is a human judgement; a line in `AGENTS.md`
  expresses it exactly and costs nothing.
- [x] **6. Benchmarks & release** — with/without measured on four real
  PRs, 24 cold runs (`benchmarks/with-without-2026-08.md`), and against
  the built-in `/code-review`: same blockers, zero below-altitude noise
  against 2.3 sections per stock review, a verdict every time, 37%
  shorter. Released as `punchcard--v1.0.0` on 2026-08-23: README with the
  doyen, Hoare, a replayed review and how it reviews; Rust and Java smoke
  runs; install verified from a fresh config.
- [x] **7. PR/MR comments as a render surface** — `/punchcard:pr` reviews
  a GitHub PR / GitLab MR and posts into it: one review (`COMMENT`) on
  GitHub whose body is the full render with sha permalinks, one MR note
  on GitLab. Deliberately no inline comments: punchcard findings are
  design-level cards spanning files, and splitting them across Files
  Changed broke the verdict's numbering and reading order in live tests.
  Re-runs update the same review in place (marker `<!-- punchcard -->`),
  so a PR carries one Punchcard entry for its whole life. No posting
  access → the review renders in the reply with one line saying why.

- [x] **8. Deep mode — done differently.** The open question was whether
  union coverage was worth N identical finder passes. The answer was
  three *different* ones: every value to its last consumer, every removed
  guarantee to its new home, the test that goes red on revert — run as
  independent subagents, judged in one place. The class that three prose
  edits had failed on (a consequence terminating inside a dependency)
  went 3/3, a new key nobody had found appeared, the clean control stayed
  clean; cost ~1.7× tokens and about twice the minutes on a complex diff
  (`benchmarks/stability-2026-08.md`, "Independent search passes").
- [x] **9. Faster.** Punchcard now finds at least what `/code-review`
  finds, for more tokens and more minutes. The measurement went the
  other direction: the same recall at its speed or better. 1.2.0 took
  the first half (the judge prepares while the finders search; pass 3
  probes); **adaptive depth** took the second: a triage at the top of
  step 3 — a diff that is both small (~under 100 changed lines) and
  shallow runs the three passes inline with no fan-out; complexity
  overrides size, escalation is one-way, and "when in doubt, fan out"
  is written into the rule. Measured twice, the way this item demanded:
  planted-flaw fixtures (every key in all eight keyed runs, zero noise
  in eleven, 1–3 min and ~50–70k tokens against 4–6 min and ~195k for
  the fanned-out baseline in the same harness), then the real-PR rubric
  three ways against `/code-review` and the bare model — where the
  flask boundary case (86 lines of rerouted dispatch; one inline run
  missed a blocker the escalated run then took in full) put the
  shallowness test into the triage rule. Large or deep diffs keep the
  pipeline and its measured ~1.5–2× cost — the price of executed
  proofs, scoped in the README
  (`benchmarks/stability-2026-08.md`, "adaptive depth", "three ways").

- [x] **10. Any harness ✔** — the skill is self-contained (constitution
  next to `SKILL.md`), installs with `npx skills add` into 116 harnesses,
  and names its own fallback: without subagents the three passes run in
  sequence. Codex, Cursor, Gemini CLI and the rest get the same reviewer
  Claude Code gets.
- [x] **11. Corpus expansion 31–34 — corpus shipped, constitution didn't.**
  Four books for the domains the corpus had no book for: concurrency,
  APIs as contracts, measurement discipline, messaging. Distilled by the
  same three-stage pipeline as phase 3 (47 principles, one revision
  round), folded into the clusters, and three forks decided (F16–F18).
  Then measured: 36 cold runs on three reverted-upstream PRs, the
  86-principle constitution against the 78-principle one. It found fewer
  pre-registered defects (7 union keys against 10), made nearly four
  times the disproven claims (11 against 3), cost twice the median per
  review, and no condition saw any of the three defects that caused the
  upstream reverts. So the distillates, clusters and forks are merged as
  dataset and the constitution stays at 78
  (`benchmarks/corpus-expansion-2026-08.md`, which also records the
  first campaign thrown away for plugin contamination and what a next
  attempt should try instead).
- [x] **12. The brief — road-tested, not yet settled.** `/punchcard:brief`
  hands the reviewer the model of a change before the diff: claim, an
  ASCII before/after map, a before/after table, the hunks where behavior
  is chosen. No findings. Measured on Sonnet 5 in two rounds and shipped
  with its limits on the record; the format will move as it gets used
  (`benchmarks/brief-2026-09.md`).
