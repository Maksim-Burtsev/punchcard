## 🟠 Ship after #1.

Finding #1 is a regression this PR introduces on malformed `Link` headers and must be fixed before merge; #2 and #3 are worth closing in the same change but do not block. The `split("=", 1)` fix the PR description is actually about is correct and well covered.

| # |  | What | Where |
|---|---|------|-------|
| 1 | 🔴 BLOCKER | One stray `"` anywhere in the header silently deletes every link after it | `src/requests/utils.py:1004` |
| 2 | 🟡 DESIGN | The quoted-string scanner now exists twice, so #1 has to be fixed twice | `src/requests/utils.py:973` |
| 3 | 🟡 DESIGN | The two load-bearing branches of the new splitter have no test | `src/requests/utils.py:1002` |

---

### 🔴 1 · One stray `"` anywhere in the header silently deletes every link after it

`src/requests/utils.py:1004` · A caller reading `r.links["last"]["url"]` gets the *first* link's URL back, with no exception and nothing that looks wrong.

`_split_link_header_entries` keeps one `in_quotes` bit for the whole header value, and it toggles on every `"` at any offset — including inside the `<...>` URI, where a quote is a literal character and not a delimiter. Once the parity is wrong, the `not in_quotes` guard below it never fires again, so every remaining `, <` boundary is swallowed:

```python
        elif char == '"':
            in_quotes = not in_quotes   # ← toggles on quotes inside <...> too, and never resets per entry
        elif char == "," and not in_quotes:
            lookahead = index + 1
            while lookahead < length and value[lookahead] == " ":
                lookahead += 1
            if lookahead < length and value[lookahead] == "<":
                entries.append(value[start:index])
                start = lookahead + 1
                index = lookahead
```

The old `re.split(", *<", value)` had no state at all, so a malformed entry could not affect the entries after it. Running the same header through both versions of `parse_header_links`:

```pycon
>>> from requests.utils import parse_header_links
>>> parse_header_links('<https://x/a"b>; rel="next", <https://x/c>; rel="last"')
# main
[{'url': 'https://x/a"b', 'rel': 'next'}, {'url': 'https://x/c', 'rel': 'last'}]
# this PR
[{'url': 'https://x/a"b', 'rel': 'last'}]
```

The merged entry then reaches `Response.links` at `src/requests/models.py:1137`, which keys the dict on `rel`:

```python
            for link in links:
                key = link.get("rel") or link.get("url")   # ← 'last' now points at the first link's url
                if key is not None:
                    resolved_links[key] = link
```

So `r.links["next"]` raises `KeyError` and `r.links["last"]["url"]` returns `https://x/a"b` — page one — which a pagination loop follows back to the page it is already on. An unterminated quote in any parameter produces the same collapse for the same reason.

> 🔧 **Fix:** make the quote state local to one link entry and reset it at each entry boundary, so a malformed entry cannot redefine the boundaries of the entries after it.

---

### 🟡 2 · The quoted-string scanner now exists twice, so #1 has to be fixed twice

`src/requests/utils.py:973` · Whoever fixes the quote handling for finding #1 has to find and change both copies, and a fix applied to one leaves the other wrong.

The escape-and-quote state machine in `_parse_header_links_params` at `src/requests/utils.py:973`:

```python
        if escaped:
            escaped = False
        elif char == "\\" and in_quotes:
            escaped = True
        elif char == '"':
            in_quotes = not in_quotes
        elif char == ";" and not in_quotes:
```

The same four rules again in `_split_link_header_entries` at `src/requests/utils.py:1000`, differing only in the delimiter on the last line:

```python
        if escaped:
            escaped = False
        elif char == "\\" and in_quotes:
            escaped = True
        elif char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
```

The commit message for `50064fd` says it "reuse[s] the same quote-tracking approach as the parameter splitter", but the approach was copied rather than reused, so RFC 8288 quoting is now knowledge this file states in two places.

> 🔧 **Fix:** let one scanner yield the split positions and have both callers tell it which delimiter they split on.

---

### 🟡 3 · The two load-bearing branches of the new splitter have no test

`src/requests/utils.py:1002` · A later change that drops either branch ships silently, because the suite this PR adds to stays green without them.

Neither branch is decoration. Deleting the backslash branch from both helpers changes what `parse_header_links` returns — `<a>; title="x\";b"; rel="next"` goes from `title` `a\";b` with `rel` `next` to a mangled `b"; rel` key — and deleting the space-skipping lookahead at `src/requests/utils.py:1008` collapses the ordinary two-link header GitHub emits into one link with the wrong `rel`. The branch none of the four added cases reaches:

```python
        elif char == "\\" and in_quotes:
            escaped = True
```

Removing that branch from both helpers and re-running the parametrization this PR extends:

```
$ PYTHONPATH=src pytest tests/test_utils.py -k parse_header_links -q
.........                                                                [100%]
9 passed, 224 deselected in 0.03s
```

Deleting the `while lookahead < length and value[lookahead] == " "` loop gives the same nine passes, so no case in the diff pins the space tolerance that `re.split(", *<", value)` used to provide.

> 🔧 **Fix:** add cases whose expected output changes when the escape branch or the space-skipping lookahead is removed — a quoted value containing `\"`, and a two-entry header with a space after the comma.

---

Out of scope, but look at `src/requests/utils.py:1047`: a parameter with no `=` at all still hits `except ValueError: break` and discards every parameter after it, which is the same silent-drop the `split("=", 1)` fix was written to close.
