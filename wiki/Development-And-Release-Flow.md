# Development And Release Flow

## Branch Roles

- `master` is the default branch and production-oriented release line.
- `develop` is the integration branch for ongoing dependency, workflow, and feature work.

## Expected Flow

1. Start feature or maintenance work from `develop`.
2. Push that work on a topic branch.
3. Open a PR into `develop`.
4. After `develop` is verified, open or update the `develop -> master` PR.

## Protected Branch Notes

- `develop` is protected.
- Do not assume you can force-push rebased history back to `develop`.
- If you rebase locally for cleanup, you may still need to merge the current `origin/develop` tip back in before the final push can succeed as a normal fast-forward update.

## PR Integration Notes

When merging multiple dependency PRs into `develop`:

- merge the PR branches into `develop`
- run verification immediately after the merge set
- keep the merge history if it helps preserve the audit trail for which PRs were absorbed
- make one follow-up compatibility commit if the merged dependency set needs corrective pins

## Current Release Notes Worth Remembering

- the main image publish workflow now targets `linux/amd64` and `linux/arm64`
- `linux/arm/v7` was removed from the main image publish path because it required unsupported dependency build work for this branch
