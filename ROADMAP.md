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
- [x] **7. PR/MR comments as a render surface** — `/punchcard:pr` reviews
  a GitHub PR / GitLab MR and posts into it: on GitHub one review
  (`COMMENT`) whose body is the full render with sha permalinks, plus
  inline comments for findings anchorable inside the diff hunks (anchors
  validated up front — out-of-diff findings live in the body, where
  GitHub allows them); on GitLab one MR note. No posting access → the
  review renders in the reply with one line saying why. Deferred tails:
  GitLab inline discussions (positions API unreliable on unchanged
  lines), sticky re-run updates (each run posts a new review).
- [ ] **8. Auto mode via subagent** — the review runs in a spawned
  subagent that triggers the punchcard skill automatically; the main agent
  receives the verdict and applies the fixes. Keeps reviewer and author in
  separate contexts — the reviewer never rewrites, the author never
  self-grades — and drops the current same-context Stop-hook compromise.
- [ ] **9. Deep mode (open question)** — the stability measurement
  (`benchmarks/stability-2026-08.md`) showed blocker findings are stable
  across runs while low-consequence tail findings trade places under the
  seven-finding cap. If union coverage is ever worth N× the cost, the
  mechanism is N merged finder passes, not a longer single review.
