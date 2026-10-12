# Security notes

Never include credentials in an issue, pull request, report, or screenshot. For sensitive findings, contact the repository owner privately through an agreed channel; do not assume GitHub private vulnerability reporting is enabled until the owner enables it.

The standalone app has no user authentication or rate limiting. Keep it local or behind access controls. Its same-origin check does not prevent non-browser clients from accessing a publicly exposed server. The endpoint allowlist reduces URL abuse but does not establish trust in every endpoint hosted by a permitted provider.

Hugging Face tokens belong in Modal Secrets; endpoint keys are entered at runtime. The optional FastAPI starter is loopback-only by default and needs protection before public exposure. Keep dependency security updates under review. No independent security audit has been completed.
