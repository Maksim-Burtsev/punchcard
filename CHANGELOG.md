# Changelog

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
