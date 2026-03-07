from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from question_engine import get_random_questions
import os

app = Flask(__name__)
app.secret_key = "supersecret"
DATABASE = "database.db"
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        class_level TEXT,
        board TEXT,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        streak INTEGER DEFAULT 0,
        medals TEXT DEFAULT 'None',
        avatar TEXT DEFAULT 'default.png'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_level TEXT,
        board TEXT,
        subject TEXT,
        difficulty TEXT,
        question TEXT,
        optionA TEXT,
        optionB TEXT,
        optionC TEXT,
        optionD TEXT,
        correct_answer TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS syllabus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_level TEXT,
        board TEXT,
        subject TEXT,
        chapter TEXT,
        topics TEXT,
        estimated_hours INTEGER DEFAULT 5
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        chapter_id INTEGER,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(chapter_id) REFERENCES syllabus(id)
    )
    """)

    conn.commit()
    conn.close()

def create_default_admin():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username,password) VALUES (?,?)",
                       ("admin", generate_password_hash("admin123")))
        conn.commit()

    conn.close()

init_db()
create_default_admin()

# ---------------- UTIL ----------------

def calculate_level(xp):
    return xp // 100 + 1

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        data = request.form
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (name,email,password,class_level,board)
        VALUES (?,?,?,?,?)
        """, (
            data["name"],
            data["email"],
            generate_password_hash(data["password"]),
            data["class_level"],
            data["board"]
        ))

        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    return render_template("dashboard.html", user=user)

@app.route("/syllabus", methods=["GET","POST"])
def syllabus():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get user details
    cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()
    class_level = user[4]
    board = user[5]

    # Get all syllabi for this class and board, grouped by subject
    cursor.execute("""
    SELECT
        id, subject, chapter, topics, estimated_hours
    FROM syllabus
    WHERE class_level = ? AND board = ?
    ORDER BY subject, chapter
    """, (class_level, board))

    syllabus_data = cursor.fetchall()

    # Group by subject
    subjects = {}
    for row in syllabus_data:
        subject = row[1]
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append({
            'id': row[0],
            'chapter': row[2],
            'topics': row[3],
            'hours': row[4]
        })

    # Calculate progress for each subject
    progress_data = {}
    for subject in subjects:
        cursor.execute("""
        SELECT COUNT(*) FROM syllabus_progress
        WHERE user_id = ? AND chapter_id IN (
            SELECT id FROM syllabus WHERE subject = ? AND class_level = ? AND board = ?
        ) AND completed = 1
        """, (session["user_id"], subject, class_level, board))

        completed = cursor.fetchone()[0]
        total = len(subjects[subject])
        progress = (completed / total * 100) if total > 0 else 0
        progress_data[subject] = {'completed': completed, 'total': total, 'percentage': progress}

    # Get completed chapters for highlighting
    cursor.execute("""
    SELECT chapter_id FROM syllabus_progress
    WHERE user_id = ? AND completed = 1
    """, (session["user_id"],))
    completed_chapters = set(row[0] for row in cursor.fetchall())

    conn.close()

    return render_template("syllabus.html",
                         user=user,
                         subjects=subjects,
                         progress_data=progress_data,
                         completed_chapters=completed_chapters)

@app.route("/mark_chapter_complete", methods=["POST"])
def mark_chapter_complete():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    chapter_id = data.get("chapter_id")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if already marked
    cursor.execute("""
    SELECT id FROM syllabus_progress
    WHERE user_id = ? AND chapter_id = ?
    """, (session["user_id"], chapter_id))

    existing = cursor.fetchone()

    if existing:
        # Toggle completion
        cursor.execute("""
        UPDATE syllabus_progress
        SET completed = 1 - completed
        WHERE user_id = ? AND chapter_id = ?
        """, (session["user_id"], chapter_id))
    else:
        # Create new entry
        cursor.execute("""
        INSERT INTO syllabus_progress (user_id, chapter_id, completed)
        VALUES (?, ?, 1)
        """, (session["user_id"], chapter_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == "POST":
        data = request.form
        avatar_file = "default.png"

        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"avatar_{session['user_id']}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                avatar_file = filename

        cursor.execute("""
        UPDATE users SET name=?, class_level=?, board=?, avatar=? WHERE id=?
        """, (
            data.get("name"),
            data.get("class_level"),
            data.get("board"),
            avatar_file,
            session["user_id"]
        ))
        conn.commit()

    cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if "user_id" not in session:
        return redirect("/login")

    subject = request.form.get("subject")
    if not subject:
        return redirect("/dashboard")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT class_level, board FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    questions = get_random_questions(user[0], user[1], subject)

    if not questions:
        # If no questions found, redirect back with error
        return redirect("/dashboard")

    session["questions"] = questions
    session["score"] = 0
    session["current_question"] = 0

    # retrieve existing high score using a new connection
    conn2 = sqlite3.connect(DATABASE)
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT MAX(score) FROM quiz_scores WHERE user_id=?", (session["user_id"],))
    high_score = cursor2.fetchone()[0] or 0
    conn2.close()

    return render_template("quiz.html", questions=questions, high_score=high_score, class_level=user[0])

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:
        return redirect("/login")

    questions = session.get("questions", [])
    if not questions:
        return redirect("/dashboard")

    score = 0

    for q in questions:
        if request.form.get(str(q[0])) == q[10]:
            score += 1

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # determine previous high score
    cursor.execute("SELECT MAX(score) FROM quiz_scores WHERE user_id=?", (session["user_id"],))
    prev_max = cursor.fetchone()[0] or 0

    # record this attempt
    cursor.execute("INSERT INTO quiz_scores (user_id, score) VALUES (?,?)", (session["user_id"], score))

    cursor.execute("SELECT xp, streak FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()

    xp_earned = score * 10
    new_streak = user[1] + 1 if score >= 7 else 0
    xp_earned += new_streak * 5
    new_xp = user[0] + xp_earned
    new_level = calculate_level(new_xp)

    medal = "Gold" if score >=9 else "Silver" if score>=7 else "Bronze" if score>=5 else "None"

    cursor.execute("""
    UPDATE users SET xp=?, level=?, streak=?, medals=?
    WHERE id=?
    """, (new_xp,new_level,new_streak,medal,session["user_id"]))

    # compute high score including this attempt
    high_score = max(prev_max, score)
    new_high = score >= prev_max

    conn.commit()
    conn.close()

    # Clear quiz session data
    session.pop("questions", None)
    session.pop("score", None)
    session.pop("current_question", None)

    return render_template("result.html", score=score, high_score=high_score, medal=medal, new_high=new_high)

@app.route("/leaderboard")
def leaderboard():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name,xp,level,medals FROM users ORDER BY xp DESC LIMIT 10")
    users = cursor.fetchall()
    conn.close()

    return render_template("leaderboard.html", users=users)

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        data = request.form
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO questions
        (class_level,board,subject,difficulty,question,
        optionA,optionB,optionC,optionD,correct_answer)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            data["class_level"],
            data["board"],
            data["subject"],
            data["difficulty"],
            data["question"],
            data["optionA"],
            data["optionB"],
            data["optionC"],
            data["optionD"],
            data["correct_answer"]
        ))

        conn.commit()
        conn.close()

    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
