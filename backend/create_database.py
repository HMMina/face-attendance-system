#!/usr/bin/env python3
"""
Create PostgreSQL database first
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host="localhost",
            user="postgres", 
            password="Minh452004a5",
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='face_attendance'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE face_attendance")
            print("✅ Database 'face_attendance' created successfully!")
        else:
            print("✅ Database 'face_attendance' already exists!")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("🗃️ Creating PostgreSQL Database...")
    create_database()
