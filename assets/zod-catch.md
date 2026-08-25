> A cold-run Punchcard review of [colinhacks/zod#6461](https://github.com/colinhacks/zod/pull/6461), exactly as the skill rendered it. Sonnet 5, 2026-08-25, run `punch-2` of the [three-way benchmark](../benchmarks/three-way-sonnet-2026-08.md) — the only review, out of twelve cold runs by three reviewers, to report finding #1. The finding was re-verified by executing the reviewer's own repro against both trees.



## 🟠 Ship after #1.

The fold has a genuine correctness gap at nested property keys — it silently pools two unrelated schemas into one where the parser keeps them independent, making the emitted JSON Schema *accept* values Zod rejects. #2 is a real algorithmic cliff worth closing before merge too; #3 can follow.

| # |  | What | Where |
|---|---|------|-------|
| 1 | 🔴 BLOCKER | Nested property fold pools two unrelated members' schemas, making the emitted JSON Schema accept what the parser rejects | `packages/zod/src/v4/core/to-json-schema.ts:490` |
| 2 | 🟡 DESIGN | Chained `.and()` calls cost cubic time to convert, ~200x slower than before this diff | `packages/zod/src/v4/core/to-json-schema.ts:490` |
| 3 | 🔵 QUESTION | No test reaches the nested-property collision that produces finding #1 | `packages/zod/src/v4/classic/tests/to-json-schema.test.ts:4079` |

---

### 🔴 1 · Nested property fold pools two unrelated members' schemas, so the emitted JSON Schema accepts values the parser rejects

`packages/zod/src/v4/core/to-json-schema.ts:490` · A consumer validating incoming JSON against the emitted schema will accept payloads Zod itself throws on.

`foldObjects`'s per-key loop at `to-json-schema.ts:490-505` merges every member's value for a shared property key as if it were one intersection at that nesting level:

```ts
for (const key in object.properties) {
  ...
  const parts: JSONSchema._JSONSchema[] = [];
  for (const other of objects) {
    const part = other.properties?.[key] ?? undeclaredConstraint(other);
    ...
  }
  const merged = parts.length === 1 ? parts[0]! : (foldObjects(parts) ?? ...);  // ← pools A.x and B.x into one object
```

But the parser's pooling (`handleIntersectionResults`, referenced in the PR's own description) only merges unrecognized-key issues that carry an *empty* path — i.e. only at the intersection's own top level. A nested path like `["x"]` gets each side's errors pushed straight through, unpooled. Reproduced directly:

```ts
// this PR
const A = z.object({ x: z.object({ a: z.string() }).strict() }).strict();
const B = z.object({ x: z.object({ b: z.string() }).strict() }).strict();
const C = A.and(B);
z.toJSONSchema(C);
// → properties.x = { properties: {a, b}, required: [a, b], additionalProperties: false }
C.safeParse({ x: { a: "1", b: "2" } });
// → success: false — two unrecognized_keys errors at path ["x"]
```

Run against `main` (`git show 1c43b774:.../to-json-schema.ts`), the same schema correctly emits `allOf: [{x:{a}}, {x:{b}}]`, which any JSON Schema validator correctly rejects `{x:{a,b}}` on — matching the parser. This diff turns a case that was already correct into one that is wrong, which is the same defect class the PR is fixing, just one level deeper than the fold's own reasoning accounts for.

> 🔧 **Fix:** only pool a property key across members when the value actually flows through the intersection's own `parse` (i.e. the pooling the parser does is scoped to the intersection's immediate result, not to any nested key two members both happen to declare) — `foldObjects`'s recursive per-key merge needs to stop treating "same key name, different outer members" as itself an intersection.

---

### 🟡 2 · Chained `.and()` calls cost cubic time to convert, ~200x slower than before this diff

`packages/zod/src/v4/core/to-json-schema.ts:490` · A schema built by folding N small objects together with `.and()` (a normal way to compose validators incrementally) goes from a linear conversion to one measured at 1.25s for N=400, versus 6ms on `main`.

Two things in this diff compound. First, `intersectionProcessor` flattens a chained intersection into one array by spreading, but the *intermediate* intersection nodes stay in `ctx.seen` with their own un-flattened `allOf` arrays, and `finalize`'s carrier loop still finds and folds each of them:

```ts
// packages/zod/src/v4/core/json-schema-processors.ts:389-393
const allOf = [...(isSimpleIntersection(a) ? (a.allOf as any[]) : [a]), ...];
json.allOf = allOf;      // a NEW array — a's own allOf array is now orphaned but still in ctx.seen
ctx.intersections.push(allOf);
```

Second, each `foldObjects` call over `m` members does `O(m)` work per shared key across `O(m)` keys — `O(m²)` per call — and this now runs once per orphaned intermediate node (sizes 2, 3, ..., N), summing to `O(N³)`:

```ts
// packages/zod/src/v4/core/to-json-schema.ts:490-499
for (const key in object.properties) {
  ...
  for (const other of objects) { ... }   // ← O(members) work, repeated per key, repeated per chain length
```

Measured directly with `z.object({k0}).and(z.object({k1}))...`, N chained members, on this PR's code vs. `main`:

```
N     main      this PR
50    1.17ms    3.81ms
100   0.80ms    18.72ms
200   1.49ms    145.76ms
400   6.16ms    1249.42ms
```

The 2x-doubling ratio (~8.6x time for 2x length) confirms cubic growth, not the quadratic the PR's own linear-time registry test guards against — that test only exercises one 2-member intersection, not a chain.

> 🔧 **Fix:** drop the orphaned intermediate `allOf` arrays from `ctx.intersections` once a parent has flattened them away (or track only reachable arrays), and avoid re-deriving each key's merged parts from scratch on every call — cache per-array fold results so a chain's `N` levels don't redo `O(N²)` work apiece.

---

### 🔵 3 · No test reaches the nested-property collision that produces finding #1

`packages/zod/src/v4/classic/tests/to-json-schema.test.ts:4079` · The `describe("intersection folding", ...)` block covers a shared key at the top level (`"a key both members declare has to satisfy both"`) but never two *different* top-level intersection members that happen to share a nested property name — exactly the input that reaches the bad merge in finding #1.

> 🔧 **Fix:** add a case with `z.object({x: innerA}).and(z.object({x: innerB}))` where `innerA`/`innerB` are distinct strict objects, and assert the emitted schema against an actual `.safeParse()` on the same input rather than only against `toMatchObject` shape.