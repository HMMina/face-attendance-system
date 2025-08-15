#!/usr/bin/env python
"""
FastAPI Server Startup Script
Direct server runner để tránh lỗi import path
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)  # Bind với 0.0.0.0 để hỗ trợ localhost và 127.0.0.1
