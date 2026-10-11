# rea-rebuild-gate

[![CI](https://github.com/BrickerP/rea-rebuild-gate/actions/workflows/ci.yml/badge.svg)](https://github.com/BrickerP/rea-rebuild-gate/actions/workflows/ci.yml)

**A GitHub Action / CLI that fails a PR when REA-style rebuild evidence is weak — or the rebuild fails its behavior evals.**

[REA](https://rea.tools/) (Reverse Engineer Anything) helps coding agents recover how software works. Agents then rewrite. A demo that “runs” is not production. This gate sits in the middle: **evidence confidence + claim→eval coverage + behavior tests** before merge.

## Result (bundled demos)

```bash
python3 src/rea_rebuild_gate.py demo
```

```
rea-rebuild-gate demo
================================================

[percent_rule]
PASS  eval  8/8 evals · 2 claims covered
  PASS  add_200_10
  PASS  sub_50_10
  PASS  add_0_10
  PASS  add_100_0
  PASS  mul_200_10
  PASS  div_200_10
  PASS  mul_50_25
  PASS  div_100_50

[speed_ramp]
PASS  eval  3/3 evals · 1 claim covered
  PASS  ticks_0
  PASS  ticks_4000
  PASS  ticks_10000

================================================
RESULT: all example rebuilds PASS evidence + behavior evals
```

Stdlib-only Python. No install step, no network calls, no API keys.

## How it works

1. **Evidence JSON** (`rea-rebuild-gate/v1`) lists recovered claims with `confidence`, `authority`, and `covers_eval`.
2. **`validate`** rejects missing fields, bad digests, empty coverage, or confidence below `--min-confidence` (default `0.8`).
3. **`eval` / `check`** loads your rebuild (`apply(**input)` or `run(input)`), runs the eval suite, and fails if any claim’s covered evals don’t pass.

This does **not** reverse-engineer binaries. It audits the *rebuild handoff* after something like REA (or a human) produced claims.

## Quick start

1. Drop `evidence.json`, `evals.json`, and `rebuild.py` in your repo (see `examples/`).
2. Add `.github/workflows/rea-rebuild-gate.yml`:

```yaml
name: rea-rebuild-gate
on: pull_request
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: BrickerP/rea-rebuild-gate@v1
        with:
          evidence: evidence.json
          evals: evals.json
          impl: rebuild.py
          min_confidence: "0.8"
```

## Evidence schema (`rea-rebuild-gate/v1`)

| field | meaning |
|---|---|
| `artifact.name` / `digest` / `kind` | What was inspected (`digest` must be `sha256:…`; `kind`: `javascript\|native\|web\|synthetic`) |
| `provider.id` / `version` | Who produced the claims (`rea`, `manual`, or `synthetic`) |
| `claims[].confidence` | `[0,1]`; must meet `--min-confidence` |
| `claims[].authority` | `observed` or `inferred` |
| `claims[].covers_eval` | Eval ids this claim is responsible for (required, non-empty) |

## CLI

```bash
python3 src/rea_rebuild_gate.py validate evidence.json
python3 src/rea_rebuild_gate.py check \
  --evidence evidence.json --evals evals.json --impl rebuild.py
python3 src/rea_rebuild_gate.py demo
```

## Examples

| folder | what it practices |
|---|---|
| `examples/percent_rule` | Operator-dependent percent value (8 evals, 2 claims) |
| `examples/speed_ramp` | Clamped linear speed ramp (3 evals, 1 claim) |

Both are **synthetic teaching fixtures**, not claims about commercial software.

## Marketplace

Publish this Action on the GitHub Marketplace (free tier first) the same way as other BrickerP gates. Track installs before any paid tier.

## Development

```bash
python3 -m unittest discover -s tests -v
```

## Author

Built by Yupeng Lu — AI agent & backend engineer. I take agents from demo to production: MCP tools, guardrails, evals, billing, real-time systems. Hire me: https://brickerp.github.io/hire/

MIT License.
