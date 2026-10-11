#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rea_rebuild_gate import (  # noqa: E402
    SCHEMA,
    main,
    run_evals,
    validate_evidence,
)

EX_PERCENT = ROOT / "examples" / "percent_rule"
EX_SPEED = ROOT / "examples" / "speed_ramp"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


class ValidateTests(unittest.TestCase):
    def test_percent_passes(self):
        errs = validate_evidence(_load(EX_PERCENT / "evidence.json"), 0.8)
        self.assertEqual(errs, [])

    def test_speed_passes(self):
        errs = validate_evidence(_load(EX_SPEED / "evidence.json"), 0.8)
        self.assertEqual(errs, [])

    def test_confidence_floor(self):
        data = _load(EX_PERCENT / "evidence.json")
        data["claims"][0]["confidence"] = 0.5
        errs = validate_evidence(data, 0.8)
        self.assertTrue(any("below --min-confidence" in e for e in errs))

    def test_missing_covers_eval(self):
        data = _load(EX_PERCENT / "evidence.json")
        data["claims"][0]["covers_eval"] = []
        errs = validate_evidence(data, 0.8)
        self.assertTrue(any("covers_eval" in e for e in errs))

    def test_bad_schema(self):
        data = _load(EX_PERCENT / "evidence.json")
        data["schema"] = "other"
        errs = validate_evidence(data, 0.8)
        self.assertTrue(any("schema" in e for e in errs))

    def test_digest_prefix(self):
        data = _load(EX_PERCENT / "evidence.json")
        data["artifact"]["digest"] = "abc"
        errs = validate_evidence(data, 0.8)
        self.assertTrue(any("sha256:" in e for e in errs))


class EvalTests(unittest.TestCase):
    def test_percent_evals_pass(self):
        evidence = _load(EX_PERCENT / "evidence.json")
        evals = _load(EX_PERCENT / "evals.json")
        rows, errs = run_evals(evidence, evals, EX_PERCENT / "rebuild.py")
        self.assertEqual(errs, [])
        self.assertTrue(all(r["ok"] for r in rows))
        self.assertEqual(len(rows), 8)

    def test_speed_evals_pass(self):
        evidence = _load(EX_SPEED / "evidence.json")
        evals = _load(EX_SPEED / "evals.json")
        rows, errs = run_evals(evidence, evals, EX_SPEED / "rebuild.py")
        self.assertEqual(errs, [])
        self.assertTrue(all(r["ok"] for r in rows))

    def test_wrong_rebuild_fails(self):
        bad = '''def apply(op, previous, current):\n    return 0.0\n'''
        with tempfile.TemporaryDirectory() as td:
            impl = Path(td) / "rebuild.py"
            impl.write_text(bad, encoding="utf-8")
            evidence = _load(EX_PERCENT / "evidence.json")
            evals = _load(EX_PERCENT / "evals.json")
            rows, errs = run_evals(evidence, evals, impl)
            self.assertTrue(errs)
            self.assertFalse(all(r["ok"] for r in rows))

    def test_claim_coverage_gap(self):
        evidence = _load(EX_PERCENT / "evidence.json")
        evidence["claims"][0]["covers_eval"] = ["does_not_exist"]
        evals = _load(EX_PERCENT / "evals.json")
        rows, errs = run_evals(evidence, evals, EX_PERCENT / "rebuild.py")
        self.assertTrue(any("not in evals" in e for e in errs))
        self.assertEqual(rows, [])


class CliTests(unittest.TestCase):
    def test_demo_exit_0(self):
        self.assertEqual(main(["demo"]), 0)

    def test_check_percent(self):
        self.assertEqual(
            main(
                [
                    "check",
                    "--evidence",
                    str(EX_PERCENT / "evidence.json"),
                    "--evals",
                    str(EX_PERCENT / "evals.json"),
                    "--impl",
                    str(EX_PERCENT / "rebuild.py"),
                ]
            ),
            0,
        )

    def test_validate_cli(self):
        self.assertEqual(
            main(["validate", str(EX_SPEED / "evidence.json"), "--min-confidence", "0.9"]),
            0,
        )


if __name__ == "__main__":
    unittest.main()
