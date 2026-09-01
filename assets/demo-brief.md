> Two briefs exactly as `/punchcard:brief` rendered them, cold, by URL, with no local checkout. Sonnet 5, 2026-09-02, runs `celery-10534-r2a` and `starlette-3431-r2b` of the [brief benchmark](../benchmarks/brief-2026-09.md), skill at `9f6256c`. The first is a one-line change; the second is a six-hundred-line feature. Nothing below the rule was edited.

---

**Bound `State._tasks_to_resolve` to fix unbounded memory growth** (1 production line changed, 90 test lines added)
https://github.com/celery/celery/pull/10534

**The claim** — a long-running event monitor (`celery events`, Flower) leaks memory without bound because `State._tasks_to_resolve` is a plain `dict` that accumulates one entry per orphaned child event and is only ever popped by a matching parent event that may never arrive; this bounds it the same way every other mapping on `State` is bounded. Capacity.

**The map**

```
before                                      after

task-received (parent unknown)              task-received (parent unknown)
        │                                            │
        ▼                                            ▼
_add_pending_task_child                     _add_pending_task_child
        │                                            │
        ▼                                            ▼
_tasks_to_resolve[parent_id] = WeakSet()    _tasks_to_resolve[parent_id] = WeakSet()
   plain dict — no eviction                    LRUCache(max_tasks_in_memory)  ← new
        │                                            │
   parent never arrives                        parent never arrives,
        │                                       cache over capacity
        ▼                                            ▼
   entry stays forever                        least-recently-used entry evicted
```

**The invariants**

|  | before | after |
|---|---|---|
| size of `_tasks_to_resolve` over process lifetime | unbounded — one entry added per orphaned `parent_id`, removed only by a matching parent event | bounded — capped at `max_tasks_in_memory`, oldest entry evicted first |
| pending-child resolution when the parent event finally arrives | always resolved, regardless of how long the wait or how many parents are pending at once | resolved only if the entry has not yet been evicted by the LRU cap |

**The decision** — bounding the container by reusing the LRU type every other `State` mapping already uses — `celery/events/state.py:425`:

```python
self._tasks_to_resolve = LRUCache(max_tasks_in_memory)  # ← was a plain dict
```

`_add_pending_task_child` (`celery/events/state.py:636-641`) and the resolving `pop` in `event()` (`celery/events/state.py:627`) are unchanged — both already used plain `__getitem__`/`__setitem__`/`.pop()`, which `LRUCache` also implements.

---

**Add `max_body_size` to `Starlette` and route classes** (shape: 156 production lines, 394 test lines, 69 doc lines)
https://github.com/Kludex/starlette/pull/3431

**The claim** — Add a configurable total-request-body-size limit, available as `max_body_size` on `Starlette`, `Router`, `Mount` and `Route`, and as `RequestBodyLimitMiddleware` for other ASGI apps; a request whose body exceeds the limit is rejected regardless of what `Content-Length` claims. Universal.

**The map**

Where the limit sits in the app-level stack:

```
before                                   after

request                                  request
  │                                        │
  ▼                                        ▼
ServerErrorMiddleware                   ServerErrorMiddleware
  │                                        │
  │                                        ▼
  │                                     RequestBodyLimitMiddleware  ← new
  │                                        │
  ▼                                        ▼
user middleware...                      user middleware...
  │                                        │
  ▼                                        ▼
ExceptionMiddleware                     ExceptionMiddleware
  │                                        │
  ▼                                        ▼
Router                                  Router
```

How a second, nested limit (e.g. a stricter one on one `Route`) combines with the app-level one:

```
before (feature absent)              after

Route.app                            RequestBodyLimitMiddleware (app limit)  ← new
  receive ──▶ endpoint                   creates the responder, wraps receive/send
                                          │
                                          ▼
                                      RequestBodyLimitMiddleware (route limit)  ← new
                                          │ finds the responder already in scope,
                                          │ retunes its max_body_size instead of
                                          │ wrapping receive a second time
                                          ▼
                                      endpoint
```

**The invariants**

|  | before | after |
|---|---|---|
| request body size cap | not configurable anywhere in the framework | configurable on `Starlette`, `Router`, `Mount`, `Route`; unset (`None`) stays uncapped |
| effective limit under nested config | — | one responder wraps receive/send per request; a nested limit retunes its `max_body_size` rather than adding a second wrapper |
| `Content-Length` as proof of size | — | used only as a fail-fast pre-check; the enforced count is bytes actually received, so an absent or understated header cannot bypass the limit |
| exceeding the limit | — | request aborts with `413 Content Too Large` |
| open files on a failed multipart parse | closed on `MultiPartException` or `OSError` only | closed on any exception, including `_RequestBodyTooLarge` and cancellation |

**The decision**

Nested limits retune the existing responder instead of stacking a second one — `starlette/middleware/body_limit.py:75`:

```python
active_responder = cast(RequestBodyLimitResponder | None, scope.get(_BODY_LIMIT_RESPONDER_SCOPE_KEY))
if active_responder is not None:
    active_responder.max_body_size = self.max_body_size  # ←
    if active_responder.total_size > active_responder.max_body_size:
        raise _RequestBodyTooLarge
    return await self.app(scope, receive, send)
```

Two independent checks close the limit: the streamed byte count on every `receive`, and a `Content-Length` recheck at response start for a body the app never read — `starlette/middleware/body_limit.py:104`:

```python
async def receive_with_limit(self) -> Message:
    if self.content_length is not None and self.content_length > self.max_body_size:
        raise _RequestBodyTooLarge

    message = await self.receive()
    if message["type"] == "http.request":
        self.total_size += len(message.get("body", b""))
        if self.total_size > self.max_body_size:  # ←
            raise _RequestBodyTooLarge
    return message

async def send_with_limit(self, message: Message) -> None:
    if message["type"] == "http.response.start":
        self.response_started = True
        if self.content_length is not None and self.content_length > self.max_body_size:  # ←
            response = PlainTextResponse("Content Too Large", status_code=413)
            await response(self.scope, self.receive, self.send)
            raise _RequestBodyLimitResponseSent
    await self.send(message)
```

Multipart cleanup widens from two named exceptions to any exception, so an interrupted parse — a body-limit abort included — still closes temp files — `starlette/formparsers.py:291`:

```python
except BaseException:
    # Close all the files if parsing or reading the request stream fails.
    for file in self._files_to_close_on_error:
        file.close()  # ←
    raise
```

The app-level middleware is inserted right after `ServerErrorMiddleware` and before user middleware, so it wraps `receive`/`send` before any user code sees them — `starlette/applications.py:74`:

```python
middleware = [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug)]
if self.max_body_size is not None:
    middleware.append(Middleware(RequestBodyLimitMiddleware, max_body_size=self.max_body_size))  # ←
middleware += self.user_middleware
middleware.append(Middleware(ExceptionMiddleware, handlers=exception_handlers, debug=debug))
```

`Route` wraps its own `self.app` when `max_body_size` is given — `starlette/routing.py:230`; `Mount` and `Router` apply the identical wrap at their own construction sites:

```python
if max_body_size is not None:
    self.app = RequestBodyLimitMiddleware(self.app, max_body_size=max_body_size)  # ←
```
