from fastapi import APIRouter
import time

router = APIRouter(
    prefix="/cron",
    tags=["Cron"],
    responses={404: {"description": "Not found"}},
)

@router.get("/wake")
async def wake_website():
    """
    Simple endpoint to wake the website/server.
    Can be called by a cron job service.
    """
    return {
        "status": "awake",
        "timestamp": time.time(),
        "message": "Server is running hot! 🔥"
    }
