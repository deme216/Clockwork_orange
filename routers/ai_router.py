from fastapi import APIRouter, HTTPException
from models.request_model import AssetRequest
from models.response_model import AssetResponse
from services import llm_service

router = APIRouter()


@router.post("/generate/svg", response_model=AssetResponse)
async def generate_asset(body: AssetRequest):
    try:
        # One call handles the entire multi-agent pipeline
        result = llm_service.run_asset_pipeline(
            prompt=body.prompt,
            style=body.style,
            use_pro=body.use_pro
        )
        return AssetResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
