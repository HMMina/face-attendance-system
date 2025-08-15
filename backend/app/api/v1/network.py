"""
API endpoints for network status and logs
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.network_log import NetworkLog
from app.schemas.network_log import NetworkLogOut
from typing import List

router = APIRouter()

@router.get("/", response_model=List[NetworkLogOut])
def get_network_logs(db: Session = Depends(get_db)):
    return db.query(NetworkLog).order_by(NetworkLog.timestamp.desc()).all()

@router.get("/device/{device_id}", response_model=List[NetworkLogOut])
def get_device_network_logs(device_id: str, db: Session = Depends(get_db)):
    return db.query(NetworkLog).filter(NetworkLog.device_id == device_id).order_by(NetworkLog.timestamp.desc()).all()

@router.get("/status")
def get_network_status(db: Session = Depends(get_db)):
    # Trả về tổng quan trạng thái mạng
    logs = db.query(NetworkLog).order_by(NetworkLog.timestamp.desc()).limit(10).all()
    return {
        "status": "online" if logs else "unknown",
        "recent_logs": len(logs),
        "last_update": logs[0].timestamp if logs else None
    }
