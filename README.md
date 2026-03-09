# ☀️ Suncoast Agent: Local-First Multi-Tool Support Stack

A sophisticated AI agent architecture designed for secure, local-first customer support automation. Built using **LangGraph**, **FastAPI**, and **Docker**, utilizing a local **Ollama** engine.

## 🌟 Key Features
- **Stateful Multi-Tool Orchestration:** Uses LangGraph to manage complex logic flows and tool-calling branches.
- **Distributed Architecture:** Headless backend running on an Apple M4 Mac Mini, accessible via Tailscale.
- **Production-Ready Dockerization:** Containerized FastAPI backend with optimized bridge networking to host-level LLM services.
- **Local LLM Integration:** Powered by Llama 3.2 via Ollama, ensuring data privacy and zero API costs.

## 🛠️ Technical Stack
- **Orchestrator:** LangGraph
- **API Framework:** FastAPI
- **LLM Engine:** Ollama (Llama 3.2 3B)
- **Deployment:** Docker / Docker Compose
- **Language:** Python 3.9 (managed via `uv`)

## 🚦 How It Works
The agent identifies user intent (e.g., Order Status or Inventory) and dynamically invokes specialized Python tools to fetch real-time data before synthesizing a natural language response.
