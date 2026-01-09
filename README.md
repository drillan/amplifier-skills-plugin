# amplifier-skills-plugin

Amplifier design philosophy, development skills, and Document-Driven Development (DDD) workflow for Claude Code.

## Installation

### For Development/Testing

Load the plugin directly when starting Claude Code:

```bash
claude --plugin-dir /path/to/amplifier-skills-plugin
```

Multiple plugins can be loaded simultaneously:

```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

**Note**: Changes to the plugin require restarting Claude Code to take effect.

### From GitHub

```bash
# 1. Add marketplace (first time only)
claude plugin marketplace add drillan/amplifier-skills-plugin

# 2. Install plugin
claude plugin install amplifier-skills
```

### Reinstall / Update

```bash
# Uninstall existing plugin
claude plugin uninstall amplifier-skills

# Update marketplace
claude plugin marketplace update drillan/amplifier-skills-plugin

# Reinstall plugin
claude plugin install amplifier-skills
```

## Skills

| Skill | Description |
|-------|-------------|
| amplifier-philosophy | Amplifier design philosophy using Linux kernel metaphor |
| module-development | Guide for creating new Amplifier modules |
| ddd-guide | Document-Driven Development workflow guide |

## DDD Commands

Document-Driven Development workflow commands for systematic feature implementation.

| Command | Phase | Description |
|---------|-------|-------------|
| `/amplifier-skills:ddd-1-plan` | 0-1 | Planning and design |
| `/amplifier-skills:ddd-2-docs` | 2 | Documentation retcon |
| `/amplifier-skills:ddd-3-code-plan` | 3 | Code implementation planning |
| `/amplifier-skills:ddd-4-code` | 4-5 | Implementation and testing |
| `/amplifier-skills:ddd-5-finish` | 6 | Finalization and cleanup |

### DDD Workflow

```
/amplifier-skills:ddd-1-plan "Add feature X"
  ↓ Creates ai_working/ddd/plan.md
/amplifier-skills:ddd-2-docs
  ↓ Updates documentation
/amplifier-skills:ddd-3-code-plan
  ↓ Creates ai_working/ddd/code_plan.md
/amplifier-skills:ddd-4-code
  ↓ Implements code
/amplifier-skills:ddd-5-finish
  ↓ Tests and commits
```

## Sources

This plugin includes content from:

- [microsoft/amplifier-module-tool-skills](https://github.com/microsoft/amplifier-module-tool-skills) - Amplifier skills
- [robotdad/amplifier-collection-ddd](https://github.com/robotdad/amplifier-collection-ddd) - DDD workflow

## Development

### Sync DDD from upstream

Manual sync:

```bash
python scripts/sync_ddd.py
```

Automated sync via GitHub Actions runs weekly (Monday 18:00 JST) or can be triggered manually from the Actions tab.

### Testing

```bash
claude --plugin-dir .
```

Then verify:
- `/help` shows plugin commands under custom-commands tab
- Skills are loadable
- DDD commands work (e.g., `/amplifier-skills:ddd-1-plan`)

## License

MIT
