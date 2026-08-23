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

The same header through both versions of parse_header_links:

  >>> parse_header_links('<https://x/a"b>; rel="next", <https://x/c>; rel="last"')
  # main
  [{'url': 'https://x/a"b', 'rel': 'next'}, {'url': 'https://x/c', 'rel': 'last'}]
  # this PR
  [{'url': 'https://x/a"b', 'rel': 'last'}]

  🔧 Fix: track quote state per entry, and only for quotes outside the <…> target.
