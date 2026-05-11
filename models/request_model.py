from pydantic import BaseModel, Field


class AssetRequest(BaseModel):
    prompt: str = Field(..., example="A medieval sword")
    style: str = Field("Cyberpunk", example="Retro 8-bit")
    use_pro: bool = Field(False, description="Switch to Claude 4.6 for higher quality")
