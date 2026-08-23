# Render with:  vhs assets/demo.tape   (from the repository root)
#
# The review body is a replay of a real run on psf/requests#7520 and lives in
# assets/demo-review.md — nothing here is invented, and the text is edited
# there, not in this tape. The setup runs inside Hide so the recording starts
# at the prompt. Everything typed here is ASCII on purpose: vhs 0.11 drops
# multibyte characters out of `Type`, so the check marks and the middle dots
# are printed from octal escapes and the rest comes out of the review file.

Output assets/demo.gif

Set Shell bash
Set FontSize 14
Set Width 1180
Set Height 700
Set Padding 20
Set Theme "Catppuccin Mocha"
Set TypingSpeed 15ms
Set Framerate 15

Hide
Type `PS1=$'\342\235\257 '` Enter
Type `D=$'\302\267'` Enter
Type `function /punchcard {` Enter
Type `  sleep 0.6` Enter
Type `  printf "\033[32m\342\234\223\033[0m \033[90mthree finder passes $D every value to its last consumer $D every removed guarantee $D the test that goes red\033[0m\n"` Enter
Type `  sleep 0.6` Enter
Type `  printf "\033[32m\342\234\223\033[0m \033[90mjudging 7 candidates against the constitution $D running main and this PR\033[0m\n\n"` Enter
Type `  sleep 0.5` Enter
Type `  awk -v E=$'\033[' '{ if ($0 ~ /Ship after/) $0=E "1;38;5;214m" $0 E "0m"; else if ($0 ~ /^  [0-9] /) { sub(/BLOCKER/, E "38;5;204m&" E "0m"); sub(/DESIGN/, E "38;5;179m&" E "0m") } else if ($0 ~ /One stray/) $0=E "1;38;5;204m" $0 E "0m"; else if ($0 ~ /severity/) $0=E "90m" $0 E "0m"; else if ($0 ~ /^src/) sub(/^[^ ]+/, E "90m&" E "0m"); else if ($0 ~ /Fix:/) sub(/Fix:.*/, E "1m&" E "0m"); print; system("sleep 0.12") }' assets/demo-review.md` Enter
Type `}` Enter
Type "clear" Enter
Show

Type "/punchcard https://github.com/psf/requests/pull/7520"
Sleep 300ms
Enter
Sleep 8s
