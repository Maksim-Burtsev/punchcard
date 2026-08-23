🟠 Ship after #1.

Finding #1 is a regression this PR introduces on malformed Link headers and must be fixed
before merge; #2 and #3 are worth closing in the same change but do not block.

  #   severity   what                                                                     where

  1   ● BLOCKER  One stray " anywhere in the header silently deletes every link after it   utils.py:1004
  2   ● DESIGN   The quoted-string scanner now exists twice, so #1 has to be fixed twice   utils.py:973
  3   ● DESIGN   The two load-bearing branches of the new splitter have no test            utils.py:1002

● 1 · One stray " anywhere in the header silently deletes every link after it
src/requests/utils.py:1004 · A caller reading r.links["last"]["url"] gets the first link's URL back,
with no exception and nothing that looks wrong.

  >>> parse_header_links('<https://x/a"b>; rel="next", <https://x/c>; rel="last"')
  # main
  [{'url': 'https://x/a"b', 'rel': 'next'}, {'url': 'https://x/c', 'rel': 'last'}]
  # this PR
  [{'url': 'https://x/a"b', 'rel': 'last'}]

  🔧 Fix: track quote state per entry, and only for quotes outside the <...> target.

● 2 · The quoted-string scanner now exists twice, so #1 has to be fixed twice
src/requests/utils.py:973 · Whoever fixes the quote handling for #1 has to find and change
both copies, and a fix applied to one leaves the other wrong.

  _parse_header_links_params  utils.py:973        _split_link_header_entries  utils.py:1000
  if escaped:                                     if escaped:
      escaped = False                                 escaped = False
  elif char == "\\" and in_quotes:                elif char == "\\" and in_quotes:
      escaped = True                                  escaped = True
  elif char == '"':                               elif char == '"':
      in_quotes = not in_quotes                       in_quotes = not in_quotes
  elif char == ";" and not in_quotes:             elif char == "," and not in_quotes:

  🔧 Fix: let one scanner yield the split positions, and have both callers name the
  delimiter they split on.

● 3 · The two load-bearing branches of the new splitter have no test
src/requests/utils.py:1002 · A later change that drops either branch ships silently, because
the suite this PR adds to stays green without them.

Removing the backslash branch from both helpers and re-running the parametrization this PR extends:

  $ PYTHONPATH=src pytest tests/test_utils.py -k parse_header_links -q
  .........                                                                [100%]
  9 passed, 224 deselected in 0.03s

  🔧 Fix: add cases whose expected output changes when the escape branch or the
  space-skipping lookahead is removed.
