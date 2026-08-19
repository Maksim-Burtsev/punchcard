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
- [x] **5. Auto mode** — a Stop hook (`hooks/punchcard_stop.py`): when the
  agent finishes a turn leaving uncommitted changes in a repo that opted in
  (a `.punchcard-auto` file at the git toplevel), the stop is blocked once
  and the agent reviews its own work. Convergence rule: only BLOCKERs are
  auto-fixed, two rounds per session maximum.
- [ ] **6. Benchmarks & release** — the same set of real MRs reviewed with
  and without Punchcard, results published in `benchmarks/`; polish, logo,
  marketplace listing.
