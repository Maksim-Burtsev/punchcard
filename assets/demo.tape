# Render with:  vhs assets/demo.tape   (from the repository root)
#
# The review body is a replay of a real run on psf/requests#7520. The review
# exactly as the skill rendered it is assets/demo-review.md; what fits on a
# terminal screen — the same text, shortened to one evidence block per card —
# is assets/demo-screen.txt, and that is what this tape streams. Nothing is
# invented, and the screen text is edited there, not in this tape.
#
# The setup runs inside Hide so the recording starts at the prompt.
# Everything typed here is ASCII on purpose: vhs 0.11 drops multibyte
# characters out of `Type`, so the check marks and the middle dots are
# printed from octal escapes and the rest comes out of the screen file.
#
# Pacing lives in the awk at the bottom: one constant sleep per line, and a
# longer one before each finding-card title.

Output assets/demo.gif

Set Shell bash
Set FontSize 13
Set Width 1000
Set Height 1060
Set Padding 16
# GitHub's own dark palette, so the GIF sits on README dark mode without a tint.
Set Theme { "name": "GitHub Dark Custom", "background": "#0d1117", "foreground": "#e6edf3", "cursor": "#e6edf3", "selection": "#264f78", "black": "#484f58", "red": "#ff7b72", "green": "#3fb950", "yellow": "#d29922", "blue": "#58a6ff", "magenta": "#bc8cff", "cyan": "#39c5cf", "white": "#b1bac4", "brightBlack": "#6e7681", "brightRed": "#ffa198", "brightGreen": "#56d364", "brightYellow": "#e3b341", "brightBlue": "#79c0ff", "brightMagenta": "#d2a8ff", "brightCyan": "#56d4dd", "brightWhite": "#f0f6fc" }
Set TypingSpeed 15ms
Set Framerate 30

Hide
Type `PS1=$'\342\235\257 '` Enter
Type `D=$'\302\267'` Enter
Type `function /punchcard {` Enter
Type `  sleep 0.6` Enter
Type `  printf "\033[32m\342\234\223\033[0m \033[90mthree finder passes $D every value to its last consumer $D every removed guarantee $D the test that goes red\033[0m\n"` Enter
Type `  sleep 0.6` Enter
Type `  printf "\033[32m\342\234\223\033[0m \033[90mjudging 7 candidates against the constitution $D running main and this PR\033[0m\n\n"` Enter
Type `  sleep 0.5` Enter
Type `  awk -v E=$'\033[' '{ p=0.045; if ($0 ~ /Ship after/) $0=E "1;38;5;214m" $0 E "0m"; else if ($0 ~ /^  [0-9] /) { sub(/BLOCKER/, E "38;5;204m&" E "0m"); sub(/DESIGN/, E "38;5;179m&" E "0m") } else if ($0 ~ /One stray/) { $0=E "1;38;5;204m" $0 E "0m"; p=0.5 } else if ($0 ~ /scanner now exists|load-bearing branches/) { $0=E "1;38;5;179m" $0 E "0m"; p=0.5 } else if ($0 ~ /severity/) $0=E "90m" $0 E "0m"; else if ($0 ~ /^src/) sub(/^[^ ]+/, E "90m&" E "0m"); else if ($0 ~ /passed,/) $0=E "32m" $0 E "0m"; else if ($0 ~ /Fix:/) sub(/Fix:.*/, E "1m&" E "0m"); system("sleep " p); print }' assets/demo-screen.txt` Enter
Type `}` Enter
Type "clear" Enter
Show

Type "/punchcard https://github.com/psf/requests/pull/7520"
Sleep 300ms
Enter
Sleep 8s
