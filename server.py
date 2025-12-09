"""FastAPI server for the furniture sales agent."""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from agents import Runner
from agent import furniture_agent, shopping_cart

load_dotenv()

# Store conversation history per connection
conversations: dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    print("Furniture Sales Agent server starting...")
    print("Make sure OPENAI_API_KEY is set in your environment or .env file")
    yield
    print("Server shutting down...")


app = FastAPI(
    title="Furniture Sales Agent",
    description="A conversational furniture sales assistant",
    lifespan=lifespan,
)


@app.get("/")
async def get_index():
    """Serve the main chat interface."""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    session_id = str(id(websocket))
    conversations[session_id] = []

    # Clear shopping cart for new session
    shopping_cart.clear()

    try:
        # Send welcome message
        welcome_message = {
            "type": "assistant",
            "content": "Welcome to Home Haven Furniture Store! I'm your personal furniture assistant. How can I help you today? Feel free to browse our categories (Sofas, Chairs, Tables, Beds, Storage) or tell me what you're looking for!"
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
                    furniture_agent,
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "FurnitureSalesAgent"}


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
