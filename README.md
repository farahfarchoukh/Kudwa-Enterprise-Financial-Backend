# Kudwa Financial Intelligence Engine (Enterprise Edition)

# Kudwa Financial Intelligence Engine

**A Production-grade AI Platform for Financial Data Integration & Analysis.**

![Status](https://img.shields.io/badge/Status-Live-success?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-Passing-green?style=flat-square)
![Architecture](https://img.shields.io/badge/Arch-Hexagonal-blue?style=flat-square)

##  Live Demo
**[Access the Live Swagger API Here](https://kudwa-financial-api.onrender.com/docs)**
*(Note: Hosted on Render Free Tier. Please allow 30-50s for cold start if inactive).*

---

##  Key Capabilities
1.  **Universal Ingestion:** recursively parses complex, nested financial JSONs (QuickBooks/Rootfi).
2.  **Intelligent Analysis:** Uses **Text-to-SQL** to answer questions like *"What is the profit margin for Q1?"* with 100% mathematical accuracy.
3.  **Self-Healing AI:** Features a **Circuit Breaker** that automatically switches between **OpenAI** and **Llama 3 (Groq)** to ensure uptime during API outages.

---

##  Setup & Installation

### Option A: Docker (Recommended)
```bash
# 1. Configure Secrets
echo "OPENAI_API_KEY=sk-..." > .env
echo "GROQ_API_KEY=gsk_..." >> .env
echo "ADMIN_API_KEY=secret123" >> .env
echo "DATABASE_URL=sqlite+aiosqlite:///./financial.db" >> .env

# 2. Run
docker-compose up --build
