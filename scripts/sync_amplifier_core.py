#!/usr/bin/env python3
"""
sync_amplifier_core.py - amplifier-coreドキュメントをスキルに同期

Usage:
    python scripts/sync_amplifier_core.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

# === 設定 ===
SOURCE_REPO = "https://github.com/microsoft/amplifier-core"
PLUGIN_ROOT = Path(__file__).parent.parent

# 参照パス変換ルール
REFERENCE_PATTERNS = [
    # amplifier-core内の参照をスキル参照に変換
    (r"\[([^\]]+)\]\(DESIGN_PHILOSOPHY\.md\)", r"[\1](@skills/amplifier-philosophy/SKILL.md)"),
    (r"\[([^\]]+)\]\(contracts/([^)]+)\)", r"[\1](@skills/module-development/SKILL.md)"),
    (r"\[([^\]]+)\]\(MODULE_SOURCE_PROTOCOL\.md\)", r"[\1](@skills/module-development/SKILL.md)"),
    # 相対パスのリンクを絶対URLに変換
    (r"\[([^\]]+)\]\(\.\./([^)]+)\)", r"[\1](https://github.com/microsoft/amplifier-core/blob/main/\2)"),
]

CREDIT_COMMENT = """\
<!--
  Source: https://github.com/microsoft/amplifier-core
  License: MIT
  Auto-synced for Claude Code Plugin format
-->

"""

PHILOSOPHY_FRONTMATTER = """\
---
name: amplifier-philosophy
description: Amplifier design philosophy using Linux kernel metaphor. Covers mechanism vs policy, module architecture, event-driven design, and kernel principles. Use when designing new modules or making architectural decisions.
version: 1.0.0
license: MIT
metadata:
  category: architecture
  complexity: medium
  original_source: https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md
---

"""

MODULE_DEV_FRONTMATTER = """\
---
name: module-development
description: Guide for creating new Amplifier modules including protocol implementation, entry points, mount functions, and testing patterns. Use when creating new modules or understanding module architecture.
version: 1.0.0
license: MIT
metadata:
  category: development
  complexity: medium
  original_source: https://github.com/microsoft/amplifier-core/tree/main/docs/contracts
---

"""

# contracts統合の順序
CONTRACT_FILES = [
    "TOOL_CONTRACT.md",
    "PROVIDER_CONTRACT.md",
    "HOOK_CONTRACT.md",
    "ORCHESTRATOR_CONTRACT.md",
    "CONTEXT_CONTRACT.md",
]


def clone_upstream(target_dir: Path) -> Path:
    """ソースリポジトリをクローン"""
    print(f"Cloning {SOURCE_REPO}...")
    subprocess.run(
        ["git", "clone", "--depth", "1", SOURCE_REPO, str(target_dir)],
        check=True,
        capture_output=True,
    )
    return target_dir


def transform_references(content: str) -> str:
    """参照パスを変換"""
    result = content
    for pattern, replacement in REFERENCE_PATTERNS:
        result = re.sub(pattern, replacement, result)
    return result


def inject_credit(content: str) -> str:
    """クレジット表記を追加（先頭に挿入）"""
    return CREDIT_COMMENT + content


def sync_philosophy(source_dir: Path, dry_run: bool = False) -> Path:
    """DESIGN_PHILOSOPHY.md → amplifier-philosophy/SKILL.md"""
    source_path = source_dir / "docs" / "DESIGN_PHILOSOPHY.md"
    target_path = PLUGIN_ROOT / "skills" / "amplifier-philosophy" / "SKILL.md"

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    content = source_path.read_text()
    content = transform_references(content)
    content = PHILOSOPHY_FRONTMATTER + inject_credit(content)

    if dry_run:
        print(f"  [DRY-RUN] Would update: {target_path}")
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)
        print(f"  Updated: {target_path}")

    return target_path


def sync_module_development(source_dir: Path, dry_run: bool = False) -> Path:
    """contracts/*.md + MODULE_SOURCE_PROTOCOL.md → module-development/SKILL.md"""
    contracts_dir = source_dir / "docs" / "contracts"
    target_path = PLUGIN_ROOT / "skills" / "module-development" / "SKILL.md"

    if not contracts_dir.exists():
        raise FileNotFoundError(f"Contracts directory not found: {contracts_dir}")

    # README.mdを概要として使用
    readme_path = contracts_dir / "README.md"
    if not readme_path.exists():
        raise FileNotFoundError(f"README not found: {readme_path}")

    sections = []

    # 概要（README.md）
    readme_content = readme_path.read_text()
    readme_content = transform_references(readme_content)
    sections.append(readme_content)

    # 各契約ファイル
    for contract_file in CONTRACT_FILES:
        contract_path = contracts_dir / contract_file
        if contract_path.exists():
            contract_content = contract_path.read_text()
            contract_content = transform_references(contract_content)
            sections.append(f"\n---\n\n{contract_content}")
        else:
            print(f"  WARNING: Contract file not found: {contract_path}")

    # MODULE_SOURCE_PROTOCOL.md（付録）
    module_source_path = source_dir / "docs" / "MODULE_SOURCE_PROTOCOL.md"
    if module_source_path.exists():
        module_source_content = module_source_path.read_text()
        module_source_content = transform_references(module_source_content)
        sections.append(f"\n---\n\n# Appendix: Module Source Protocol\n\n{module_source_content}")
    else:
        print(f"  WARNING: MODULE_SOURCE_PROTOCOL.md not found")

    # 統合
    combined_content = "\n".join(sections)
    combined_content = MODULE_DEV_FRONTMATTER + inject_credit(combined_content)

    if dry_run:
        print(f"  [DRY-RUN] Would update: {target_path}")
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(combined_content)
        print(f"  Updated: {target_path}")

    return target_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync amplifier-core docs to skills"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without applying"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Amplifier Core Sync")
    print("=" * 60)

    # 一時ディレクトリにクローン
    with tempfile.TemporaryDirectory() as tmp_dir:
        source_dir = clone_upstream(Path(tmp_dir) / "amplifier-core")

        print("\n[1/2] Syncing amplifier-philosophy...")
        sync_philosophy(source_dir, dry_run=args.dry_run)

        print("\n[2/2] Syncing module-development...")
        sync_module_development(source_dir, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN complete. No files were modified.")
    else:
        print("Sync complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
