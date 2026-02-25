from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from question_engine import get_random_questions

app = Flask(__name__)
app.secret_key = "supersecret"
DATABASE = "database.db"

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
        medals TEXT DEFAULT 'None'
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

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    subject = request.form["subject"]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT class_level, board FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    questions = get_random_questions(user[0], user[1], subject)
    session["questions"] = questions
    session["score"] = 0

    return render_template("quiz.html", questions=questions)

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    questions = session["questions"]
    score = 0

    for q in questions:
        if request.form.get(str(q[0])) == q[10]:
            score += 1

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
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

    conn.commit()
    conn.close()

    return render_template("result.html", score=score)

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
