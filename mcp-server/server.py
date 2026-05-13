import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from openai import OpenAI
from dotenv import load_dotenv


# 1. Load the .env file
load_dotenv()

app = Server("vectorflow-tools")

# 2. Get API Key
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_vector_asset",
            description="Generates raw SVG code for a 2D game asset.",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_name": {"type": "string", "description": "e.g., 'sword'"},
                    "style": {"type": "string", "description": "e.g., 'Cyberpunk'"}
                },
                "required": ["asset_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "generate_vector_asset":
        asset = arguments.get("asset_name")
        style = arguments.get("style", "Standard")

        try:
            resp = client.chat.completions.create(
                model="~google/gemini-flash-latest",
                messages=[
                    {"role": "system", "content": "Output ONLY raw SVG code. No markdown."},
                    {"role": "user", "content": f"Draw a {style} {asset}."}
                ]
            )
            return [types.TextContent(type="text", text=resp.choices[0].message.content)]
        except Exception as e:
            # Errors must be returned as text, not printed
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    # RUN THE SERVER
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    # Ensure no other code in this file uses 'print()'
    asyncio.run(main())
