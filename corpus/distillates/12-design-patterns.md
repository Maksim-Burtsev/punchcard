# 12. Design Patterns: Elements of Reusable Object-Oriented Software — Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides

> The book treats every design decision as a bet on what will change: good structure isolates each likely axis of variation behind one boundary so a future variant touches one module instead of every caller. Its instruments are abstract coupling, composition over implementation inheritance, and controlled creation — and its own closing warning is that each of these buys flexibility with indirection that must be paid for by a real, demonstrated need. For a reviewer this means judging diffs by which changes they make cheap, which they make expensive, and whether the flexibility being bought will ever be used.

## Principles

### 12.1 Ask what varies in this change, and verify the varying concept sits behind one boundary
- **Why:** Every pattern in the book is the same move applied to a different aspect — algorithm, representation, platform, request, state — so that future variants stay local instead of forcing edits across all clients.
- **Applies:** Any diff introducing a second variant of something (format, algorithm, backend, creation path) or adding conditional logic keyed on a variant.
- **Unless:** The axis will never actually vary; encapsulating imagined change is speculative machinery the book explicitly warns against.
- **Source:** Section 1.6 (Designing for Change); index cluster "encapsulation of..."

### 12.2 Require modules to depend on abstract interfaces at their boundaries, not concrete classes
- **Why:** Abstract coupling — holding a reference to a type rather than a specific implementation — is the mechanism that lets collaborators be swapped without touching callers; a concrete reference spreads implementation knowledge into every dependent.
- **Applies:** New dependencies between modules or subsystems, especially where multiple implementations exist or are plausible.
- **Unless:** A single implementation used in one place needs no interface layer; something must ultimately instantiate the concrete class.
- **Source:** Section 1.6 (Programming to an Interface, not an Implementation); Glossary (abstract coupling)

### 12.3 Prefer composition and delegation over implementation inheritance when a change varies behavior
- **Why:** Inheritance is white-box reuse — the subclass sees and depends on parent internals, so parent changes ripple into every child — and it fixes behavior at compile time, while composed objects vary independently behind interfaces.
- **Applies:** Diffs adding subclasses to reuse or tweak behavior, or overriding methods purely to borrow implementation.
- **Unless:** Interface inheritance (subtyping to a shared contract) is fine and central to the book; delegation must simplify more than it complicates, since webs of small objects are harder to trace than a static hierarchy.
- **Source:** Section 1.6 (Inheritance versus Composition); Glossary (black-box vs white-box reuse)

### 12.4 Confine construction of variant concrete types to one creation seam
- **Why:** Scattered direct constructor calls hard-wire a family choice into every call site, making a swap a hunt-and-fix exercise where one missed site produces inconsistent behavior.
- **Applies:** Code instantiating platform-, vendor-, or variant-specific classes at multiple sites; shared modules where the created types vary by client or configuration.
- **Unless:** Value objects and stable single-implementation types need no factory; a creator subclass whose only job is choosing a type is worse than a parameterized creator.
- **Source:** Section 1.6 (cause of redesign #1); Section 2.5; Factory Method and Prototype — Consequences

### 12.5 Reject class hierarchies that multiply along two independent axes; split the axes and join them by delegation
- **Why:** Encoding two dimensions in subclass names (platform x widget, format x algorithm) yields N x M classes where each new variant must be reimplemented per member of the other axis; separate hierarchies joined by a bridge yield N + M.
- **Applies:** New classes whose names concatenate two concerns, or client code instantiating platform-specific cross-product types.
- **Unless:** With one implementation and no expected second, the implementor hierarchy is degenerate overhead — the book calls this out explicitly.
- **Source:** Bridge — Motivation, Consequences; index (class hierarchy: explosion)

### 12.6 Flag branching on runtime type or element kind where polymorphic dispatch would do — and place operations on whichever axis changes less
- **Why:** A type-switch (including single-vs-group special-casing over part-whole structures) must be found and edited at every consumer whenever the hierarchy changes; it is exactly the coupling dynamic dispatch removes. When operations multiply over a stable hierarchy, externalize them visitor-style; when types multiply, keep operations on the types — each choice makes the other axis expensive.
- **Applies:** if/else or switch ladders over instanceof, type tags, or leaf-vs-composite checks; changes widening a base interface implemented by many types to serve one feature.
- **Unless:** Uniform treatment trades away type-system safety on container invariants; externalized operations that force new public state accessors are their own red flag.
- **Source:** Section 2.8; Composite — Consequences; Visitor — Applicability, Consequences

### 12.7 Keep cross-boundary interfaces narrow and free of representation details
- **Why:** A client that knows how another object stores its data must change when the storage does — an integer-index accessor silently welds every caller to an array layout — and each method added to a widely implemented interface grows the contract every implementor must honor.
- **Applies:** New interfaces or callback contracts between modules; API changes exposing indices, internal collections, or mutable internals; additions serving one privileged caller; state one module stores on behalf of another (make it an opaque token).
- **Unless:** Within a module's own implementation direct structure access is fine; a wide interface confined to a genuinely privileged, bounded owner is the memento's legitimate trick.
- **Source:** Section 1.6 (cause of redesign #4); Section 2.8; Memento — Consequences; index (interface bloat)

### 12.8 When an action needs undo, queuing, logging, or multiple triggers, require it reified as an object decoupled from its trigger — and require undo to restore exact state
- **Why:** Hard-wiring an operation to its trigger leaves nowhere to keep the state history needs and multiplies classes by triggers times requests; and computed inverses (move back by the same delta) accumulate drift across do/undo cycles until state diverges.
- **Applies:** UI events, endpoints, or job triggers wired directly to business logic in systems needing undo, audit, retry, or replay; any undo/recovery implementation.
- **Unless:** A trivial one-shot action with a single caller and no history needs is a plain callback; wrapping it in a command object is ceremony. Full snapshots may be too expensive — strictly ordered deltas are acceptable.
- **Source:** Section 2.7; Command — Motivation, Implementation (error accumulation); Memento — Implementation

### 12.9 Review the runtime object graph and message flow, not just the class list — and question every reference that becomes bidirectional
- **Why:** The static class diagram hides who actually talks to whom and in what order; cycles, hidden god-objects, and chatty protocols are visible only in the request flow. References are intrinsically directed — a Drawing knows its Shapes, Shapes need not know their Drawing — and each back-reference is an invariant someone must now maintain, ideally in exactly one place (the operations that establish or break the link).
- **Applies:** Architecture-level review of nontrivial changes; diffs adding parent pointers, mutual imports, or callbacks that close a dependency cycle.
- **Unless:** Some patterns legitimately need parent references and callbacks; the ask is that bidirectionality be a justified decision, not an accident. Trivial local changes need no interaction analysis.
- **Source:** Appendix B (class vs object vs interaction diagrams; directed references); Composite — Implementation (parent references)

### 12.10 Reject any pattern or added indirection without a demonstrated need for the flexibility it buys
- **Why:** The book's own closing caution: patterns achieve variability through indirection, which costs comprehension and performance, so each layer is justified only where that variability is actually required. Subclassing is the cheap first step; composition-based machinery is more flexible and more complex — evolve toward it when variation appears, not before.
- **Applies:** Any diff introducing factories, strategies, observers, wrapper layers, registries, or hooks — demand the concrete change scenario the flexibility serves, ideally a second variant that already exists.
- **Unless:** Where a documented cause of redesign genuinely applies (multiple platforms, swappable algorithms, undo, open-ended extension), the extra structure is the cheaper option — do not use this rule to strip needed seams.
- **Source:** Section 1.8 (closing caution); Discussion of Creational Patterns

## Review heuristics

- Grep the diff for direct `new ConcreteType(...)` calls: if the type belongs to a swappable family and appears at multiple call sites, creation needs a seam.
- Any instanceof/switch-on-type ladder, or special-casing of single-item vs container, is a defect candidate — ask why dispatch is not polymorphic.
- For every new subclass, ask: is this subtyping to a contract, implementation borrowing a delegate would do, or one cell of a growing N x M cross-product?
- For every new abstraction layer (factory, strategy, observer, wrapper), ask for the second variant it serves; if none exists or is scheduled, flag it as speculative.
- On new or widened interfaces, check what the consumer actually calls — the contract should be that subset, and it should expose no indices, internal collections, or storage layout.
- Sketch the object graph the diff creates: new back-references, dependency cycles, and mid-update notifications (observers reading half-updated state) hide in the message flow, not the class list.
