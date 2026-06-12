import json
import os
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from models.request_models import StreamRequest
from services.session_service import load_session, save_session
from services.episode_logger import Episode, log_episode
from services.llm_service import FALLBACK_CHAIN


router = APIRouter()
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


@router.post("/ai/stream")
async def stream_chat(body: StreamRequest):
    messages = load_session(body.session_id)
    system_instruction = {"role": "system", "content": body.system}

    if not messages:
        messages = [system_instruction]
    else:
        messages[0] = system_instruction

    messages.append({"role": "user", "content": body.message})

    async def _token_generator():
        stream_start = time.time()
        full_response = ""
        in_tokens, out_tokens = 0, 0
        final_model_used = None

        # --- LAB 11 FALLBACK LOGIC ---
        # We try each model in the chain. If the connection fails or returns an error
        # BEFORE the stream starts, we move to the next model.
        for model_name in FALLBACK_CHAIN:
            try:
                print(f"[STREAM] Attempting model: {model_name}")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True,
                    stream_options={"include_usage": True},
                    timeout=15.0  # Shorter timeout for faster failover
                )

                # If we successfully get the first chunk, we commit to this model
                for chunk in response:
                    final_model_used = model_name
                    if chunk.choices:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            full_response += delta
                            yield f"data: {json.dumps({'token': delta})}\n\n"

                    if chunk.usage:
                        in_tokens = chunk.usage.prompt_tokens
                        out_tokens = chunk.usage.completion_tokens

                # If the loop finishes successfully, break the model_name loop
                break

            except Exception as e:
                print(f"[STREAM] {model_name} failed: {str(e)[:50]}. Trying next...")
                continue

        if not final_model_used:
            yield f"data: {json.dumps({'error': 'All models failed'})}\n\n"
            return

        # Finalize and Log
        latency = int((time.time() - stream_start) * 1000)

        # A3 Requirement: Ensure model_used is logged
        log_episode(Episode(
            session_id=body.session_id,
            event_type="stream_end",
            model=final_model_used,  # Log which one actually worked
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency
        ))

        messages.append({"role": "assistant", "content": full_response})
        save_session(body.session_id, messages)

        # Send a final metadata packet so the UI knows which model was used
        yield f"data: {json.dumps({'model_used': final_model_used, 'status': 'complete'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_token_generator(), media_type="text/event-stream")
