# Suggested Commands

## Validation
```bash
# Full plugin validation (CPV)
cd /tmp/ai-maestro-assistant-manager-agent
CLAUDE_PRIVATE_USERNAMES="emanuelesabetta" uv run --with pyyaml --with types-PyYAML python scripts/validate_plugin.py . --verbose
```

## Git
```bash
git config user.name "Emasoft"
git config user.email "713559+Emasoft@users.noreply.github.com"
```

## Version Bumping
```bash
uv run python scripts/bump_version.py <major|minor|patch>
```

## GitHub CLI
```bash
gh issue list --state open
gh issue create --title "..." --body "..."
gh pr create --title "..." --body "..."
```

## Python Formatting
```bash
uv run ruff format --line-length=320 scripts/
uv run ruff check scripts/
```

## Project Structure Check
```bash
find . -name "*.md" -path "*/skills/*" | head -50
wc -c skills/*/SKILL.md
```
