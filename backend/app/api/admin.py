from fastapi import APIRouter, Depends, HTTPException, status
from bson.objectid import ObjectId
import datetime

from ..api.deps import get_current_user
from ..core.permissions import require_admin
from ..database.connection import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/audit-logs")
async def get_audit_logs(limit: int = 100, current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Retrieve system action audit logs for system security and tracing."""
    db = get_db()
    logs = await db.audit_logs.find({}).sort("createdAt", -1).limit(limit).to_list(length=limit)
    for log in logs:
        log["_id"] = str(log["_id"])
        if log.get("userId"):
            log["userId"] = str(log["userId"])
        if log.get("createdAt"):
            log["createdAt"] = log["createdAt"].isoformat()
    return logs

@router.get("/users")
async def list_users(current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """List all registered users who have not been soft deleted."""
    db = get_db()
    users = await db.users.find({"isDeleted": {"$ne": True}}).to_list(length=1000)
    for u in users:
        u["_id"] = str(u["_id"])
        u["password"] = "[REDACTED]"
        if u.get("createdAt"):
            u["createdAt"] = u["createdAt"].isoformat()
        if u.get("updatedAt"):
            u["updatedAt"] = u["updatedAt"].isoformat()
    return users

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: str, current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Toggle a user between Active and Deactivated states."""
    db = get_db()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
        
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    new_status = "Deactivated" if user.get("status") == "Active" else "Active"
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": new_status, "updatedAt": datetime.datetime.utcnow()}}
    )
    
    # Write audit log entry
    await db.audit_logs.insert_one({
        "userId": ObjectId(current_user["id"]),
        "action": "Toggle User Status",
        "details": f"Toggled status of user {user_id} to {new_status}",
        "createdAt": datetime.datetime.utcnow()
    })
    
    return {"message": f"User status updated to {new_status}"}

@router.delete("/users/{user_id}")
async def soft_delete_user(user_id: str, current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Soft delete a user by setting isDeleted to True."""
    db = get_db()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
        
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"isDeleted": True, "updatedAt": datetime.datetime.utcnow()}}
    )
    
    # Write audit log entry
    await db.audit_logs.insert_one({
        "userId": ObjectId(current_user["id"]),
        "action": "Soft Delete User",
        "details": f"Soft-deleted user {user_id}",
        "createdAt": datetime.datetime.utcnow()
    })
    
    return {"message": "User soft-deleted successfully"}


# ── Settings ────────────────────────────────────────────────────────────

# Default settings (persisted to DB if collection exists)
_DEFAULT_SETTINGS = {
    "attendanceThreshold": 75,
    "finePerDay": 50,
    "smsSendEnabled": True,
    "emailSendEnabled": True,
    "gracePeriodDays": 0,
    "maxLeavePerSemester": 15,
}

@router.get("/settings")
async def get_settings(current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Fetch current system configuration settings."""
    db = get_db()
    row = await db.settings.find_one({"key": "system"})
    if row:
        row.pop("_id", None)
        row.pop("key", None)
        return row
    return _DEFAULT_SETTINGS

@router.put("/settings")
async def update_settings(body: dict, current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Persist system configuration settings."""
    db = get_db()
    await db.settings.update_one(
        {"key": "system"},
        {"$set": {"key": "system", **body, "updatedAt": datetime.datetime.utcnow()}},
        upsert=True
    )
    await db.audit_logs.insert_one({
        "userId": ObjectId(current_user["id"]),
        "action": "Update Settings",
        "details": f"Updated system settings: {list(body.keys())}",
        "createdAt": datetime.datetime.utcnow()
    })
    return {"message": "Settings saved successfully"}


# ── SMS Log ──────────────────────────────────────────────────────────────

@router.get("/sms-log")
async def get_sms_log(limit: int = 100, current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Return sent SMS history records."""
    db = get_db()
    logs = await db.sms_logs.find({}).sort("sentAt", -1).limit(limit).to_list(length=limit)
    for log in logs:
        log["_id"] = str(log["_id"])
        if log.get("sentAt"): log["sentAt"] = log["sentAt"].isoformat()
    return logs


# ── Activity Log (alias for audit-logs, called from frontend) ─────────────

@router.get("/activity")
async def get_activity_log(limit: int = 100, current_user: dict = Depends(get_current_user), _=Depends(require_admin)):
    """Activity log alias consumed by admin_activity_logs screen."""
    db = get_db()
    logs = await db.audit_logs.find({}).sort("createdAt", -1).limit(limit).to_list(length=limit)
    result = []
    for log in logs:
        result.append({
            "id": str(log["_id"]),
            "action": log.get("action", ""),
            "details": log.get("details", ""),
            "timestamp": log["createdAt"].isoformat() if log.get("createdAt") else None,
            "userId": str(log["userId"]) if log.get("userId") else None,
        })
    return result
