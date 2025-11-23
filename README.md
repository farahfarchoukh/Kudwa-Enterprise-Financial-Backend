# Kudwa Financial Intelligence Engine (Enterprise Edition)

**Production-grade Async API for Heterogeneous Financial Data Integration & AI Analysis**

![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=flat-square)
![Coverage](https://img.shields.io/badge/Tests-Passing-success?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20|%20AsyncSQLAlchemy%20|%20Docker-blue?style=flat-square)

## Project Overview

This system solves the challenge of unifying fragmented financial data (QuickBooks vs. Rootfi) into a single source of truth, enriched by a deterministic AI layer (Text-to-SQL) for 100% accurate financial insights.

### Architectural Decisions

1.  **Hexagonal Architecture (Clean Arch)**:
    *   **Domain Layer** (`src/domain`): Pure business entities (Pydantic/SQLAlchemy). Zero dependencies on external frameworks.
    *   **Infrastructure** (`src/infrastructure`): Isolated adapters for OpenAI, SQLite, and File Parsers.
    *   **Application** (`src/app`): Service layer orchestrating the flow.

2.  **Strategy Pattern for Ingestion**:
    *   Data parsing logic is encapsulated in strategies (`QuickBooksParser`, `RootfiParser`).
    *   **Why?** Adheres to the **Open-Closed Principle**. Adding a new vendor (e.g., Xero) requires adding 1 class, not rewriting the service.

3.  **Async I/O Concurrency**:
    *   Built on **FastAPI** + **aiosqlite**.
    *   **Why?** Financial ingestion and AI inference are I/O bound. Blocking code would cripple the API under load. Async allows high throughput.

4.  **AI Reliability (Text-to-SQL)**:
    *   We reject "Chat with PDF" (RAG) for math. It hallucinates.
    *   We use **Text-to-SQL**. The LLM translates *Intent* -> *SQL*. The Database performs the *Math*.
    *   **Result**: Zero arithmetic hallucinations.

---

## Setup & Installation

### Option A: Docker (Production Ready)
The system is fully containerized.

```bash
# 1. Add secrets (Create .env file)
echo "OPENAI_API_KEY=sk-..." > .env
echo "ADMIN_API_KEY=secret123" >> .env
echo "DATABASE_URL=sqlite+aiosqlite:///./financial.db" >> .env

# 2. Boot up
docker-compose up --build