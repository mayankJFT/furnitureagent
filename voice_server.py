"""Voice-enabled FastAPI server for ProVia Doors sales agent using OpenAI Realtime API."""

import asyncio
import base64
import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from agents import Runner
from provia_agent import provia_agent

load_dotenv()

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
    description="A voice-enabled conversational door sales assistant",
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
    """WebSocket endpoint for voice-based interaction using browser speech APIs."""
    await websocket.accept()
    session_id = str(id(websocket))
    conversations[session_id] = []

    try:
        # Send welcome message
        welcome = {
            "type": "assistant",
            "content": "Welcome to ProVia Doors! I'm ready to help you find the perfect door. You can speak to me or type your questions."
        }
        await websocket.send_json(welcome)

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

                # Send response (client will use browser TTS)
                await websocket.send_json({
                    "type": "assistant",
                    "content": response_content,
                    "speak": True  # Signal client to speak this
                })

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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "ProViaDoorsSalesAgent", "mode": "voice-enabled"}


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
