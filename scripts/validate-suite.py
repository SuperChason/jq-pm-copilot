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
FIRST_PRINCIPLES_PROTOCOL = (
    ROOT / "skills" / "jq-pm-grilling" / "references" / "first-principles-protocol.md"
)
PRODUCT_CONTEXT_PROTOCOL = (
    ROOT / "skills" / "jq-pm-grilling" / "references" / "product-context-protocol.md"
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
    if not FIRST_PRINCIPLES_PROTOCOL.is_file():
        fail("缺少第一性原理产品推导协议")
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
        if "first-principles-protocol.md" not in text:
            fail(f"{skill_file.relative_to(ROOT)} 未接入第一性原理产品推导协议")

        for relative_reference in REFERENCE_PATTERN.findall(text):
            target = (skill_dir / relative_reference).resolve()
            if ROOT not in target.parents:
                fail(f"{skill_file.relative_to(ROOT)} 引用了仓库外文件：{relative_reference}")
            if not target.exists():
                fail(
                    f"{skill_file.relative_to(ROOT)} 引用不存在："
                    f"{target.relative_to(ROOT)}"
                )


def validate_v041_behavior() -> None:
    grilling = (ROOT / "skills" / "jq-pm-grilling" / "SKILL.md").read_text(encoding="utf-8")
    review = (ROOT / "skills" / "jq-pm-review" / "SKILL.md").read_text(encoding="utf-8")
    prototype = (ROOT / "skills" / "jq-pm-prototype" / "SKILL.md").read_text(encoding="utf-8")
    ui_spec = (ROOT / "skills" / "jq-ui-spec" / "SKILL.md").read_text(encoding="utf-8")
    research = (ROOT / "skills" / "jq-pm-research" / "SKILL.md").read_text(encoding="utf-8")
    briefing = (ROOT / "skills" / "jq-pm-briefing" / "SKILL.md").read_text(encoding="utf-8")
    context_protocol = PRODUCT_CONTEXT_PROTOCOL.read_text(encoding="utf-8")

    if "逐题拷问" not in frontmatter_value(grilling, "description"):
        fail("jq-pm-grilling 的触发描述缺少逐题拷问入口")
    review_description = frontmatter_value(review, "description") or ""
    if any(term in review_description for term in ("grill", "逐题拷问", "压力测试")):
        fail("jq-pm-review 的触发描述与 jq-pm-grilling 重叠")
    if "可点击原型" not in frontmatter_value(prototype, "description"):
        fail("jq-pm-prototype 的触发描述缺少可点击原型入口")
    ui_description = frontmatter_value(ui_spec, "description") or ""
    if any(term in ui_description for term in ("制作企业产品原型", "可点击原型")):
        fail("jq-ui-spec 的触发描述与 jq-pm-prototype 重叠")
    if "并行 Agent" not in research:
        fail("jq-pm-research 缺少可选并行调研规则")
    if "跨会话交接" not in briefing:
        fail("jq-pm-briefing 缺少跨会话交接规则")
    for term in ("CONTEXT-MAP.md", "关键产物与路径", "敏感", "建议下一 Skill"):
        if term not in context_protocol:
            fail(f"产品上下文协议缺少 v0.4.1 要求：{term}")


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
        excluded_skills = case.get("excluded_skills", [])
        if not isinstance(excluded_skills, list):
            fail(f"验收题 {case_id} 的 excluded_skills 必须是列表")
        unknown_excluded = set(excluded_skills) - set(EXPECTED_SKILLS)
        if unknown_excluded:
            fail(f"验收题 {case_id} 排除了未知 Skill：{', '.join(unknown_excluded)}")
        if set(expected_skills) & set(excluded_skills):
            fail(f"验收题 {case_id} 同时期望并排除了同一 Skill")
        covered_skills.update(expected_skills)
        if not case.get("prompt") or not case.get("must_behaviors"):
            fail(f"验收题 {case_id} 缺少 prompt 或 must_behaviors")
    if covered_skills != set(EXPECTED_SKILLS):
        missing = set(EXPECTED_SKILLS) - covered_skills
        fail(f"跨平台验收题没有覆盖全部 Skill：{', '.join(sorted(missing))}")
    if "first-principles-rebuild" not in seen_ids:
        fail("跨平台验收题缺少第一性原理推导场景")
    required_cases = {
        "multi-domain-context",
        "parallel-research-optional",
        "cross-session-handoff",
        "ui-spec-only",
    }
    missing_cases = required_cases - seen_ids
    if missing_cases:
        fail(f"跨平台验收题缺少 v0.4.1 场景：{', '.join(sorted(missing_cases))}")


def main() -> None:
    version = validate_versions()
    validate_skills()
    validate_v041_behavior()
    validate_evals(version)
    validate_sensitive_terms()
    print(f"PASS: jq-pm-copilot v{version}")
    print(f"PASS: {len(EXPECTED_SKILLS)} 个 Skill 目录、跨 Skill 引用和平台清单完整")
    print("PASS: 全部 8 个 Skill 已接入第一性原理产品推导协议")
    print("PASS: v0.4.1 多业务域、交接、调研与路由边界规则完整")
    print("PASS: 跨平台验收题覆盖全部 8 个 Skill")
    print("PASS: 未发现已配置的公司品牌词")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
