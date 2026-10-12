# Deploy AtlasLaunch on Northflank

This deployment hosts the Next.js interface and its `/api/infer` proxy in one CPU service. N-ATLaS stays on the existing Modal GPU endpoint. No database or Hugging Face token is needed in the web service.

## Service settings

| Setting | Value |
| --- | --- |
| Repository | `pmman-sudo/atlaslaunch` |
| Branch | `master` |
| Build type | Dockerfile / BuildKit |
| Build context | `/` |
| Dockerfile | `/Dockerfile` |
| Runtime port | `3000`, HTTP, public HTTPS ingress |
| Runtime command override | None; use the image command |
| Runtime variables | `PORT=3000`, `HOSTNAME=0.0.0.0` (also set in image) |
| Health check | HTTP GET `/health` on port 3000 |

Use the existing free service allocation; a build or runtime resource upgrade can cost money and is a separate decision. The Docker build needs more memory than the idle web app. Runtime memory suitability must be confirmed from the deployment's actual logs and metrics.

The health route checks only the web application, not Modal GPU readiness. Do not use inference as a platform health check: that would repeatedly start or bill the GPU.

## Replacing the old DrainWatch service

The existing Northflank project `drainwatch` also contains `aidledger-api` and `drainwatch-db`. Replace only the `drainwatch-api` service source/settings. Do not delete the whole project or its database. Preserve the former source reference and service configuration for rollback. Remove DrainWatch-specific database/environment links from the replacement service without deleting the underlying shared secrets or database.

Disable automatic deployment while changing source/build/port settings, then build the intended AtlasLaunch commit and deploy it. Re-enable automatic deployment only after the replacement settings are complete. Keeping the existing service ID preserves its generated hostname; a display-name change does not necessarily change the ID or hostname.

## After the deployment is healthy

1. Open the service's HTTPS URL and verify the AtlasLaunch home page and starter downloads.
2. Use Local fixture to exercise prompts and export without GPU calls.
3. For a live test, select Live endpoint, use OpenAI-compatible chat and model `NCAIR1/N-ATLaS`, and enter the Modal endpoint URL and endpoint API key in the app. The key is held in tab memory, sent through the web server to Modal, and omitted from reports.
4. Export results before refreshing. This app has no result database or import feature.

The standalone application has no built-in login or request quotas. Use Northflank access controls for a restricted tester deployment; hosting it does not inherit the ChatGPT site's private-access controls. Keep keys out of build arguments, images, GitHub, public browser configuration, and request logs. See SECURITY.md before opening access more widely.

## Rollback

Switch to the previous DrainWatch image and restore the recorded source, environment links, command, health-check, and port settings. A source change does not erase the old repository or database. The old DrainWatch frontend will stop serving its original API workflows while this service is running AtlasLaunch.

References: [Northflank deployment guide](https://northflank.com/docs/v1/application/getting-started/build-and-deploy-your-code), [Next.js standalone output](https://nextjs.org/docs/app/api-reference/config/next-config-js/output).
