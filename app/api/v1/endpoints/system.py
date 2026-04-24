from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/last-update")
def get_last_update():
    # MVP 先回固定格式，之後再接 update_job_log
    return {
        "last_successful_update_at": None,
        "last_job_type": None,
        "status": "UNKNOWN"
    }