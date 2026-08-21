---
description: Review a GitHub PR or GitLab MR with Punchcard and post the review into it
argument-hint: <PR/MR url | number>
---

Run the punchcard skill on the given target and post the result.

Target: $ARGUMENTS — a GitHub PR / GitLab MR URL, or a bare number
resolved against the current repository's origin. No argument and no
inferable PR for the current branch: say so and stop.

Perform the full punchcard review of that PR/MR exactly as the skill
prescribes, then post it following the skill's "Posting to a PR/MR"
section — including its interactive confirmation, its render mapping,
and its degradation ladder when posting is not possible. The skill is
the single source of truth; this command only names the target and the
intent to post.
