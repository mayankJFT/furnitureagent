# ProVia Doors Voice Sales Agent

A voice-enabled conversational sales assistant for ProVia Doors, built with OpenAI Agents SDK and a real-time web interface.

## Features

- **Voice Interaction** - Speak naturally with auto-listen mode for hands-free conversation
- **Text-to-Speech** - Agent responds with both text and voice
- **ProVia Product Catalog** - Entry doors, storm doors, patio doors, glass options, hardware, finishes
- **Product Search** - Search by keywords, filter by features
- **Compatibility Checking** - Check hardware/glass/frame compatibility with door series
- **Energy Star & Warranty Info** - Access certification and warranty details

## Entry Door Series

- **Embarq** - Premium 2.5" thick fiberglass, highest efficiency
- **Signet** - Premium fiberglass with dovetailed construction
- **Heritage** - Mid-range fiberglass with enhanced woodgrain
- **Legacy** - Value 20-gauge steel doors

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the server

```bash
python voice_server.py
```

Or with uvicorn:

```bash
uvicorn voice_server:app --host 0.0.0.0 --port 8000
```

### 4. Open the interface

Navigate to http://localhost:8000 in Chrome or Edge (for speech recognition support).

## Voice Controls

- **Auto-Listen Mode** - Toggle for hands-free conversation
- **Microphone Button** - Click to start/stop listening
- **Stop Button** - Stop the agent from speaking
- **Quick Actions** - Pre-defined queries for common questions

## Project Structure

```
├── provia_agent.py       # ProVia sales agent with 20+ tools
├── door_catalog.py       # Product catalog loader from test.json
├── test.json             # ProVia product data
├── voice_server.py       # FastAPI WebSocket server
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment configuration
├── static/
│   └── voice_index.html  # Voice-enabled chat interface
└── README.md
```

## Example Conversations

- "Tell me about your entry door options"
- "What's the difference between Embarq and Signet?"
- "Show me decorative glass patterns"
- "What hardware works with the Signet series?"
- "Do you have Energy Star certified doors?"
- "What are the warranty options?"
- "I need a door for a coastal area"

## API Endpoints

- `GET /` - Voice chat interface
- `GET /health` - Health check
- `WS /ws/voice` - WebSocket for voice interaction
- `WS /ws/text` - WebSocket for text-only interaction
