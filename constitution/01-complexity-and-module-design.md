# 1. Complexity and Module Design

This chapter answers whether a change lowers or raises the long-term cost of reading and changing the
system: does each module hide a secret worth a boundary, and is its decomposition driven by measured
comprehension load rather than by line count. Design findings here are weighted by exposure and churn — block where the shape is
expensive to undo (published or cross-team surface, wire format, schema, security or concurrency
path) or where the touched code is hot or brand new; elsewhere report as a non-blocking note and say
which mode the finding is in (F2).

### 1.1 Require each new module boundary to hide a nameable secret
**Finding:** A new class, package, layer or component is added and the reviewer cannot name the
internal choice it lets you reverse without rippling to callers. The tells are visible in the diff: an
interface that is getters and setters over the data structure behind it; a layer whose methods have
the same signatures as the layer beneath; a type whose callers must know its storage shape, its call
order, or its representation to use it at all. Flag it and ask which alternative the boundary keeps
open. The same finding fires when a boundary exists but the diff punches through it — a caller
reaching past the entry point into the internals of what it calls.
**Unless:** An internal boundary cheap to refactor, with all callers in this build, does not owe
crystal-ball design; genuinely simple data holders exist legitimately; and dispatchers, plus multiple
real implementations of one interface, repeat signatures by design. Weight the demand by how
expensive the exposure is to undo (F2). A boundary whose secret is a forecast rather than a present
consumer is 3.2's finding, not this one.
**Sources:** (01, 02, 12, 13, 18; F2)

### 1.2 Flag over-decomposition as hard as under-decomposition
**Finding:** Pass-through methods that only forward, a class with one caller and one collaborator, a
facade that adds no decision, a helper extracted so small that its name says less than its body, a
parameter threaded through units that never read it, a parallel hierarchy the diff must edit in
lockstep to add one variant. Also file the reverse-direction finding on refactors: an extraction
whose pieces cannot be understood or exercised standing alone, that needs the reader to flip between
the halves to understand either, or that breaks a loop's early exit, is a defect against the
refactoring, not an improvement (F5).
**Unless:** A subtask that is genuinely independent, or a general-purpose mechanism being peeled away
from special-purpose policy, is worth its interface even when small; a delegating entry point that
narrows a subsystem's surface is doing real work; and where the codebase's existing convention is
thin wrappers of that shape, 1.7 applies instead.
**Sources:** (01, 05, 11, 13, 14; F5)

### 1.3 Trigger decomposition findings on measured load, never on length
**Finding:** Never file a finding whose stated reason is size, in either direction — not "this method
is too long", not "this file grew". The signals that fire are countable in the diff: nesting past
about three levels, decision points approaching ten in one unit, or live variables plus injected
collaborators in play together past roughly seven. Mixed abstraction levels inside one sequence are a
separate signal independent of any count: a raw SQL string, an SDK call, a bit twiddle or a byte
offset sitting among intention-named steps (F5). For a unit the diff creates, judge against the
budget; for a unit it merely extends, judge the trend against that unit's own baseline. When a signal
fires, ask for the smallest remedy in scope — the new behavior landing as its own tested unit —
rather than a drive-by decomposition of the host.
**Unless:** Intrinsically branchy code with no simpler form (a parser table, a state machine, an
exhaustive dispatch over a closed set) trips the counters without being a defect; a long unit with a
simple interface and one abstraction level throughout is fine. Treat a numeric budget as an
invitation to look, never as an auto-reject (F5).
**Sources:** (01, 02, 09, 11; F5)

### 1.4 Treat duplicated knowledge as a defect on sight
**Finding:** The same piece of knowledge — a format, a rule, an invariant, a protocol step, a magic
value, a unit or encoding assumption — now exists in two places, such that one side changing leaves
the other silently wrong. This fires with no copied text: a computation over another module's data
layout, a constant that must match a schema, a switch that must gain an arm whenever a sibling
hierarchy does. One knowing, briefly-lived second copy may be tolerated when the diff names it; a
third copy blocks. Forks of a module and vendored copies are findings in their own right, because
every future fix must chase every copy (F3).
**Unless:** Two things that merely resemble each other are not duplicated knowledge — do not force
lookalikes into one shape when they answer to different reasons to change; where unification is
unclear the remedy is to move the copies next to each other and make them symmetrical, not to invent
a premature helper.
**Sources:** (01, 02, 05, 13, 14, 18; F3)

### 1.5 Keep the complexity on the implementer's side of the interface
**Finding:** The change makes callers cope with something the module could absorb: a new required
parameter the module could compute or default, a mandatory call order (configure-then-use,
init-before-read, cleanup the caller must remember), pre- or post-processing every caller must repeat
at each call site, a returned value every caller must interpret the same way, or a decision punted
upward that the module is better placed to make. A module has more callers than implementers, so the
cost is multiplied by the number of call sites the diff can be seen to have.
**Unless:** Parameters callers genuinely know better than the module stays exposed; pulling
complexity down is only right for concerns close to the module's purpose — dragging unrelated
concerns inside is leakage, not depth. Signals the caller must act on are not to be absorbed into
silence.
**Sources:** (01, 07, 12, 13, 14)

### 1.6 Refuse structural degradation bought with unmeasured performance
**Finding:** The diff inlines a call, denormalizes state, caches a value, hoists a computation across
a boundary, or flattens an abstraction, and its justification is speed with no profile, benchmark or
production measurement attached. Flag the missing evidence, not the technique. The same applies to
new caches and copies added for speed: they create a second home for a fact and a staleness question,
so the measurement is the price of admission.
**Unless:** A measurement accompanies the change — then judge the fix on the data, and check that the
faster version still means the same thing. Where the cost is algorithmic and visible in the diff (a
lookup inside a loop over the same collection), no profile is needed to accept the fix.
**Sources:** (05, 07, 11, 13, 18)

### 1.7 Conform to how this codebase already solves this class of problem
**Finding:** The diff introduces a second way of doing something the surrounding code already does —
a different wiring style, a different way of composing units, a hand-rolled mechanism beside the one
the project or its framework already provides, a novel layering direction. Grep before objecting and
before accepting: if the established solution exists and works, an equally good novel one is the
finding, because two conventions cost every future reader a lookup. A half-migrated convention is
worse than either alternative.
**Unless:** An argued, stated divergence is fine — silent divergence is not; conformance to a pattern
the project is deliberately migrating away from entrenches it; and a convention change is welcome
when the author migrates the existing occurrences or names the owner and end date for the migration.
**Sources:** (01, 14, 18)
