# The Corpus

Thirty books. Not a survey of the industry — a deliberate, narrow worldview.
Punchcard's constitution is synthesized from these sources and no others;
repeated authors are a feature, not sampling bias: this is *who you hire*
when you install the plugin. Where the schools disagree, the conflict is
resolved explicitly (see `corpus/conflicts.md`, phase 3 of the
[roadmap](ROADMAP.md)) — never averaged away.

## I. The engineering canon

| # | Book | Why it's here |
|---|---|---|
| 1 | **A Philosophy of Software Design** — John Ousterhout | Complexity, deep modules, information hiding, strategic vs tactical programming. The philosophical spine. |
| 2 | **Code Complete, 2nd ed.** — Steve McConnell | The systematic reference on construction: complexity management, defensive programming, routines, data, quality. |
| 3 | **The Pragmatic Programmer, 20th Anniversary ed.** — Thomas, Hunt | Pragmatism, responsibility, coupling, orthogonality, reversibility, deliberate trade-offs. |
| 4 | **The Practice of Programming** — Kernighan, Pike | The laconic canon of clarity: simplicity, interfaces, errors, testing, portability. |
| 5 | **Refactoring, 2nd ed.** — Martin Fowler | Code smells, behavior-preserving transformations, small steps vs unjustified rewrites. |
| 6 | **Working Effectively with Legacy Code** — Michael Feathers | Safe change in existing software: seams, characterization tests, dependency breaking. |
| 7 | **Modern Software Engineering** — David Farley | The empirical counterweight: feedback, experimentation, incremental delivery, no dogma. |
| 8 | **Software Engineering at Google** — Winters, Manshreck, Wright | Code review, readability, testing, change over time, scale. Officially free. |
| 9 | **Code That Fits in Your Head** — Mark Seemann | Cognitive complexity budgets, vertical slices, risk management, small safe changes. |
| 10 | **The Programmer's Brain** — Felienne Hermans | How code reading actually works: working memory, chunking, cognitive load. |
| 11 | **Clean Code, 2nd ed. (2025)** — Robert C. Martin | The influential school on names, functions, errors, tests. Used critically, not as absolute law. |
| 12 | **Design Patterns** — Gamma, Helm, Johnson, Vlissides | Intent, structure, consequences, and *cost* of the classic patterns — including when a pattern is unjustified. |

## II. Local design, responsibilities, domain boundaries

| # | Book | Why it's here |
|---|---|---|
| 13 | **Implementation Patterns** — Kent Beck | Low-level design as communication: state, behavior, symmetry, expressiveness. |
| 14 | **Object Design** — Wirfs-Brock, McKean | Responsibility-driven design: collaborations, stereotypes, cohesion, boundaries. |
| 15 | **Domain-Driven Design** — Eric Evans | Ubiquitous language, bounded contexts, aggregates, ownership of domain invariants. |
| 16 | **Patterns of Enterprise Application Architecture** — Martin Fowler | The vocabulary and trade-offs of enterprise patterns; application/domain/persistence boundaries. |
| 17 | **Clean Architecture** — Robert C. Martin | Dependency rule, boundaries, policy/detail separation. One influential school, not a universal answer. |
| 18 | **Just Enough Software Architecture** — George Fairbanks | The anti-dogma counterweight: how much architecture the risk actually justifies. |

## III. Architecture, change, technical debt

| # | Book | Why it's here |
|---|---|---|
| 19 | **Fundamentals of Software Architecture, 2nd ed.** — Richards, Ford | Architecture characteristics, styles, decisions, trade-off analysis. |
| 20 | **Software Architecture: The Hard Parts** — Ford, Richards, Sadalage, Dehghani | Decomposition, coupling, granularity, data ownership — decisions with no universally right answer. |
| 21 | **Building Evolutionary Architectures, 2nd ed.** — Ford, Parsons, Kua, Sadalage | Changeability, fitness functions, controlling architectural degradation. |
| 22 | **Software Design X-Rays** — Adam Tornhill | Project history as review signal: hotspots, temporal coupling, debt prioritized by data. |
| 23 | **Code Reading** — Diomidis Spinellis | Review is first of all *reading* unfamiliar code and rebuilding its mental model. |

## IV. Tests as proof of behavior

| # | Book | Why it's here |
|---|---|---|
| 24 | **Test-Driven Development: By Example** — Kent Beck | Short feedback loops, red-green-refactor, executable examples. |
| 25 | **Growing Object-Oriented Software, Guided by Tests** — Freeman, Pryce | Outside-in TDD, ports/adapters, test smells as design signals. |
| 26 | **Unit Testing: Principles, Practices, and Patterns** — Vladimir Khorikov | The counterweight: value of a test, resistance to refactoring, limits of mocks. |

## V. Data, production, reliability, security

| # | Book | Why it's here |
|---|---|---|
| 27 | **Designing Data-Intensive Applications, 2nd ed.** — Kleppmann, Riccomini | Data models, transactions, replication, consistency — error classes style rules can't see. |
| 28 | **Release It!, 2nd ed.** — Michael Nygard | Stability patterns: timeouts, circuit breakers, bulkheads, failure containment. |
| 29 | **Building Secure and Reliable Systems** — Adkins et al. | Security and reliability co-designed: least privilege, resilience, recovery. Officially free. |
| 30 | **Secure by Design** — Johnsson, Deogun, Sawano | Security as a design property: domain primitives, validation, safe error handling. |

## Sourcing rules

- Original English editions; the editions named above (minor edition
  drift accepted where the core content is unchanged).
- Searchable PDF or EPUB. No DRM circumvention — a file that can't be
  read legally gets replaced with a legally available copy.
- №8 is officially free at [abseil.io/resources/swe-book](https://abseil.io/resources/swe-book);
  №29 at [google.github.io](https://google.github.io/building-secure-and-reliable-systems/raw/toc.html).
- **Source books live in `books/` and are gitignored. They never enter
  git, GitHub, or any published artifact.** Only the synthesis — written
  in our own words — ships (`corpus/`, `constitution/`).

## Synthesis rules

- One distillation per book, in our own words, no quotes beyond 15 words.
- No per-school weight normalization: the corpus's narrowness and repeated
  authors are deliberate — this is the persona's worldview.
- Where sources conflict, the fork goes into `corpus/conflicts.md` and is
  resolved explicitly by the maintainer. Averaging is forbidden.
