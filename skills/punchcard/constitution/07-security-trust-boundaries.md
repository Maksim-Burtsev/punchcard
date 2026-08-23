# 7. Security and Trust Boundaries

This chapter answers what a change decides to trust, where that trust is established once and made
provable, and what must now be correct for the system's security claims to survive. Rigor here scales
with risk of failure and exposure rather than with diff size, so a one-line flip of a default, a
config value or a boolean on a trust path carries the same bar as a feature (F2), and a blocking
finding still names one concrete fixable thing.

### 7.1 Parse untrusted input once at the edge of its trust region into a value that carries its proof
**Finding:** External data — a request body, a message, an uploaded document, a runtime-fetched
configuration — enters as raw primitives, a map or a transfer object and travels into logic that
interprets it, with the checking spread over the path: a boolean validity call whose answer is
discarded, null/range/format guards inside private helpers, a re-parse at the sink. The other
direction is the same finding: a check inside the region that passes and fails on exactly the same
inputs as the edge check is duplication, and the ask is the parsed type, not a fourth guard. When the
author answers that the value was already validated, the reviewer must be able to point at the
enforcing site; if the barricade is not locatable in the tree, the missing boundary is the finding.
Order matters at the edge itself — a cheap origin, size or character gate belongs before the
expensive parser, regex or deserializer that an oversized input can stall.
**Unless:** Count kinds of control, not checks: a different mechanism at a different boundary — a
parse at the edge, a uniqueness constraint at the store, a rate or blast-radius cap — is layering,
not duplication, and is endorsed where failure is costly. Transfer objects are deliberately
unencapsulated at the wire edge; the finding is their reach inward, not their existence. Assertions
about states the design makes impossible are a different tool from validating what a stranger sent
(F7).
**Sources:** (02, 09, 14, 30; F7)

### 7.2 Re-establish trust for anything that left the system's control and came back
**Finding:** The diff derives an authorization decision, a price, a quota, a tenant selection or a
write from a value the client round-tripped — a hidden field, a cookie or session blob, a URL
parameter, a claim in a token used past what the issuer actually asserts — or from configuration and
cross-boundary payloads fetched at runtime, without re-deriving it from a store the caller cannot
edit. A second shape of the same defect: read-modify-write through a local model over a record other
writers also produce, which silently deletes every field this code did not decode. On tolerance, split
per field — unknown fields, unbranched enum arms and extra payload the code never reads are tolerated
by design; a consumed field whose value cannot be interpreted must fail loudly at the boundary before
any state change, never default quietly.
**Unless:** Round-tripped state is legitimate where nothing security- or money-bearing is derived from
it and tampering costs the tamperer only; a signed or encrypted envelope whose verification is
locatable in the diff is a store the caller cannot edit. For the write side, restricting the write to
owned fields is an equally good answer to round-tripping the remainder (F7).
**Sources:** (16, 27, 29, 30; F7)

### 7.3 Put enforcement at the resource, with per-request end-user context
**Finding:** The check and the act sit in different places and something can route around the check —
a handler that authorizes and a store, job or internal endpoint that accepts the same write from any
caller; an internal RPC taking an already-authorized subject id on the caller's word; a service split
described as a security boundary where the callee simply trusts the calling service's identity. A
comment, route prefix or convention claiming enforcement happens upstream ("auth is handled at the
gateway") is a claim, not an enforcing site — 7.1's rule applies to authorization exactly as to
validation: point at the code that refuses the request, or the missing boundary is the finding. The
same finding fires when a check and its guarded action are separated by a window another actor can
use. Draw trust regions by attacker reachability and blast radius, never by team ownership or by the
diagram: ask what set of code must now be correct for the claim to hold, and flag the change that
enlarges it — a new module reaching the sensitive store, a broad surface (a shell, a generic host API,
standing production credentials) handed out where three named operations would do.
**Unless:** Inside one process and one deploy unit, co-designed neighbours may trust each other under
an explicit contract, and paranoid symmetric checking there is the defect. A mediated choke point is
real cost — a new failure point needing its own availability story — so do not demand one for a
handful of actions, and it must forward the caller's identity rather than act under its own
privileged role. Splitting code that sits wholly inside one trust boundary buys interfaces, not
security (F7, F9).
**Sources:** (14, 29, 30; F7, F9)

### 7.4 Make every claimed security property enforceable at one locatable place
**Finding:** The change asserts a property — no injection here, this data is always encrypted, only
this role reaches that operation — and the enforcement is a habit rather than a thing: hand-rolled
escaping repeated per call site, a query or markup fragment concatenated from a plain string, an
authorization check copied into each new handler. Ask for the guarantee to travel in the value
reaching the sink, so review shrinks to the constructors and the sink and every pass-through hop can
be ignored. Escape hatches are part of the finding: an unreviewed or scattered bypass makes the whole
scheme decorative. Universal claims are not closed by a green suite — a passing test shows the case
it ran, so demand a structural constraint (a type that makes the illegal value unrepresentable, a
store-level constraint, a single door) or an argument covering every execution; existential claims
(this input is now rejected, this bug no longer reproduces) are closed by the test, and its absence is
then the finding (F15).
**Unless:** A framework or safe type is not a boundary against malicious in-process code, only against
honest mistakes, and it cannot catch a wrong design decision. Building the mechanism for one call site
is speculative indirection, and one stretched to cover every corner case becomes unauditable — the
second and third copy are what earn it. Where the platform already enforces the property, a
duplicate application-level enforcement is waste that can fight the platform.
**Sources:** (02, 18, 29, 30; F15)

### 7.5 Design the failure path of every security decision, and state its posture
**Finding:** An error branch around authorization, revocation, credential verification, policy or
config loading, or quota does not say what it permits: an exception swallowed and the request
continuing, a lookup failure treated as an empty deny list, a missing field defaulted to allow, a
cached decision served past what anyone agreed to. An attacker who can cause load or an outage then
weakens the check for free. Two hard rules: authorization, revocation, quota and integrity paths fail
closed, and no failure may grant a capability the principal did not already hold. Failure crossing
this boundary is explicit — a domain refusal typed apart from a technical fault, an unknown outcome
distinguishable from both, and no value returned from an error branch that the call site cannot tell
from success; prefer a fast refusal to a slow answer and no result to a wrong one (F8).
**Unless:** Failing closed everywhere manufactures outages. A policy distributor may fail static on a
complete last-known-good artifact with a bounded age and an alert whenever it is used, and where
availability is the asset a path may fail open with loud alerting — but the posture is stated in the
diff, not left to be inferred. A degraded or stale answer is acceptable only when it is labeled
distinctly from a fresh one and its reduced guarantee is agreed by the owner; a feature that is not
safe when stale is disabled, not served best-effort (F8).
**Sources:** (02, 14, 29, 30; F8)

### 7.6 Treat the failure output and the stored record as attack surface
**Finding:** A rejected value is echoed back into an error message, a log line or a response, handing
the attacker control of a string that a second system — a log viewer, an analytics pipeline, a support
console — will later interpret. A whole object, entity or transfer type is interpolated into a log or
exception, so every field added next release joins the log silently. Malformed input is repaired
rather than rejected: characters stripped, values coerced, encodings guessed, producing a derivative
no validator ever saw. On the record side, a new privileged or support operation lands with no
structured trace of the concrete action taken, or a personal field is stored with no stated owner and
no way to erase it, or a log carries the sensitive payload itself.
**Unless:** Failure analysis still needs something: a stable reason code, the field name, a length or
a hash, a correlation or request id, named fields read through explicit accessors. One-time
canonicalization — decoding to a known encoding, normalizing Unicode — followed by validation is
legitimate; silent scrubbing is not. Audit volume nobody reads is not an improvement, and an alarm
that fires daily is worse than none — fix the frequency rather than deleting the record.
**Sources:** (09, 27, 29, 30)

### 7.7 Hold configuration and defaults to the same bar as the code
**Finding:** The safety of the change rests on something that is not reviewed like code — a framework
default, a container or transport setting, a parser feature flag, an IAM or deployment manifest, a
feature toggle that is a live branch in production behavior. The tell is a single setting standing
alone as the entire defense, or a test that asserts the setting round-trips a constant instead of
observing the effect (the header present, only the intended methods answering, the transport
enforced) — a setting silently changes on a library upgrade with no compile or runtime error. Also
flag a fix applied only where it was observed — patched on the live instance, or in one copy of a shared idiom —
rather than in the image, template or helper everything is rebuilt from, and ask what stops a
downgrade past a security fix: the answer is a version floor, not a ban on rollback. Exercise
evidence for bad-day paths — break-glass, fallback, degraded mode, rollback, restore, failover — is
6.8.
**Unless:** Some knobs cannot round-trip through review — emergency traffic draining, live capacity
tuning — and the ask there is a logged, alarmed override, not a block. Where the defect is provably
one-off local logic, the class-wide sweep does not apply.
**Sources:** (18, 29, 30; F2)
