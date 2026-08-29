# 10. Architecture at Scale and Distribution

This chapter answers what a reviewer owes a change that is expensive to undo: which decisions in the
diff are one-way doors, what the author gave up to buy them, whether a new boundary between
deployable units actually delivers the independence it claims, and what a hop between them must state
once messages rather than calls carry the work.

### 10.1 Price the review by what it costs to undo this change, not by how many lines it touches
**Finding:** The diff contains an edit whose reversal would need other people's schedules — a new
process or ownership boundary, a transport or serialization choice, a public or cross-team signature,
a persisted format, a vendor or platform commitment deep enough that its types reach code above the
adapter. Those get the full argument no matter how small they are: a three-line change to who owns a
table is architecture, and "it is only a config value" is where one-way doors usually hide. Run the
comparison in the other direction too, and say which mode a finding is in: a deep structural objection
against a large but locally reversible edit inside one module, in cold code nobody has touched, is a
note rather than a block. Escalate a design finding back to blocking when the touched code is hot,
brand new, or sits on a security or concurrency path.
**Unless:** Correctness and security are never discounted by this rule — they do not scale with
reversibility, exposure or churn. Reversibility is not a license to wave through a small edit that
merely looks reversible; the test is whether every consumer can be moved back by this team alone.
High impact with genuinely low likelihood is not a blocker, and a decision already made in context,
with its consequences recorded, is not relitigated on every read of the file.
**Sources:** (16, 18, 19, 20, 22, 32; F2)

### 10.2 Make a structural change state what it gives up, and where the reason will still be readable
**Finding:** The change picks between structural alternatives — synchronous or asynchronous, shared
library or shared service, split or keep, broker or direct call, cache or recompute — and the
justification lists only benefits. An option with no visible cost has an undiscovered one, so ask for
the sacrifice and for who absorbs it: which team, which latency budget, which on-call rotation, which
future migration. Two related findings. A proposal framed strictly as A-or-B has usually never
examined the middle, and the middle is normally where the answer sits, so make the framing itself the
finding and ask which point on the range this diff chooses. And where the change establishes a rule
other code must now follow — a new boundary, a communication style, a data-ownership shift, a
dependency with lock-in — the reasoning must land somewhere durable and singular; a rationale that
exists only in the PR thread is gone by the next quarter.
**Unless:** Routine feature and bugfix diffs owe no trade-off essay, and design choices confined
inside one module belong to the author. A tally of pluses and minuses is not a verdict — criteria are
unweighted until this system's context weights them. A few decisions really are binary (a vendor-fixed
protocol, an on/off switch), and "it is a spectrum" is not permission to skip deciding: a middle
position still has to name its point and its costs.
**Sources:** (16, 18, 19, 20, 32, 34; F15)

### 10.3 Keep the burden of proof on the new process boundary, and name the driver that pays for it
**Finding:** The diff carves a new deployable unit out of an existing one, or turns a local call into
a remote one, with no named driver — fault isolation, differing scale profile, volatile code that
wants its own release cadence, restricted access, an owner who is genuinely someone else. Size is not
a driver. Then check the forces pulling the other way, all visible in the diff: a local join replaced
by a remote fetch on a request path, a transitive synchronous chain where one part going down takes
the callers with it, halves that still deploy, test and scale together, and a remainder that can only
be named "other" or "non-X", which means the cut went across cohesion rather than along it. A new
remote hop also owes the coarse facade that holds no logic of its own, plus the per-call obligations
the failure chapter sets out — bounded wait, defined behavior on expiry, authentication, idempotency.
**Unless:** Some boundaries are given: client to server, application to database, integration between
genuinely separate applications. There the demand is the coarse-grained interface, not avoidance —
and in-process designs stay fine-grained rather than being coarsened for an imagined future split.
Ownership legitimately decides where a boundary goes, not whether it must become a process boundary.
A split made to put sensitive data out of reach is endorsed when the reviewer can name both the asset
that becomes unreachable and the per-request end-user context the callee enforces; otherwise ask for
in-process isolation first. Background flows where nobody waits tolerate far more chatter than a
user-facing path.
**Sources:** (16, 18, 19, 20, 29, 32, 34; F9)

### 10.4 Check claimed independence against the operational dependency set, not the diagram
**Finding:** The change describes a component as independently deployable while adding, or leaving in
place, something both sides must bootstrap through: one database or schema, a shared entity library,
a broker or orchestrator, a lockstep frontend, a common release train, a blocking request-reply hop
that fuses their availability. The weaker side's characteristics become both sides' characteristics,
so the reviewer's question is mechanical — after this diff, can either side be deployed, scaled or
rolled back without the other? If not, say so plainly and let the change be judged as an edit inside
one deployable unit. Carving a service out is not by itself decoupling, and a split that leaves a
shared store behind has bought coordination cost and network failure modes while buying no
independence.
**Unless:** Deliberately deploying things together is not the defect; claiming an independence you do
not have is. A monolith or modular monolith is one unit by design and sharing a store there costs
nothing extra. A few closely related services that are really one bounded context may legitimately
share data when the team accepts the single-unit consequence. Read-only replicas or caches fed by the
one owning writer are the normal middle path, not a violation.
**Sources:** (17, 19, 20, 21, 34; F9)

### 10.5 License shared code across a deployment boundary by how slowly it changes, and pin it by version
**Finding:** The diff extracts a shared library or canonical service carrying domain rules across
teams or deployables, adds a parameter or flag to an existing one to serve a single new caller, or
declares a dependency on a floating latest build rather than a pinned version. Effective reuse is
abstraction times low volatility: a shared piece that keeps changing forces every consumer to retest
and redeploy in lockstep — precisely the coordination cost the boundary existed to avoid — and a
canonical model for a fast-moving core entity must satisfy everyone at once. Where the shared portion
is large or volatile, the finding is the boundary, not the library: ask whether these are one service,
or whether ownership should move so one team holds both sides.
**Unless:** The remedy is never a fork or a vendored copy — those are their own finding, because every
fix must then chase every copy, and knowledge living in two places is a defect on sight. Cross-cutting
operational concerns (logging, metrics, tracing, auth, discovery, protocol and serialization handling,
security primitives) are exactly where a single shared implementation beats consistency by convention,
and are never a reason to merge services. A runtime shared service is right for polyglot estates or
fast-changing behavior, at the cost of latency, scaling and availability. Very fine library
granularity makes the dependency graph the new problem.
**Sources:** (20, 21, 22, 32, 34; F3)

### 10.6 Give a workflow that spans services a named owner for its state, and choose the coordination style deliberately
**Finding:** The diff adds a multi-step process across services, or a failure branch, cancellation,
retry or reassignment to an existing one, and nothing owns the transient state — what ran, what
failed, what is retrying. That state always exists: unowned, either a domain service quietly turns
into a front controller, or every status query fans out to rebuild a snapshot from the participants.
Read the new cross-service call on three axes at once — synchronous or asynchronous, atomic or
eventual, orchestrated or choreographed — because picking one silently fixes the others, and the
synchronous-atomic-orchestrated corner is the most expensive place to live. Flag it when the corner
was defaulted into rather than chosen. Also flag a choreographed flow where each new error branch
adds links the happy path never needed, pushing workflow knowledge into services that should know
only their own domain, and two channels between the same pair where a notification can outrun the
data it announces. The identifier that state is filed under, and the expiry that keeps it from
growing forever, belong to 10.10; this rule is about who owns the state and how the flow coordinates.
**Unless:** A mediator is itself a coupling point, a bottleneck and a single point of failure; for
linear fire-and-forget flows with rare errors, choreography scales better and an orchestrator is
over-building. Workflow state can legitimately ride in the message at the price of a fatter contract.
High coupling is sometimes the right purchase — transactional integrity really is easier with
synchronous mediated calls; the finding is the unexamined position, not the expensive one.
**Sources:** (19, 20, 27, 34; F10)

### 10.7 When one capability's changelist touches most of the fleet, review the boundaries instead of the pieces
**Finding:** A single feature arrives as coordinated edits across most services or modules, or needs
sign-off and parallel work from several teams to ship at all. That is the decomposition failing under
a cross-cutting concern, not a large feature, and reviewing the pieces individually ratifies it. Say
it out loud and put the structural options on the table: merge the units, move ownership so one team
holds the seam, or place the new boundary where ownership already is. The same reading applies to a
seam the diff creates whose two sides land with different owners, and to work split along
frontend/backend/DBA lines while the system is split by domain — every feature then crosses every
silo. Coordination cost grows faster than the number of parties, so the fix is fewer owners per
change, not better meetings.
**Unless:** Some boundaries genuinely belong to another owner and cross-team agreement is the point —
shared platform, security and compliance surfaces exist to be coordinated. Where the services are
genuinely separate units and the cross-cutting thing is a variation point, the remedy is a new
component inside each obeying the local dependency rule, not a merge. Reorganizing people costs far
more than moving code, so this argues for placing new boundaries where ownership already sits, never
for demanding a reorg inside a review.
**Sources:** (17, 20, 21, 22, 34; F9)

### 10.8 Turn a boundary rule you would otherwise police by eye into a check the build runs
**Finding:** The change introduces or leans on an architectural rule that only a reviewer's memory
enforces — allowed dependency directions, forbidden imports across a bounded context, cycle freedom,
a component size or dependency ceiling, a latency or startup budget, referential integrity across
services. Imports go where they please and boundaries erode between reviews, so these are exactly the
rules that belong in the build rather than in a reviewer's head: 11.6 supplies the trigger and what
the check must carry. On a codebase already past the limit, do not set an unreachable bar or delete
the rule: cascade it, warning at one threshold and failing the build at a tighter one over time.
**Unless:** Some judgments stay manual on purpose — what counts as shared domain logic, whether a component's
responsibility is coherent — and if verifying the rule needs domain knowledge, it is a test, not an
architecture check. A threshold may legitimately be a documented function of load rather than a
constant, and a metric breach is a prompt to look, never a verdict: no measure separates complexity
inherent in a hard problem from complexity caused by bad factoring. Single-concern checks can also
all pass while the combination regresses, so name the quality a caching, replication or retry change
might quietly break.
**Sources:** (19, 20, 21; F15)

### 10.9 Treat arrival order as an accident, and price what buying it back costs
**Finding:** The diff makes a consumer depend on the order messages arrive in: updates applied in
receipt order across channels, partitions or retries; replica count or handler concurrency raised on
an order-sensitive handler; a multi-part send routed to a load-balanced pool with nothing pinning one
sequence to one consumer. Independent routing, retries and parallel consumers all reorder, so order
is never given — it is bought. Read the purchase when the diff makes one: a concurrency limit of one,
or a per-item acknowledgement gating the next dispatch, restores order by deleting the parallelism the
fan-out existed for, and that trade is stated rather than merged as a bug fix. The two honest remedies
are one consumer per ordered stream, or resequencing behind a bounded buffer, and both owe the same
three things — consecutive numbers assigned where the items are produced, in a field of their own; a
capacity on the buffer; and a timeout on a gap. Gap detection keyed on message ids, UUIDs or
timestamps does not work, because identifiers minted for uniqueness are neither ordered nor
consecutive, and a hardcoded start index or window size only holds while both ends restart together.
**Unless:** Within one ordered partition consumed by one instance the guarantee is real and needs no
machinery. Where order does not matter, competing consumers are the cheap and correct way to scale and
demanding sequence numbers there is ceremony. Windowed flow control needs influence over the producer,
which the receiving end of someone else's stream does not have — buffering and reordering is all there
is. A stand-in for a missing item is legitimate where approximate data beats late data, provided the
substitution is visible to whoever reads the result.
**Sources:** (34)

### 10.10 Correlate on an identifier the flow owns, and bound whatever accumulates behind it
**Finding:** The change pairs a response to a request, or gathers several messages into one result,
and the match runs on something the flow does not control: arrival order, timing, a content heuristic,
a broker-assigned message id or delivery tag, or a business key now carrying two meanings. Transport
ids are re-minted by every intermediary that consumes and republishes — a router, a translator, a tap,
a proxy — and some platforms instead copy one id onto every derived message, so it is not even unique.
Ask for a dedicated identifier the flow mints and carries end to end, in the envelope rather than the
body, so routers, taps and monitors can filter without parsing payloads; where an intermediary funnels
many callers onto one downstream channel, it mints its own and restores the caller's id and reply
address on the way back. Then follow whatever that key accumulates — an aggregate, a pending-request
map, a callback registry, a dedup history, a process instance — and find three answers in the diff:
what makes the set complete, what evicts an entry whose awaited message never arrives, and what the
flow does when one expires. Entries added on send and removed only on reply leak forever, because lost
replies are normal; purge too eagerly and a latecomer silently opens a fresh group under the same
identity. A completeness test that is an assumed count, with no timeout path and no record of a
dropped latecomer, is the same finding.
**Unless:** One caller, one outstanding request, no intermediaries, a private reply channel — there
the channel itself is the correlation. Where a reply becomes the next request, carrying forward the
identifier it arrived with is correct, and minting a fresh one per hop pays only where someone must
retrace the path step by step. Where the responder only echoes transport ids, a request-id-to-task map
is the right shape rather than a smell, and body fields are the documented fallback on transports with
no custom headers. Fire-and-forget fan-out needs no accumulator at all; where an incomplete result is
meaningless, wait-for-all plus an explicit timeout error is the correct completeness rule; and storing
only the fact of closure is cheap, so generous retention margins cost little. Who owns the workflow
state and which coordination style it runs under is 10.6.
**Sources:** (34)

### 10.11 Treat a new consumer, replica or subscription as a change to the contract
**Finding:** The diff attaches something new to an existing channel, or scales what is already there,
and the delivery semantics decide what that means: a second logical consumer on a point-to-point
channel silently steals messages from the first, while extra instances on a broadcast subscription
each process everything and duplicate every side effect, so parallelism there has to come from inside
one consumer. Both arrive disguised — a logging, audit or monitoring consumer hung on a work queue, a
channel flipped to broadcast so it can be, replicas added to a broadcast subscriber to share the load,
a queue sharded by hand to get concurrency. Observation belongs on a tap that republishes, never on
the working channel. Two obligations ship with the subscription itself: a stable identity with a
teardown path, because an inactive durable subscription accumulates without limit and anything
presenting the same identity inherits the backlog, including a different application; and a stated
bound on consumption rate — a concurrency or prefetch cap for push delivery, a blocking wait rather
than a busy poll for pull, and never a thread, process or task per message.
**Unless:** Competing instances of one logical consumer are exactly what a point-to-point channel is
for, and where the backlog is genuine and the capacity exists, adding them is the right answer. Push
is more efficient than polling for sparse traffic, and pull costs a cycle of latency that is wrong
where immediate forwarding is the requirement. Broker-side filtering beats receiving and discarding,
but criteria too rich for its filter language legitimately live in code — and filtering is not access
control. Dropping updates is safe for full snapshots and loses fields when applied to deltas. Where a
consumer cannot keep up, slowing the producer leaves the wrong party in control; that is a finding
about rate, not a reason to refuse the consumer.
**Sources:** (34)
