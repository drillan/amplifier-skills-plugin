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

### From Marketplace (将来)

```bash
claude plugin install amplifier-skills@drillan
```

## Skills

| Skill | Description |
|-------|-------------|
| amplifier-philosophy | Amplifier design philosophy using Linux kernel metaphor |
| module-development | Guide for creating new Amplifier modules |
| python-standards | Python coding standards for Amplifier |
| ddd-guide | Document-Driven Development workflow guide |

## DDD Commands

Document-Driven Development workflow commands for systematic feature implementation.

| Command | Phase | Description |
|---------|-------|-------------|
| `/amplifier-skills:ddd:1-plan` | 0-1 | Planning and design |
| `/amplifier-skills:ddd:2-docs` | 2 | Documentation retcon |
| `/amplifier-skills:ddd:3-code-plan` | 3 | Code implementation planning |
| `/amplifier-skills:ddd:4-code` | 4-5 | Implementation and testing |
| `/amplifier-skills:ddd:5-finish` | 6 | Finalization and cleanup |

### DDD Workflow

```
/amplifier-skills:ddd:1-plan "Add feature X"
  ↓ Creates ai_working/ddd/plan.md
/amplifier-skills:ddd:2-docs
  ↓ Updates documentation
/amplifier-skills:ddd:3-code-plan
  ↓ Creates ai_working/ddd/code_plan.md
/amplifier-skills:ddd:4-code
  ↓ Implements code
/amplifier-skills:ddd:5-finish
  ↓ Tests and commits
```

## Sources

This plugin includes content from:

- [microsoft/amplifier-module-tool-skills](https://github.com/microsoft/amplifier-module-tool-skills) - Amplifier skills
- [robotdad/amplifier-collection-ddd](https://github.com/robotdad/amplifier-collection-ddd) - DDD workflow

## Development

### Sync DDD from upstream

```bash
uv run python scripts/sync_ddd.py
```

### Testing

```bash
claude --plugin-dir .
```

Then verify:
- `/help` shows plugin commands under custom-commands tab
- Skills are loadable
- DDD commands work (e.g., `/amplifier-skills:ddd:1-plan`)

## License

MIT
