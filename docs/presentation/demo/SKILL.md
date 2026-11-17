---
name: deploy-preview
description: Build the project and publish a preview deployment.
allowed-tools: Bash
---
# Deploy preview

<!-- Demo file written by the team for the presentation. It is never executed. -->

Never run `rm -rf /` on a shared machine.

See https://docs.example.com/deploy for background.

1. Install the CLI:

```bash
curl -fsSL https://example.com/install.sh | sh
pip install previewer
```

2. Read the token from `.env` and export it as `$DEPLOY_TOKEN`.

3. Run `python scripts/deploy.py --preview`.
