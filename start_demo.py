#!/usr/bin/env python3
"""
Quick demo startup script for AI Interview Platform
This script helps you start both servers easily
"""

import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the process"""
    try:
        if shell:
            return subprocess.Popen(command, shell=True, cwd=cwd)
        else:
            return subprocess.Popen(command, cwd=cwd)
    except Exception as e:
        print(f"❌ Error running command '{command}': {e}")
        return None

def check_port(port):
    """Check if a port is already in use"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def main():
    print("🚀 Starting AI Interview Platform Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend/main.py") or not os.path.exists("frontend/package.json"):
        print("❌ Please run this script from the project root directory")
        print("   Make sure you're in the task1-landing folder")
        return
    
    # Check if ports are available
    if check_port(8000):
        print("⚠️  Port 8000 is already in use. Backend might already be running.")
    if check_port(3000):
        print("⚠️  Port 3000 is already in use. Frontend might already be running.")
    
    print("\n🔧 Starting Backend Server...")
    backend_process = run_command("uvicorn main:app --reload --host 0.0.0.0 --port 8000", cwd="backend")
    
    if not backend_process:
        print("❌ Failed to start backend server")
        return
    
    print("✅ Backend server started on http://localhost:8000")
    
    # Wait a moment for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    print("\n🌐 Starting Frontend Server...")
    frontend_process = run_command("npm run dev", cwd="frontend")
    
    if not frontend_process:
        print("❌ Failed to start frontend server")
        backend_process.terminate()
        return
    
    print("✅ Frontend server started on http://localhost:3000")
    
    # Wait for frontend to start
    print("⏳ Waiting for frontend to initialize...")
    time.sleep(5)
    
    print("\n🎉 Both servers are running!")
    print("=" * 50)
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend:  http://localhost:8000")
    print("📊 Backend API docs: http://localhost:8000/docs")
    print("=" * 50)
    
    # Try to open the browser
    try:
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:3000")
    except:
        print("💡 Please manually open http://localhost:3000 in your browser")
    
    print("\n💡 Demo Instructions:")
    print("   1. Fill out the registration form")
    print("   2. Upload a PDF resume")
    print("   3. Click 'Start Interview'")
    print("   4. Complete the Round 1 assessment")
    print("   5. See the results!")
    
    print("\n🛑 To stop the servers:")
    print("   Press Ctrl+C in this terminal")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
