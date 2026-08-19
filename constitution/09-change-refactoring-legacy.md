# 9. Change, Refactoring and Legacy

This chapter answers what a diff does to the cost of the next change: whether one concern's change
landed in one place, whether restructuring and behavior change were kept apart, what evidence stood
behind a behavior-preserving rework, and how a rescue of untested code, a staged migration or a
deliberate shortcut must be declared. Findings here are weighted by exposure and churn — block where
the shape is expensive to undo or the touched code is hot or brand new, and say which mode the
finding is in (F2).

### 9.1 Read where the diff landed as evidence about the boundaries
**Finding:** One coherent change — a single rule, field, format or user-visible behavior — had to be
edited into several modules in lockstep, and each edit exists only because of the others. The tells
are in the file list plus the code around it: the same new field added to a request type, a mapper, a
validator, an entity and a template; a new variant requiring an arm in three sibling switches; a
parallel hierarchy that must grow a class in each branch. Flag the boundary, not the individual
edits, and name which module should have absorbed the change. The same finding fires the other way:
a diff that repeatedly patches one file the surrounding code has clearly been patching before —
stacked special cases, a growing chain of flags on one call — is reporting a concept that has no home.
**Unless:** Wide but shallow edits with no shared reason to change — a mechanical rename, a
formatting pass, an interface a compiler forced — are not scatter. Vertical slices legitimately touch
a layer per stage when each layer's edit means something different there. Cross-service ripple is
chapter 10's finding, not this one; here the scope is modules inside one deployable.
**Sources:** (01, 03, 05, 07, 21, 22; F2)

### 9.2 Keep one hat per edit: restructuring and behavior change never share a diff
**Finding:** A diff moves, renames, extracts, inlines or reshapes code and also alters what the code
does. Read the mechanical parts adversarially — a changed comparison, an added guard, a swapped
default, a dropped branch, a reordered call with observable effects buried inside a large move is
the highest-yield defect in review, because neither the reviewer nor the tests can attribute it. A
production change arriving in the same diff as a deleted test, a loosened assertion or a widened
tolerance is the strongest form of this finding and blocks. Ask for two diffs: the restructuring with
tests unchanged and passing, then the behavior change with its own failing-first test.
**Unless:** Formatting, import order and other non-semantic noise riding along with a functional
change is harmless; when the tooling performs the change and the tests are solid, a signature edit
inside a refactor is still a refactor. A behavior change forced by the restructuring — a name that
was already a lie, a bug the extraction makes unrepresentable — is fine when called out explicitly
in the diff rather than left for the reviewer to notice.
**Sources:** (05, 06, 07, 08, 09, 24; F11)

### 9.3 Demand behavior evidence that existed and passed before a behavior-preserving rework
**Finding:** The diff claims to preserve behavior, and the reviewer cannot point at the tests that
covered the touched behavior before the change and still cover it after. Without a pre-existing net,
"refactoring" is an unverified rewrite and should be reviewed as new code, line by line. Tests
written after the rework, against the reworked code, do not close this — they pin the new behavior,
whatever it turned out to be. The same finding fires when the rework's only claimed net is a slow
end-to-end suite or manual verification for a localized logic change.
**Unless:** The touched code was pre-existing and untested and this diff is actively bringing it
under test — then 9.4 governs. A mechanical, signature-preserving move performed by tooling, whose
result the reviewer can verify is character-identical, needs less; so does code whose behavior is
fully constrained by types the compiler checks.
**Sources:** (05, 06, 08, 09, 22, 24; F11)

### 9.4 Grant the legacy exception only to a diff that is actually bringing the code under test, and book the scar
**Finding:** Check two facts visible in the diff: is the touched code pre-existing and untested, and
is this change putting it under test? When both hold, ugly seams are accepted as booked debt —
widened visibility, an extracted interface, an injected collaborator, a delegating shell — provided
the seam is declared in source and carries a named follow-up, and the characterization test lands
here or in the next change. Coarse black-box or pinch-point coverage is an acceptable safety net for
one behavior-preserving step. When either fact is false — new code, or code already under test — the
seam is a design defect and 9.3 holds with no discount. Blocks that survive inside the exception:
reflection or covert access into privates; a logic change riding the mechanical move; a coarse net
with no owner, expiry or named replacement; and any new behavior sprouted alongside the rescue
without its own fast local test.
**Unless:** Nothing about the rescue licenses leaky design in the new code it adds; new behavior in
an untested host belongs in a separately tested sprouted or wrapped unit, not woven into the host.
On a pinned quirk, silence is the finding in both directions: a characterization test recording
surprising behavior without a callout, and — worse — a quirk quietly corrected inside a diff
labeled behavior-preserving.
**Sources:** (06, 22, 24; F11)

### 9.5 Require a large restructuring to arrive as small, individually releasable, individually revertible steps
**Finding:** The change set is too large to actually be read, or it is a single step that cannot be
released or reverted on its own: an old and a new implementation swapped wholesale, a representation
replaced in place across the tree, a rewrite that must land complete or not at all. Ask for the
staged form — the new representation built beside the old, callers moved a few at a time behind the
original interface, incomplete work guarded so the mainline stays releasable at every step. Each step
must state how it is undone in production, not just in the repository.
**Unless:** A genuinely atomic change that is smaller as one step than as three — the compiler forces
all call sites, and splitting it would create a broken intermediate state — is correct as one diff. A
mechanical change that is large in lines but uniform in kind is readable at scale; judge by the
number of distinct things to check, never by the line count (F5).
**Sources:** (07, 08, 09, 21, 22, 24; F5)

### 9.6 Give every migration, toggle and parallel path a named owner, a removal plan and an end
**Finding:** The diff leaves two live ways to do one thing and names nobody to delete one: a feature
flag with no removal condition, an old and a new code path both reachable, a deprecated function with
no replacement named and nothing preventing new call sites, a compatibility shim with no end date, a
half-migrated convention. The missing owner and end are the finding, not the temporary duplication.
Where the old name or path must stay, require deprecating delegation to the new one plus a migration
note, never a silent change of what an existing name means.
**Unless:** A shim is itself the finding when the build can prove every consumer moved in this change
— then the one-shot reshape is correct and the compatibility layer is speculative (F12). A toggle
that is a permanent operational control rather than a migration device is not on a clock; it just has
to say so.
**Sources:** (08, 09, 21, 24; F12)

### 9.7 Make every deliberate shortcut say so out loud
**Finding:** The diff takes a knowingly worse option — bolts a special case onto a shape that does
not fit it, makes a copy instead of unifying, leaves a known-wrong behavior in place, defers the
split — and says nothing. Unstated shortcuts are what normalize decay, because the next reader cannot
tell a decision from an accident. Require the trade in the source or the change description: what was
skipped, why now, what would have to be true to fix it. When a diff is acceptable only because the
surrounding code is already what it is, that sentence belongs in the review explicitly — an approval
that hides its own reasoning teaches the next author that the shape is endorsed.
**Unless:** A stated shortcut is an approval, not a block, on cold, low-exposure code; do not convert
"named debt" into a demand for the ideal design, and approve improvement over perfection (F2).
Correctness and security shortcuts are never discounted this way — a naming ritual does not buy a
trust-boundary hole. A ceremonial marker with no content ("TODO: fix later") is the same silence in
different clothing.
**Sources:** (01, 03, 06, 08, 21, 22; F2)
