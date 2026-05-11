from pydantic import BaseModel


class AssetResponse(BaseModel):
    svg: str          # The final cleaned SVG code
    brief: str        # The Creative Agent's description
    model_used: str
    latency_ms: int
    cost_usd: float
