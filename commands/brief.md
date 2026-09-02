---
description: Brief a PR, MR or the current branch with Punchcard — the reviewer's orientation before the review, never a review
argument-hint: <PR/MR url | branch>
---

Run the punchcard brief on the given target.

Target: $ARGUMENTS — a GitHub PR / GitLab MR URL, or a branch or range in
the current repository. No argument: the current branch against the
repository's default branch. Standing on the default branch with no
argument there is nothing to brief, and the brief says exactly that in
one line and stops.

Write the brief of that change exactly as `skills/punchcard/BRIEF.md`
prescribes — it lives next to the punchcard skill — including its four
sections, its grounded map, its rule that nothing is cut to fit, and its
ban on findings. The brief renders in the conversation and is never
posted into the PR/MR. BRIEF.md is the single source of truth; this
command only names the target.

Two things about the reply itself. The user's own words around this
command set the language of the brief: a user who wrote their message in
Russian gets the brief in Russian, whatever language this command, the
skill file, the diff and the description are in; only the four section
titles stay in English. And the reply is the brief alone, starting at its
bold header line — no sentence before it about being ready to write it.
