# Preparation checks

Validated locally during repository preparation, October 11–12, 2026:

- Clean dependency installation with `npm ci`: passed.
- JavaScript adapter tests: 12 passed.
- Python starter and Modal API tests: 26 passed. One upstream Starlette/httpx deprecation warning was emitted.
- `npm run typecheck`: passed, including Next.js route type generation.
- `npm run build`: passed using Next.js 16.3.4 and the Webpack build command.
- Production HTTP smoke checks: six passed (home page, invalid request, cross-origin rejection, local endpoint rejection, and two downloadable ZIPs).
- Staged source and packaged archives checked for common credential patterns and unwanted dependency/runtime files: none found.
- Included owner smoke-test report compared byte-for-byte with the supplied export: identical.

The tests use mocks and local requests; they did not make new GPU inference calls. GitHub Actions has not run yet. The standalone adaptation has not received a browser visual review or independent developer testing. The earlier owner live inference results are documented separately in EVIDENCE.md.
