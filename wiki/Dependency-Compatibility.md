# Dependency Compatibility

This page records the dependency decisions that currently keep `develop` working.

## Backend

Current noteworthy backend pins from [`../backend/requirements.txt`](../backend/requirements.txt):

- `fastapi==0.120.4`
- `pydantic==1.10.22`
- `aiostream==0.7.1`
- `idna==3.11`
- `makefun==1.16.0`
- `pycparser==3.0`
- `cryptography==46.0.6`

### Important Rule

`fastapi` is intentionally pinned to `0.120.4` because the current backend remains on Pydantic v1.

Do not bump FastAPI independently unless you are also doing the backend migration required for newer Pydantic expectations and verifying the entire API/auth stack.

## Frontend

Current noteworthy frontend versions from [`../frontend/package.json`](../frontend/package.json):

- `vue: ^2.7.16`
- `vuetify: ^2.7.2`
- `vue-chartjs: ^3.5.1`
- `@mdi/font: ^7.4.47`
- `sass: ^1.98.0`
- `@vue/eslint-config-prettier: ^6.0.0`
- `prettier: ^1.19.1`

### Important Rules

- keep `vue-chartjs` on the Vue 2 compatible line
- keep `@vue/eslint-config-prettier` on the ESLint 6 compatible line
- do not assume grouped frontend dependency PRs are safe to merge without verification, especially when they touch Vue, Vuetify, ESLint, or formatting tooling

## How To Handle Future Dependency PRs

1. Merge or cherry-pick the dependency PR into a topic branch off `develop`.
2. Run the verification commands from the runbook.
3. If the update is incompatible:
   - keep the merge history if desired
   - add a follow-up compatibility commit that restores the known-good version
   - document the reason here

This approach keeps the repo history honest while preserving a working branch.
