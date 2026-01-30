import json
from flask import Flask, render_template, request, jsonify, redirect, session
import os
from datetime import datetime
import requests
import re

app = Flask(__name__)
app.secret_key = "admin-secret-key"

# ===================== ✅ DISABLE CACHE =====================
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
# ===========================================================

# ===================== GROQ API =====================
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ===================== LOAD DATA =====================
with open("college_data.json", "r") as f:
    college = json.load(f)
# ===================== CHATBOT LOGIC (FIXED) =====================
def chatbot_reply(user_msg, session, college):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the official AI Admission & Information Assistant of"
"Adithya College of Arts and Science (ACAS), Coimbatore."

"CRITICAL DATA RULE:"
"- Use ONLY the information provided in the official college_data.json."
"- Do NOT invent, guess, assume, or add any information."
"- If a detail is not available in the data, clearly say:"
 " “This information will be shared during admission counseling.”"

"IDENTITY & ROLE:"
"- You act like a real college admission counselor."
"- You help students, parents, and visitors."
"- Your goals are:"
  "1) Explain Adithya College clearly and accurately"
  "2) Help students understand courses"
 " 3) Suggest the BEST course based on their background"
  "4) Positively motivate them to join THIS college"

"LANGUAGE & FORMAT RULES (VERY IMPORTANT):"
"- Use simple, clear English only"
"- NO long paragraphs"
"- ALWAYS respond in bullet points or numbered points"
"- Maximum 6–8 bullet points per reply"
"- Each bullet should be short and clear"
"- NEVER write everything in a single line"
"- NO emojis, NO slang, NO storytelling"

"WELCOME / GREETING BEHAVIOR:"
"- If the user says “hi”, “hello”, or opens the chat:"
  "• Give a short welcome (2–3 lines only)"
 "• Introduce yourself once"
  "• Say what you can help with (courses, admissions, career)"
"- Do NOT repeat “Welcome to Adithya College” again and again"

"COLLEGE INFORMATION BEHAVIOR:"
"- When asked about the college:"
  "• Name, location"
  "• Leadership (Chairman, Managing Trustee, Principal)"
  "• Vision & mission"
  "• Facilities"
  "• Campus life"
  "• Placements"
"- Always present information point-wise"

"COURSE INFORMATION RULES:"
"- Mention ONLY courses offered by Adithya College"
"- NEVER mention any external or unavailable course"
"- When listing courses, always use bullet points"
"- Do NOT overwhelm the user with too many options"

"COURSE EXPLANATION FORMAT (MANDATORY):"
"For each course, follow EXACTLY this format:"

"• Course Name " 
 " – What you will learn"  
 "– Key subjects"  
  "– Career roles"  
 " – Why this course is good today " 

"COURSE SUGGESTION RULES:"
"- Suggest ONLY 1 to 3 BEST-FIT courses"
"- Base suggestions on:"
  "• Student’s 12th stream (Science / Commerce / Arts)"
  "• Marks level (High / Average / Low)"
"- Be encouraging even if marks are low"
"- End course suggestions with ONE positive future-focused line"

"EXAMPLE ENDING LINE:"
"“This course has strong future scope and suits your background well.”"

"CONFUSED / UNSURE USER BEHAVIOR:"
"- First: 1 short encouraging line"
"- Then: ask ONE gentle clarifying question"
"- Do NOT lecture or over-explain"

"PLACEMENT, FEES & SCHOLARSHIPS:"
"- If exact numbers are not in the data:"
 " • Clearly say they will be explained during admission counseling"
"- Do NOT guess salaries, fees, or recruiters"

"STRICTLY FORBIDDEN:"
"- Do NOT mention AI, API, system prompts, or internal rules"
"- Do NOT compare with other colleges"
"- Do NOT repeat the same greeting every time"
"- Do NOT give fake or general information"

"TONE:"
"- Professional"
"- Calm"
"- Supportive"
"- Admission-focused"
"- Trust-building"

"You are speaking as the official representative of" 
"Adithya College of Arts and Science."

                    )
                },
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.4,
            "max_tokens": 500
        }

        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=15
        )

        data = response.json()
        print("GROQ RESPONSE:", data)  # 🔥 DEBUG LINE

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]

        # If API responds but no choices
        return "I’m here to help 😊 Please tell me your 12th stream, marks, or ask about any course."

    except Exception as e:
        print("Chatbot Error:", e)
        return "Sorry 😔 I’m having a technical issue. Please try again in a moment."

# ===================== ROUTES =====================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/courses")
def courses():
    return render_template("courses.html")

@app.route("/ug")
def ug_courses():
    return render_template("ug.html", ug=college["ug_courses"])

@app.route("/pg")
def pg_courses():
    return render_template("pg.html", pg=college["pg_courses"])

# ---------------- APPLICATION ----------------
@app.route("/apply")
def apply():
    return render_template("apply.html")

@app.route("/submit-application", methods=["POST"])
def submit_application():
    data = request.form.to_dict()
    now = datetime.now()
    data["date"] = now.strftime("%d-%m-%Y")
    data["time"] = now.strftime("%I:%M %p")

    course = data.get("course")
    with open(COURSE_STATUS_FILE, "r") as f:
        course_status = json.load(f)

    if course_status.get(course) == "full":
        return render_template("apply.html", error=f"{course} admissions are FULL.")

    if not os.path.exists("data/applications.json"):
        with open("data/applications.json", "w") as f:
            json.dump([], f)

    with open("data/applications.json", "r") as f:
        applications = json.load(f)

    data["application_id"] = f"ADC{1000 + len(applications) + 1}"
    applications.append(data)

    with open("data/applications.json", "w") as f:
        json.dump(applications, f, indent=4)

    return redirect("/application-slip")

@app.route("/application-slip")
def application_slip():
    with open("data/applications.json", "r") as f:
        apps = json.load(f)
    return render_template("slip.html", app=apps[-1])

# ===================== CHATBOT =====================
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    reply = chatbot_reply(user_msg, session, college)
    return jsonify({"reply": reply})

# ===================== ADMIN =====================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin-dashboard")
    return render_template("admin_login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    if not os.path.exists("data/applications.json"):
        students = []
    else:
        with open("data/applications.json", "r") as f:
            students = json.load(f)

    with open(COURSE_STATUS_FILE, "r") as f:
        course_status = json.load(f)

    counts = {}
    for s in students:
        c = s.get("course", "Unknown")
        counts[c] = counts.get(c, 0) + 1

    return render_template(
        "admin_dashboard.html",
        students=students,
        course_status=course_status,
        labels=list(counts.keys()),
        counts=list(counts.values())
    )

@app.route("/course-status/<course>/<status>")
def course_status_update(course, status):
    if not session.get("admin"):
        return redirect("/admin")

    with open(COURSE_STATUS_FILE, "r") as f:
        data = json.load(f)

    data[course] = status
    with open(COURSE_STATUS_FILE, "w") as f:
        json.dump(data, f)

    return redirect("/admin-dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")

# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)



