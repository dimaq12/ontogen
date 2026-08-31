# Expr spike: results (F0, 2026-08-20)

Test corpus — live v0 expressions (booking post, cross-entity invariant,
skill property). Criteria: typecheck, printers to 2 languages, SMT encoding,
readability. Run: `run_spike.py`.

| criterion | A: py-ast subset | B: lark (custom) | C: cel-python |
|---|---|---|---|
| parser | **stdlib, 0 dependencies** | ours, ~25 lines of grammar | someone else's package (lark inside) |
| lexicon ownership | Python (maximally stable expressions) | US (against D4) | Google CEL (a spec exists, but sum is not in the spec) |
| typecheck | ours, over our AST; errors with line/column in Russian | ours | ours ON TOP OF SOMEONE ELSE'S AST |
| Go printer | ok (aggregates — IIFE loops) | to write | to write over someone else's AST |
| Python printer | **free (ast.unparse)** | to write | to write |
| SMT (z3) | **ok: post reserve PROVEN; mutant without guard — counterexample [av=0,cap=1]; bounded aggregates work** | to write | to write |
| readability in the genome | `all(t.qty > 0 for t in out)` — like v0 propcheck, familiar | `all(t: ... for t in out)` | `out.all(t, t.qty > 0)` — its own style |
| rejections | "no field 'availble'; available: [...]", "call outside the whitelist" | — | English, CEL terms |

## Verdict: A — Expr = a subset of Python expressions (stdlib ast)

- We own neither the grammar nor the parser — only the WHITELIST of nodes
  (our spec = the list + type rules; versioned trivially). D4 is
  fulfilled more strongly than expected: not a "similar" language was borrowed, but the native one.
- The printer to the second dialect (python) is free — the F3 exam gets cheaper.
- The SMT encoding is direct; the F2 judgment is shown working already in the spike.
- Rule bodies (assignments + if) — the same ast, mode="exec", the whitelist
  is extended with Assign/If — a natural continuation, the same parser.
- Risk (in PREDICTIONS P7): "the interpreter creeps into a language" — here creeping
  = extending the whitelist; every new node — through UNEXPRESSIBLE.

B rejected: owning the grammar against D4, writing everything ourselves with no benefit.
C rejected: someone else's AST + our own syntax style + sum outside the CEL spec + English
errors; the benefit (Google's spec) does not pay off.
