# Incident Triage Copilot

A multimodal emergency call & incident triage dashboard. Ingests audio calls,
SMS texts, and scene photos; masks PII before anything reaches a cloud LLM;
extracts structured incident data; and runs a deterministic rule-based
urgency classifier to auto-populate dispatch cards.

```
Audio / SMS / Photo -> STT + Vision -> PII masking -> Extraction LLM
                                                              |
                                                              v
                                          Rule-based urgency classifier
                                                              |
                                                              v
                                                  Dispatch dashboard
```

## Why it's built this way

- **The urgency classifier is deterministic, not an LLM call.** The
  extraction LLM only fills in a fixed set of structured fields (location,
  injury severity, hazard flags). A plain rule table then maps those fields
  to Category 1/2/3 -- so sorting is predictable, testable, and explainable.
  Every dispatch card shows exactly which rule fired.
- **PII masking happens before extraction**, not after -- phone numbers,
  emails, and stated names are regex-redacted before the masked text is
  sent to any LLM.
- **Two run modes.** `MOCK_MODE=true` (the default) needs no API keys, no
  internet access, and no audio/vision models -- every step returns
  realistic canned data so you can demo and test the whole pipeline
  instantly. Flip to `MOCK_MODE=false` and add a Groq API key to run real
  Whisper transcription and real LLM extraction/vision.

## Project layout

```
backend/
  app/
    main.py          FastAPI app + routers
    config.py         Settings (reads .env)
    models.py         Pydantic schemas (IncidentEntities, DispatchCard, ...)
    routers/           audio.py, sms.py, photo.py, dashboard.py
    services/
      stt.py           faster-whisper speech-to-text (+ mock)
      vision.py        Groq vision captioning (+ mock)
      extraction.py    Groq LLM -> structured IncidentEntities (+ mock)
      pii.py           regex-based PII masking guardrail
      classifier.py    deterministic urgency scoring engine
      pipeline.py      wires the above together in order
      store.py         in-memory dispatch card store
  tests/
    test_classifier.py
    test_pii.py
  requirements.txt
  .env.example
frontend/
  src/
    App.jsx, api.js, styles.css
    components/DispatchCard.jsx, PriorityBadge.jsx, UploadPanel.jsx
  package.json
```

## Setup (Windows / PowerShell + conda)

### Backend

```powershell
cd backend
conda create -n triage-copilot python=3.11 -y
conda activate triage-copilot
pip install -r requirements.txt
copy .env.example .env
# .env defaults to MOCK_MODE=true, so it runs with no API key needed
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs.

To run with real models: set `MOCK_MODE=false` in `.env` and add your
`GROQ_API_KEY` (free at https://console.groq.com). faster-whisper will
download the `small` model automatically on first use.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Type an SMS message, or upload an audio/photo
file, and watch a dispatch card appear with its priority category and the
rules that triggered it.

### Tests

```powershell
cd backend
pytest tests/ -v
```

10 unit tests cover the classifier (every category boundary, and that
Category 1 always wins over Category 2 signals) and the PII masker (phone
numbers, emails, stated names, and that clean text is left untouched).

## Extending this

- **Real-time streaming audio**: replace the batch `/api/audio` upload with
  a websocket endpoint that feeds rolling audio chunks into faster-whisper's
  streaming API, emitting partial transcripts to the dashboard as they
  arrive.
- **Better name redaction**: swap the regex name-matcher in `pii.py` for a
  proper NER model (e.g. Microsoft Presidio) for free-text name detection.
- **Persistence**: swap `services/store.py`'s in-memory list for Postgres or
  Redis -- no other file needs to change, since routers only call
  `add_card` / `list_cards`.
- **Eval set**: build a small labeled set of sample calls/photos and assert
  the extraction + classifier pipeline produces the expected category for
  each -- this is the single strongest thing to show evaluators, since it
  proves the safety-critical sorting logic actually works.
