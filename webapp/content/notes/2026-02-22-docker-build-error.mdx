---
title: "Docker Build Error: ERR_MODULE_NOT_FOUND"
date: "2026-02-22"
tags: ["docker", "build", "vite", "nodejs", "troubleshooting"]
summary: "Explanation of why the ERR_MODULE_NOT_FOUND error occurs during Vite builds in Docker, specifically due to copy overwrites of node_modules."
---

# Docker Build Error: ERR_MODULE_NOT_FOUND

## Issue Summary

During deployment on Google Cloud Build, the Next.js/Vite frontend build step repeatedly failed with the following error:

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/app/frontend/node_modules/dist/node/cli.js' imported from /app/frontend/node_modules/.bin/vite
```

## Root Cause Analysis

The issue stems from a subtle order-of-operations conflict within the Dockerfile combined with a missing `.dockerignore` file.

Here is what was happening during the build:

1. **`Sending build context to Docker daemon 512.4MB`**: This log line indicates that Docker was transferring 500+ MB of local files to the build daemon. This massive size was because it was including the local `node_modules` folder (from the Mac host).
2. **`RUN cd frontend && npm install`**: Docker correctly installed the pure Linux dependencies inside the container's `/app/frontend/node_modules` folder.
3. **`COPY webapp/frontend/ ./frontend/`**: Immediately *after* the correct dependencies were installed, this command copied the entire local `frontend` directory from the Mac into the container.
4. **The Overwrite Conflict**: Because `node_modules` was locally present in the `webapp/frontend` folder, step 3 completely overwrote the fresh Linux `node_modules` generated in step 2 with the Mac-specific `node_modules`.

### Why specifically `vite`?

When packages like `vite` or `esbuild` are installed, npm downloads binary executables that are specifically compiled for the host operating system (e.g., Mac ARM64 vs. Linux x64). Furthermore, the `.bin/vite` file is a symlink that points to a specific internal path. When the Mac's `node_modules` (containing Mac symlinks and Mac binaries) overwrote the Linux container's `node_modules`, the symlinks broke, causing the `ERR_MODULE_NOT_FOUND` error.

## Resolution

The fix was to explicitly prevent the local `node_modules` from ever entering the Docker build context by using a `.dockerignore` file.

Created a `.dockerignore` file at the root of the project with the following content:

```bash
# Ignore local npm dependencies
**/node_modules

# Ignore git directory
.git
**/.git

# Ignore build artifacts pointing to local paths
**/dist
**/build

# Ignore local environment files
**/.env
**/.env.local
**/.env.*.local

# Ignore macOS files
**/.DS_Store
```

### Benefits of the Fix

1. **Successful Builds**: The container now retains its freshly built, OS-correct `node_modules` without them being overwritten in subsequent `COPY` steps.
2. **Drastically Faster Uploads**: The build context sent to the Docker daemon drops from >500MB to just a few megabytes, dramatically speeding up the start time of the build process.
