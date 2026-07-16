#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_INPUTS = (
    ".agents",
    ".claude-plugin",
    ".codex-plugin",
    "evals",
    "skills",
    "scripts",
    "third-party-notices",
    "CHANGELOG.md",
    "README.md",
)
WORKBUDDY_SKILLS = (
    "jq-pm-grilling",
    "jq-pm-discovery",
    "jq-pm-research",
    "jq-pm-prd",
    "jq-pm-prototype",
    "jq-pm-review",
    "jq-pm-briefing",
    "jq-ui-spec",
)
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def version() -> str:
    manifest = json.loads(
        (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    return manifest["version"]


def archive_file(archive: zipfile.ZipFile, source: Path, target: str) -> None:
    info = zipfile.ZipInfo(target, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, source.read_bytes())


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for child in sorted(path.rglob("*")):
        if child.is_file() and "__pycache__" not in child.parts:
            yield child


def build_main_package(release_version: str) -> Path:
    output = DIST / f"jq-pm-copilot-v{release_version}.zip"
    prefix = Path(f"jq-pm-copilot-v{release_version}")
    with zipfile.ZipFile(output, "w") as archive:
        for relative_input in PACKAGE_INPUTS:
            source = ROOT / relative_input
            for file_path in iter_files(source):
                relative_path = file_path.relative_to(ROOT)
                archive_file(archive, file_path, str(prefix / relative_path))
    return output


def build_workbuddy_skill(skill_name: str, release_version: str) -> bytes:
    skill_root = ROOT / "skills" / skill_name
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for file_path in iter_files(skill_root):
            relative_path = file_path.relative_to(skill_root)
            if relative_path.parts and relative_path.parts[0] == "agents":
                continue
            archive_file(archive, file_path, str(relative_path))
    return output.getvalue()


def build_workbuddy_bundle(release_version: str) -> Path:
    output = DIST / f"jq-pm-copilot-workbuddy-v{release_version}.zip"
    with zipfile.ZipFile(output, "w") as archive:
        manifest = {
            "name": "jq-pm-copilot",
            "version": release_version,
            "platform": "WorkBuddy",
            "install_order": list(WORKBUDDY_SKILLS),
            "note": "解压本文件后，将 8 个 Skill ZIP 全部导入 WorkBuddy。",
        }
        info = zipfile.ZipInfo("workbuddy-manifest.json", FIXED_ZIP_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(
            info,
            json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
        )
        for skill_name in WORKBUDDY_SKILLS:
            skill_bytes = build_workbuddy_skill(skill_name, release_version)
            info = zipfile.ZipInfo(
                f"{skill_name}-v{release_version}.zip",
                FIXED_ZIP_TIME,
            )
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, skill_bytes)
    return output


def write_checksums(paths: tuple[Path, ...]) -> Path:
    output = DIST / "SHA256SUMS.txt"
    lines = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> None:
    subprocess.run(
        ["python3", str(ROOT / "scripts" / "validate-suite.py")],
        cwd=ROOT,
        check=True,
    )
    release_version = version()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    main_package = build_main_package(release_version)
    workbuddy_package = build_workbuddy_bundle(release_version)
    checksums = write_checksums((main_package, workbuddy_package))

    print(f"BUILT: {main_package.relative_to(ROOT)}")
    print(f"BUILT: {workbuddy_package.relative_to(ROOT)}")
    print(f"BUILT: {checksums.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
