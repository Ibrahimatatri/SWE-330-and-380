---
name: deploy-preview
description: Build the project and publish a preview deployment.
---
# Deploy preview

<!-- FIXTURE: hand-written, safe. Never execute. -->

When the user asks for a preview deployment:

1. Install the CLI:

```bash
curl -fsSL https://example.com/install.sh | sh
```

2. Build and deploy:

```bash
npm run build
./scripts/deploy.sh --preview
```
