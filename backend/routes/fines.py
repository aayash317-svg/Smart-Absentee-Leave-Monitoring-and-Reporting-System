import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import Optional

from ..db import get_db
from .auth import get_current_user_from_token, safe_object_id

router = APIRouter(prefix="/api/fines", tags=["fines"])

class PayFineRequest(BaseModel):
    paymentMode: str  # Online, Cash

@router.get("/student")
def get_student_fines(user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    
    # Verify user is student
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user or user["role"] != "Student":
        raise HTTPException(status_code=403, detail="Only students can view individual fines")
        
    student = db.students.find_one({"userId": safe_object_id(user_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    fines = list(db.finePayments.find({"studentId": student["_id"]}).sort("paymentDate", -1))
    for f in fines:
        f["_id"] = str(f["_id"])
        f["studentId"] = str(f["studentId"])
        f["paymentDate"] = f["paymentDate"].isoformat()
        
    return fines

@router.post("/pay/{payment_id}")
def pay_fine(payment_id: str, req: PayFineRequest, user_id: str = Depends(get_current_user_from_token)):
    db = get_db()

    fine_payment = db.finePayments.find_one({"_id": safe_object_id(payment_id)})
    if not fine_payment:
        raise HTTPException(status_code=404, detail="Fine record not found")

    if fine_payment["status"] == "Paid":
        raise HTTPException(status_code=400, detail="Fine is already paid")

    # --- BUG FIX: Ownership Check ---
    # Ensure the logged-in student owns this fine record.
    # Staff (Dean/HOD/Coordinator) are allowed to process payments on behalf.
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == "Student":
        # Verify this fine belongs to the logged-in student
        student = db.students.find_one({"userId": safe_object_id(user_id)})
        if not student or student["_id"] != fine_payment["studentId"]:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to pay this fine record"
            )

    # --- BUG FIX: Unique receipt number using timestamp + user suffix ---
    timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    receipt_no = f"REC-{timestamp_str}-{user_id[-4:]}"

    db.finePayments.update_one(
        {"_id": safe_object_id(payment_id)},
        {"$set": {
            "status": "Paid",
            "paymentDate": datetime.datetime.utcnow(),
            "paymentMode": req.paymentMode,
            "receiptNo": receipt_no
        }}
    )

    # Deduct student's total fine (floor at 0.0)
    student_for_update = db.students.find_one({"_id": fine_payment["studentId"]})
    if student_for_update:
        current_fine = student_for_update.get("totalFine", 0.0)
        new_fine = max(0.0, current_fine - fine_payment["amount"])
        db.students.update_one(
            {"_id": fine_payment["studentId"]},
            {"$set": {"totalFine": round(new_fine, 2)}}
        )

    # Log Audit
    db.auditLogs.insert_one({
        "userId": safe_object_id(user_id),
        "action": "Paid Fine",
        "details": f"Paid fine ID {payment_id} of Rs. {fine_payment['amount']} via {req.paymentMode}. Receipt: {receipt_no}",
        "createdAt": datetime.datetime.utcnow()
    })

    return {
        "message": "Fine payment successful",
        "receiptNo": receipt_no,
        "amount": fine_payment["amount"]
    }

@router.get("/receipt/{payment_id}")
def get_receipt(payment_id: str, user_id: str = Depends(get_current_user_from_token)):
    db = get_db()
    
    fine_payment = db.finePayments.find_one({"_id": safe_object_id(payment_id)})
    if not fine_payment:
        raise HTTPException(status_code=404, detail="Fine payment record not found")
        
    student = db.students.find_one({"_id": fine_payment["studentId"]})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    return {
        "paymentId": str(fine_payment["_id"]),
        "amount": fine_payment["amount"],
        "paymentDate": fine_payment["paymentDate"].strftime("%d-%b-%Y %I:%M %p"),
        "paymentMode": fine_payment.get("paymentMode", "Online"),
        "status": fine_payment["status"],
        "receiptNo": fine_payment.get("receiptNo", "N/A"),
        "student": {
            "fullName": student["fullName"],
            "registerNo": student["registerNo"],
            "enrollNo": student["enrollNo"],
            "program": student["program"],
            "departmentName": student["departmentName"],
            "semester": student["semester"],
            "section": student["section"]
        }
    }

@router.get("/rules")
def get_fine_rules(user_id: str = Depends(get_current_user_from_token)):
    """Get the current fine rules (minimum attendance threshold, fine per day, grace days)."""
    db = get_db()
    rules = db.fineRules.find_one({})
    if rules:
        rules["_id"] = str(rules["_id"])
        if "createdAt" in rules:
            rules["createdAt"] = rules["createdAt"].isoformat()
    return rules


@router.post("/generate/{student_id}")
def generate_fine_for_student(student_id: str, user_id: str = Depends(get_current_user_from_token)):
    """
    BUG FIX: Auto-generate a fine record for a student if their attendance
    is below the minimum threshold defined in fineRules.
    Only Dean, HOD, or Coordinator can trigger this.
    """
    db = get_db()

    # Auth: only staff roles can generate fines
    user = db.users.find_one({"_id": safe_object_id(user_id)})
    if not user or user["role"] not in ["Dean", "HOD", "Coordinator"]:
        raise HTTPException(status_code=403, detail="Only staff can generate fines")

    student = db.students.find_one({"_id": safe_object_id(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Fetch fine rules
    rules = db.fineRules.find_one({})
    if not rules:
        raise HTTPException(status_code=404, detail="No fine rules configured")

    min_att = rules.get("minAttendance", 75.0)
    fine_per_day = rules.get("fineAmountPerDay", 100.0)
    grace_days = rules.get("graceDays", 3)

    current_att = student.get("attendancePercentage", 100.0)

    if current_att >= min_att:
        return {"message": f"Student attendance ({current_att}%) is above the threshold ({min_att}%). No fine needed."}

    # Count unexcused absences for fine calculation
    unexcused_count = db.absentees.count_documents({
        "studentId": student["_id"],
        "status": "Unexcused"
    })

    # Apply grace days
    chargeable_days = max(0, unexcused_count - grace_days)
    if chargeable_days == 0:
        return {"message": f"Student has {unexcused_count} unexcused absence(s), within the {grace_days}-day grace period. No fine generated."}

    fine_amount = round(chargeable_days * fine_per_day, 2)

    # Check if a pending fine already exists to avoid duplicates
    existing_pending = db.finePayments.find_one({
        "studentId": student["_id"],
        "status": "Pending"
    })
    if existing_pending:
        return {"message": "A pending fine already exists for this student.", "fineId": str(existing_pending["_id"])}

    # Insert new fine payment record
    result = db.finePayments.insert_one({
        "studentId": student["_id"],
        "amount": fine_amount,
        "paymentDate": datetime.datetime.utcnow(),
        "paymentMode": "Online",
        "status": "Pending",
        "receiptNo": None,
        "createdAt": datetime.datetime.utcnow()
    })

    # Update student's totalFine
    db.students.update_one(
        {"_id": student["_id"]},
        {"$set": {"totalFine": round(student.get("totalFine", 0.0) + fine_amount, 2)}}
    )

    # Notify student about fine
    db.notifications.insert_one({
        "recipientId": student["userId"],
        "title": "Attendance Fine Generated",
        "message": f"A fine of Rs. {fine_amount} has been generated for {chargeable_days} unexcused absence(s). Please clear it to avoid hall ticket block.",
        "type": "Fine Alert",
        "isRead": False,
        "createdAt": datetime.datetime.utcnow()
    })

    # Audit log
    db.auditLogs.insert_one({
        "userId": safe_object_id(user_id),
        "action": "Generated Fine",
        "details": f"Generated fine of Rs. {fine_amount} for student {student['fullName']} ({chargeable_days} chargeable days)",
        "createdAt": datetime.datetime.utcnow()
    })

    return {
        "message": "Fine generated successfully",
        "fineId": str(result.inserted_id),
        "amount": fine_amount,
        "chargeableDays": chargeable_days
    }

