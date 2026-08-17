# Roadmap

- [x] **1. Walking skeleton** — plugin structure, `/punchcard` command, skill
  v0 with a ten-principle stub constitution, smoke-tested on a planted-flaw
  diff.
- [ ] **2. The corpus** — ~30 classic software engineering books (EPUB/PDF),
  balanced across schools: code construction, design, architecture, testing
  and change, operations, engineering wisdom. Sources live in `books/`
  (gitignored — the corpus never ships; only the synthesis does).
- [ ] **3. The synthesis** — the heart of the project. One distillation pass
  per book (5–10 durable principles in our own words: statement, rationale,
  scope, source), then cross-book clustering, a conflict register where the
  schools disagree (resolved explicitly — that's the persona's worldview),
  and a final constitution of ~50–80 principles that replaces the v0 stub.
  Plus `BIBLIOGRAPHY.md`.
- [ ] **4. GitLab/GitHub inline** — findings posted as inline discussions on
  the MR/PR diff lines; summary comment is the verdict plus the list. The
  review lives where the code lives.
- [ ] **5. Auto mode** — a hook so that when agents finish work and
  self-review, Punchcard runs automatically. Convergence rule: only BLOCKERs
  are auto-fixed, two rounds maximum.
- [ ] **6. Benchmarks & release** — the same set of real MRs reviewed with
  and without Punchcard, results published in `benchmarks/`; polish, logo,
  marketplace listing.
