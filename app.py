"""
EduGalaxy - Gamified Quiz Learning Platform
A Flask application for students to take quizzes, earn XP, level up, and compete.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import math
import random
import json
import re

app = Flask(__name__)
app.secret_key = 'edugalaxy_secret_key_2024'

# --- REAL WORLD SYLLABUS DATABASE ---
SYLLABUS_DB = {
    'CBSE': {
        '1': {
            'math': ['Numbers up to 100', 'Addition and Subtraction (1-digit)', 'Basic 2D Shapes', 'Measurements (Length, Weight)', 'Time and Money'],
            'science': ['Our Body and Senses', 'My Family and Neighbourhood', 'Plants and Animals Around Us', 'Means of Transport', 'The Sky Above Us'],
            'english': ['Basic Phonics and Alphabets', 'Naming Words (Nouns)', 'Describing Words (Adjectives)', 'Simple Sentence Formation', 'Picture Reading']
        },
        '2': {
            'math': ['Numbers up to 1000', 'Addition and Subtraction (2-digit)', 'Introduction to Multiplication', '3D Shapes', 'Handling Money'],
            'science': ['Types of Plants', 'Useful Animals', 'Seasons and Weather', 'Air and Water', 'Keeping Safe and Healthy'],
            'english': ['Proper and Common Nouns', 'Singular and Plural', 'Action Words (Verbs)', 'Pronouns', 'Reading Short Stories']
        },
        '3': {
            'math': ['Numbers up to 9999', 'Multiplication and Division Basics', 'Fractions (Halves and Quarters)', 'Measurement of Time', 'Smart Charts (Data)'],
            'science': ['Living and Non-Living Things', 'Parts of a Plant', 'Water as a Resource', 'The Solar System', 'Human Body Basics'],
            'english': ['Tenses (Past, Present, Future)', 'Adverbs', 'Prepositions', 'Synonyms and Antonyms', 'Paragraph Writing']
        },
        '4': {
            'math': ['Large Numbers (6-digit)', 'Advanced Multiplication & Division', 'Factors and Multiples', 'Fractions & Decimals', 'Geometry (Angles)'],
            'science': ['Digestive and Excretory Systems', 'Adaptations in Animals', 'States of Matter', 'Force, Work and Energy', 'Our Environment'],
            'english': ['Reading Comprehension', 'Subject and Predicate', 'Types of Sentences', 'Conjunctions', 'Creative Writing']
        },
        '5': {
            'math': ['Indian and International Numeration', 'HCF and LCM', 'Advanced Fractions', 'Perimeter, Area, and Volume', 'Basic Algebra Basics'],
            'science': ['Skeletal and Nervous Systems', 'Pollination and Repro', 'Rocks and Minerals', 'Light and Shadows', 'Simple Machines'],
            'english': ['Advanced Grammar', 'Direct and Indirect Speech', 'Active and Passive Voice', 'Idioms and Phrases', 'Essay Writing']
        }
    },
    'ICSE': {
        '1': {
            'math': ['Numbers 1 to 100', 'Addition (Carrying)', 'Subtraction (Borrowing)', 'Metric Measures', 'Basic Fraction Concepts'],
            'science': ['About Me & My Body', 'Food We Eat', 'Types of Houses', 'Living Things', 'Sun, Moon, and Stars'],
            'english': ['Vowels and Consonants', 'Articles (A, An, The)', 'Position Words', 'Punctuation Basics', 'Simple Comprehension']
        },
        '2': {
            'math': ['Numbers up to 1000', 'Multiplication as Repeated Addition', 'Plane and Solid Figures', 'Capacity and Weight', 'Patterns'],
            'science': ['My Needs (Food, Water, Shelter)', 'Neighborhood Places', 'Plant Life Cycle', 'Transport Types', 'Time and Direction'],
            'english': ['Gender Nouns', 'Subject-Verb Agreement', 'Adjectives and Opposites', 'Creative Picture Composition', 'Story Sequencing']
        },
        '3': {
            'math': ['4-digit Numbers', 'Basic Operations', 'Money Calculations', 'Data and Graphs', 'Logical Reasoning'],
            'science': ['Human Body (Internal Organs)', 'Birds and Insects', 'Properties of Water', 'Cleanliness and Hygiene', 'Safety Rules'],
            'english': ['Collective Nouns', 'Simple Tenses', 'Interjections', 'Informal Letter Writing', 'Literature Comprehension']
        },
        '4': {
            'math': ['6-digit Numbers', 'Mixed Operations', 'Factors & Multiples', 'Geometry Measurement', 'Time Intervals'],
            'science': ['Teeth and Digestion', 'Air Composition', 'Solutions and Solvents', 'Light and Shadows', 'Friction and Force'],
            'english': ['Advanced Reading Comprehension', 'Vocabulary Development', 'Complex Sentences', 'Formal Letter Writing', 'Poetry Analysis']
        },
        '5': {
            'math': ['Large Numbers', 'Prime and Composite Numbers', 'Decimals and Fractions', 'Ratio and Proportion', 'Percentages'],
            'science': ['Circulatory System', 'Plant Reproduction', 'Interdependence in Nature', 'Sound and Noise', 'Energy Forms'],
            'english': ['Advanced Grammar Usage', 'Debate and Speech Writing', 'Literary Devices', 'Extensive Reading', 'Creative Story Writing']
        }
    }
}


# Database configuration
DATABASE = 'database.db'

def get_db_connection():
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and sample questions."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
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
    ''')

    # Create learning progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            topic TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT,
            difficulty TEXT,
            subject TEXT
        )
    ''')

    # Check if questions exist, if not add sample questions
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            # Easy questions
            ("What is the capital of France?", "London", "Paris", "Berlin", "Madrid", "B", "Easy", "Geography"),
            ("What is 2 + 2?", "3", "4", "5", "6", "B", "Easy", "Math"),
            ("Which planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "B", "Easy", "Science"),
            ("What is the largest ocean?", "Atlantic", "Indian", "Arctic", "Pacific", "D", "Easy", "Geography"),
            ("What is H2O commonly known as?", "Salt", "Sugar", "Water", "Oxygen", "C", "Easy", "Science"),

            # Medium questions
            ("What is the square root of 144?", "10", "11", "12", "13", "C", "Medium", "Math"),
            ("Who wrote 'Romeo and Juliet'?", "Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain", "B", "Medium", "English"),
            ("What is the chemical symbol for Gold?", "Go", "Gd", "Au", "Ag", "C", "Medium", "Science"),
            ("Which country has the largest population?", "USA", "India", "China", "Russia", "C", "Medium", "Geography"),
            ("What year did World War II end?", "1943", "1944", "1945", "1946", "C", "Medium", "History"),

            # Hard questions
            ("What is the derivative of x^2?", "x", "2x", "2", "x^2", "B", "Hard", "Math"),
            ("Who developed the theory of relativity?", "Isaac Newton", "Albert Einstein", "Nikola Tesla", "Stephen Hawking", "B", "Hard", "Physics"),
            ("What is the powerhouse of the cell?", "Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus", "C", "Hard", "Biology"),
            ("What is the speed of light approximately?", "300,000 km/s", "150,000 km/s", "500,000 km/s", "100,000 km/s", "A", "Hard", "Physics"),
            ("In what year was the first computer programmer?", "1843", "1945", "1950", "1960", "A", "Hard", "Computer Science")
        ]

        cursor.executemany('''
            INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer, difficulty, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_questions)

    conn.commit()
    conn.close()

def calculate_level(xp):
    """Calculate level from XP using formula: level = floor(xp / 100) + 1"""
    return math.floor(xp / 100) + 1

def get_medal(xp):
    """Determine medal based on XP thresholds."""
    if xp >= 1000:
        return 'Diamond'
    elif xp >= 600:
        return 'Gold'
    elif xp >= 300:
        return 'Silver'
    elif xp >= 100:
        return 'Bronze'
    return 'None'

def get_xp_reward(difficulty):
    """Get XP reward based on question difficulty."""
    rewards = {
        'Easy': 10,
        'Medium': 20,
        'Hard': 30
    }
    return rewards.get(difficulty, 10)

# Initialize database on startup
init_db()

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        class_level = request.form['class_level']
        board = request.form['board']

        # Hash password
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, password, class_level, board)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, class_level, board))
            conn.commit()
            conn.close()

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'error')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """User dashboard route."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('dashboard.html', user=user)

# --- PROCEDURAL "AI" LESSON GENERATOR ---
def generate_ai_lesson(subject, class_level, board):
    """
    Generates an interactive, age-appropriate lesson covering fundamental concepts
    for Class 1-5 students based on subject, class, and board.
    """
    subject_val = subject or ""
    subject_clean = subject_val.lower().strip()
    if 'science' in subject_clean or 'evs' in subject_clean:
        subject_clean = 'science'
    elif 'math' in subject_clean:
        subject_clean = 'math'
    elif 'english' in subject_clean:
        subject_clean = 'english'

    class_match = re.search(r'Class\s*(\d+)', class_level)
    class_num = class_match.group(1) if class_match else "1"

    # Select a real-world syllabus topic
    syllabus_topic = f"General {subject.title()}"
    board_key = "CBSE" if "CBSE" in board else "ICSE"
    
    if board_key in SYLLABUS_DB and class_num in SYLLABUS_DB[board_key]:
        if subject_clean in SYLLABUS_DB[board_key][class_num]:
            topics = SYLLABUS_DB[board_key][class_num][subject_clean]
            if topics:
                syllabus_topic = random.choice(topics)

    # Basic templates tuned for young kids
    lesson_data = {
        'title': f"{subject.title()} Adventure for Class {class_num}!",
        'syllabus_topic': syllabus_topic, # Store the specific topic
        'intro': f"Welcome to your {board} {subject.title()} lab. Today's focus: {syllabus_topic}!",
        'fact_1': f"Did you know? In {subject}, everything is connected like stars in a galaxy.",
        'fact_2': "You are learning things that real astronauts use every day.",
        'core_concept': f"Today we are exploring {syllabus_topic}. Let's look closely at how it works and ask big questions!",
        'interactive_prompt': "Keep moving, explorer! When you are ready, hit the test button to see what you remember about this topic."
    }

    if "math" in subject_clean:
        lesson_data['intro'] = f"Welcome to the Number Nebula, Class {class_num} explorer! Today we are mastering: {syllabus_topic}."
        lesson_data['fact_1'] = "Numbers are the secret code of the universe. If you know math, you can speak to computers and build spaceships!"
        if class_num in ["1", "2"]:
            lesson_data['core_concept'] = f"While we study '{syllabus_topic}', remember that math is like magical tools for solving puzzles."
        elif class_num in ["3", "4", "5"]:
            lesson_data['core_concept'] = f"Your mission today involves '{syllabus_topic}'. You're entering advanced territory!"
        
    elif "science" in subject_clean or "evs" in subject_clean:
        lesson_data['intro'] = f"Welcome to the Bio-Dome, Class {class_num} scientist! Let's discover: {syllabus_topic}."
        lesson_data['fact_1'] = "The Earth is giant rock flying through space at 67,000 miles per hour, but gravity keeps us from flying off!"
        lesson_data['core_concept'] = f"As we look into '{syllabus_topic}', remember that everything around us is made of stardust."

    elif "english" in subject_clean:
        lesson_data['intro'] = f"Greetings, Class {class_num} wordsmith! Ready to unlock the power of language with {syllabus_topic}?"
        lesson_data['fact_1'] = "Words are like magic spells. The more words you know, the more clearly you can share your amazing ideas."
        lesson_data['core_concept'] = f"Today's focus is {syllabus_topic}. Try combining these new rules inside the matrix."

    return lesson_data

@app.route('/learn', methods=['GET', 'POST'])
def learn():
    """Interactive learning hub route for Class 1-5 students."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()

    # Determine if user is in target tier (Tier 1-5)
    class_level_str = user['class_level']
    # Use regex to find the tier number to avoid "Tier 1" matching "Tier 10"
    tier_match = re.search(r'Tier\s*(\d+)', class_level_str)
    tier_num = int(tier_match.group(1)) if tier_match else 0
    is_junior = 1 <= tier_num <= 5

    subject = request.form.get('subject') if request.method == 'POST' else None
    lesson = None

    # Calculate progress for each subject
    class_match = re.search(r'Class\s*(\d+)', class_level_str)
    class_num = class_match.group(1) if class_match else '1'
    board_key = 'CBSE' if 'CBSE' in user['board'] else 'ICSE'
    progress = {}
    for subj_key in ['math', 'science', 'english']:
        total_topics = len(SYLLABUS_DB.get(board_key, {}).get(class_num, {}).get(subj_key, []))
        if total_topics > 0:
            cursor.execute(
                'SELECT COUNT(DISTINCT topic) FROM learning_progress WHERE user_id = ? AND subject = ?',
                (session['user_id'], subj_key)
            )
            completed = cursor.fetchone()[0]
            progress[subj_key] = min(int((completed / total_topics) * 100), 100)
        else:
            progress[subj_key] = 0

    if subject:
        lesson = generate_ai_lesson(subject, user['class_level'], user['board'])
        # Record this topic as studied
        topic_learned = lesson.get('syllabus_topic', '')
        if topic_learned:
            cursor.execute(
                'INSERT INTO learning_progress (user_id, subject, topic) VALUES (?, ?, ?)',
                (session['user_id'], (subject or "").lower().strip(), topic_learned)
            )
            conn.commit()
            # Recalculate progress after learning
            subj_key_for_progress = (subject or "").lower().strip()
            total_topics = len(SYLLABUS_DB.get(board_key, {}).get(class_num, {}).get(subj_key_for_progress, []))
            if total_topics > 0:
                cursor.execute(
                    'SELECT COUNT(DISTINCT topic) FROM learning_progress WHERE user_id = ? AND subject = ?',
                    (session['user_id'], subj_key_for_progress)
                )
                completed = cursor.fetchone()[0]
                progress[subj_key_for_progress] = min(int((completed / total_topics) * 100), 100)

    conn.close()

    return render_template('learn.html', user=user, is_junior=is_junior, lesson=lesson, subject=subject, progress=progress)

# --- PROCEDURAL "AI" QUIZ GENERATOR ---
def generate_ai_quiz(topic):
    """
    Generates a 5-question multiple choice quiz on any topic using a procedural 
    algorithm and extensive templates. It mimics an AI by identifying keywords 
    and generating plausible questions and distractors.
    """
    topic_clean = topic.lower().strip()
    
    # Very basic procedural templates for "infinite" topics
    templates = [
        {"q": f"What is the primary function of {topic} in modern systems?", "a": "Data Processing", "b": "Energy Conversion", "c": "Structural Support", "d": "Signal Transmission"},
        {"q": f"Who is most commonly associated with the early development of {topic}?", "a": "Alan Turing", "b": "Marie Curie", "c": "A specialized research team", "d": "Nikola Tesla"},
        {"q": f"In the context of {topic}, what does the core mechanism rely on?", "a": "Quantum Entanglement", "b": "Algorithmic Efficiency", "c": "Chemical Reactions", "d": "Mechanical Force"},
        {"q": f"What is the biggest challenge currently facing advancements in {topic}?", "a": "Scalability", "b": "Heat Dissipation", "c": "Material Scarcity", "d": "Latency"},
        {"q": f"Which field benefits the most from innovations in {topic}?", "a": "Astrophysics", "b": "Cybersecurity", "c": "Biomedical Engineering", "d": "Telecommunications"}
    ]
    
    # Math specific
    if "math" in topic_clean or "algebra" in topic_clean or "calculus" in topic_clean:
        num1 = random.randint(10, 100)
        num2 = random.randint(2, 20)
        ans = num1 * num2
        templates[0] = {"q": f"If an algorithm scales by {num1} factor and iterates {num2} times, what is the base computation count?", "a": str(ans), "b": str(ans + 10), "c": str(ans - 10), "d": str(ans * 2)}
        templates[0]['correct'] = 'A'
    
    # Science specific
    if "space" in topic_clean or "physics" in topic_clean or "quantum" in topic_clean:
        templates[1] = {"q": f"What physical principle governs the behavior of {topic} in a vacuum?", "a": "Thermodynamics", "b": "Special Relativity", "c": "Quantum Mechanics", "d": "Fluid Dynamics"}
    
    # Shuffle and pick 5 (or use all 5 templates and shuffle options)
    quiz_data = []
    difficulties = ["Easy", "Medium", "Hard", "Hard", "Hard"] # AI quizzes are harder
    
    for i in range(5):
        t = templates[i % len(templates)]
        
        # Determine correct answer (randomly assign A, B, C, D)
        correct_letter = t.get('correct', random.choice(['A', 'B', 'C', 'D']))
        
        # Scramble the options into the final A B C D slots so it's not always A
        options_list = [t['a'], t['b'], t['c'], t['d']]
        # If we didn't statically set correct, assume t['a'] is the real correct answer in the template conceptually for our simple procedural generator
        real_answer_text = t['a'] if 'correct' not in t else t[t['correct'].lower()]
        
        random.shuffle(options_list)
        
        # Find which letter got the real answer text
        if options_list[0] == real_answer_text: final_correct = 'A'
        elif options_list[1] == real_answer_text: final_correct = 'B'
        elif options_list[2] == real_answer_text: final_correct = 'C'
        else: final_correct = 'D'

        quiz_data.append({
            'id': f"ai_gen_{random.randint(1000, 9999)}",
            'question': t['q'],
            'option_a': options_list[0],
            'option_b': options_list[1],
            'option_c': options_list[2],
            'option_d': options_list[3],
            'correct_answer': final_correct,
            'difficulty': difficulties[i],
            'subject': topic.title()
        })
        
    return quiz_data

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Quiz page route - shows random questions or generates AI quiz based on topic."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    questions = []
    
    # Check if this is an AI generation request
    topic = request.form.get('topic') if request.method == 'POST' else None
    
    if topic:
        # Generate procedural quiz using our "AI" algorithm
        questions = generate_ai_quiz(topic)
        # Store these in session so we can grade them
        session['current_ai_quiz'] = questions
    else:
        # Regular fallback quiz from SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 5')
        questions = [dict(row) for row in cursor.fetchall()] # Convert Row objects to dicts so they are serializable
        conn.close()
        
        if not questions:
            flash('No questions available!', 'error')
            return redirect(url_for('dashboard'))
            
        session['current_ai_quiz'] = questions # Store for grading either way

    return render_template('quiz.html', questions=questions, topic=topic)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Process quiz answers and calculate XP."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current user data
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()

    total_xp_earned = 0
    correct_ans_count = 0
    streak_count = user['streak'] if user else 0
    streak = user['streak']
    
    # Get the questions we stored in session
    stored_questions = session.get('current_ai_quiz', [])

    # Process each answer
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = str(key.split('_', 1)[1]) # id might be 'ai_gen_1234'
            selected_answer = value

            # Find the question in stored session data
            question = None
            for q in stored_questions:
                if str(q['id']) == question_id:
                    question = q
                    break

            if question and selected_answer == question['correct_answer']:
                correct_ans_count += 1

                # Calculate XP
                xp_val = get_xp_reward(question['difficulty'])

                # Streak bonus
                streak_count += 1
                streak_bonus = 0
                if streak_count > 1:
                    streak_bonus = 10 * (streak_count - 1)

                total_xp_earned += xp_val + streak_bonus
            else:
                # Reset streak on wrong answer
                streak_count = 0

    # Update user XP and stats
    new_xp = user['xp'] + total_xp_earned
    new_level = calculate_level(new_xp)
    new_medal = get_medal(new_xp)

    cursor.execute('''
        UPDATE users
        SET xp = ?, level = ?, streak = ?, medals = ?
        WHERE id = ?
    ''', (new_xp, new_level, streak_count, new_medal, session['user_id']))
    conn.commit()
    conn.close()

    flash(f'You earned {total_xp_earned} XP! Correct answers: {correct_ans_count}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard page showing user rankings by XP."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, xp, level, medals FROM users ORDER BY xp DESC')
    users = cursor.fetchall()
    conn.close()

    return render_template('leaderboard.html', users=users)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin page for adding quiz questions."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Simple admin check (in production, use proper admin role)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()

    if user['email'] != 'admin@edugalaxy.com':
        conn.close()
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        question = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        difficulty = request.form['difficulty']
        subject = request.form['subject']

        cursor.execute('''
            INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer, difficulty, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question, option_a, option_b, option_c, option_d, correct_answer, difficulty, subject))
        conn.commit()
        flash('Question added successfully!', 'success')

    conn.close()
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
