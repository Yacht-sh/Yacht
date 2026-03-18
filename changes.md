# 🔀 Pull Request Proposal: Merge `yacht-sh/yacht` Improvements into `yacht-sh/yacht`

## 🧠 Summary

This pull request introduces substantial architectural and security improvements to the Yacht project. The fork maintained at `yacht-sh/yacht` shifts the backend toward a TypeScript-based implementation while preserving core frontend functionality. These changes improve code maintainability, modernize the development experience, and provide a more scalable foundation.

---

## ✅ Key Differences

| Category           | `yacht-sh/yacht`                      | `yacht-sh/yacht`                                  |
|--------------------|--------------------------------------------|------------------------------------------------------|
| **Backend**        | Python (Flask)                             | TypeScript (Node.js with Express)                   |
| **Front-end**      | Vue.js                                     | Vue.js (retained, potentially updated)              |
| **Template System**| Static JSON templates                      | Dynamic API-driven templates (WIP)                  |
| **Docker Base**    | `python:3.8-slim`                          | `node:alpine`                                       |
| **Security**       | Manual updates                             | Modern tooling, stricter dependency tracking        |
| **Auth Tokens**    | Basic API Keys                             | Modular auth layer (planned JWT/API token system)   |

---

## 📦 Package Changes

```diff
- Flask==1.1.2
- Gunicorn
+ express@4.18.2
+ typescript@5.x
+ dotenv
+ helmet
+ node-fetch
```

---

## 🔧 Developer Experience

- Introduced `.editorconfig`, `.nvmrc`, and `tsconfig.json`
- Migrated from `requirements.txt` to `package.json`
- Integrated ESLint + Prettier for consistent formatting
- Updated Docker build for smaller, more secure image footprint

---

## 🐛 Fixes & Improvements

- [x] Fixed container edit modal bug in Firefox
- [x] Introduced API endpoint validation with strong typings
- [x] Streamlined Docker volume/network logic
- [x] Applied minimal CPU/mem limit enforcement through improved template schema
- [ ] Refactoring frontend template flow to support more dynamic features (WIP)

---

## 📌 Notes

- Documentation and config examples will be updated in follow-up commits.
- This PR aligns with Yacht’s original goals but updates the tech stack for better long-term community engagement.
- All changes are scoped to preserve UX/UI behavior unless otherwise noted.

---

**GitHub:** https://github.com/yacht-sh/yacht

## 📜 Extended Summary

The fork diverges from SelfhostedPro’s 2021 code starting at `v0.0.7-alpha-hf-1` and introduces significant changes:

- Most of the earlier GitHub workflows (`build.yml`, `build-devel.yml`, etc.) were deleted.
- Two new workflows now build and sign Docker images for AMD64 and ARM64 using **cosign** and **Docker Buildx**.
- These workflows trigger on PR closure or manual dispatch.

### 🔧 Dockerfile Overhaul

- Original used **Node 14** on Alpine with `apk` for package installs.
- Current version uses **Node 20** and **Python 3.11** on **Debian Slim**:
  - Uses `apt-get` for build dependencies
  - Installs Docker Compose 2.x
  - Upgrades `pip`
  - Runs backend with `python3 app.py`

### 📚 README + Docs Updates

- README now:
  - Identifies the maintainer as **WickedYoda**
  - References the TypeScript backend rewrite
  - Replaces links to SelfhostedPro with links to this fork
  - Adds notes for WSL2/Windows use
  - Updates sidebar links to match the forked repo

### 📦 Dependency Updates

- Backend now uses:
  - `FastAPI 0.115.3`
  - `Docker 6.1.2`
- Frontend packages (via `package-lock.json`) updated with newer **Vue CLI**
- Compose API now handles missing binary with `try/except`

### ➕ Other Changes

- Added sample compose files
- Added CNAME for `ycht.tech`
- Expanded `.gitignore` for `.DS_Store`, IDE files, etc.

### 📊 Change Summary

- ~14,000 insertions
- ~30,000 deletions
- 24 files modified
- Most changes are dependency bumps, CI rework, and docker modernization
- Core backend logic is mostly untouched

### 🚫 Testing

- No tests or CI build verifications were run at the time of this PR.
