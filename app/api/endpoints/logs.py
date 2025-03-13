from fastapi import APIRouter, Request, HTTPException, Query
from app.core.config import settings

router = APIRouter()


@router.get("/logs", summary="Get application logs")
async def get_logs(
        request: Request,
        offset: int = Query(0, description="Start index for logs"),
        limit: int = Query(100, description="Number of log entries to return")
):
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Logs not available")
    log_handler = request.app.state.log_handler
    logs = log_handler.get_logs(offset=offset, limit=limit)
    return {"logs": logs, "offset": offset, "limit": limit, "total": len(list(log_handler.logs))}
