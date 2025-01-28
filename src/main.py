#!/usr/bin/env python3

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Generator
import uvicorn

from shared import CONFIG

# These imports assume your "modern" Beta OpenAI code
# that has client.beta.* is available.
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

from sse_starlette.sse import EventSourceResponse  # SSE streaming utility

from fastapi.middleware.cors import CORSMiddleware

import asyncio

# Create your OpenAI client
client = OpenAI()

# Pre-create your assistant (with the code_interpreter tool, as you showed)
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)

# Create an empty thread at startup
thread = client.beta.threads.create()

# Define a custom EventHandler for SSE streaming
class SSEEventHandler(AssistantEventHandler):
    """
    Captures text deltas and tool calls and sends them out
    via a queue or yield to the SSE stream.
    """
    def __init__(self, queue):
        """
        :param queue: an asyncio.Queue (or similar) to push text events to.
        """
        super().__init__()
        self.queue = queue

    @override
    def on_text_created(self, text) -> None:
        """
        Called when new text is created. We'll push this to the queue as an event.
        """
        # For a fresh text, you could push an event about the start of content.
        text: str = "assistant > "
        self.queue.put_nowait(text)

    @override
    def on_text_delta(self, delta, snapshot):
        """
        Called for streaming text chunks. We'll push them as incremental updates.
        """
        self.queue.put_nowait(delta.value)
        print(f"Delta sent: {delta.value}")  # Debugging log

    @override
    def on_tool_call_created(self, tool_call):
        """
        If a tool call is created, push that info. We'll simply identify it in the SSE.
        """
        self.queue.put_nowait(f"\n[Tool Call Created: {tool_call.type}]\n")

    @override
    def on_tool_call_delta(self, delta, snapshot):
        """
        Stream any code or logs from the code interpreter usage.
        """
        if delta.type == "code_interpreter":
            ci = delta.code_interpreter
            if ci.outputs:
                for output in ci.outputs:
                    if output.type == "logs":
                        self.queue.put_nowait(output.logs)


# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

root_path: str = CONFIG["app"]["ROOT_PATH"]

if root_path != "":
    root_prefix = f"/{root_path}"
else:
    root_prefix = ""

print(f"root_path: {root_path}")
print(f"root_prefix: {root_prefix}")

app = FastAPI(
    root_path=f"/{root_path}",
    title="AI Chat App"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    """
    Return the main page (Jinja template).
    """
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "root_prefix": root_prefix
        }
    )


@app.get("/chat-stream", response_class=EventSourceResponse)
async def chat_stream(prompt: str):
    """
    This endpoint uses SSE to stream AI responses in real time.
    """
    queue = asyncio.Queue()

    async def event_generator():
        """
        An async generator that yields SSE "data" events from the queue.
        """
        try:
            while True:
                next_text = await queue.get()
                yield {"data": next_text}
        except asyncio.CancelledError:
            # The client has disconnected
            print("Client disconnected from SSE stream.")
            raise

    # Insert the user's new message into the thread
    _ = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # Our custom SSE event handler that will push text to the queue
    sse_handler = SSEEventHandler(queue)

    # We run the OpenAI streaming in a background task
    async def run_openai():
        # Stream a response for the new user message
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=sse_handler
        ) as stream:
            stream.until_done()

        # Once done, we can push a sentinel or final message
        await queue.put("[DONE]")

    asyncio.create_task(run_openai())

    # Return SSE streaming response
    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream",
            "Transfer-Encoding": "chunked",
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(asctime)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default"],
                    "level": "INFO"
                }
            }
        }
    )
