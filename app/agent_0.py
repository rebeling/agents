import asyncio
import json
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import ChatMessage
from app.specs import REDIS_CHANNEL, publish_to_redis, redis_client

load_dotenv()

# Store active WebSocket connections
active_connections: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up Agent...")
    await initialize_redis_topics()
    asyncio.create_task(monitor_messages())
    yield
    print("Shutting down Agent...")


app = FastAPI(lifespan=lifespan)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
templates = Jinja2Templates(directory="app/frontend/templates")


# Server chat page
@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")
    active_connections.append(websocket)
    try:
        async for content in websocket.iter_text():
            # print(f"Received raw content: {content}")
            try:
                parsed = json.loads(content)
                # print(f"Parsed content: {parsed}")
                msg = ChatMessage(**parsed)

                # !beware: not happens in monitor_messages or twice
                await websocket.send_json(msg.model_dump())
                await publish_to_redis(msg)
                print(f"Published to Redis: {msg.content}")

            except json.JSONDecodeError as e:
                print(f"Invalid JSON received: {content}, error: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")

    except WebSocketDisconnect as e:
        print(f"Connection closed: {e.code}: {e.reason}")
        if websocket in active_connections:
            active_connections.remove(websocket)
        return
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)
        return


async def initialize_redis_topics():
    # Create empty list for the topic if it doesn't exist
    await redis_client.delete(REDIS_CHANNEL)
    print(f"Initialized Redis topic: {REDIS_CHANNEL}")


async def monitor_messages():
    # Subscribe to the chat channel
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message and active_connections:
            try:
                # print(f"pubsub {message}")
                data = json.loads(message["data"])
                content = data.get("response", data.get("content", ""))
                sender = data.get("sender", "unknown")
                # print(f"Received from {sender}: {content}")

                # recieved an answer from one of the agents
                # Send to all connected WebSocket clients
                for connection in active_connections:
                    try:
                        if sender != "Agent Rebel" and content != "":
                            parsed = {
                                "type": "message",
                                "content": content,
                                "sender": sender,
                                "role": "user",
                            }
                            msg = ChatMessage(**parsed)
                            # !beware: not happens in monitor_messages or twice
                            await connection.send_json(msg.model_dump())
                    except Exception as e:
                        print(f"Error sending to client: {e}")

            except Exception as e:
                print(f"Error processing message: {e}")


if __name__ == "__main__":
    import uvicorn

    print("Starting Agent Rebel on port 7999...")
    uvicorn.run(app, host="0.0.0.0", port=7999)
