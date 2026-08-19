# 4. Domain Model and Types That Constrain

This chapter answers two questions about a diff: which concepts in it have earned a type of their
own, and whether the modelling style matches the rules this system really has. It judges the shape
of domain code and its types — not process boundaries, transaction span, or the codebase-wide error
strategy.

### 4.1 Give a type only to a distinction the application behaves differently on
**Finding:** The diff introduces a wrapper, subclass, enum arm, interface hierarchy or mapping layer,
and nothing in the change branches on the distinction, the constructor enforces no rule, and every
use unwraps immediately back to the primitive. The same applies upward: a rich domain model, mapper
family or ceremony layer added over rows whose only behaviour is read and write. Flag the ceremony
and say out loud that no wrapper is wanted, so the next reviewer does not reverse the call.
**Unless:** The type carries an invariant, keeps two same-typed neighbours in one signature from
being silently swapped, or marks a real trust or access boundary — then it earns its place even with
one call site. Transfer and storage shapes may mirror a table or payload without behaviour; that is
the shape's job, not an anemia defect. Domain-logic style follows rule complexity and what the
platform's tooling speaks: transaction script, table module and domain model can coexist, and
CRUD-ish logic owes none of them (F4).
**Sources:** (13, 14, 16, 24, 25, 30; F4)

### 4.2 Move a rule the callers keep re-checking into the type that owns the value
**Finding:** The diff adds another site that checks the same thing about a raw primitive — a range, a
format, non-emptiness, a normalization, a qualifier that must be applied before use — or adds a
caller that must remember a rule the value does not carry. That rule is now knowledge living in two
places: note it at the second copy, block at the third (F3). The remedy is a named type whose
construction enforces the rule, not a shared `validate...` helper, which leaves exactly as many call
sites free to forget it.
**Unless:** There is one interpreting site and the rest is pass-through plumbing that never reads the
value; the value genuinely spans the full range of its primitive; or the rule varies by caller, in
which case it is policy belonging to the context and not an invariant of the value. Do not redefine a
well-known external term (ISBN, email) to fit a local rule — introduce a new term beside it.
**Sources:** (05, 09, 13, 15, 25, 30; F3, F4)

### 4.3 Make construction the enforcement point, and enforce the whole concept
**Finding:** A type in the diff can exist in a state its own rules forbid: two-phase initialization,
required fields settable later, a name that promises a constrained concept behind nothing but a null
check where the business has real bounds, or a value whose interpreting qualifier — currency, unit,
tenant, time zone — arrives as a separate parameter from a separate source. Malformed input is
repaired, clamped or defaulted instead of refused. Ask for construction that either yields a valid
value or fails loudly.
**Unless:** A non-public no-arg constructor with field-level hydration exists for persistence — that
is legitimate and not a finding (F4). Reconstituting data that is already stored may be more lenient
than creating a new value; balking on bad stored state still beats silently repairing it. Do not
invent a bound to satisfy the rule: an unknown limit is a question for a domain expert, not a number
to guess. A single deliberate canonicalization step before validation is fine.
**Sources:** (09, 13, 15, 25, 30; F4)

### 4.4 Leave exactly one door to state an invariant depends on
**Finding:** The diff opens a second route to state the type is supposed to protect: a getter handing
out an owned mutable collection, date, buffer or child entity; a constructor storing an externally
supplied mutable reference; a generic setter where the business has named transitions (an order
flipping from paid back to unpaid); or a caller assembling and mutating an object's interior parts
and then saving it. The invariant is advisory the moment two routes exist.
**Unless:** Passing an internal reference transiently is fine — holding it is not. Immutable value
fields may be exposed directly, and inside one module where shared mutation is the stated protocol
copies are waste. Prefer moving the computation into the owner over any form of exposure; a
defensive copy that misleads a caller expecting its edits to stick is its own defect. Genuinely
evolving entities stay mutable — the demand is a named transition, not immutability everywhere.
**Sources:** (05, 13, 15, 24, 30)

### 4.5 Keep the rule beside the data it constrains, and judge anemia against the model that exists
**Finding:** A handler, job, batch script or template in the diff pulls several fields off an object
and derives a business outcome — eligibility, pricing, a limit, a status decision — that the owner
could answer itself, while that owner already holds behaviour of the same kind. It escalates when
the same rule now appears in a second handler, or lands in code that has been patched for this
reason before: that repetition is the signal to move the logic up the scale, and it is cheapest
early. A domain type whose signatures name web request, framework or messaging types is 5.5's
finding, not this one — raise it there.
**Unless:** A codebase deliberately built on transaction scripts or table modules is making a
whole-application choice, not committing a per-diff defect — do not demand a rich model or mapping
ceremony where no domain model exists (F4). Sequencing several objects through a workflow legitimately
belongs to a coordinator or a domain service named for the activity. Application, session and
process state is not entity state. Thin adapters and mappers at the edge are supposed to depend on
infrastructure.
**Sources:** (11, 13, 14, 15, 16, 25; F4)

### 4.6 Name the concept the branches keep spelling out
**Finding:** The diff adds one more branch, flag or sentinel to a place already carrying several for
the same reason: null or `-1` or `"unknown"` standing for a domain case, a boolean parameter
selecting behaviour, string matching on a code, or another "may this happen now" guard around a call
whose sibling guard lives in some other service. Scattered guards of that kind cannot be audited —
learning the rules requires grepping — and one forgotten branch is a direct business loss. Say which
concept would collapse the branches: a named case, a state type, a variant with its own behaviour.
**Unless:** A single local stable conditional is simpler than dispatch smeared across classes, and
not every noun deserves an object. Two states with always-legal transitions need no state object. A
weird rule may be a real requirement — check the domain intent before calling it accidental. And the
finding names the missing concept; a large remodel is a costed decision, not an automatic demand on
this diff (F2). Where the missing concept is a failure outcome, how it is represented is 6.2's rule,
not this one's.
**Sources:** (05, 11, 13, 15, 24, 30; F2)
