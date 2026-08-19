# Punchcard sample — redis-py#4258

> Repo: redis/redis-py · PR: https://github.com/redis/redis-py/pull/4258 · reviewed at commit 33a54836afa36b1efd8184ee6068c22b10042d18 · 2026-08-19

---

## 🟡 Ship it, then fix #1.

### 🟡 1 · The "only if it is still ours" guard is a non-atomic check-then-clear, so under threads it narrows the overwrite race without closing it

`redis/lock.py:290`

```python
        # Only clear token after successful release, and only if it is still ours.
        if self.local.token == expected_token:
            self.local.token = None
```

**Why:** The guard is a compare followed by a separate assignment. With `thread_local=False`, `self.local` is a plain `SimpleNamespace` shared by every thread (`redis/lock.py:153`), and nothing makes the compare and the clear one operation — a thread whose `acquire()` stores its fresh token between those two statements still has that token blanked.

The async twin genuinely holds the guarantee the comment states: in the success-path guard at `redis/asyncio/lock.py:289-291` there is no `await` between the comparison and the assignment, so tasks on one event loop cannot interleave inside it. The identical wording in the sync file promises the same invariant, but preemptive threads can interleave where cooperative tasks cannot.

The damage lands on the overwritten acquirer: its next `release()` finds the token gone and raises the "not owned or is already unlocked" `LockError` at `redis/lock.py:276`, and with the default `timeout=None` the key was set with no TTL (`px=None` at `redis/lock.py:243`), so the lock stays held until someone deletes the key by hand — the same stranded state this PR exists to fix.

The new test `test_release_does_not_clear_another_acquirers_token` (`tests/test_lock.py:241`) drives the interleaving deterministically through a monkeypatched `do_release`, which pins the guard's behavior but cannot reach the window between the compare and the clear; the PR description says the conditional clear "would close it in both", which overstates what the sync code enforces. This does not block: the window shrank from a full network round trip to two statements, and it only opens in the non-default shared-token configuration.

**Fix:** Either make the compare-and-clear atomic under threads (the token namespace needs a mutex or an equivalent single operation), or downgrade the comment and the claim from "closed" to "narrowed" so the next reader does not build on an invariant the sync code does not enforce.
