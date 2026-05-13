python -m venv .venv

.venv\Scripts\activate

pip install fastapi uvicorn openai streamlit python-dotenv mcp

uvicorn main:app --reload

streamlit run streamlit_app.py

python mcp-server/server.py

npx @modelcontextprotocol/inspector
