# Customer Support Intelligence Platform

An end-to-end AI-powered platform that analyzes customer support interactions to extract actionable insights using speech-to-text, large language models, and deterministic reasoning.

## 🔍 What This System Does
- Ingests real-world customer support audio in multiple formats (WAV, MP3, M4A, FLAC, OGG)
- Transcribes calls using Whisper
- Extracts structured insights using LLMs with robust validation
- Derives call resolution using deterministic evidence-based logic
- Stores historical data for analysis
- Presents insights through a product-style dashboard

## 🧠 Key Features
- Multimodal audio processing
- LLM-based semantic understanding
- Human-readable insight cards
- Call history exploration with filtering
- Analytics dashboard with actionable conclusions
- Clean separation of backend and frontend

## 🏗 Architecture
- **Backend:** FastAPI, SQLite, Whisper, Ollama (Phi-3)
- **Frontend:** Streamlit
- **AI Pipeline:** Speech-to-text → LLM extraction → deterministic reasoning
- **Storage:** Structured relational database

## 🚀 Use Cases
- Customer support quality monitoring
- Issue trend analysis
- Operational bottleneck detection
- Internal support analytics tooling

## 📌 Status
Fully functional prototype with production-style architecture.
