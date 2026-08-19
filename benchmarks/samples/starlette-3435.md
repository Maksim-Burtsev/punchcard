# Punchcard sample — starlette#3435

> Repo: encode/starlette · PR: https://github.com/encode/starlette/pull/3435 · reviewed at commit 9e0b0bd02af5ca09b5c37505541678a79aafbfa3 · 2026-08-19

---

## 🟢 Ship it.

The new method mirrors the existing `send_push_promise` pattern exactly, every send-wrapping middleware in the tree already passes the new message type through, and the two that buffer the response are precisely the two this change teaches to forward it.
