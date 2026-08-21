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
  and the constitution — 11 chapters, 78 principles (`constitution/`) —
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
- [ ] **6. Benchmarks & release** — the same set of real MRs reviewed with
  and without Punchcard, results published in `benchmarks/`; polish, logo,
  marketplace listing.
- [x] **7. PR/MR comments as a render surface** — `/punchcard:pr` reviews
  a GitHub PR / GitLab MR and posts into it: one review (`COMMENT`) on
  GitHub whose body is the full render with sha permalinks, one MR note
  on GitLab. Deliberately no inline comments: punchcard findings are
  design-level cards spanning files, and splitting them across Files
  Changed broke the verdict's numbering and reading order in live tests.
  Re-runs update the same review in place (marker `<!-- punchcard -->`),
  so a PR carries one Punchcard entry for its whole life. No posting
  access → the review renders in the reply with one line saying why.

- [ ] **8. Deep mode (open question)** — the stability measurement
  (`benchmarks/stability-2026-08.md`) showed blocker findings are stable
  across runs while low-consequence tail findings trade places under the
  seven-finding cap. If union coverage is ever worth N× the cost, the
  mechanism is N merged finder passes, not a longer single review.
