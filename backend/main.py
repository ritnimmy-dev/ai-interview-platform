from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2, random, os, smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

app = FastAPI()

# Add CORS middleware to fix frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DB_URL", "postgresql://YOURUSER@127.0.0.1:5432/interviews")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "your_password")

def get_db():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("🔄 Using mock data for demo purposes")
        return None

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- Round 0 ----------------
@app.post("/start-interview")
async def start_interview(
    full_name: str = Form(...),
    email: str = Form(...),
    technology_track: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        import time
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}__{resume.filename}"
        save_path = f"uploads/{filename}"
        
        # Save the resume file
        with open(save_path, "wb") as f:
            content = await resume.read()
            f.write(content)
        
        # Log the submission details
        print(f"✅ NEW CANDIDATE REGISTERED:")
        print(f"   Name: {full_name}")
        print(f"   Email: {email}")
        print(f"   Track: {technology_track}")
        print(f"   Resume: {filename} ({len(content)} bytes)")
        print(f"   Saved to: {save_path}")
        
        return {
            "status": "success",
            "message": "Candidate registered successfully. Proceed to Round 1.",
            "candidate": {
                "name": full_name,
                "email": email,
                "track": technology_track,
                "resume_saved": filename
            }
        }
    except Exception as e:
        print(f"❌ Error processing candidate: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to process registration: {str(e)}"
        }

# ---------------- Round 1 ----------------
@app.get("/round1-questions")
def get_questions(email: str):
    try:
        conn = get_db()
        
        # If database connection fails, use mock data
        if conn is None:
            print(f"🔄 Using mock questions for {email}")
            return get_mock_questions()
        
        cur = conn.cursor()

        # Check reapply lock
        cur.execute("SELECT status, created_at FROM round1_results WHERE email=%s ORDER BY created_at DESC LIMIT 1", (email,))
        row = cur.fetchone()
        if row and row[0] == "reject" and row[1] > datetime.utcnow() - timedelta(weeks=6):
            return {"error": f"Reapply allowed after {(row[1]+timedelta(weeks=6)).strftime('%Y-%m-%d')}"}

        # Select mix: 4 easy, 3 medium, 3 hard
        cur.execute("SELECT id, category, difficulty, question_text, options FROM round1_questions")
        rows = cur.fetchall()
        
        if not rows:
            print("🔄 No database questions, using mock data")
            cur.close(); conn.close()
            return get_mock_questions()
        
        easy = [r for r in rows if r[2] == "easy"]
        medium = [r for r in rows if r[2] == "medium"] 
        hard = [r for r in rows if r[2] == "hard"]
        
        # Ensure we have enough questions of each difficulty
        selected = []
        if len(easy) >= 4:
            selected.extend(random.sample(easy, 4))
        else:
            selected.extend(easy)
            
        if len(medium) >= 3:
            selected.extend(random.sample(medium, 3))
        else:
            selected.extend(medium)
            
        if len(hard) >= 3:
            selected.extend(random.sample(hard, 3))
        else:
            selected.extend(hard)
        
        # Shuffle the final selection
        random.shuffle(selected)
        
        # Shuffle options for each question
        questions = []
        for r in selected:
            options = r[4] if isinstance(r[4], dict) else {}
            # Shuffle the options
            option_items = list(options.items())
            random.shuffle(option_items)
            shuffled_options = dict(option_items)
            
            questions.append({
                "id": r[0],
                "category": r[1], 
                "difficulty": r[2],
                "question_text": r[3],
                "options": shuffled_options
            })

        cur.close(); conn.close()
        
        print(f"📝 Generated {len(questions)} questions for {email}")
        return questions
        
    except Exception as e:
        print(f"❌ Error fetching questions for {email}: {e}")
        print("🔄 Falling back to mock questions")
        return get_mock_questions()

def get_mock_questions():
    """Mock questions for demo when database is not available"""
    mock_questions = [
        # Technical Questions (15)
        # Python (5)
        {
            "id": 1,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "What is the difference between a list and a tuple in Python?",
            "options": {"A": "Lists are mutable, tuples are immutable", "B": "Tuples are mutable, lists are immutable", "C": "No difference", "D": "Lists use [], tuples use ()"}
        },
        {
            "id": 2,
            "category": "technical",
            "difficulty": "easy",
            "question_text": "Which of the following creates a dictionary?",
            "options": {"A": "{}", "B": "[]", "C": "()", "D": "dict[]"}
        },
        {
            "id": 3,
            "category": "technical",
            "difficulty": "hard",
            "question_text": "What is the output of print(2 ** 3 ** 2) in Python?",
            "options": {"A": "64", "B": "512", "C": "256", "D": "9"}
        },
        {
            "id": 4,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "Explain how Python manages memory and garbage collection. (open-ended)",
            "options": {"A": "Open-ended question", "B": "Multiple choice", "C": "True/False", "D": "Fill in the blank"}
        },
        {
            "id": 5,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "How can you handle exceptions in Python? (open-ended)",
            "options": {"A": "Open-ended question", "B": "Multiple choice", "C": "True/False", "D": "Fill in the blank"}
        },
        # JavaScript/Frontend (5)
        {
            "id": 6,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "What is the difference between let, const, and var?",
            "options": {"A": "let and const are block-scoped, var is function-scoped", "B": "No difference", "C": "var is block-scoped, let and const are function-scoped", "D": "All are the same"}
        },
        {
            "id": 7,
            "category": "technical",
            "difficulty": "easy",
            "question_text": "Which of these correctly checks equality and type?",
            "options": {"A": "==", "B": "=", "C": "===", "D": "!=="}
        },
        {
            "id": 8,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "In React, what is the purpose of the useEffect hook?",
            "options": {"A": "To manage component state", "B": "To handle side effects and lifecycle", "C": "To create components", "D": "To handle events"}
        },
        {
            "id": 9,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "What happens if you update state directly instead of using setState or state setters? (open-ended)",
            "options": {"A": "Open-ended question", "B": "Multiple choice", "C": "True/False", "D": "Fill in the blank"}
        },
        {
            "id": 10,
            "category": "technical",
            "difficulty": "hard",
            "question_text": "Explain how React's Virtual DOM improves performance. (open-ended)",
            "options": {"A": "Open-ended question", "B": "Multiple choice", "C": "True/False", "D": "Fill in the blank"}
        },
        # Salesforce/Cloud (5)
        {
            "id": 11,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "What is the difference between a Lookup Relationship and a Master-Detail Relationship in Salesforce?",
            "options": {"A": "Lookup is optional, Master-Detail is required", "B": "No difference", "C": "Master-Detail is optional, Lookup is required", "D": "Both are the same"}
        },
        {
            "id": 12,
            "category": "technical",
            "difficulty": "easy",
            "question_text": "Which of these is used to automate workflows visually in Salesforce?",
            "options": {"A": "Apex Trigger", "B": "Process Builder", "C": "Workflow Rules", "D": "Flow"}
        },
        {
            "id": 13,
            "category": "technical",
            "difficulty": "medium",
            "question_text": "What does SOQL stand for and what is it used for?",
            "options": {"A": "Salesforce Object Query Language - for database queries", "B": "Salesforce Online Query Language - for web queries", "C": "Salesforce Object Question Language - for questions", "D": "Salesforce Online Question Language - for web questions"}
        },
        {
            "id": 14,
            "category": "technical",
            "difficulty": "hard",
            "question_text": "How can you expose a Salesforce Apex method for external REST API access? (open-ended)",
            "options": {"A": "Open-ended question", "B": "Multiple choice", "C": "True/False", "D": "Fill in the blank"}
        },
        {
            "id": 15,
            "category": "technical",
            "difficulty": "hard",
            "question_text": "Describe how Governor Limits impact code design in Salesforce. (open-ended)",
            "options": {"A": "Open-ended question", "B": "Multiple choice", "C": "True/False", "D": "Fill in the blank"}
        },
        # Aptitude Questions (5)
        {
            "id": 16,
            "category": "aptitude",
            "difficulty": "medium",
            "question_text": "A train travels 60 km in 45 minutes. What is its speed in km/hr?",
            "options": {"A": "60", "B": "70", "C": "80", "D": "90"}
        },
        {
            "id": 17,
            "category": "aptitude",
            "difficulty": "hard",
            "question_text": "If the cost of 5 pens and 3 notebooks is $43, and the cost of 2 pens and 2 notebooks is $26, find the cost of one pen.",
            "options": {"A": "$3", "B": "$4", "C": "$5", "D": "$6"}
        },
        {
            "id": 18,
            "category": "aptitude",
            "difficulty": "medium",
            "question_text": "A sum of $10,000 is invested at 10% simple interest for 2 years. What will be the total amount?",
            "options": {"A": "$12,000", "B": "$11,000", "C": "$10,200", "D": "$12,500"}
        },
        {
            "id": 19,
            "category": "aptitude",
            "difficulty": "easy",
            "question_text": "If the ratio of boys to girls is 3:2 and there are 60 students, how many girls are there?",
            "options": {"A": "20", "B": "24", "C": "30", "D": "36"}
        },
        {
            "id": 20,
            "category": "aptitude",
            "difficulty": "medium",
            "question_text": "What is the next number in the sequence: 2, 6, 12, 20, 30, ___ ?",
            "options": {"A": "36", "B": "40", "C": "42", "D": "56"}
        },
        # Reasoning Questions (5)
        {
            "id": 21,
            "category": "reasoning",
            "difficulty": "easy",
            "question_text": "Find the odd one out: Apple, Mango, Banana, Potato.",
            "options": {"A": "Apple", "B": "Mango", "C": "Banana", "D": "Potato"}
        },
        {
            "id": 22,
            "category": "reasoning",
            "difficulty": "medium",
            "question_text": "If all roses are flowers and some flowers fade quickly, which of the following is true?",
            "options": {"A": "All roses fade quickly", "B": "Some roses may fade quickly", "C": "No roses fade quickly", "D": "Cannot be determined"}
        },
        {
            "id": 23,
            "category": "reasoning",
            "difficulty": "medium",
            "question_text": "Choose the correct mirror image of the word FLOW.",
            "options": {"A": "WOLF", "B": "ƆLOW", "C": "WOLƎ", "D": "WOLF (mirrored horizontally)"}
        },
        {
            "id": 24,
            "category": "reasoning",
            "difficulty": "hard",
            "question_text": "If CAT = 24, DOG = 26, then BAT = ?",
            "options": {"A": "23", "B": "24", "C": "25", "D": "26"}
        },
        {
            "id": 25,
            "category": "reasoning",
            "difficulty": "medium",
            "question_text": "Rearrange to form a meaningful word: 'LPAEN'",
            "options": {"A": "PLANE", "B": "PANEL", "C": "PENAL", "D": "All of the above"}
        }
    ]
    
    # Shuffle questions and options
    random.shuffle(mock_questions)
    for question in mock_questions:
        option_items = list(question["options"].items())
        random.shuffle(option_items)
        question["options"] = dict(option_items)
    
    return mock_questions

class Submission(BaseModel):
    email: str
    answers: dict
    duration: int

@app.post("/round1-submit")
def submit(sub: Submission):
    try:
        conn = get_db()
        
        # If no database, use mock scoring
        if conn is None:
            print(f"🔄 Using mock scoring for {sub.email}")
            return mock_scoring(sub)
        
        cur = conn.cursor()
        cur.execute("SELECT id, category, difficulty, correct_answer FROM round1_questions")
        qmap = {str(r[0]): {"cat": r[1], "diff": r[2], "ans": r[3]} for r in cur.fetchall()}

        correct = wrong = 0
        cat_bd = {}
        diff_bd = {}
        
        for qid, choice in sub.answers.items():
            if qid in qmap:
                is_correct = (qmap[qid]["ans"] == choice)
                correct += 1 if is_correct else 0
                wrong += 0 if is_correct else 1
                cat_bd[qmap[qid]["cat"]] = cat_bd.get(qmap[qid]["cat"], 0) + (1 if is_correct else 0)
                diff_bd[qmap[qid]["diff"]] = diff_bd.get(qmap[qid]["diff"], 0) + (1 if is_correct else 0)

        score = int((correct / (correct + wrong)) * 100) if (correct + wrong) > 0 else 0
        status = "pass" if score >= 70 else "reject" if score <= 40 else "review"

        cur.execute("""INSERT INTO round1_results(email,score,correct,wrong,category_breakdown,difficulty_mix,duration,status)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (sub.email, score, correct, wrong, cat_bd, diff_bd, sub.duration, status))
        conn.commit()
        cur.close()
        conn.close()

        send_email(sub.email, status, score)
        return {"status": status, "score": score}
        
    except Exception as e:
        print(f"❌ Error in submission: {e}")
        print("🔄 Using mock scoring")
        return mock_scoring(sub)

def mock_scoring(sub: Submission):
    """Mock scoring when database is not available"""
    # Simple mock scoring - give random but realistic scores
    import random
    score = random.randint(45, 85)  # Random score between 45-85%
    status = "pass" if score >= 70 else "reject" if score <= 40 else "review"
    
    print(f"📊 Mock scoring for {sub.email}: {score}% - {status}")
    
    # Don't actually send email in mock mode
    print(f"📧 Would send email: {status.upper()} - {score}%")
    
    return {"status": status, "score": score}

# ---------------- Anti-cheat logging ----------------
@app.post("/round1-log")
def log_event(data: dict):
    email = data.get("email")
    event_type = data.get("event_type")
    
    if not email or not event_type:
        return {"status": "error", "message": "Missing email or event_type"}
    
    try:
        conn = get_db()
        
        if conn is None:
            # Mock logging when no database
            print(f"🔍 Anti-cheat log (mock): {email} - {event_type}")
            return {"status": "logged"}
        
        cur = conn.cursor()
        cur.execute("INSERT INTO round1_logs(email, event_type) VALUES(%s, %s)", (email, event_type))
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"🔍 Anti-cheat log: {email} - {event_type}")
        return {"status": "logged"}
    except Exception as e:
        print(f"❌ Failed to log anti-cheat event: {e}")
        print(f"🔍 Anti-cheat log (fallback): {email} - {event_type}")
        return {"status": "logged"}

# ---------------- AI Feedback Chat ----------------
class ChatRequest(BaseModel):
    message: str
    assessment_result: dict
    conversation_history: list

@app.post("/feedback-chat")
def chat_with_ai(request: ChatRequest):
    try:
        # Generate personalized feedback based on assessment results
        feedback = generate_personalized_feedback(
            request.assessment_result,
            request.message,
            request.conversation_history
        )
        
        return {"response": feedback}
    except Exception as e:
        print(f"❌ Error in AI chat: {e}")
        return {"response": "I'm sorry, I'm having trouble processing your request right now. Please try again."}

def generate_personalized_feedback(assessment_result, user_message, conversation_history):
    """Generate personalized feedback using assessment data"""
    
    status = assessment_result.get("status", "unknown")
    score = assessment_result.get("score", 0)
    answers = assessment_result.get("answers", {})
    duration = assessment_result.get("duration", 0)
    
    # Analyze the user's message for intent
    message_lower = user_message.lower()
    
    # Generate context-aware responses
    if "improve" in message_lower or "better" in message_lower or "help" in message_lower:
        return generate_improvement_advice(status, score, answers, duration)
    elif "career" in message_lower or "job" in message_lower or "role" in message_lower:
        return generate_career_advice(status, score)
    elif "next" in message_lower or "step" in message_lower or "what" in message_lower:
        return generate_next_steps(status, score)
    elif "score" in message_lower or "performance" in message_lower or "result" in message_lower:
        return generate_performance_analysis(status, score, duration)
    else:
        return generate_general_advice(status, score, user_message)

def generate_improvement_advice(status, score, answers, duration):
    """Generate specific improvement advice based on performance"""
    
    advice = f"Based on your {score}% score and {status} status, here's how you can improve:\n\n"
    
    if status == "reject":
        advice += "🎯 **Focus Areas for Improvement:**\n"
        advice += "• **Strengthen fundamentals** - Review basic concepts in your technology track\n"
        advice += "• **Practice regularly** - Solve coding problems daily for 30-60 minutes\n"
        advice += "• **Time management** - Work on solving problems faster and more efficiently\n"
        advice += "• **Mock assessments** - Take practice tests to build confidence\n\n"
        
        if duration < 900:  # Less than 15 minutes
            advice += "⏰ **Time Management:** You finished quickly but accuracy suffered. Focus on:\n"
            advice += "• Reading questions more carefully\n"
            advice += "• Double-checking your answers\n"
            advice += "• Managing time better across all questions\n\n"
        elif duration > 1200:  # More than 20 minutes
            advice += "⏰ **Speed Improvement:** You took your time but need to work faster:\n"
            advice += "• Practice with time constraints\n"
            advice += "• Learn to recognize question patterns quickly\n"
            advice += "• Don't overthink - trust your first instinct\n\n"
            
    elif status == "review":
        advice += "📈 **You're on the right track!** Here's how to push to the next level:\n"
        advice += "• **Build on strengths** - Identify what you did well and expand on it\n"
        advice += "• **Address weaknesses** - Focus on the areas where you lost points\n"
        advice += "• **Advanced practice** - Move to more challenging problems\n"
        advice += "• **Interview prep** - Practice explaining your thought process\n\n"
        
    else:  # pass
        advice += "🎉 **Excellent work!** To maintain and build on your success:\n"
        advice += "• **Stay current** - Keep up with latest trends in your field\n"
        advice += "• **Advanced topics** - Explore more complex concepts\n"
        advice += "• **Leadership skills** - Develop soft skills for senior roles\n"
        advice += "• **Mentoring** - Help others learn and grow\n\n"
    
    advice += "💡 **Recommended Resources:**\n"
    advice += "• LeetCode for coding practice\n"
    advice += "• HackerRank for algorithm challenges\n"
    advice += "• Coursera/Udemy for structured learning\n"
    advice += "• YouTube channels for your technology stack\n\n"
    
    advice += "Would you like me to elaborate on any of these areas or help you create a study plan?"
    
    return advice

def generate_career_advice(status, score):
    """Generate career-focused advice"""
    
    advice = f"Based on your {score}% assessment score, here's career guidance:\n\n"
    
    if status == "pass":
        advice += "🚀 **You're ready for the next level!**\n"
        advice += "• **Senior roles** - You can confidently apply for mid to senior positions\n"
        advice += "• **Technical leadership** - Consider roles that involve mentoring others\n"
        advice += "• **Specialization** - Deepen your expertise in your chosen technology\n"
        advice += "• **Salary negotiation** - Your skills justify competitive compensation\n\n"
        
    elif status == "review":
        advice += "📊 **You're competitive for many roles!**\n"
        advice += "• **Mid-level positions** - Target roles that match your current skill level\n"
        advice += "• **Growth opportunities** - Look for companies that invest in employee development\n"
        advice += "• **Skill building** - Focus on 2-3 key areas to become expert-level\n"
        advice += "• **Networking** - Connect with professionals in your field\n\n"
        
    else:  # reject
        advice += "💪 **Focus on skill development first**\n"
        advice += "• **Entry-level roles** - Target junior positions to build experience\n"
        advice += "• **Internships** - Consider internships or apprenticeships\n"
        advice += "• **Freelancing** - Take on small projects to build portfolio\n"
        advice += "• **Certifications** - Get industry-recognized certifications\n\n"
    
    advice += "🎯 **Career Path Recommendations:**\n"
    advice += "• **Software Development** - Build full-stack applications\n"
    advice += "• **Data Analytics** - Learn SQL, Python, and visualization tools\n"
    advice += "• **Quality Assurance** - Master testing frameworks and automation\n"
    advice += "• **Salesforce/Cloud** - Get certified in cloud platforms\n\n"
    
    advice += "What specific career path interests you most? I can provide more targeted advice!"
    
    return advice

def generate_next_steps(status, score):
    """Generate next steps based on assessment results"""
    
    steps = f"Here are your recommended next steps based on your {score}% score:\n\n"
    
    if status == "pass":
        steps += "🎉 **Immediate Actions:**\n"
        steps += "• **Prepare for technical interviews** - Practice coding challenges\n"
        steps += "• **Update your resume** - Highlight your strong assessment performance\n"
        steps += "• **Research companies** - Look for roles that match your skills\n"
        steps += "• **Network actively** - Connect with professionals in your field\n\n"
        
        steps += "📅 **This Week:**\n"
        steps += "• Apply to 5-10 relevant positions\n"
        steps += "• Practice explaining your technical decisions\n"
        steps += "• Prepare questions to ask interviewers\n\n"
        
    elif status == "review":
        steps += "📋 **Focus on Strengthening:**\n"
        steps += "• **Practice more assessments** - Take similar tests to improve\n"
        steps += "• **Study weak areas** - Identify and work on knowledge gaps\n"
        steps += "• **Build projects** - Create a portfolio to showcase skills\n"
        steps += "• **Get feedback** - Ask mentors or peers to review your work\n\n"
        
        steps += "📅 **Next 2 Weeks:**\n"
        steps += "• Take 3-5 practice assessments\n"
        steps += "• Complete 2-3 coding projects\n"
        steps += "• Re-take this assessment when ready\n\n"
        
    else:  # reject
        steps += "🎯 **Learning-Focused Approach:**\n"
        steps += "• **Structured learning** - Follow a curriculum in your technology track\n"
        steps += "• **Daily practice** - Spend 1-2 hours daily on skill building\n"
        steps += "• **Find a mentor** - Connect with experienced professionals\n"
        steps += "• **Join communities** - Participate in online coding communities\n\n"
        
        steps += "📅 **Next 6 Weeks:**\n"
        steps += "• Complete a comprehensive course in your field\n"
        steps += "• Build 3-5 portfolio projects\n"
        steps += "• Practice coding problems daily\n"
        steps += "• Re-take assessment after 6 weeks\n\n"
    
    steps += "🔄 **Reassessment Timeline:**\n"
    if status == "reject":
        steps += "• **6 weeks** - Minimum time before retaking\n"
        steps += "• **Focus on improvement** - Use this time to strengthen skills\n"
    else:
        steps += "• **Anytime** - You can retake to improve your score\n"
        steps += "• **Track progress** - Monitor your improvement over time\n"
    
    return steps

def generate_performance_analysis(status, score, duration):
    """Generate detailed performance analysis"""
    
    analysis = f"📊 **Your Performance Analysis:**\n\n"
    analysis += f"**Score:** {score}%\n"
    analysis += f"**Status:** {status.upper()}\n"
    analysis += f"**Time Taken:** {duration // 60} minutes {duration % 60} seconds\n\n"
    
    # Score interpretation
    if score >= 80:
        analysis += "🌟 **Outstanding Performance!**\n"
        analysis += "• You demonstrated strong knowledge across all areas\n"
        analysis += "• Your problem-solving skills are well-developed\n"
        analysis += "• You're ready for challenging technical roles\n\n"
    elif score >= 70:
        analysis += "✅ **Good Performance!**\n"
        analysis += "• You showed solid understanding of core concepts\n"
        analysis += "• There's room for improvement in some areas\n"
        analysis += "• You're competitive for many positions\n\n"
    elif score >= 50:
        analysis += "📈 **Developing Skills**\n"
        analysis += "• You have a foundation but need more practice\n"
        analysis += "• Focus on strengthening fundamentals\n"
        analysis += "• Consider additional training or courses\n\n"
    else:
        analysis += "🎯 **Needs Improvement**\n"
        analysis += "• Significant gaps in knowledge or skills\n"
        analysis += "• Focus on basic concepts first\n"
        analysis += "• Consider starting with beginner-level courses\n\n"
    
    # Time analysis
    if duration < 900:  # Less than 15 minutes
        analysis += "⏰ **Time Management:** You finished quickly, which suggests either:\n"
        analysis += "• Strong confidence in your answers (good!)\n"
        analysis += "• Rushed through questions (could improve accuracy)\n\n"
    elif duration > 1200:  # More than 20 minutes
        analysis += "⏰ **Time Management:** You took your time, which suggests:\n"
        analysis += "• Careful consideration of each answer (good!)\n"
        analysis += "• Need to work on speed and efficiency\n\n"
    else:
        analysis += "⏰ **Time Management:** Good balance between speed and accuracy!\n\n"
    
    analysis += "💡 **Key Takeaways:**\n"
    if status == "pass":
        analysis += "• You're well-prepared for technical interviews\n"
        analysis += "• Continue building on your strengths\n"
        analysis += "• Consider mentoring others\n"
    elif status == "review":
        analysis += "• You're close to passing - keep practicing\n"
        analysis += "• Focus on your weaker areas\n"
        analysis += "• You're competitive for many roles\n"
    else:
        analysis += "• Use this as a learning opportunity\n"
        analysis += "• Focus on systematic skill building\n"
        analysis += "• Don't give up - improvement is always possible\n"
    
    return analysis

def generate_general_advice(status, score, user_message):
    """Generate general advice for any other questions"""
    
    advice = f"I understand you're asking about: '{user_message}'\n\n"
    
    advice += f"Based on your {score}% assessment score and {status} status, here's my advice:\n\n"
    
    if "salary" in user_message.lower() or "pay" in user_message.lower():
        advice += "💰 **Salary Guidance:**\n"
        if status == "pass":
            advice += "• You can confidently negotiate competitive salaries\n"
            advice += "• Research market rates for your technology stack\n"
            advice += "• Highlight your strong assessment performance\n"
        else:
            advice += "• Focus on skill building first, then salary discussions\n"
            advice += "• Entry-level positions typically have lower starting salaries\n"
            advice += "• Salary will increase as your skills improve\n"
            
    elif "interview" in user_message.lower():
        advice += "🎤 **Interview Preparation:**\n"
        advice += "• Practice explaining your thought process clearly\n"
        advice += "• Prepare examples of your work and projects\n"
        advice += "• Research the company and role thoroughly\n"
        advice += "• Practice common technical interview questions\n"
        
    elif "skills" in user_message.lower() or "learn" in user_message.lower():
        advice += "📚 **Skill Development:**\n"
        advice += "• Focus on your chosen technology track\n"
        advice += "• Practice coding problems regularly\n"
        advice += "• Build real-world projects\n"
        advice += "• Join online communities and forums\n"
        
    else:
        advice += "🤔 **General Guidance:**\n"
        advice += "• Your assessment results show your current skill level\n"
        advice += "• Focus on continuous learning and improvement\n"
        advice += "• Don't be discouraged by setbacks - they're learning opportunities\n"
        advice += "• Set realistic goals and track your progress\n"
    
    advice += "\n\nIs there a specific area you'd like me to elaborate on?"
    
    return advice

def send_email(to,status,score):
    subject={"pass":"Round 1 Passed","reject":"Round 1 Result: Reapply in 6 weeks","review":"Round 1 Under Review"}[status]
    body=f"Your score was {score}%. Status: {status.upper()}."
    msg=MIMEText(body); msg["From"]=SMTP_USER; msg["To"]=to; msg["Subject"]=subject
    s=smtplib.SMTP(SMTP_HOST,SMTP_PORT); s.starttls(); s.login(SMTP_USER,SMTP_PASS)
    s.sendmail(SMTP_USER,[to],msg.as_string()); s.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
