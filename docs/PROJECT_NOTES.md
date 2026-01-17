# Project Notes

# Project Title :
Multimodal AI System for Customer Support Analytics

### What is this project?
This project analyzes customer support call recordings by converting audio into text and extracting structured insights such as sentiment, issue type, and resolution status using AI.

### Why this project?
Customer support calls contain valuable info which are difficult to analyze manually. This system automates insight extraction from unstructured raw audio data.

### What kind of AI does it use?
- Speech-to-text for audio processing (Whisper).
- Generative AI (LLM) for understanding and extracting insights.

### What is Whisper used for?
Whisper is an automatic speech recognition (ASR) system developed by OpenAI. Whisper converts raw audio recordings into text transcripts, which enables language-based analysis.

### Why Whisper?
It performs well across accents and noisy environments and does not require training.

## Whisper Integration Test
- Successfully transcribed .flac audio files from the LibriSpeech dev-clean dataset.
- Whisper (base model) produced accurate text output for short speech clips.
- CPU-based transcription is slower but acceptable for a prototype system.

# Commands to run: 
venv\Scripts\activate.bat (or) venv\Scripts\Activate.ps1
- activate.bat is a Windows batch script that activates your Python virtual environment.
python experiments/test_whisper.py

### LLM Output Validation Test
- Tested local LLM (Phi-3) using Ollama for transcript analysis.
- Successfully obtained structured JSON output from Phi-3 via Python.
- The model correctly identified sentiment, issue type, and resolution status.
- This confirms reliable use of Generative AI for insight extraction from text.

### LLM Output Reliability Issues
- Observed that LLM outputs may include explanations, markdown formatting, or malformed JSON.
- Implemented prompt constraints and output sanitization to enforce valid structured output.
- This highlights the probabilistic nature of generative models and the need for validation in AI systems.

### End-to-End Pipeline Test
- Successfully combined Whisper and LLM into a single processing pipeline.
- The system converts audio input into text and extracts structured insights using Generative AI.
- This validates the multimodal design of the project.

## Database Design
The system stores processed call data in a relational database. Each record represents a single customer support call, including the audio reference, transcript, extracted insights, and timestamp. This enables trend analysis and historical querying.

### Database Verification
- Currently using an sqlite database to store the data.
- Confirmed successful storage of transcripts and AI-generated insights.

### why sqlite?
- It is light weight relational db, more reliable and follows acid properties.
- It is easier to migrate to MySQL for better scaling in the future if required.

### Database Persistence Verified
- Verified insertion and retrieval of records from the db.
- Each records stores audio_path, transcript, ai generated insights andtimestamp.
- Confirms end-to-end data persistence for analytics and dashboard usage.

### FastAPI Backend Initialization
- Initialized FastAPI as the main application layer.
- Implemented a health check to verify server availability.

### Why FastAPI?
- It has better performance, is lightweight and easy integration with python pipelines, sqlite.

### FastAPI Multimodal Endpoint Completed
- Implemented a robust POST API endpoint to process customer support call audio.
- Integrated Whisper for speech-to-text and an LLM for structured insight extraction.
- Added JSON extraction and validation to handle non-deterministic LLM outputs.
- The endpoint successfully returns transcripts and AI-generated insights.

### Analytics Read APIs
- Implemented REST API's to retrieve stored call records and aggregate insights.
- Added summary endpoints to analyze sentiment and issue trends across customer calls.
- These APIs enable dashboard visualization and management-level insights.

### Schema Updation
- Have slightly altered the database structure for better insights extraction and visualisation.
- Newly added field:
  - sentiment
  - issue_category
  - urgency
  - agent_behavior
  - call_outcome

### Prompt Engineering Refinements
- Improved LLM prompt design using few-shot examples covering common customer support scenarios.
- Added semantic guidelines for each classification field to reduce ambiguity.
- Ensured all examples used strictly valid JSON to prevent parsing failures.
- Few-shot prompting significantly improved consistency of LLM outputs.


### Robust Handling of Non-Deterministic LLM Outputs
- Observed multiple LLM output issues including malformed JSON, missing fields, and plain-text responses.
- Implemented a layered robustness strategy:
  - JSON substring extraction from raw LLM output
  - Primary parsing using `json`
  - Fallback parsing using `json5`
  - Single controlled retry with strict JSON-only prompt
  - Deterministic fallback values to guarantee system stability


### Schema Validation Using Pydantic
- Introduced a `CallAnalysis` Pydantic model to formally define the expected output schema.
- All LLM-generated insights are validated against the model before being accepted.
- Prevents invalid or unexpected values from entering the database.
- Improves API contract clarity and FastAPI documentation automatically.

### Backend Stability and Async Safety
- Identified Whisper and LLM inference as blocking operations.
- Offloaded AI processing to background threads using `asyncio.to_thread`.
- Ensures FastAPI event loop remains responsive during heavy processing.

## Final Pipeline Stability
- `/analyze-call` endpoint now returns HTTP 200 consistently.
- The system guarantees:
  - valid structured insights
  - safe database insertion
  - resilience to LLM formatting errors
- AI pipeline and backend logic frozen after achieving stability.



## Decision to Add Frontend Layer
- After stabilizing the backend and AI pipeline, a frontend layer was planned to improve usability and demonstration.
- The frontend is intended to consume existing REST APIs without modifying backend logic.
- This separation ensures backend stability while enabling better visualization and interaction.


## Frontend Technology Selection
- Selected **Streamlit** for frontend development due to:
  - Rapid development capability
  - Minimal boilerplate
  - Native support for data visualization
- Streamlit allows quick integration with REST APIs using HTTP requests.
- The choice prioritizes clarity and demonstration over heavy UI complexity.



## Frontend Scope Definition
- Frontend responsibilities are intentionally limited to:
  - Uploading customer support call audio
  - Displaying transcription results
  - Displaying AI-extracted structured insights
  - Visualizing aggregate analytics summaries
- No authentication or advanced UI styling included to maintain simplicity.



## Backend–Frontend Integration Strategy
- Frontend communicates with backend using existing REST endpoints:
  - POST `/analyze-call`
  - GET `/calls`
  - GET `/calls/summary`
- No direct database access from the frontend.
- Backend remains the single source of truth for processing and storage.



## Incremental Development Approach
- Frontend development planned after backend stabilization to avoid repeated redeployment.
- APIs are treated as frozen contracts during frontend development.
- Any required UI changes should not introduce backend refactoring.


## Deployment Readiness Consideration
- Frontend is designed to work with both local and deployed backend instances.
- API base URL can be easily updated for deployment environments.
- This approach simplifies future cloud deployment and demonstrations.






















