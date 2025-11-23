# Kudwa Project - Technical Architecture Report

# Kudwa Financial Intelligence Platform: Technical Architecture Report

**Version:** 1.0.0 (Production Release)
**Engineering Lead:** Farah Farchoukh

---

## 1. Executive Summary
This document outlines the architectural decisions behind the Kudwa Financial Backend. The system provides a unified interface for ingesting heterogeneous financial data (QuickBooks, Rootfi) and delivering deterministic, AI-driven insights.

**Core Philosophy:** Accuracy over Generativity. In financial contexts, hallucination is unacceptable. Therefore, this system utilizes a **Text-to-SQL** approach rather than standard RAG, ensuring that all quantitative figures are calculated mathematically by the database engine, while the AI is reserved for qualitative narrative generation.

---

## 2. System Architecture

### 2.1 Hexagonal Architecture (Ports & Adapters)
The system adheres to **Clean Architecture** principles to ensure long-term maintainability and testability.
*   **Domain Layer:** Pure business entities (`TransactionDTO`) with zero external dependencies.
*   **Infrastructure Layer:** Isolated adapters for SQLite, OpenAI/Groq, and File Parsing. This allows for swapping providers (e.g., moving from SQLite to PostgreSQL) without touching business logic.
*   **Application Layer:** Service orchestrators managing data flow and transaction boundaries.

### 2.2 High-Concurrency Async I/O
Financial ingestion and LLM inference are high-latency operations. We utilized **FastAPI** with **AsyncSQLAlchemy (aiosqlite)**. This non-blocking I/O model ensures the API remains responsive even during heavy ingestion loads or long-running AI queries.

---

## 3. Artificial Intelligence Strategy

### 3.1 Deterministic Text-to-SQL Engine
We rejected vector-based RAG for financial math due to known accuracy issues. Instead, we implemented a specialized Agent:
1.  **Intent Translation:** The LLM translates natural language questions into strict SQLite syntax.
2.  **Safety Guardrails:** Generated SQL is sanitized against a blocklist (`DROP`, `DELETE`) to prevent injection.
3.  **Execution:** The database performs the aggregation (`SUM`, `AVG`, `CASE WHEN`), ensuring 100% precision.

### 3.2 Multi-Model High Availability (Circuit Breaker)
To ensure production reliability (99.9% uptime), the AI Engine implements a **Self-Healing Fallback Mechanism**:
1.  **Primary:** OpenAI GPT-3.5/4 (Standard).
2.  **Failover:** If the primary provider experiences latency, rate limits, or billing errors, the system automatically hot-swaps to **Llama 3 via Groq**.
3.  **Result:** The user experiences zero downtime, maintaining business continuity even during provider outages.

---

## 4. Data Engineering & ETL

### 4.1 Recursive "Deep Search" Parsing
Financial exports (like QuickBooks) often have unpredictable, deeply nested JSON structures. We implemented a **Recursive Heuristic Parser** that scans the JSON tree to locate transaction lists automatically, regardless of depth.

### 4.2 The Strategy Pattern
Ingestion logic is encapsulated in Strategy classes (`QuickBooksParser`, `RootfiParser`), strictly adhering to the **Open-Closed Principle**. Adding a new vendor (e.g., Xero) requires adding a single class, with no risk of regression to existing pipelines.

---

## 5. Infrastructure & Deployment
*   **Containerization:** Fully Dockerized application ensuring environment parity between Dev and Prod.
*   **CI/CD:** Automated GitHub Actions pipeline runs Pytest suites on every commit to prevent regressions.
*   **Cloud Deployment:** Hosted on Render with auto-deployment triggers.
