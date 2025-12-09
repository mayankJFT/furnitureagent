"""Voice-enabled FastAPI server for ProVia Doors sales agent with streaming audio-text sync."""

import asyncio
import base64
import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI

from agents import Runner
from provia_agent import provia_agent

load_dotenv()

# Initialize OpenAI client for TTS
client = AsyncOpenAI()

# Store conversation history per connection
conversations: dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    print("ProVia Doors Voice Sales Agent starting...")
    print("Make sure OPENAI_API_KEY is set in your environment or .env file")
    yield
    print("Server shutting down...")


app = FastAPI(
    title="ProVia Doors Voice Agent",
    description="A voice-enabled conversational door sales assistant with streaming sync",
    lifespan=lifespan,
)


@app.get("/")
async def get_index():
    """Serve the main chat interface."""
    with open("static/voice_index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.websocket("/ws/text")
async def websocket_text_endpoint(websocket: WebSocket):
    """WebSocket endpoint for text-based chat."""
    await websocket.accept()
    session_id = str(id(websocket))
    conversations[session_id] = []

    try:
        # Send welcome message
        welcome_message = {
            "type": "assistant",
            "content": "Welcome to ProVia Doors! I'm your personal door consultant. I can help you find the perfect entry door, storm door, or patio door for your home. Would you like to explore our door series, or do you have specific requirements in mind?"
        }
        await websocket.send_json(welcome_message)

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            if not user_message.strip():
                continue

            # Add user message to conversation history
            conversations[session_id].append({
                "role": "user",
                "content": user_message
            })

            # Send typing indicator
            await websocket.send_json({"type": "typing", "content": True})

            try:
                # Run the agent
                result = await Runner.run(
                    provia_agent,
                    input=conversations[session_id],
                )

                # Extract the response
                response_content = result.final_output

                # Add assistant response to history
                conversations[session_id].append({
                    "role": "assistant",
                    "content": response_content
                })

                # Send response
                await websocket.send_json({
                    "type": "assistant",
                    "content": response_content
                })

            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}. Please try again."
                await websocket.send_json({
                    "type": "error",
                    "content": error_message
                })

            # Stop typing indicator
            await websocket.send_json({"type": "typing", "content": False})

    except WebSocketDisconnect:
        # Clean up on disconnect
        if session_id in conversations:
            del conversations[session_id]
        print(f"Client {session_id} disconnected")


@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """WebSocket endpoint for voice-based interaction with streaming audio-text sync."""
    await websocket.accept()
    session_id = str(id(websocket))
    conversations[session_id] = []

    try:
        # Send welcome message with streaming
        welcome = "Welcome to ProVia Doors! I'm ready to help you find the perfect door."
        await stream_response_with_audio(websocket, welcome)

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            msg_type = message_data.get("type", "text")
            content = message_data.get("content", "")

            if not content.strip():
                continue

            # Add to conversation history
            conversations[session_id].append({
                "role": "user",
                "content": content
            })

            # Send processing indicator
            await websocket.send_json({"type": "processing", "content": True})

            try:
                # Run the agent
                result = await Runner.run(
                    provia_agent,
                    input=conversations[session_id],
                )

                response_content = result.final_output

                # Add to history
                conversations[session_id].append({
                    "role": "assistant",
                    "content": response_content
                })

                # Stream response with synchronized audio
                await stream_response_with_audio(websocket, response_content)

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Sorry, I encountered an error: {str(e)}"
                })

            await websocket.send_json({"type": "processing", "content": False})

    except WebSocketDisconnect:
        if session_id in conversations:
            del conversations[session_id]
        print(f"Voice client {session_id} disconnected")


async def stream_response_with_audio(websocket: WebSocket, text: str):
    """Stream text word-by-word with synchronized TTS audio chunks."""

    # Clean text for TTS
    clean_text = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")

    # Signal start of streaming response
    await websocket.send_json({
        "type": "stream_start",
        "content": ""
    })

    # Split into sentences for better audio chunking
    import re
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)

    for sentence in sentences:
        if not sentence.strip():
            continue

        # Split sentence into words
        words = sentence.split()

        try:
            # Generate TTS audio for this sentence
            response = await client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=sentence,
                response_format="mp3"
            )

            # Get audio data
            audio_data = response.content
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Calculate approximate timing per word
            # Average speaking rate is ~150 words per minute = 400ms per word
            word_duration_ms = 350

            # Send words with timing info
            for i, word in enumerate(words):
                await websocket.send_json({
                    "type": "stream_word",
                    "word": word + (" " if i < len(words) - 1 else ""),
                    "index": i,
                    "delay": word_duration_ms
                })

            # Send audio chunk for this sentence
            await websocket.send_json({
                "type": "stream_audio",
                "audio": audio_base64,
                "format": "mp3",
                "wordCount": len(words)
            })

            # Small delay between sentences
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"TTS Error: {e}")
            # Fallback: just send words without audio
            for i, word in enumerate(words):
                await websocket.send_json({
                    "type": "stream_word",
                    "word": word + (" " if i < len(words) - 1 else ""),
                    "index": i,
                    "delay": 100
                })

    # Signal end of streaming
    await websocket.send_json({
        "type": "stream_end",
        "fullText": text
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "ProViaDoorsSalesAgent", "mode": "streaming-voice"}


@app.get("/api/key-status")
async def key_status():
    """Check if OpenAI API key is configured."""
    key = os.getenv("OPENAI_API_KEY", "")
    return {
        "configured": bool(key and key.startswith("sk-")),
        "partial": key[:8] + "..." if key else None
    }


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
