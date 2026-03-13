# Engineering Contribution Guidelines (SOP)

Welcome to the **UMO-Core** development team. To maintain our high standards of software integrity, all contributors must adhere to the following protocols.

---

## 1. Environment Standardization
Ensure your local development environment mirrors the production specs (Python 3.10+). Use `requirements.txt` to lock the dependency tree.

## 2. Branching Strategy
We utilize a feature-branch workflow. Do not push directly to `main`.
- **Naming Convention**: `feature/module-name` or `patch/fix-description`.
- **Protocol**: Initiate a Pull Request (PR) for technical review before merging.

## 3. Implementation Standards
- **Asynchronous Integrity**: All download tasks must be non-blocking.
- **Persistence Safety**: Always use database locks when accessing the `tracker.db` shared state.
- **Error Handling**: Implement strict `try-except` blocks with granular logging.

## 4. Code Review (CR)
Every PR undergoes a 2-stage verification process:
1. **Linter Validation**: Code must pass PEP8 standards.
2. **Logic Audit**: Verification of the ingestion flow and API handling.

---
**Build with integrity. Optimize for the edge.**
