# 25. Growing Object-Oriented Software, Guided by Tests — Steve Freeman, Nat Pryce

> Design is grown, not specified: each feature starts as a failing test written from outside the system, and the difficulty of writing that test is the primary signal about the design underneath. Objects are defined by the messages they send to collaborators they were handed, not by the data they hold, so a review looks at wiring, roles and boundaries before it looks at algorithms. Tests are production artifacts — their names, values and failure messages are part of what the change delivers. The reviewer's recurring question is not "does this work?" but "what is this test telling us about the code it exercises?"

## Principles

### 25.1 Prove the change runs end to end through the real deployment path before growing features on it
- **Why:** A thin slice built, deployed and exercised through the system's actual external entry points flushes out integration, packaging and environment risk while there is still budget to react. Systems tested only through internal objects have shipped with entry points that did nothing at all.
- **Applies:** New systems and subsystems, and the first change introducing a new deployment target, protocol or external integration.
- **Unless:** Not every change must re-prove the pipeline, and the skeleton is deliberately trivial — it is not a licence for up-front design. In brownfield code the equivalent is end-to-end cover over the area being changed.
- **Source:** Ch. 4, First, Test a Walking Skeleton

### 25.2 Expect each feature to arrive with a failing acceptance test in domain vocabulary that drives the system from outside
- **Why:** An outside-in test defines when the work is done, keeps the change scoped to what was asked, and survives changes of database, protocol and UI toolkit because it names none of them.
- **Applies:** Any user-visible feature or behavioural change with a stakeholder-meaningful outcome.
- **Unless:** Acceptance tests are slow and, for asynchronous systems, flakier than unit tests. Refactorings, internal cleanups and cases better served by a focused unit test need none.
- **Source:** Ch. 5, Start Each Feature with an Acceptance Test; Ch. 1, Testing End-to-End

### 25.3 Treat an awkward test as a report about the production code, not a testing problem to work around
- **Why:** Long setup, a bloated constructor, a wall of expectations and a chain of stubs are the same structures that will make the code expensive to change later. The feedback is cheapest while the code is fresh, and the workaround leaves the defect in place.
- **Applies:** Any diff where test setup is disproportionate to the behaviour asserted, where a test reaches through several objects, or where a test was loosened to make it pass.
- **Unless:** Persistence, concurrency, asynchrony and UI are genuinely hard to test and have their own techniques; friction caused by the platform is not evidence against the design. Test difficulty is a hint to investigate, not a verdict.
- **Source:** Ch. 5, Listen to the Tests; Ch. 20, Listening to the Tests

### 25.4 Reject unit tests that mock types the team does not own — wrap the library in a thin adapter and integration-test that
- **Why:** A mock of a third-party type encodes a guess about how that library behaves, so the test passes while production fails and stays green through the upgrade that broke the assumption. It also yields no design feedback, because the mocked API cannot be changed.
- **Applies:** Tests standing in for a framework, vendor SDK, driver or message client; domain classes importing external types directly.
- **Unless:** Occasional mocking of an external type is justified to provoke behaviour that is hard to produce for real (exceptions, rollbacks), and third-party value types need no adapter to be testable — though translating them into domain equivalents at the boundary is still usually worth it, the exception being types so fundamental they are simply used as they are. A thin veneer over a stable library may only be integration-testable, which is acceptable.
- **Source:** Ch. 8, Only Mock Types That You Own / Write an Adapter Layer

### 25.5 Demand every collaborator an object cannot function without at construction; let notifications and adjustments default to something safe
- **Why:** Finishing an object by setting fields afterwards compiles cleanly and fails at runtime, often misleadingly. Separating dependencies from peers that merely observe and from knobs that merely tune makes the coupling in the design visible — and stops a notification being mislabelled as a dependency and forced into a wiring cycle.
- **Applies:** Any object with collaborators; constructor changes; listener registration; circular wiring problems; return values and callback arguments that might be absent.
- **Unless:** Listeners and strategies legitimately arrive after construction, and the same collaborator can be a hard dependency in one system and a notification in another. Do not push a genuine dependency into a defaulted setter just to shorten a signature, and do not pass null where a null implementation or an absent type says it better.
- **Source:** Ch. 6, Object Peer Stereotypes; Ch. 20, Too Many Dependencies; Ch. 17, Compromising on a Constructor

### 25.6 Flag code that reads its own surroundings instead of being handed what it needs
- **Why:** Built-in knowledge of configuration, hostnames, singletons, clocks and global loggers prevents the code from being reused, reconfigured or placed in a test, and buries decisions where nobody looks. Explicit relationships also make the object graph itself the place where behaviour is composed.
- **Applies:** Domain and application logic at any depth below the process boundary.
- **Unless:** Something must read the real environment — the composition root at the process boundary is where it belongs, and it legitimately touches everything. Threading a value through six layers purely to avoid one static can cost more than the static.
- **Source:** Ch. 6, Context Independence; Ch. 17, Teasing Apart Main

### 25.7 Make callers state intent to a narrow, domain-named role interface rather than pull data out of a concrete class
- **Why:** Getter chains publish structure, so a change in a distant object ripples through every caller; depending on a concrete type drags in every method other clients need, leaving the actual collaboration implicit. Naming the slice actually used surfaces a domain concept and makes the interaction cheap to re-implement.
- **Applies:** Calls across module boundaries, especially accessor chains, logic branching on another object's state, and tests that double a concrete class; strongest when the caller uses two methods out of ten.
- **Unless:** Asking is fine for values, collections, factories and genuine queries, and chaining is fine in a declarative layer such as a test DSL or builder. Do not invent a role interface for a value type, or one whose only implementation would be named "Impl". Legacy code you cannot change at once is an accepted temporary compromise.
- **Source:** Ch. 2, Tell, Don't Ask; Ch. 20, Break Glass in Case of Emergency

### 25.8 Give a recurring domain concept its own small immutable type instead of a bare string, int or generic container
- **Why:** A raw value hides which concept it represents and gives related logic nowhere to live, so each addition edits every signature along the chain. A named type makes the concept findable, stops quantities of different kinds being confused, and lets behaviour gather next to the data.
- **Applies:** Identifiers, prices, quantities, units and field groups that travel together across layers; parameter lists growing one primitive at a time.
- **Unless:** Not every primitive earns a wrapper — the trigger is expressiveness now, not anticipated future fields. These authors kept a private boolean where an enum read worse. Value types stay immutable and are not candidates for mocking.
- **Source:** Ch. 7, Value Types; Ch. 18, Domain Types Are Better Than Strings

### 25.9 Require each test to constrain exactly what its scenario needs and no more
- **Why:** An incidental call stated as strictly as the real assertion hides what the test is for and breaks under unrelated refactorings — caching, reordering, an added field, a reformatted message. Over-constrained suites make people afraid to change code.
- **Applies:** Tests with several expectations, whole-object equality, exact-string matching on formatted output, or enforced call sequences; distinguishing setup from the behaviour under test.
- **Unless:** Where order or count is the contract — a bid sent once, a protocol whose completion must follow its matches, a cache that must query once — pin it explicitly. Loosening is not licence to ignore the collaborator whose behaviour is the point, and a chain of ignored objects hints at a missing collaborator.
- **Source:** Ch. 24, Specify Precisely What Should Happen and No More; Ch. 14, Allowances

### 25.10 Judge a test by the quality of its failure: name, values and message should locate the fault without a debugger
- **Why:** The purpose of a test is to fail informatively; a failure reporting only that something differed costs hours and eventually gets the test deleted. Names describing the scenario and result, values that are obviously canned or named constants, and builders that default everything the case ignores turn each red build into a diagnosis.
- **Applies:** Every new or modified test, especially in CI-only, generated, configuration-heavy or integration code; also tests differing only by a trailing digit, and diffs where a type change forced mass hand-edits to literals.
- **Unless:** Diagnostic scaffolding must not swamp intent — if explanations pile onto an assertion, make the values self-describing instead. Two obvious arguments need no builder, and shared builders can drift into an object-mother pile.
- **Source:** Ch. 23, Diagnostics Are a First-Class Feature; Ch. 21, Test Names Describe Features; Ch. 22, Constructing Complex Test Data

### 25.11 Take timing out of the objects: inject the executor, externalize the scheduler, and wait for observable success with a timeout
- **Why:** An object that spawns threads or starts its own timers hides a system-wide concern behind its API, so functional and synchronization defects arrive tangled and no test can know when the system is stable. A fixed sleep is either slow or unreliable, and a test asserting a state the system already occupies passes without testing anything.
- **Applies:** Changes creating threads, pools, timers, retry loops or future-dated actions inside domain logic; end-to-end tests over queues or background work; any newly added sleep in a test.
- **Unless:** Do not decouple where the framework already owns threading. Stress tests give reassurance, not proof, and must be watched failing before they are trusted. Externalizing the scheduler trades fidelity for speed, so keep a few slow whole-system tests. Polling cannot see states that were overwritten — prefer listening where events exist.
- **Source:** Ch. 26, Separating Functionality and Concurrency Policy; Ch. 27, Wait for Success / Externalize Event Sources

## Review heuristics

- Read the new tests before the production code: a long setup block, a bloated constructor, class mocking, widened visibility or a subclass-for-testing is the finding, and the fix belongs in the production code.
- Scan the import list of every domain class in the diff — a framework, driver, ORM or UI type there, or a singleton/clock/config read, means the boundary is in the wrong place.
- Check every mock against ownership: if the mocked type is third-party, ask for a thin adapter plus one integration test instead.
- Check each new constructor: are all parameters things the object cannot work without, do any always travel together under an unnamed concept, and do the arguments serve one job or several?
- Look for strings, ints and generic collections repeated across three or more signatures — that is a domain type asking to be born.
- Count what each test pins: exact call order, call counts, whole-object equality and formatted-string matches that the scenario does not require are future false failures.
- Grep the diff for sleeps, self-started threads and internal timers, and for a test that would pass against the system's starting state.
