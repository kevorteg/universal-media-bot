# Universal Media Orchestrator (UMO-Core)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![qBittorrent](https://img.shields.io/badge/Client-qBittorrent-lightgrey?logo=qbittorrent&logoColor=white)](https://www.qbittorrent.org/)
[![TMDB](https://img.shields.io/badge/Data%20Source-TMDB-01d277?logo=themoviedb&logoColor=white)](https://www.themoviedb.org/)
[![Red Team](https://img.shields.io/badge/Audited%20by-Red%20Team-red?logo=target&logoColor=white)](#)
## Table of Contents
- [Technical Overview](#technical-overview)
- [System Architecture](#system-architecture)
- [Core Capabilities](#core-capabilities)
- [Deployment Logic](#deployment-logic)
- [Security & Integrity](#security--integrity)
- [Roadmap](#engineering-roadmap)

---

## Technical Overview
UMO-Core is a high-performance media discovery and ingestion pipeline designed for autonomous operation. It leverages heuristic search algorithms and asynchronous task orchestration to manage large-scale media libraries.

---

## System Architecture

| Component | Engineering Description | Technology Stack |
| :--- | :--- | :--- |
| **Discovery Engine** | Heuristic trend analysis via TMDB API endpoints. | Python / Requests / JSON |
| **Ingestion Pipeline** | Multi-threaded task queuing for concurrent media processing. | Concurrent.Futures / yt-dlp |
| **Persistence Layer** | Relational data mapping for persistent state tracking. | SQLite3 / Thread-Safe Locks |
| **Remote Orchestrator** | API-driven command & control via qBittorrent Web UI. | qbittorrent-api v2.0+ |
| **Control Interface** | Glassmorphic management dashboard for real-time telemetry. | HTML5 / CSS3 / Flask-Jinja2 |

---

## Core Capabilities

<details>
<summary><b>[+] Autonomous Media Discovery (Discovery V2)</b></summary>
The system implements a polling mechanism that queries global trending endpoints. It applies content filters and genre-specific masks to prioritize high-value assets for internal ingestion.
</details>

<details>
<summary><b>[+] Asynchronous Torrent Routing</b></summary>
Incoming magnet links are validated and dispatched to the qBittorrent RPC interface. The orchestrator monitors the peer-to-peer state and updates the central database via event-driven hooks.
</details>

<details>
<summary><b>[+] Metadata Enrichment & Normalization</b></summary>
Automatically scrapes TMDB for poster assets and production metadata to ensure a normalized data structure across the library.
</details>

---

## Deployment Logic

### Phase 1: Dependency Provisioning
The system requires the following binary environments:
- **Python v3.10+**: [python.org/downloads](https://www.python.org/downloads/)
- **qBittorrent (Web UI enabled)**: [qbittorrent.org/download](https://www.qbittorrent.org/download.php)
- **FFmpeg Engine**: [ffmpeg.org/download](https://ffmpeg.org/download.html)

Initialize the virtual environment and install the required dependency tree:
```bash
python -m venv venv
source venv/bin/activate  # atau .\venv\Scripts\activate pada Windows
pip install -r requirements.txt
```

### Phase 2: Credential Acquisition & Injection
To interface with global media databases, you must provision the following tokens:

#### 1. TMDB API Access (Discovery Layer)
- **Endpoint**: [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
- **Protocol**: Create a developer account and generate a v3 API Key to populate `TMDB_API_KEY`.

#### 2. qBittorrent RPC (Ingestion Layer)
- Ensure **Web UI** is active in `Tools -> Options -> Web UI`.
- Map your local host and credentials to the `.env` container:
```bash
# Core API Access
TMDB_API_KEY=your_secured_token
# Torrent RPC Credentials
QB_URL=http://127.0.0.1:8080
QB_USER=admin
QB_PASS=adminadmin
```

### Phase 3: Runtime Execution
Execute the master orchestrator to initiate the command-line interface:
```bash
python main.py
```

---

## Security & Integrity
The system is architected with a strict `.gitignore` policy to prevent sensitive credential leakage. The persistence layer utilizes thread-locking mechanisms to prevent race conditions during high-concurrency ingestion cycles.

**[!] Disclaimer:** This tool is designed for educational purposes and personal media management. Ensure compliance with local data regulations.

---

## Engineering Roadmap
The following modules are scheduled for upcoming development cycles:
- **[ ] AI-Synced Subtitles**: Deep learning models for automatic subtitle synchronization.
- **[ ] Plex/Jellyfin Integration**: Direct export of metadata to media server formats.
- **[ ] Multi-Tenant Auth**: Role-based access control (RBAC) for the Web Dashboard.
- **[ ] P2P Health Monitoring**: Advanced metrics for tracker and peer health.
- **[ ] Distributed Ingestion**: Multi-node support for high-throughput downloads.

---
**Build Status:** `STABLE` | **Deployment Model:** `EDGE` | **Architecture:** `MONOLITHIC-ORCHESTRATOR`
