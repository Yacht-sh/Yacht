# Dependency Compatibility

This page records dependency pins and integration constraints that affect the current Docker build and application runtime. Exact backend versions are pinned in [`../backend/requirements.txt`](../backend/requirements.txt); frontend ranges are declared in [`../frontend/package.json`](../frontend/package.json) and resolved by `package-lock.json`.

## Backend

The Docker image uses Node `26` for the Vue build and Python `3.15.2` for both Python stages.

### FastAPI and JWT

- `fastapi==0.165.0`, `pydantic==2.14.4`, and `pydantic-settings==2.16.3` form the current Pydantic v2 stack. Upgrade and validate them together with the routers and settings.
- `libre-fastapi-jwt==0.23.1` exposes asynchronous validation and subject-reading methods. Keep calls to `jwt_required()`, `jwt_refresh_token_required()`, and `get_jwt_subject()` awaited. For synchronous route handlers, run authentication through FastAPI's async `Depends(auth_check)` dependency rather than calling it directly.
- Token creation and cookie-setting calls are synchronous in the current integration; do not add `await` to them without checking the library API.

### Password hashing

- The application pairs `passlib==1.7.4` with `bcrypt==4.3.0`. Do not upgrade bcrypt to 5.x without also replacing or upgrading Passlib: Passlib's backend self-test uses a 255-byte probe that bcrypt 5 rejects. Bcrypt 4.3 removes `bcrypt.__about__`, so Passlib may emit a trapped version-probe warning; verify actual hash/verify behavior when changing either dependency.
- Passlib 1.7.4 also imports `pkg_resources`. The Docker wheel-builder and runtime stages both install `setuptools<81`, because newer Setuptools releases no longer provide that module. A deprecation warning for `pkg_resources` may still appear.

### Docker and SSE streams

- `aiodocker==0.27.0` and `aiostream==0.8.2` are used for container log and statistics streams. Keep Docker clients context-managed and explicitly close nested stream iterators when an SSE connection ends.
- The app-specific statistics route uses `stat_generator` from `api.actions.apps_runtime`; `api.actions.apps` must re-export it for the router.

## Frontend

- The frontend remains on Vue 2 (`vue: ^2.7.16`) and Vuetify 2 (`vuetify: ^2.6.15`). Keep Vue 2 integrations such as `vue-chartjs: ^3.5.1` on Vue 2-compatible releases.
- `vuetify-loader` is not installed. The Vuetify plugin therefore imports the full `vuetify` build and `vuetify/dist/vuetify.min.css` so Vuetify components render. If switching back to the tree-shakeable `vuetify/lib` entry, add and lock a compatible loader and verify all components are registered.
- Linting uses ESLint 10's flat config in [`../frontend/eslint.config.mjs`](../frontend/eslint.config.mjs), with `@eslint/js` 10, `eslint-plugin-vue` 10, `vue-eslint-parser` 10, and Prettier 3 plus `eslint-plugin-prettier` 5. Keep the Vue 2 preset (`flat/vue2-essential`); the default Vue 3 preset reports Vue 2 syntax as deprecated.
- The lint config allows Vue 2/Vuetify conventions used by this codebase, including dotted slot-name modifiers. Prettier and some Vue convention rules are warnings so existing formatting and component naming do not fail lint.
- Use `npm run lint` for the frontend lint check. Do not restore the removed legacy `.eslintrc.js` or `@vue/cli-plugin-eslint`; ESLint 10 expects flat config.
- Axios requests use cookies for JWT authentication. An unauthenticated `/auth/me` check can return 401 before login; that response is expected when no access cookie is present.

## Future Dependency Updates

1. Apply dependency updates on a topic branch and review both manifest and lockfile changes.
2. Run the checks in the [verification runbook](./Verification-Runbook.md), including a Docker build.
3. Exercise login, token refresh, password hash/verify, and app log/stat SSE flows when changing the related backend dependencies.
4. Record any new compatibility constraint here, with the affected versions and the behavior it protects.
