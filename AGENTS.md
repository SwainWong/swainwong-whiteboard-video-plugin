# Whiteboard video plugin maintenance

- This directory is the canonical source of this independent plugin. Do not edit installed caches.
- Keep one discoverable Skill: `skills/whiteboard-video/SKILL.md`.
- The eleven recipes D01–D11 are the supported catalog. Do not resurrect the rejected stage-tour effect.
- Update README and effect contracts when public inputs or behavior change. Keep implementation detail in linked references.
- Keep scene inputs explicit. Never silently substitute the demo car or SALE for missing user content.
- Editable paths, runtime images, visual references and completed-stage snapshots are different asset roles.
- Stage overview is vertical, uses real completed frames and requires provenance; snapshots are not reconstructed invented pages.
- Workspaces, dependencies, renders and review state belong outside the installed plugin. Package via `scripts/package_plugin.py`.
- Validate with Python unittest discovery, runtime tests, fresh-workspace rendering and targeted pixel review. Tests/render/decode are not user or audiovisual acceptance.
- Keep copied assets and fonts attributed in `docs/ASSET-PROVENANCE.md`; do not bundle third-party research videos, secrets or machine paths.
