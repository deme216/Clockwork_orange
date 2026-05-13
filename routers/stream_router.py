import json
import os
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from models.request_models import StreamRequest
from services.session_service import load_session, save_session
from services.episode_logger import Episode, log_episode


router = APIRouter()
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


@router.post("/ai/stream")
async def stream_chat(body: StreamRequest):
    messages = load_session(body.session_id)
    system_instruction = {"role": "system", "content": body.system}

    if not messages:
        messages = [system_instruction]
    else:
        messages[0] = system_instruction  # Update the persona in memory so it doesn't revert to ASCII/DALL-E mode

    messages.append({"role": "user", "content": body.message})

    async def _token_generator():
        stream_start = time.time()
        full_response = ""
        in_tokens, out_tokens = 0, 0
        model = "google/gemini-3.1-flash-lite"

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )

        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    yield f"data: {json.dumps({'token': delta})}\n\n"

            if chunk.usage:
                in_tokens = chunk.usage.prompt_tokens
                out_tokens = chunk.usage.completion_tokens

        # Finalize
        latency = int((time.time() - stream_start) * 1000)
        log_episode(Episode(
            session_id=body.session_id, event_type="stream_end",
            model=model, input_tokens=in_tokens, output_tokens=out_tokens, latency_ms=latency
        ))

        messages.append({"role": "assistant", "content": full_response})
        save_session(body.session_id, messages)
        yield "data: [DONE]\n\n"

    return StreamingResponse(_token_generator(), media_type="text/event-stream")
