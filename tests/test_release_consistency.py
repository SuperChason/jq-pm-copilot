from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class TestReleaseConsistency(unittest.TestCase):
    def test_versions_stay_in_sync(self) -> None:
        codex_version = read_json(".codex-plugin/plugin.json")["version"]
        claude_version = read_json(".claude-plugin/plugin.json")["version"]
        marketplace = read_json(".claude-plugin/marketplace.json")["plugins"][0]
        eval_version = read_json("evals/cross-platform-cases.json")["version"]
        self.assertEqual(
            {
                codex_version,
                claude_version,
                marketplace["version"],
                marketplace["source"]["ref"].removeprefix("v"),
                eval_version,
            },
            {codex_version},
        )

    def test_changelog_starts_with_current_version(self) -> None:
        version = read_json(".codex-plugin/plugin.json")["version"]
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        first_version = re.search(r"^## (\d+\.\d+\.\d+)$", changelog, re.MULTILINE)
        self.assertIsNotNone(first_version)
        self.assertEqual(first_version.group(1), version)

    def test_readme_has_no_stale_clone_tag(self) -> None:
        version = read_json(".codex-plugin/plugin.json")["version"]
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        tags = set(re.findall(r"git clone --branch v(\d+\.\d+\.\d+)", readme))
        self.assertEqual(tags, {version})


if __name__ == "__main__":
    unittest.main()
