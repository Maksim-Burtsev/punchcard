# 31. Java Concurrency in Practice — Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea

> Concurrent code that passes its tests proves nothing: a race is a probabilistic event, and code that works by lucky timing is still wrong. The reviewer's unit of judgment is not the statement but the policy — which thread may touch which state, under which lock, with which visibility guarantee — and the policy either holds for every access or it does not hold at all. Sequential intuition is inadmissible evidence: compilers, caches, and processors reorder freely wherever the memory model imposes no edge, so "I wrote the fields before the reference" is not an argument. The cheapest correct concurrency is the state you never share; after that come immutability and delegation to proven building blocks; hand-rolled lock choreography is the last resort, and hand-rolled lock-free code is expert territory. Most of what this book forbids was done in the name of performance nobody measured.

## Principles

### 31.1 Every access to shared mutable state synchronizes — reads included, under one consistent lock
- **Why:** A reader that skips the lock can see stale or torn values, so an unsynchronized getter beside a synchronized setter is a bug, not an optimization; a variable guarded by different locks at different sites is guarded by nothing. There are no "special" situations where the rule relaxes. And concurrency is contagious: once one background task, timer, or framework callback touches a piece of state, every code path touching that state must synchronize too.
- **Applies:** Fields written under a lock but read bare; new code paths reaching a guarded field; a diff adding a scheduled task, listener, or handler that reads existing application state; lightweight-visibility (volatile-style) fields used beyond simple one-writer status flags.
- **Unless:** The three legitimate escapes: state never shared, immutable, or thread-confined — and confinement should be structural (locals, per-thread holders), not tribal knowledge.
- **Source:** Ch. 1.4; 2.4; 3.1; 3.3

### 31.2 A sequence of atomic operations is not atomic — compound actions need a single indivisible step
- **Why:** Check-then-act and read-modify-write leave a window between observation and action in which another thread invalidates the observation: lazy-init checks, put-if-absent built from separate calls, size-then-index on a shared collection, increments on visibility-only fields. Individually thread-safe calls do not compose, and the failure is duplicate work, lost updates, and broken invariants — not a crash.
- **Applies:** Any decision made on a value read in a previous statement of shared state; check-then-insert on shared maps; caches built as get-compute-put (register the in-flight computation atomically, not the finished value, when the work must run once); `++` or toggle on a volatile-style field.
- **Unless:** The whole compound action is delegated to a primitive that is atomic itself (compare-and-set, an atomic put-if-absent), or duplicated computation is cheap and idempotent and the race is knowingly accepted.
- **Source:** Ch. 2.2; 4.4; 5.1–5.2; 5.6; 15.1

### 31.3 Variables coupled by an invariant share one lock, or collapse into one immutable holder swapped atomically
- **Why:** When one variable constrains another (lower/upper, value/version), making each individually thread-safe is worthless — between the two separate updates observers see the invariant broken. This is also why a composite of thread-safe parts is not thread-safe the moment it adds a cross-component constraint: the parts' safety does not add up.
- **Applies:** Related fields converted to separate atomics; a diff adding a second state variable, range check, or veto to a previously delegating class; two related values fetched in separate synchronized calls; "we made everything atomic" refactors.
- **Unless:** Genuinely independent state variables may each delegate to their own thread-safe holder — that is the recommended baseline design.
- **Source:** Ch. 2.3; 4.1; 4.3; 15.3.1

### 31.4 Default to immutable objects, final fields, and no escape of internals — especially not `this` during construction
- **Why:** Immutable objects are inherently thread-safe and survive even improper publication; every field made immutable shrinks the state space a reviewer must hold. Conversely, a returned internal collection, a constructor that starts a thread or registers a listener, or state passed to alien code turns private state public and voids every local invariant — and an object exposed mid-construction can be seen incomplete. The guarantee is brittle: one non-final field or one post-construction mutation and readers may see changing state.
- **Applies:** Mutable fields never mutated after construction; getters returning internal collections or arrays; constructors registering callbacks or starting threads; mutators added to classes shared without synchronization.
- **Unless:** State that genuinely must mutate in place; register-after-construction via a factory; creating (not starting) a thread in a constructor is fine.
- **Source:** Ch. 3.2; 3.4; 4.2; 16.3

### 31.5 Every cross-thread handoff needs a real ordering edge — reject racy lazy initialization and half-synchronized fast paths
- **Why:** A plain field write is not publication: the memory model lets another thread see the reference before the object's constructor-set state — a current pointer to a partially constructed object, worse than a stale null. Check-without-lock-then-lock lazy init is exactly this bug. Visibility piggybacked on unrelated nearby synchronization is order-of-statements fragile and evaporates under refactoring.
- **Applies:** Lazily initialized shared fields read without synchronization; double-checked locking without the visibility fix; any write in one thread read in another with no lock, atomic, thread start/join, or documented library-handoff edge between them.
- **Unless:** Safe idioms are cheap — eager init, a small synchronized accessor, holder idioms, concurrent-structure handoffs; truly immutable objects tolerate any publication; piggybacking on an ordering a class documents as contract (queue put before take) is the safe form.
- **Source:** Ch. 3.5; 16.1–16.2

### 31.6 Delegate to proven concurrent building blocks; hand-rolled coordination and novel lock-free code are last resorts
- **Why:** Standard concurrent collections, latches, semaphores, futures, and blocking queues encode subtle protocols — safe publication, interruption, timed waits — that ad-hoc flag-and-wait constructions get wrong, and the concurrent collections scale where lock-wrapped ones collapse. Novel lock-free algorithms over linked structures are harder still (helping schemes, the ABA hazard with recycled nodes) — "a task best left to experts."
- **Applies:** Custom latch/semaphore/queue logic from raw waits, flags, or busy-wait loops; a whole collection serialized under one lock; homegrown lock-free structures where a standard one exists; CAS loops over multi-pointer structures without a cited published algorithm.
- **Unless:** The library genuinely lacks the semantics; exclusive whole-collection access (atomic multi-key updates) rules out fine-grained structures; single-variable CAS loops follow a simple canonical pattern and are fine.
- **Source:** Ch. 5.2; 5.5; 8.5; 14.2; 15.4

### 31.7 Cancellation is a protocol: never swallow the signal, make it reach blocking calls, interrupt only threads you own
- **Why:** Catching a cancellation signal and doing nothing erases the evidence a stop was requested — the catcher rarely owns the thread and has no right to end the request. A polled boolean is not cancellation: it is never re-checked while the task blocks in a queue, socket, or lock wait. And interrupting a thread you did not create delivers a signal whose meaning you cannot know; cancellation flows through task handles and lifecycle methods, not into borrowed threads.
- **Applies:** Empty or log-only catches around interruption; retry loops that drop the interrupted status; stop-flags on loops that also block; long-running loops with no cancellation points; code interrupting pool or caller threads directly.
- **Unless:** Code that owns the thread's interruption policy (a dedicated worker about to exit) may consume the signal; purely CPU-bound loops may poll at a chosen frequency — a responsiveness trade, not a correctness one.
- **Source:** Ch. 5.4; 7.1–7.2

### 31.8 Everything that owns threads gets a lifecycle, and no failure dies silently
- **Why:** Threads outlive their creating method and there is no preemptive stop, so a service that starts threads but offers no shutdown either leaks them or forces callers to violate ownership. A task's uncaught exception kills its thread invisibly — the application appears to work while a service degrades or a single-threaded scheduler goes permanently dead. Fire-and-forget submission whose results nobody retrieves has the same effect: the failure happened and no one will ever know.
- **Applies:** New classes starting threads or executors with no stop method; worker loops running submitted or plugin code without a catch-and-report path; futures submitted but never inspected; daemon status or finalizers standing in for a real shutdown path.
- **Unless:** An executor scoped to one method call (create, submit, await, shut down) is legitimately simple; result-bearing tasks surface exceptions at retrieval — provided retrieval actually happens.
- **Source:** Ch. 6.2.5; 7.2–7.4

### 31.9 Bound the resources and the waits: queue capacities, thread counts, saturation behavior, and time budgets are explicit decisions
- **Why:** Assuming consumers keep up with producers "is a prescription for rearchitecting your system later" — unbounded queues and thread-per-task both look fine in development and collapse under production traffic. Once bounded, something must give at saturation: throw, drop, or push back on the submitter — the choice encodes what the system does at its worst moment and must not be inherited as a default. Deadlines follow the same logic: a timed-out wait plus a still-running task is only half a timeout, and a concurrent computation needs a termination path for the no-result case, not just success.
- **Applies:** New producer-consumer paths where arrival rate is client-controlled; pools with hard-coded sizes (the right count derives from cores, wait/compute ratio, and the scarcest downstream resource); untimed blocking waits on responsiveness-sensitive paths; fan-out code whose done-signal fires only on success.
- **Unless:** Bounded pools plus tasks that wait on other tasks in the same pool invite starvation deadlock — dependent-task systems need different configurations; genuinely unbounded waits can be the contract for dedicated background consumers.
- **Source:** Ch. 5.3; 6.3.7; 8.1–8.3; 8.5.1

### 31.10 Multiple locks demand a fixed global order, and no alien method is ever called with a lock held
- **Why:** Deadlock needs only a cycle, the system never recovers on its own, and each nested acquisition looks locally reasonable — only a global ordering argument proves them compatible; order derived from argument order (transfer(from, to)) is a deadlock awaiting two opposite calls. A call through an abstraction barrier under a lock is unanalyzable: you cannot know what locks the callee takes, and that is how cooperating objects that each look correct deadlock together.
- **Applies:** Any diff adding a nested acquisition; listener or callback notification inside a locked region; synchronized whole methods mixing state update with outbound calls; tasks acquiring from two resource pools in varying order.
- **Unless:** Code that never holds two locks cannot lock-order deadlock — restructuring to that is the cheapest fix; timed/polled acquisition with backoff is a legitimate escape hatch; where releasing the lock breaks needed atomicity, use a state protocol (mark-then-act) instead of holding through the call.
- **Source:** Ch. 10.1–10.2

### 31.11 Right before fast: performance-motivated concurrency changes show measurements, and the real win is less sharing
- **Why:** The quest for performance is probably the largest single source of concurrency bugs — intuition about bottlenecks is usually wrong, uncontended synchronization is cheap, and trading safety for speed often yields neither. When contention is real, the levers in order: move slow and blocking work outside the critical section (never splitting an atomic action), give independent state independent locks, then eliminate the sharing — per-thread state and end-of-run aggregation remove the coordination cost entirely, where better locks merely manage it. Watch for optimizations that create hot fields (shared counters, cached aggregates) and for object pools whose synchronization costs more than allocation.
- **Applies:** Diffs removing or narrowing synchronization without profiling data; locks held across I/O or long computation; one monitor over unrelated state; new shared statistics on hot paths; microbenchmark justifications lacking warm-up, consumed results, or realistic contention.
- **Unless:** With measurements showing a real contended bottleneck, these techniques are exactly right; atomicity boundaries always win over lock-scope shaving.
- **Source:** Ch. 11; 12.2–12.3; 15.3.2

### 31.12 The synchronization policy is written down — which lock guards which field, the class's promise, the wait's predicate
- **Why:** The common decay path of a thread-safe class is a later diff adding a field or method that skips a discipline nobody recorded; users of undocumented classes are forced into risky guesses. The same applies to condition waits: every wait tests an explicit predicate, in a loop, under the lock that guards it (wakeups are spurious and signals are shared), and every state transition that could satisfy a waiter must notify — an undocumented protocol makes both halves unverifiable, by maintainers and tools alike.
- **Applies:** New guarded fields without a guard note or annotation; new classes with no thread-safety statement; waits not wrapped in a predicate loop; new mutation paths on classes that have waiters; single-notification added without proof that all waiters share one predicate.
- **Unless:** A class not documented thread-safe is simply presumed unsafe — the burden falls on classes claiming safety; wake-all is the correct default until measurement justifies the single-notification proof.
- **Source:** Ch. 2.4; 4.5; 14.2; Appendix A

## Review heuristics

- For every shared mutable field the diff touches, name the lock that guards it and verify every access site — reads included — acquires that same lock; a field accessed sometimes with and sometimes without its lock is the classic bug pattern.
- Find each decision made on previously read shared state (null-check-then-create, contains-then-add, size-then-index) and ask what makes the observation-to-action window atomic.
- Trace any object that crosses a thread boundary and name the happens-before edge that publishes it; a bare field assignment is not one.
- For every new thread, executor, queue, or background loop: who stops it, what bounds it, what happens at saturation, and where does an uncaught failure surface?
- Scan for the mechanical catalog: swallowed interruptions, lock/unlock not paired with finally, waits outside a predicate loop, sleep or blocking calls while holding a lock, non-volatile spin flags, double-checked lazy init, threads started from constructors, unexplained sleep/yield/priority tweaks.
- Any callback, listener, or overridable method invoked inside a locked region is a deadlock finding until shown otherwise.
- When synchronization is removed, narrowed, or replaced by something cleverer in the name of speed, ask for the measurement and the contention evidence before the correctness argument even starts.
