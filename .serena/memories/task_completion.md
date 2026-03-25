# What To Do When a Task is Completed

1. Run CPV validation: `CLAUDE_PRIVATE_USERNAMES="emanuelesabetta" uv run --with pyyaml --with types-PyYAML python scripts/validate_plugin.py . --verbose`
2. Verify 0 issues across CRITICAL, MAJOR, MINOR levels
3. Check SKILL.md char counts stay under 4000 (MINOR threshold)
4. Commit with descriptive message
5. Push to remote: `git push origin main`
6. Update GitHub issues if applicable (close with `gh issue close`)
7. Bump version in plugin.json if features were added
