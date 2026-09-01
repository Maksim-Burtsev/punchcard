---
description: Brief a PR, MR or branch with Punchcard — the reviewer's orientation before the review, never a review
argument-hint: <PR/MR url | number | branch>
---

Run the punchcard brief on the given target.

Target: $ARGUMENTS — a GitHub PR / GitLab MR URL, a bare number resolved
against the current repository's origin, or a branch or range. No
argument: fall back to the local targets the brief prescribes —
uncommitted work, otherwise the current branch against the default
branch.

Write the brief of that change exactly as `skills/punchcard/BRIEF.md`
prescribes — it lives next to the punchcard skill — including its four
sections, its grounded map, its rule that nothing is cut to fit, and its
ban on findings. The brief renders in the conversation and is never
posted into the PR/MR. BRIEF.md is the single source of truth; this
command only names the target.
