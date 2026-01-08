#!/usr/bin/env python3
"""
sync_ddd.py - DDDコレクションをamplifier-skills-pluginに同期

Usage:
    python scripts/sync_ddd.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# === 設定 ===
SOURCE_REPO = "https://github.com/robotdad/amplifier-collection-ddd"
PLUGIN_ROOT = Path(__file__).parent.parent

# エージェント → コマンド マッピング (フラット構造)
AGENT_TO_COMMAND = {
    "planning-architect.md": "ddd-1-plan.md",
    "documentation-retroner.md": "ddd-2-docs.md",
    "code-planner.md": "ddd-3-code-plan.md",
    "implementation-verifier.md": "ddd-4-code.md",
    "finalization-specialist.md": "ddd-5-finish.md",
}

# 参照パス変換ルール
REFERENCE_PATTERNS = [
    (r"@ddd:context/", "@skills/ddd-guide/references/"),
    (r"@ddd:", "@skills/ddd-guide/references/"),
    (r"@foundation:IMPLEMENTATION_PHILOSOPHY\.md", "@skills/amplifier-philosophy/SKILL.md"),
    (r"@foundation:MODULAR_DESIGN_PHILOSOPHY\.md", "@skills/amplifier-philosophy/SKILL.md"),
    (r"@foundation:", "@skills/amplifier-philosophy/"),
]

CREDIT_COMMENT = """\
<!--
  Source: https://github.com/robotdad/amplifier-collection-ddd
  License: MIT
  Auto-converted for Claude Code Plugin format
-->

"""

SKILL_MD_TEMPLATE = """\
---
name: ddd-guide
description: Document-Driven Development workflow for existing codebases. Provides systematic planning, documentation-first design, and implementation verification.
version: 1.0.0
license: MIT
metadata:
  category: workflow
  complexity: high
  original_source: https://github.com/robotdad/amplifier-collection-ddd
---

# Document-Driven Development (DDD) Guide

## Core Principle

**Documentation IS the specification. Code implements what documentation describes.**

DDD inverts traditional development: update documentation first, then implement code to match.

## Why DDD?

- **Catches design flaws early** - Before expensive code changes
- **Prevents documentation drift** - Docs and code stay synchronized
- **Enables human review** - Humans approve specs, not code
- **AI-friendly** - Clear specifications reduce hallucination

## Six-Phase Workflow

| Phase | Name | Command | Deliverable |
|-------|------|---------|-------------|
| 0-1 | Planning | /ddd 1-plan | plan.md |
| 2 | Documentation | /ddd 2-docs | Updated docs |
| 3 | Code Planning | /ddd 3-code-plan | code_plan.md |
| 4 | Implementation | /ddd 4-code | Working code |
| 5-6 | Finalization | /ddd 5-finish | Tested, committed |

## Core Techniques

### Retcon Writing

Document features as if they already exist. No future tense.

- Bad: "This feature will add..."
- Good: "This feature provides..."

### File Crawling

Process files one at a time to avoid context overflow:

1. Generate index with `[ ]` checkboxes
2. Process one file per iteration
3. Mark `[x]` when complete

### Context Poisoning Prevention

Eliminate contradictions:

- One authoritative location per concept
- Delete duplicates, don't update
- Resolve conflicts before proceeding

## When to Use DDD

**Use DDD for:**
- Multi-file changes
- New features in existing codebases
- Complex integrations

**Skip DDD for:**
- Typo fixes
- Single-file changes
- Emergency hotfixes

## References

See `@skills/ddd-guide/references/` for detailed documentation:

- `core-concepts/` - Techniques and methodologies
- `phases/` - Step-by-step phase guides
- `philosophy/` - Underlying principles

## Remember

**Documentation first.** If it's not documented, it doesn't exist.

**Retcon, don't predict.** Write as if the feature already exists.

**One source of truth.** Delete duplicates, don't update them.
"""


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
    """クレジット表記を追加"""
    # YAMLフロントマターがある場合はその後に挿入
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return f"---{parts[1]}---\n\n{CREDIT_COMMENT}{parts[2].lstrip()}"
    # フロントマターがない場合は先頭に追加
    return CREDIT_COMMENT + content


def update_frontmatter_name(content: str, new_name: str) -> str:
    """フロントマターのname:フィールドを更新"""
    if not content.startswith("---"):
        return content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return content

    frontmatter = parts[1]
    # name: を置換
    frontmatter = re.sub(r"^name:\s*.*$", f"name: {new_name}", frontmatter, flags=re.MULTILINE)

    return f"---{frontmatter}---{parts[2]}"


def convert_agents_to_commands(source_dir: Path, dry_run: bool = False) -> list[Path]:
    """agents/ → commands/ に変換（フラット構造）"""
    agents_dir = source_dir / "agents"
    commands_dir = PLUGIN_ROOT / "commands"

    if not agents_dir.exists():
        raise FileNotFoundError(f"agents directory not found: {agents_dir}")

    converted = []
    for agent_file, command_file in AGENT_TO_COMMAND.items():
        source_path = agents_dir / agent_file
        target_path = commands_dir / command_file

        if not source_path.exists():
            print(f"  WARNING: {source_path} not found, skipping")
            continue

        content = source_path.read_text()
        content = transform_references(content)
        content = inject_credit(content)

        # フロントマターのnameをファイル名に合わせる（サジェスト用）
        command_name = command_file.replace(".md", "")
        content = update_frontmatter_name(content, command_name)

        if dry_run:
            print(f"  [DRY-RUN] Would create: {target_path}")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content)
            print(f"  Created: {target_path}")

        converted.append(target_path)

    return converted


def copy_context_to_skills(source_dir: Path, dry_run: bool = False) -> list[Path]:
    """context/ → skills/ddd-guide/references/ にコピー"""
    context_dir = source_dir / "context"
    references_dir = PLUGIN_ROOT / "skills" / "ddd-guide" / "references"

    if not context_dir.exists():
        raise FileNotFoundError(f"context directory not found: {context_dir}")

    copied = []
    for md_file in context_dir.rglob("*.md"):
        relative_path = md_file.relative_to(context_dir)
        target_path = references_dir / relative_path

        content = md_file.read_text()
        content = transform_references(content)
        content = inject_credit(content)

        if dry_run:
            print(f"  [DRY-RUN] Would create: {target_path}")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content)
            print(f"  Created: {target_path}")

        copied.append(target_path)

    return copied


def generate_skill_md(dry_run: bool = False) -> Path:
    """SKILL.md を生成"""
    skill_path = PLUGIN_ROOT / "skills" / "ddd-guide" / "SKILL.md"

    if dry_run:
        print(f"  [DRY-RUN] Would create: {skill_path}")
    else:
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(SKILL_MD_TEMPLATE)
        print(f"  Created: {skill_path}")

    return skill_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync DDD collection to amplifier-skills-plugin")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    print("=" * 60)
    print("DDD Collection Sync")
    print("=" * 60)

    # 一時ディレクトリにクローン
    with tempfile.TemporaryDirectory() as tmp_dir:
        source_dir = clone_upstream(Path(tmp_dir) / "ddd")

        print("\n[1/3] Converting agents to commands...")
        convert_agents_to_commands(source_dir, dry_run=args.dry_run)

        print("\n[2/3] Copying context to skills...")
        copy_context_to_skills(source_dir, dry_run=args.dry_run)

        print("\n[3/3] Generating SKILL.md...")
        generate_skill_md(dry_run=args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN complete. No files were modified.")
    else:
        print("Sync complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
