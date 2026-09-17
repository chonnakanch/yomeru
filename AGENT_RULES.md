# Agent Execution Rules & Coding Protocol

You are an AI developer agent tasked with building the application incrementally. Adhere strictly to the execution rules, testing standards, and dependency protocols outlined below.

---

## 1. Phased Execution Protocol

1. **Sequential Implementation:** Work strictly one phase at a time following `plan.md` and the designated phase specification (e.g., `phase-1.md`). Do not write code, setup configurations, or prepare assets for future phases.
2. **Phase Boundary Enforcement:** A phase is considered complete ONLY when all code is implemented, unit tests pass, integration tests pass, and manual verification steps are satisfied.
3. **Phase Sign-Off:** Before moving to the next phase, summarize the completed phase, report test results, and request confirmation from the user to proceed to the next phase.

---

## 2. Testing Requirements (Mandatory)

Every phase must include automated test coverage before being marked complete.

### A. Unit Testing
* **Requirement:** Write unit tests for all individual functions, service modules, classes, and UI components.
* **Scope:** Test edge cases, invalid inputs, failure states, data transformations, and isolated business logic.
* **Mocking:** Mock external network calls, system drivers, and heavy ML models during unit test runs to keep execution fast.

### B. Integration Testing
* **Requirement:** Write integration tests verifying communication across system boundaries.
* **Scope:**
  * **Backend:** Test full HTTP API endpoints (request payload -> pipeline -> response payload) using test clients (e.g., FastAPI `TestClient`).
  * **Frontend/IPC:** Test sidecar communication, database read/writes, and state changes across handlers.
* **Environment:** Ensure integration tests run in a clean, reproducible test environment.

### C. Definition of Done for Testing
* 100% of unit tests must pass.
* 100% of integration tests must pass.
* No test failure can be ignored, skipped, or commented out to force completion.

---

## 3. Tooling & Dependency Guardrail (Strict Approval Rule)

Before executing any terminal command, building a package, or running code:

1. **Pre-flight Dependency Check:** Check whether all required CLI tools, system packages, global binaries, or library dependencies are present in the environment (e.g., `pytest`, `uvicorn`, `cargo-tauri`, `pyinstaller`).
2. **Missing Tool Protocol:** If ANY tool, command, CLI utility, system dependency, or library package is missing:
   * **DO NOT** attempt to automatically install, run `pip install`, `npm install`, `cargo install`, or run system package managers (`brew`, `apt`, `choco`) without user approval.
   * **STOP** execution immediately.
   * **INFORM** the user clearly with the following structure:
     * **Missing Item:** The name and version of the missing tool or package.
     * **Reason Required:** Why this item is necessary for the current phase.
     * **Proposed Command:** The exact terminal command needed to install it.
   * **ASK** for explicit permission: *"Would you like me to run this installation command now?"*
3. **Wait for Confirmation:** Proceed with execution ONLY after the user explicitly approves the installation.

---

## 4. Code Quality & Error Handling

* **Fail Fast:** Handle errors explicitly. Do not use blank `except:` blocks or swallow errors silently.
* **Type Safety:** Use type annotations (Python type hints, TypeScript interfaces, Rust types) across all codebases.
* **Clean Terminal Output:** Ensure test scripts and execution tasks output clear, readable error messages and assertion summaries.