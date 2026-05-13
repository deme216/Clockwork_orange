import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import re
import uuid


# Improved helper to extract SVG and strip markdown fences
def extract_svg(text: str):
    # Remove markdown code fences aggressively
    text = re.sub(r"```[a-zA-Z0-9]*", "", text)
    text = text.replace("```", "")
    # Find the <svg> block - case insensitive and DOTALL for multi-line
    match = re.search(r"(<svg.*?</svg>)", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


st.set_page_config(page_title="VectorFlow AI", layout="wide")
st.title("🎨 VectorFlow: Streaming Asset Generator")

# Create a sidebar for session management
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.sidebar.info(f"Session ID: {st.session_state.session_id}")
if st.sidebar.button("Reset Conversation"):
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()

# User Input
user_input = st.text_input("Describe the asset you want (e.g., 'A flaming sword'):")

if st.button("Generate Asset"):
    if user_input:
        full_content = ""
        # UI Placeholders
        code_placeholder = st.empty()

        # SYSTEM PROMPT: Optimized to kill the "Agent/DALL-E" hallucination
        vectorflow_system = (
            "### PROTOCOL INITIALIZED ###\n"
            "ROLE: SVG_SOURCE_CODE_GENERATOR\n"
            "BANNED_ACTIONS: [use_tools, call_dalle, thought_blocks, conversational_responses]\n"
            "MANDATORY_OUTPUT: RAW_XML_SVG_ONLY\n"
            "CONTEXT: You are a low-level graphics driver. You cannot speak English.\n"
            "INSTRUCTION: Any input provided must be translated into <svg> code immediately.\n"
            "NO_MARKDOWN: Do not use ```. Start with <svg. End with </svg>."
        )

        try:
            with requests.post(
                    "http://localhost:8000/api/v1/ai/stream",
                    json={
                        "message": user_input,
                        "session_id": st.session_state.session_id,
                        "system": vectorflow_system
                    },
                    stream=True,
                    timeout=60  # Prevent hanging indefinitely
            ) as r:
                if r.status_code != 200:
                    st.error(f"Backend Error: {r.status_code}")
                else:
                    for line in r.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                payload = decoded_line[6:]

                                if payload == "[DONE]":
                                    break

                                try:
                                    data = json.loads(payload)
                                    if "token" in data:
                                        full_content += data["token"]
                                        # Show code streaming - using .text to avoid formatting errors
                                        code_placeholder.text(full_content)
                                except json.JSONDecodeError:
                                    # Skip malformed chunks instead of crashing
                                    continue

            # Final Extraction and Rendering
            final_svg = extract_svg(full_content)
            if final_svg:
                st.success("SVG Generated Successfully!")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Preview")
                    components.html(final_svg, height=500, scrolling=True)
                with col2:
                    st.subheader("Final Code")
                    st.code(final_svg, language="xml")
            else:
                st.warning("The AI output did not contain a valid <svg> tag.")
                with st.expander("Debug: Raw AI Response"):
                    st.text(full_content)

        except requests.exceptions.RequestException as req_err:
            st.error(f"Network/API Error: {req_err}")
        except Exception as e:
            st.error(f"Unexpected System Error: {e}")
    else:
        st.warning("Please enter a description first.")
