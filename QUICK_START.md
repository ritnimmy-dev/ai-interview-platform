# 🚀 AI Interview Platform - Quick Start Guide

## What You've Built
A professional AI-powered interview platform with:
- **Round 0**: Beautiful candidate registration form
- **Round 1**: 25-minute aptitude quiz with anti-cheat features
- **Backend**: FastAPI server with PostgreSQL database
- **Frontend**: Modern Next.js interface

## 🎯 Demo-Ready Features
✅ **Professional UI** - Clean, modern design with validation  
✅ **File Upload** - PDF resume handling with proper error handling  
✅ **CORS Fixed** - Frontend and backend communicate seamlessly  
✅ **Form Validation** - Real-time validation with helpful error messages  
✅ **Database Ready** - PostgreSQL setup with sample questions  
✅ **Anti-Cheat** - Timer, focus tracking, and question shuffling  

---

## 🚀 How to Run Your Platform

### Step 1: Start the Backend
```bash
cd backend
uvicorn main:app --reload
```
You should see: `Uvicorn running on http://127.0.0.1:8000`

### Step 2: Start the Frontend (New Terminal)
```bash
cd frontend
npm run dev
```
You should see: `Local: http://localhost:3000`

### Step 3: Test Everything
```bash
python test_platform.py
```

---

## 🧪 Demo Flow

1. **Open**: http://localhost:3000
2. **Fill Form**: 
   - Name: "John Doe"
   - Email: "john@example.com" 
   - Track: "Python Development"
   - Upload: Any PDF file
3. **Submit**: Click "Start Interview"
4. **Success**: You'll see "Interview started successfully!"
5. **Redirect**: Automatically goes to Round 1 quiz

---

## 🔧 Troubleshooting

**Backend won't start?**
- Check if port 8000 is free: `lsof -i :8000`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start?**
- Check if port 3000 is free: `lsof -i :3000`
- Install dependencies: `npm install`

**CORS errors?**
- Backend has CORS middleware configured
- Make sure backend is running on port 8000

**File upload fails?**
- Check if `uploads/` directory exists in backend
- Verify file is actually a PDF

---

## 📁 Project Structure
```
task1-landing/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── database_setup.sql    # Database schema
│   └── uploads/             # Resume storage
├── frontend/
│   ├── app/
│   │   ├── page.js          # Landing page (Round 0)
│   │   └── round1/page.jsx  # Quiz page (Round 1)
│   └── package.json
├── test_platform.py         # Test script
└── QUICK_START.md          # This guide
```

---

## 🎉 You're Ready!

Your platform is now **demo-ready** with:
- Professional candidate registration
- Secure file uploads
- Real-time form validation
- Clean, modern interface
- Proper error handling

**Next Steps**: Test the complete flow and show it to your stakeholders!

---

## 💡 Pro Tips for Cursor

**To run both servers easily:**
1. Open two terminal tabs in Cursor
2. Tab 1: `cd backend && uvicorn main:app --reload`
3. Tab 2: `cd frontend && npm run dev`

**To test quickly:**
- Use the test script: `python test_platform.py`
- Check backend logs for file uploads
- Use browser dev tools to see network requests

**To debug:**
- Backend logs show in terminal where you ran uvicorn
- Frontend errors show in browser console
- Check the Network tab for API calls
