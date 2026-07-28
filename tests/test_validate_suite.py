from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-suite.py"
SPEC = importlib.util.spec_from_file_location("validate_suite", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATE_SUITE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE_SUITE)


class TestFrontmatterValue(unittest.TestCase):
    def test_reads_required_value(self) -> None:
        text = "---\nname: sample-skill\ndescription: 示例\n---\n\n# 正文\n"
        self.assertEqual(
            VALIDATE_SUITE.frontmatter_value(text, "name"),
            "sample-skill",
        )

    def test_returns_none_without_complete_frontmatter(self) -> None:
        self.assertIsNone(
            VALIDATE_SUITE.frontmatter_value("---\nname: sample-skill\n", "name")
        )


class TestReferencePattern(unittest.TestCase):
    def test_matches_supported_relative_reference(self) -> None:
        text = "读取 references/example.md 和 ../shared/references/rule.md。"
        self.assertEqual(
            VALIDATE_SUITE.REFERENCE_PATTERN.findall(text),
            [
                "references/example.md",
                "../shared/references/rule.md",
            ],
        )


class TestRepositoryValidation(unittest.TestCase):
    def test_full_validation_suite_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
