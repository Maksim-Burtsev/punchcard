# Punchcard sample — httpx#3769

> Repo: encode/httpx · PR: https://github.com/encode/httpx/pull/3769 · reviewed at commit ff7190eda0ab308f1d884b228e17b32e6fdac756 · 2026-08-19

---

## 🟡 Ship it, then fix #1, #2.

| # |  | What | Where |
|---|---|------|-------|
| 1 | 🟡 DESIGN | A raising mount still leaks every mount after it | `httpx/_client.py:1272` |
| 2 | 🟡 DESIGN | The bug fix lands without its reproducing test | `tests/client/test_client.py:269` |

### 🟡 1 · A raising mount still leaks every mount after it

`httpx/_client.py:1272`

The cleanup loop this diff adds inside the new `finally` of `Client.close`, at `httpx/_client.py:1272`, closes the mounted transports sequentially with nothing guarding one against the other:

```python
            finally:
                for transport in self._mounts.values():
                    if transport is not None:
                        transport.close()
```

The PR states its goal as ensuring "all transports are properly closed", but the mechanism it adds protects against exactly one raiser — the main transport. If the first mounted transport's `close()` raises, the loop aborts and every mount after it is never closed, which is the same leak this PR exists to fix, moved one slot down.

Multiple mounts are the normal case, not an edge case. `Client.__init__` at `httpx/_client.py:697` builds `_mounts` from the environment proxy map plus any user-supplied `mounts`, so a client running with both `HTTP_PROXY` and `HTTPS_PROXY` set already carries two closable mount transports.

The same shape is repeated at all four changed sites: the `finally` loops of `Client.__exit__` at `httpx/_client.py:1305`, `AsyncClient.aclose` at `httpx/_client.py:1991`, and `AsyncClient.__aexit__` at `httpx/_client.py:2024` each abandon the remaining mounts on the first mount that raises.

**Fix:** Make each transport's cleanup independent of every other's outcome at all four sites — a raise from any one transport, main or mounted, must still let the rest close.

---

### 🟡 2 · The bug fix lands without its reproducing test

`tests/client/test_client.py:269`

This change is presented as a bug fix, yet the diff touches no test file, so nothing would go red if the `try`/`finally` were reverted. The closest existing coverage is the test transport inside `test_context_managed_transport_and_mount`, whose `close` at `tests/client/test_client.py:269` only records an event:

```python
        def close(self):
            ...
            self.events.append(f"{self.name}.close")
```

That test, and its sibling `test_context_managed_transport` above it, only assert the order of close events on transports that never fail, so neither exercises the path this PR changes: a transport whose `close()` or `__exit__()` raises while mounts are still open.

The specific missing case is a client with a mounted transport whose main transport raises on close, asserting that the mount's close still ran — in both the sync and async clients, since all four cleanup paths changed.

**Fix:** Add the raising-transport case, sync and async, asserting mounted transports are still closed.
