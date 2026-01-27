I will modify the project to ensure tests are automatically run during the build process.

### 1. Frontend Build Update
I will modify `frontend/package.json` to prepend the test runner to the build script. This ensures that `npm run build` will fail if tests fail, preventing broken builds.
- **Change**: `"build": "vite build"` → `"build": "vitest run && vite build"`

### 2. Create Unified Build Script
Since the project consists of both a backend and a frontend, I will create a root-level `build.sh` script to serve as the master build command. This script will:
1.  **Backend**: Install dependencies (`uv sync`) and run tests (`pytest`).
2.  **Frontend**: Install dependencies (`npm install`) and run the build script (which now includes tests).

This approach guarantees that "building" the project (via `./build.sh`) verifies the integrity of both the backend and frontend.

### Implementation Steps
1.  **Edit `frontend/package.json`**: Update the `build` script.
2.  **Create `build.sh`**: Write a shell script in the root directory to orchestrate the process.
3.  **Verify**: Run `./build.sh` to ensure tests run and the build completes successfully.
