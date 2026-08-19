#!/usr/bin/env python3
"""Punchcard auto-mode Stop hook.

When the agent finishes a turn leaving uncommitted changes in a repo that
opted in (a `.punchcard-auto` file at the git toplevel), block the stop once
and instruct the agent to run the punchcard skill on its own work.
Convergence rule: BLOCKER findings only, at most 2 review rounds per
session.
# ponytail: round counter is per-session-total, not per-piece-of-work; a
# long session gets at most 2 auto-reviews. Key the counter by diff hash if
# that ever matters.
"""
import json
import os
import subprocess
import sys
import tempfile

MAX_ROUNDS = 2


def sh(*args, cwd=None):
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd, timeout=8)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    cwd = payload.get("cwd") or os.getcwd()

    top = sh("git", "-C", cwd, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return 0
    toplevel = top.stdout.strip()
    if not os.path.exists(os.path.join(toplevel, ".punchcard-auto")):
        return 0

    dirty = sh("git", "-C", toplevel, "status", "--porcelain")
    if not dirty.stdout.strip():
        return 0

    session = payload.get("session_id", "unknown")
    state = os.path.join(tempfile.gettempdir(), f"punchcard-auto-{session}")
    rounds = 0
    if os.path.exists(state):
        try:
            rounds = int(open(state).read().strip() or 0)
        except ValueError:
            rounds = 0
    if rounds >= MAX_ROUNDS:
        return 0
    with open(state, "w") as f:
        f.write(str(rounds + 1))

    print(json.dumps({
        "decision": "block",
        "reason": (
            f"Punchcard auto-review (round {rounds + 1} of {MAX_ROUNDS}): "
            "invoke the punchcard skill on the uncommitted changes now. "
            "Fix BLOCKER findings only — report DESIGN and QUESTION findings "
            "without acting on them, and do not restructure beyond the "
            "blockers. If the verdict contains no BLOCKERs, state the "
            "verdict in one line and finish."
        ),
    }))
    return 0


def selftest():
    import shutil
    tmp = tempfile.mkdtemp()
    repo = os.path.join(tmp, "r")
    os.makedirs(repo)
    sh("git", "init", "-q", repo)
    open(os.path.join(repo, "f.py"), "w").write("x = 1\n")

    def run(payload):
        p = subprocess.run([sys.executable, __file__], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.stdout.strip()

    sid = f"selftest-{os.getpid()}"
    # no marker file -> silent pass
    assert run({"cwd": repo, "session_id": sid}) == ""
    # marker + dirty tree -> block, twice
    open(os.path.join(repo, ".punchcard-auto"), "w").close()
    assert '"block"' in run({"cwd": repo, "session_id": sid})
    assert '"block"' in run({"cwd": repo, "session_id": sid})
    # third round -> convergence, silent pass
    assert run({"cwd": repo, "session_id": sid}) == ""
    # clean tree -> silent pass even with marker
    sid2 = sid + "b"
    sh("git", "-C", repo, "add", "-A")
    sh("git", "-C", repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "t")
    assert run({"cwd": repo, "session_id": sid2}) == ""
    shutil.rmtree(tmp)
    os.unlink(os.path.join(tempfile.gettempdir(), f"punchcard-auto-{sid}"))
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        sys.exit(main())
