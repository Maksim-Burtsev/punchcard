# Changelog

## 1.4.0 — 2026-08-25

- **Measured three ways on Sonnet 5, on unseen PRs.** Five PRs — three
  from repositories no Punchcard benchmark had touched — by the bare
  model, Punchcard, and `/code-review`: four cold runs each, 60 in all,
  with determinism and token cost captured for every condition for the
  first time. Punchcard was the only condition to catch the campaign's
  deepest blocker (zod#6461's emitted JSON Schema accepting objects the
  parser rejects — verified by execution), the only one with zero
  disproven claims in 20 runs, and the only one with a verdict every
  time, at a median cost in the bare prompt's bracket. Also on the
  record: recall parity, tail instability for everyone, two 🟢 verdicts
  that missed that same zod blocker, and the death of the noise gap on
  Sonnet (`benchmarks/three-way-sonnet-2026-08.md`).
- **The README sells what the numbers support.** The hero claim now
  cites the three-way benchmark instead of the Opus-era comparison, what
  the doyen reads is a list rather than a sentence, the research question
  behind the corpus is stated out loud, and a "Built, measured, rejected"
  record shows the features that didn't survive their own numbers. The
  zod catch — the real card, word for word, in `assets/zod-catch.md` —
  is linked where it belongs, one clause in "Punchcard and friends".

## 1.3.0 — 2026-08-25

- **Adaptive depth.** A triage at the top of the search: a diff that is
  both small (~under 100 changed lines) and shallow — one concern, no
  rewired control flow — runs the three passes inline, in sequence, with
  no subagent fan-out; complexity overrides size, a mechanical sweep
  qualifies only while it stays small, and escalation is one-way with
  nothing discarded. Measured twice: on planted-flaw fixtures (every
  planted key in all eight keyed runs, zero noise in eleven, 1–3 minutes
  and ~50–70k tokens against 4–6 minutes and ~195k for the fanned-out
  baseline in the same harness), and on the real-PR rubric against
  `/code-review` and the bare model three ways. The flask boundary case
  — 86 lines of rerouted dispatch, one run inline missing a blocker the
  escalated run then took in full — is what put the shallowness test
  and "when in doubt, fan out" into the rule
  (`benchmarks/stability-2026-08.md`, "adaptive depth" and "three ways").

## 1.2.0 — 2026-08-24

- **The wait is working time.** While the three finders search, the judge
  reads the intent, routes the diff and loads its chapters; judging
  starts when the last finder returns. And pass 3 probes instead of
  running suites: named tests, at most three executions, the deciding
  revert-and-run left to the judge. Measured: flask median 6:56 (was
  8–13 min), requests 5:04, the clean control 4:14 with zero judge
  re-runs; every stable key intact, noise zero
  (`benchmarks/stability-2026-08.md`, "the judge prepares").

## 1.1.0 — 2026-08

- **Installs in any agent harness.** Punchcard follows the Agent Skills
  standard: `npx skills add Maksim-Burtsev/punchcard` puts it into every
  harness on the machine, and the constitution now ships inside the skill
  directory instead of at the plugin root, so a copied skill still has its
  78 principles. A root `plugin.json` covers the harnesses that install
  plugins; harnesses without slash commands post a review by saying `post`
  next to the target.
- **The demo replays 2.9× faster, and shows the whole review.** 25.8 s down
  to 9.0 s, streamed line by line: the verdict and readout, the summary
  table, then all three finding cards. The VHS tape that renders it
  (`assets/demo.tape`), the review exactly as the skill rendered it
  (`assets/demo-review.md`) and the screen text it streams
  (`assets/demo-screen.txt`) are in the repository.
- **The corpus gets a face.** ISBNs for all 30 books in `CORPUS.md`, a
  cover collage in `assets/corpus.png` built by `scripts/covers.py`, and a
  README that traces one book → principle → benchmark finding.
- **No double work.** The three search passes bring back what they
  executed; the judge re-runs only what decides a verdict and reads the
  constitution once. Finders on a cheaper model were measured and
  rejected — they lost a blocker that had never been missed. Measured in
  `benchmarks/stability-2026-08.md`, "Faster".

## 1.0.0 — 2026-08

The first release. Everything below was built and measured in the open;
each line links to the pull request that landed it.

- **A constitution, not a mood.** 30 classic books distilled into 349
  principles ([#2](https://github.com/Maksim-Burtsev/punchcard/pull/2)),
  clustered into 11 themes with 15 decided conflicts between schools
  ([#3](https://github.com/Maksim-Burtsev/punchcard/pull/3)), and
  synthesized into 78 numbered principles wired into the skill with
  per-diff chapter routing
  ([#4](https://github.com/Maksim-Burtsev/punchcard/pull/4)).
- **Calibrated on real PRs.** Six open-source pull requests, every claim
  checked by execution; four systematic faults fixed and re-verified,
  and the first clean "Ship it."
  ([#5](https://github.com/Maksim-Burtsev/punchcard/pull/5)).
- **Output format v3.** A four-status verdict ladder with a one-sentence
  readout, a summary table, real-code evidence cards with the language's
  own comment markers, a Fix that is direction and never a patch, and a
  "Ship it." that is a verified checklist
  ([#7](https://github.com/Maksim-Burtsev/punchcard/pull/7)).
- **Stability measured.** Ten cold runs across two PRs: every
  blocker-class finding at 5/5, zero noise; a mechanical enumeration
  step was tested and rejected because it reallocated the finding cap
  rather than widening it
  ([#8](https://github.com/Maksim-Burtsev/punchcard/pull/8)).
- **`/punchcard:pr`.** Review a GitHub PR or GitLab MR and post one
  coherent review into it — updated in place on re-runs, rendered in the
  reply with one line of explanation when posting is not possible
  ([#10](https://github.com/Maksim-Burtsev/punchcard/pull/10)).
- **No auto mode.** A Stop hook was built, measured against real work,
  and removed: no automatic trigger fits, and a line in `AGENTS.md` does
  the job exactly
  ([#6](https://github.com/Maksim-Burtsev/punchcard/pull/6),
  [#13](https://github.com/Maksim-Burtsev/punchcard/pull/13)).
- **Beyond Python.** Cold runs on Go and JavaScript PRs, every claim
  demonstrated by running both trees
  ([#14](https://github.com/Maksim-Burtsev/punchcard/pull/14)).
- **No finding count.** Scope is the only limit and everything that
  passes the gate is rendered; search follows every changed value to its
  last consumer, inside the repository and out. Measured: the blocker a
  full card set used to crowd out is back at 5/5, zero noise, a third
  fewer tokens — and two classes written down as still uncovered
  ([#17](https://github.com/Maksim-Burtsev/punchcard/pull/19)).
- **The coverage tail.** A behavior change no test exercises is a
  finding and needs no runtime demonstration — the evidence is the named
  missing case. Measured: the requests escape-branch finding back at
  3/3, a coverage card on every flask run, zero noise
  ([#20](https://github.com/Maksim-Burtsev/punchcard/pull/20)).
- **Three independent search passes.** The one class the reviewer kept
  missing — a consequence that terminates inside a dependency — resisted
  three prose edits. Reading Claude Code's built-in `/code-review` showed
  why: it searches from several independent angles and one of them asks
  what every removed line used to guarantee. Search is now three finder
  passes in separate contexts, judged in one; the class went from 1 in 11
  to 3/3, the clean control stayed clean, at about 1.7× the tokens
  ([#21](https://github.com/Maksim-Burtsev/punchcard/pull/21)).
- **With and without.** The same four PRs reviewed by the bare model,
  by Punchcard, and by Claude Code's built-in `/code-review`, three cold
  runs each, matched by mechanism — so the trade can be made with numbers
  ([#15](https://github.com/Maksim-Burtsev/punchcard/pull/15)).
