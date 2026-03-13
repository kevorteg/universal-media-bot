# Vulnerability Disclosure Policy (VDP)

Security and system integrity are paramount at **UMO-Core**. We welcome security researchers to audit our codebase.

---

## 1. Responsible Disclosure
If you identify a security flaw (e.g., credential exposure, SQL injection, unauthorized RCE), please do not disclose it publicly.
- **Reporting Channel**: Open a confidential Issue tagged as `SECURITY-AUDIT` or contact the maintainer directly.

## 2. Audit Scope
- Media discovery API handling.
- Database persistence layer.
- Web Admin Dashboard (XSS/CSRF).

## 3. Out of Scope
- Misconfiguration of local `.env` files by users.
- Third-party dependency vulnerabilities (upstream issues).

## 4. Remediation Timeline
Our Red Team will acknowledge the report within 48 hours and provide a remediation ETA.

---
**Thank you for securing the Media Orchestrator.**
