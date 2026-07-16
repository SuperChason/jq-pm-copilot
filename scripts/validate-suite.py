#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = (
    "jq-pm-grilling",
    "jq-pm-discovery",
    "jq-pm-research",
    "jq-pm-prd",
    "jq-pm-prototype",
    "jq-pm-review",
    "jq-pm-briefing",
    "jq-ui-spec",
)
PLATFORM_MANIFESTS = (
    ROOT / ".codex-plugin" / "plugin.json",
    ROOT / ".claude-plugin" / "plugin.json",
)
BANNED_BRAND_TERMS = (
    "北京" + "久其",
    "久其" + "软件",
    "Jiuqi" + " Software",
)
REFERENCE_PATTERN = re.compile(
    r"(?<![\w:/])((?:\.\./|references/|assets/|scripts/)"
    r"[A-Za-z0-9._/-]+\.(?:md|mjs|js|css|html))"
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"缺少文件：{path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"JSON 格式错误：{path.relative_to(ROOT)}：{exc}")


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    for line in text[4:end].splitlines():
        name, separator, value = line.partition(":")
        if separator and name.strip() == key:
            return value.strip()
    return None


def validate_versions() -> str:
    manifests = [load_json(path) for path in PLATFORM_MANIFESTS]
    versions = {manifest.get("version") for manifest in manifests}
    if len(versions) != 1 or None in versions:
        fail("Codex 与 Claude Code 插件版本不一致")

    version = versions.pop()
    for path, manifest in zip(PLATFORM_MANIFESTS, manifests):
        if manifest.get("name") != "jq-pm-copilot":
            fail(f"插件名称错误：{path.relative_to(ROOT)}")
        if manifest.get("skills") != "./skills/":
            fail(f"Skill 入口错误：{path.relative_to(ROOT)}")

    codex_marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    codex_plugins = codex_marketplace.get("plugins", [])
    claude_plugins = claude_marketplace.get("plugins", [])
    if len(codex_plugins) != 1 or len(claude_plugins) != 1:
        fail("平台 Marketplace 必须只发布一个 jq-pm-copilot 插件")
    if codex_plugins[0].get("name") != "jq-pm-copilot":
        fail("Codex Marketplace 插件名称错误")
    if claude_plugins[0].get("name") != "jq-pm-copilot":
        fail("Claude Marketplace 插件名称错误")
    codex_source = codex_plugins[0].get("source", {})
    if codex_source.get("source") != "local" or codex_source.get("path") != "./":
        fail("Codex Marketplace 必须直接安装仓库根目录中的插件")
    if claude_plugins[0].get("source", {}).get("ref") != f"v{version}":
        fail("Claude Marketplace 的发布标签与插件版本不一致")
    if claude_plugins[0].get("version") != version:
        fail("Claude Marketplace 的插件版本与插件清单不一致")

    return version


def validate_skills() -> None:
    skills_root = ROOT / "skills"
    actual_skills = tuple(sorted(path.name for path in skills_root.iterdir() if path.is_dir()))
    if set(actual_skills) != set(EXPECTED_SKILLS):
        fail(
            "Skill 集合不一致："
            f"期望 {', '.join(EXPECTED_SKILLS)}；实际 {', '.join(actual_skills)}"
        )

    for skill_name in EXPECTED_SKILLS:
        skill_dir = skills_root / skill_name
        skill_file = skill_dir / "SKILL.md"
        agent_file = skill_dir / "agents" / "openai.yaml"
        if not skill_file.is_file():
            fail(f"缺少 {skill_file.relative_to(ROOT)}")
        if not agent_file.is_file():
            fail(f"缺少 {agent_file.relative_to(ROOT)}")

        text = skill_file.read_text(encoding="utf-8")
        if frontmatter_value(text, "name") != skill_name:
            fail(f"{skill_file.relative_to(ROOT)} 的 name 与目录名不一致")
        description = frontmatter_value(text, "description")
        if not description:
            fail(f"{skill_file.relative_to(ROOT)} 缺少 description")
        if "platform-capability-fallback.md" not in text:
            fail(f"{skill_file.relative_to(ROOT)} 未接入跨平台能力降级协议")

        for relative_reference in REFERENCE_PATTERN.findall(text):
            target = (skill_dir / relative_reference).resolve()
            if ROOT not in target.parents:
                fail(f"{skill_file.relative_to(ROOT)} 引用了仓库外文件：{relative_reference}")
            if not target.exists():
                fail(
                    f"{skill_file.relative_to(ROOT)} 引用不存在："
                    f"{target.relative_to(ROOT)}"
                )


def validate_sensitive_terms() -> None:
    excluded_parts = {".git", "dist", "__pycache__"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in excluded_parts for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for term in BANNED_BRAND_TERMS:
            if term.lower() in text.lower():
                fail(f"{path.relative_to(ROOT)} 包含禁止公开的公司品牌词：{term}")


def validate_evals(version: str) -> None:
    evals = load_json(ROOT / "evals" / "cross-platform-cases.json")
    if evals.get("version") != version:
        fail("跨平台验收题版本与插件版本不一致")
    cases = evals.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        fail("跨平台验收题数量不足")
    seen_ids: set[str] = set()
    covered_skills: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not case_id or case_id in seen_ids:
            fail("跨平台验收题存在空 ID 或重复 ID")
        seen_ids.add(case_id)
        expected_skills = case.get("expected_skills")
        if not isinstance(expected_skills, list) or not expected_skills:
            fail(f"验收题 {case_id} 缺少 expected_skills")
        unknown_skills = set(expected_skills) - set(EXPECTED_SKILLS)
        if unknown_skills:
            fail(f"验收题 {case_id} 引用了未知 Skill：{', '.join(unknown_skills)}")
        covered_skills.update(expected_skills)
        if not case.get("prompt") or not case.get("must_behaviors"):
            fail(f"验收题 {case_id} 缺少 prompt 或 must_behaviors")
    if covered_skills != set(EXPECTED_SKILLS):
        missing = set(EXPECTED_SKILLS) - covered_skills
        fail(f"跨平台验收题没有覆盖全部 Skill：{', '.join(sorted(missing))}")


def main() -> None:
    version = validate_versions()
    validate_skills()
    validate_evals(version)
    validate_sensitive_terms()
    print(f"PASS: jq-pm-copilot v{version}")
    print(f"PASS: {len(EXPECTED_SKILLS)} 个 Skill 目录、跨 Skill 引用和平台清单完整")
    print("PASS: 跨平台验收题覆盖全部 8 个 Skill")
    print("PASS: 未发现已配置的公司品牌词")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
