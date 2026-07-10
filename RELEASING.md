# Releasing (maintainer notes)

## Pre-launch checklist (Day 8–9)
- [ ] LICENSE = full AGPL-3.0 text (Affero, not plain GPL!)
- [ ] Tests green: `python -m pytest tests/`
- [ ] `pip install -e ".[cli]" && quorum demo` works from a fresh clone
- [ ] README GIF present + renders on GitHub
- [ ] Repo social-preview image set (Settings → Social preview)
- [ ] Topics set; good-first-issue labels created (see below)
- [ ] Hosted demo off free tier; LLM spend cap set; QUORUM_BACKEND=mock fallback tested

## PyPI publish (makes `pip install quorum-council` real)
One-time: create account at pypi.org → enable 2FA → create API token.
```bash
python -m pip install build twine --upgrade
python -m build                    # dist/quorum_ai-0.1.0*.whl + .tar.gz
python -m twine upload dist/*      # paste PyPI token
```
Then tag:
```bash
git tag v0.1.0 && git push origin v0.1.0
```
GitHub → Releases → Draft new release → v0.1.0 → paste highlights from BUILDLOG.

## Good-first-issues to create before launch
1. "Add a relocation council" (YAML only, link CONTRIBUTING §1)
2. "Add a grad-school council" (YAML only)
3. "i18n: add Spanish disclaimers" (i18n.py)
4. "CLI: --output markdown flag for verdicts"
5. "Docs: translate FAQ to 中文"

## Post-spike guardrails
- Issue templates funnel: bug / new council / transcript report
- Respond to first-day issues in hours; label fast; thank everyone
- If API spend spikes: set QUORUM_BACKEND=mock on the hosted demo (stays interactive)
