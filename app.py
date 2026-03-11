"""
EduGalaxy - Gamified Quiz Learning Platform
A Flask application for students to take quizzes, earn XP, level up, and compete.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, make_response
import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import math
import random
import json
import re

app = Flask(__name__)
app.secret_key = 'edugalaxy_secret_key_2024'

# --- COMPREHENSIVE MULTI-BOARD SYLLABUS DATABASE ---
SYLLABUS_DB = {
    'CBSE': {
        '1': {
            'english': ['Alphabet and Phonics', 'Vowels and Consonants', 'Two-letter and Three-letter Words', 'Use of A / An', 'Naming Words (Nouns)', 'Action Words (Verbs)', 'Simple Sentences', 'Rhymes and Short Stories'],
            'hindi': ['स्वर और व्यंजन', 'मात्राएँ', 'दो और तीन अक्षर वाले शब्द', 'शब्द और वाक्य', 'संज्ञा (basic)', 'चित्र देखकर शब्द लिखना', 'छोटी कविताएँ'],
            'math': ['Numbers 1–100', 'Addition', 'Subtraction', 'Shapes', 'Patterns', 'Measurement (long/short, heavy/light)', 'Time (day/night)']
        },
        '2': {
            'english': ['Nouns', 'Pronouns', 'Verbs', 'Adjectives', 'Articles', 'Prepositions', 'Sentence Formation', 'Comprehension'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'लिंग', 'वचन', 'वाक्य निर्माण', 'छोटी कहानी'],
            'math': ['Numbers up to 1000', 'Addition and Subtraction', 'Multiplication (basic)', 'Shapes', 'Measurement', 'Time and Money'],
            'evs': ['My Family', 'My Body', 'Food and Health', 'Plants', 'Animals', 'Water', 'Transport']
        },
        '3': {
            'english': ['Parts of Speech', 'Tenses (basic)', 'Adjectives', 'Prepositions', 'Paragraph Writing', 'Story Writing'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'विशेषण', 'लिंग और वचन', 'अनुচ্ছেদ लेखन'],
            'math': ['Numbers up to 10,000', 'Addition and Subtraction', 'Multiplication', 'Division', 'Fractions', 'Measurement', 'Time and Money'],
            'evs': ['Family and Friends', 'Food and Nutrition', 'Water', 'Plants', 'Animals', 'Transport and Communication'],
            'gk': ['Animals and Birds', 'Famous People', 'Countries and Flags', 'Basic Science Facts', 'Sports']
        },
        '4': {
            'english': ['Nouns and Kinds of Nouns', 'Pronouns', 'Tenses', 'Adverbs', 'Prepositions', 'Letter Writing'],
            'hindi': ['संज्ञा और सर्वनाम', 'क्रिया और काल', 'विशेषण', 'लिंग और वचन', 'अनुच्छेद लेखन', 'पत्र लेखन'],
            'math': ['Large Numbers', 'Multiplication and Division', 'Fractions', 'Geometry', 'Measurement', 'Data Handling'],
            'evs': ['Plants and Animals', 'Food and Digestion', 'Air and Water', 'Natural Resources'],
            'sst': ['Our Earth', 'Our Country India', 'Maps and Directions', 'Environment'],
            'gk': ['Important Days', 'Famous Personalities', 'Science and Inventions', 'Geography Facts'],
            'computer': ['Introduction to Computers', 'Input and Output Devices', 'Paint Program', 'Word Processing', 'Internet Basics']
        },
        '5': {
            'english': ['Parts of Speech Revision', 'Tenses', 'Articles', 'Adverbs', 'Conjunctions', 'Story Writing'],
            'hindi': ['संज्ञा और भेद', 'सर्वनाम', 'क्रिया और काल', 'मुহাवরে', 'अनुच्छेद लेखन', 'पत्र लेखन'],
            'math': ['Large Numbers', 'Fractions', 'Decimals', 'Geometry', 'Measurement', 'Data Handling'],
            'evs': ['Plants', 'Animals', 'Environment', 'Natural Resources'],
            'sst': ['Earth and Solar System', 'States of India', 'Early Civilizations', 'Environment Protection'],
            'gk': ['World Geography', 'Space', 'Famous Scientists', 'Sports and Awards'],
            'computer': ['Hardware and Software', 'Operating System', 'Word Processor', 'Presentation Software', 'Internet Safety']
        }
    },
    'ICSE': {
        '1': {
            'english': ['Alphabet and Phonics', 'Naming Words', 'Action Words', 'Simple Sentences', 'Rhymes and Stories'],
            'math': ['Numbers', 'Addition', 'Subtraction', 'Shapes', 'Measurement'],
            'evs': ['Myself', 'My Family', 'Plants', 'Animals', 'Food']
        },
        '2': {
            'english': ['Nouns', 'Pronouns', 'Verbs', 'Adjectives', 'Sentence Formation'],
            'math': ['Numbers up to 1000', 'Addition and Subtraction', 'Multiplication', 'Shapes'],
            'evs': ['Body Parts', 'Food', 'Plants', 'Animals'],
            'gk': ['Animals', 'Countries', 'Sports']
        },
        '3': {
            'english': ['Parts of Speech', 'Tenses', 'Adverbs', 'Composition Writing', 'Letter Writing'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'विशेषण', 'अनुच्छेद लेखन'],
            'math': ['Numbers', 'Multiplication and Division', 'Fractions', 'Geometry', 'Measurement'],
            'evs': ['Plants', 'Animals', 'Human Body', 'Environment'],
            'sst': ['Earth and Maps', 'Early History', 'India'],
            'gk': ['Science Facts', 'World Knowledge', 'Current Events'],
            'computer': ['Computer Basics', 'Paint', 'Word Processing', 'Internet']
        },
        '4': {
            'english': ['Parts of Speech', 'Tenses', 'Adverbs', 'Composition Writing', 'Letter Writing'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'विशेषण', 'अनुच्छेद लेखन'],
            'math': ['Numbers', 'Multiplication and Division', 'Fractions', 'Geometry', 'Measurement'],
            'evs': ['Plants', 'Animals', 'Human Body', 'Environment'],
            'sst': ['Earth and Maps', 'Early History', 'India'],
            'gk': ['Science Facts', 'World Knowledge', 'Current Events'],
            'computer': ['Computer Basics', 'Paint', 'Word Processing', 'Internet']
        },
        '5': {
            'english': ['Parts of Speech', 'Tenses', 'Adverbs', 'Composition Writing', 'Letter Writing'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'विशेषण', 'अनुच्छेद लेखन'],
            'math': ['Numbers', 'Multiplication and Division', 'Fractions', 'Geometry', 'Measurement'],
            'evs': ['Plants', 'Animals', 'Human Body', 'Environment'],
            'sst': ['Earth and Maps', 'Early History', 'India'],
            'gk': ['Science Facts', 'World Knowledge', 'Current Events'],
            'computer': ['Computer Basics', 'Paint', 'Word Processing', 'Internet']
        }
    },
    'WBSE': {
        '1': {
            'bengali': ['বর্ণমালা', 'স্বরবর্ণ', 'ব্যঞ্জনবর্ণ', 'সহজ শব্দ', 'ছড়া'],
            'math': ['সংখ্যা', 'যোগ', 'বিয়োগ', 'আকার'],
            'evs': ['আমার পরিবার', 'গাছপালা', 'প্রাণী']
        },
        '2': {
            'bengali': ['শব্দ গঠন', 'বাক্য গঠন', 'ছোট গল্প'],
            'math': ['সংখ্যা', 'যোগ ও বিয়োগ', 'গুণ'],
            'evs': ['গাছ', 'প্রাণী', 'জল'],
            'gk': ['পশু', 'পাখি', 'দেশ']
        },
        '3': {
            'bengali': ['বিশেষ্য', 'সর্বনাম', 'ক্রিয়া', 'অনুচ্ছেদ লেখা'],
            'english': ['Nouns', 'Verbs', 'Sentences'],
            'math': ['Numbers', 'Multiplication', 'Division'],
            'evs': ['Environment', 'Plants', 'Animals'],
            'gk': ['Famous People', 'Countries']
        },
        '4': {
            'bengali': ['পদ পরিচয়', 'বাক্য রচনা', 'অনুচ্ছেদ লেখা', 'পত্র লেখা'],
            'english': ['Parts of Speech', 'Tenses', 'Composition'],
            'math': ['Fractions', 'Decimals', 'Geometry'],
            'evs': ['Nature', 'Animals', 'Environment'],
            'sst': ['India', 'Maps', 'History Basics'],
            'gk': ['Science Facts', 'Geography'],
            'computer': ['Computer Basics', 'Paint', 'Word Processor', 'Internet']
        },
        '5': {
            'bengali': ['পদ পরিচয়', 'বাক্য রচনা', 'অনুচ্ছেদ লেখা', 'পত্র লেখা'],
            'english': ['Parts of Speech', 'Tenses', 'Composition'],
            'math': ['Fractions', 'Decimals', 'Geometry'],
            'evs': ['Nature', 'Animals', 'Environment'],
            'sst': ['India', 'Maps', 'History Basics'],
            'gk': ['Science Facts', 'Geography'],
            'computer': ['Computer Basics', 'Paint', 'Word Processor', 'Internet']
        }
    }
}


# Database configuration
ACHIEVEMENTS = [
    {'id': 'first_step',   'name': 'First Step',     'icon': '🚀', 'desc': 'Complete your first lesson',           'xp_req': 1,    'color': '#fb923c'},
    {'id': 'bronze_mind',  'name': 'Bronze Mind',    'icon': '🥉', 'desc': 'Reach 100 XP',                         'xp_req': 100,  'color': '#cd7f32'},
    {'id': 'silver_mind',  'name': 'Silver Mind',    'icon': '🥈', 'desc': 'Reach 300 XP',                         'xp_req': 300,  'color': '#c0c0c0'},
    {'id': 'gold_mind',    'name': 'Gold Mind',      'icon': '🥇', 'desc': 'Reach 600 XP',                         'xp_req': 600,  'color': '#ffd700'},
    {'id': 'diamond_mind', 'name': 'Diamond Mind',   'icon': '💎', 'desc': 'Reach 1000 XP',                        'xp_req': 1000, 'color': '#a5f3fc'},
    {'id': 'streak_3',     'name': 'On Fire',        'icon': '🔥', 'desc': 'Complete 3 lessons in a row',          'xp_req': 50,   'color': '#f97316'},
    {'id': 'polymath',     'name': 'Polymath',       'icon': '📚', 'desc': 'Study 3 different subjects',           'xp_req': 150,  'color': '#a78bfa'},
    {'id': 'scientist',    'name': 'Scientist',      'icon': '🔬', 'desc': 'Complete 5 experiments',               'xp_req': 200,  'color': '#34d399'},
    {'id': 'storyteller',  'name': 'Storyteller',    'icon': '📖', 'desc': 'Read 5 story chapters',                'xp_req': 50,   'color': '#60a5fa'},
    {'id': 'voice_hero',   'name': 'Voice Hero',     'icon': '🎤', 'desc': 'Complete 3 voice challenges',          'xp_req': 75,   'color': '#f472b6'},
    {'id': 'puzzle_master','name': 'Puzzle Master',  'icon': '🧩', 'desc': 'Solve 5 puzzles correctly',            'xp_req': 100,  'color': '#facc15'},
    {'id': 'explorer',     'name': '3D Explorer',    'icon': '🌍', 'desc': 'Visit the 3D Learning Island',         'xp_req': 20,   'color': '#22d3ee'},
]

DAILY_CHALLENGES = [
    {'q': 'What is 7 × 8?',                        'ans': '56',         'subject': 'math',    'xp': 30},
    {'q': 'Spell "Beautiful"',                       'ans': 'beautiful',  'subject': 'english', 'xp': 25},
    {'q': 'What is the capital of India?',           'ans': 'new delhi',  'subject': 'gk',      'xp': 25},
    {'q': 'How many planets in our solar system?',   'ans': '8',          'subject': 'science', 'xp': 30},
    {'q': 'What is 15 + 27?',                        'ans': '42',         'subject': 'math',    'xp': 25},
    {'q': 'Name the longest river in India.',        'ans': 'ganga',      'subject': 'gk',      'xp': 30},
    {'q': 'What is H₂O?',                           'ans': 'water',      'subject': 'science', 'xp': 25},
    {'q': 'What is 9 × 9?',                          'ans': '81',         'subject': 'math',    'xp': 30},
    {'q': 'Spell "Elephant"',                        'ans': 'elephant',   'subject': 'english', 'xp': 20},
    {'q': 'How many sides does a hexagon have?',     'ans': '6',          'subject': 'math',    'xp': 20},
    {'q': 'What gas do plants absorb?',              'ans': 'carbon dioxide','subject':'science','xp': 30},
    {'q': 'Which is the largest ocean?',             'ans': 'pacific',    'subject': 'gk',      'xp': 25},
    {'q': 'What is the national animal of India?',   'ans': 'tiger',      'subject': 'gk',      'xp': 20},
    {'q': 'What is 100 ÷ 4?',                        'ans': '25',         'subject': 'math',    'xp': 25},
]


DATABASE = 'database.db'

def get_db_connection():
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            topic TEXT,
            mode TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            challenge_done INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    try:
        cursor.execute('ALTER TABLE learning_progress ADD COLUMN mode TEXT DEFAULT "General"')
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def calculate_level(xp):
    return math.floor(xp / 100) + 1

def get_medal(xp):
    if xp >= 1000: return 'Diamond'
    elif xp >= 600: return 'Gold'
    elif xp >= 300: return 'Silver'
    elif xp >= 100: return 'Bronze'
    return 'None'

def get_user_achievements(user_xp, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT subject FROM learning_progress WHERE user_id=?', (user_id,))
    subjects_studied = [r['subject'] for r in cursor.fetchall()]
    cursor.execute('SELECT COUNT(*) as c FROM learning_progress WHERE user_id=? AND mode="experiment"', (user_id,))
    exp_count = cursor.fetchone()['c']
    cursor.execute('SELECT COUNT(*) as c FROM learning_progress WHERE user_id=? AND mode="storybook"', (user_id,))
    story_count = cursor.fetchone()['c']
    cursor.execute('SELECT COUNT(*) as c FROM learning_progress WHERE user_id=? AND mode="voice"', (user_id,))
    voice_count = cursor.fetchone()['c']
    cursor.execute('SELECT COUNT(*) as c FROM learning_progress WHERE user_id=? AND mode="puzzle"', (user_id,))
    puzzle_count = cursor.fetchone()['c']
    cursor.execute('SELECT COUNT(*) as c FROM learning_progress WHERE user_id=?', (user_id,))
    total_lessons = cursor.fetchone()['c']
    conn.close()

    unlocked = []
    for a in ACHIEVEMENTS:
        earned = False
        if a['id'] == 'first_step' and total_lessons >= 1: earned = True
        elif a['id'] == 'bronze_mind' and user_xp >= 100: earned = True
        elif a['id'] == 'silver_mind' and user_xp >= 300: earned = True
        elif a['id'] == 'gold_mind' and user_xp >= 600: earned = True
        elif a['id'] == 'diamond_mind' and user_xp >= 1000: earned = True
        elif a['id'] == 'streak_3' and total_lessons >= 3: earned = True
        elif a['id'] == 'polymath' and len(subjects_studied) >= 3: earned = True
        elif a['id'] == 'scientist' and exp_count >= 5: earned = True
        elif a['id'] == 'storyteller' and story_count >= 5: earned = True
        elif a['id'] == 'voice_hero' and voice_count >= 3: earned = True
        elif a['id'] == 'puzzle_master' and puzzle_count >= 5: earned = True
        elif a['id'] == 'explorer' and total_lessons >= 1: earned = True
        unlocked.append({**a, 'earned': earned})
    return unlocked

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        class_level = request.form['class_level']
        board = request.form['board']
        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (name, email, password, class_level, board) VALUES (?, ?, ?, ?, ?)''',
                           (name, email, hashed_password, class_level, board))
            conn.commit()
            conn.close()
            flash('Account created! Welcome to EduGalaxy! 🚀', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'error')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    session.clear()
    flash('Fly safe, Commander! 👋', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()

    # Progress
    cursor.execute('SELECT subject, COUNT(*) as cnt FROM learning_progress WHERE user_id=? GROUP BY subject', (session['user_id'],))
    subject_progress = {r['subject']: r['cnt'] for r in cursor.fetchall()}

    # Activity last 7 days
    cursor.execute('''SELECT date(completed_at) as day, COUNT(*) as cnt
                      FROM learning_progress WHERE user_id=?
                      GROUP BY day ORDER BY day DESC LIMIT 7''', (session['user_id'],))
    activity_raw = cursor.fetchall()

    # Recent lessons
    cursor.execute('''SELECT subject, topic, mode, completed_at FROM learning_progress
                      WHERE user_id=? ORDER BY completed_at DESC LIMIT 5''', (session['user_id'],))
    recent = cursor.fetchall()

    # Daily challenge
    today = datetime.date.today().isoformat()
    cursor.execute('SELECT * FROM daily_log WHERE user_id=? AND date=?', (session['user_id'], today))
    daily_done = cursor.fetchone()
    conn.close()

    board = user['board']
    board_key = 'CBSE' if 'CBSE' in board else ('ICSE' if 'ICSE' in board else 'WBSE')
    class_match = re.search(r'Class\s*(\d+)', user['class_level'])
    class_num = class_match.group(1) if class_match else '1'
    subjects = list(SYLLABUS_DB.get(board_key, {}).get(class_num, {}).keys())

    # XP progress
    next_level_xp = user['level'] * 100
    current_level_xp = (user['level'] - 1) * 100
    denom = next_level_xp - current_level_xp
    xp_progress = round(((user['xp'] - current_level_xp) / denom * 100)) if denom > 0 else 0
    xp_progress = max(0, min(100, xp_progress))

    progress = {
        'math': min(100, subject_progress.get('math', 0) * 10),
        'science': min(100, subject_progress.get('science', 0) * 10 + subject_progress.get('evs', 0) * 10),
        'english': min(100, subject_progress.get('english', 0) * 10),
    }

    achievements = get_user_achievements(user['xp'], user['id'])
    daily_challenge = DAILY_CHALLENGES[int(today.replace('-','')) % len(DAILY_CHALLENGES)]
    activity = {r['day']: r['cnt'] for r in activity_raw}

    return render_template('dashboard.html',
        user=user, subjects=subjects, progress=progress,
        achievements=achievements, daily_challenge=daily_challenge,
        daily_done=bool(daily_done), recent=recent, activity=activity,
        xp_progress=xp_progress, next_level_xp=next_level_xp)


@app.route('/learn/interactive', methods=['GET', 'POST'])
def learn_interactive():
    """Main interactive learning portal."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    subject = request.form.get('subject') if request.method == 'POST' else request.args.get('subject')
    mode = request.form.get('mode') if request.method == 'POST' else request.args.get('mode', 'storybook')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    board = user['board']
    board_key = 'CBSE' if 'CBSE' in board else ('ICSE' if 'ICSE' in board else 'WBSE')
    class_match = re.search(r'Class\s*(\d+)', user['class_level'])
    class_num = class_match.group(1) if class_match else '1'

    if not subject:
        # If no subject, pick the first one available
        avail_subjects = list(SYLLABUS_DB.get(board_key, {}).get(class_num, {}).keys())
        subject = avail_subjects[0] if avail_subjects else 'General'

    topics = SYLLABUS_DB.get(board_key, {}).get(class_num, {}).get(subject, ['General Introduction'])
    
    return render_template('learn_interactive.html', user=user, subject=subject, mode=mode, topics=topics)

@app.route('/api/lesson_content')
def get_lesson_content():
    """API to provide content for specific topics and modes."""
    subject = request.args.get('subject', '').lower()
    topic = request.args.get('topic', 'General Knowledge')
    mode = request.args.get('mode', 'storybook')
    
    # Subject to Character Mapping (Expanded with Female and Kid Characters)
    CHAR_POOL = {
        'math': [
            {'name': 'Naruto', 'catchphrase': 'Believe it!', 'image': 'naruto.png', 'color': '#fb923c'},
            {'name': 'Sakura', 'catchphrase': 'Shannaro!', 'image': 'sakura.png', 'color': '#f472b6'},
            {'name': 'Boruto', 'catchphrase': 'I\'ll do it my way!', 'image': 'boruto.png', 'color': '#fb923c'}
        ],
        'english': [
            {'name': 'Luffy', 'catchphrase': 'I will be the King of Pirates!', 'image': 'luffy.png', 'color': '#f87171'},
            {'name': 'Nami', 'catchphrase': 'I love money and maps!', 'image': 'nami.png', 'color': '#fb923c'},
            {'name': 'Chopper', 'catchphrase': 'I\'m a doctor!', 'image': 'chopper.png', 'color': '#f87171'}
        ],
        'hindi': [
            {'name': 'Tanjiro', 'catchphrase': 'I will never give up!', 'image': 'tanjiro.png', 'color': '#2dd4bf'},
            {'name': 'Nezuko', 'catchphrase': 'Mmh mmmh!', 'image': 'nezuko.png', 'color': '#f472b6'},
            {'name': 'Zenitsu', 'catchphrase': 'Protect me!', 'image': 'zenitsu.png', 'color': '#facc15'}
        ],
        'bengali': [
            {'name': 'Ichigo', 'catchphrase': 'I will protect everyone!', 'image': 'ichigo.png', 'color': '#fb923c'},
            {'name': 'Rukia', 'catchphrase': 'Feel the frost!', 'image': 'rukia.png', 'color': '#60a5fa'}
        ],
        'science': [
            {'name': 'Goku', 'catchphrase': 'Let\'s go beyond!', 'image': 'goku.png', 'color': '#60a5fa'},
            {'name': 'Bulma', 'catchphrase': 'I\'m a genius!', 'image': 'bulma.png', 'color': '#2dd4bf'}
        ],
        'evs': [
            {'name': 'Goku', 'catchphrase': 'Pure heart!', 'image': 'goku.png', 'color': '#60a5fa'},
            {'name': 'Anya', 'catchphrase': 'Waku Waku!', 'image': 'anya.png', 'color': '#f472b6'}
        ],
        'sst': [
            {'name': 'Deku', 'catchphrase': 'Plus Ultra!', 'image': 'deku.png', 'color': '#4ade80'},
            {'name': 'Ochaco', 'catchphrase': 'Zero Gravity!', 'image': 'ochaco.png', 'color': '#f472b6'}
        ],
        'gk': [
            {'name': 'Naruto', 'catchphrase': 'Dattebayo!', 'image': 'naruto.png', 'color': '#fb923c'},
            {'name': 'Hinata', 'catchphrase': 'I must try harder...', 'image': 'hinata.png', 'color': '#a78bfa'}
        ],
        'computer': [
            {'name': 'Ichigo', 'catchphrase': 'Bankai!', 'image': 'ichigo.png', 'color': '#fb923c'},
            {'name': 'Anya', 'catchphrase': 'Starlight Anya!', 'image': 'anya.png', 'color': '#f472b6'}
        ]
    }

    # Select a random character for the subject
    options = CHAR_POOL.get(subject, CHAR_POOL['math'])
    char = random.choice(options)
    
    # Procedural content generation based on subject and topic
    story_text = f"{char['name']} is here to help you master {topic}! "
    audio_text = f"Hi kids! I am {char['name']}. {char['catchphrase']} Let's learn about {topic} together! "
    
    if 'math' in subject:
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        story_text += f"{char['name']} needs to solve a Ninja Scroll equation: {num1} + {num2}. Can you help him find the answer? It's {num1+num2}!"
        audio_text += f"We have a math puzzle! What is {num1} plus {num2}?"
        game_data = {'type': 'math', 'q': f"{num1} + {num2}", 'a': num1+num2}
    elif 'english' in subject or 'hindi' in subject or 'bengali' in subject:
        story_text += f"To find the One Piece, {char['name']} must learn the secret word: {topic}. Say it loud to sail forward!"
        audio_text += f"Let's practice our words. The topic is {topic}. Repeat after me: {topic}."
        game_data = {'type': 'word', 'word': topic}
    elif 'science' in subject or 'evs' in subject:
        story_text += f"{char['name']} is training to use the power of {topic}! He needs to understand how the universe works to get stronger."
        audio_text += f"Welcome to the training ground! We are investigating {topic} today. Feel the energy!"
        game_data = {'type': 'science', 'target': topic}
    else:
        story_text += f"Exploring {topic} helps {char['name']} become a better hero. Every bit of knowledge is a step closer to victory!"
        audio_text += f"Let's explore {topic}. It's going to be Plus Ultra!"
        game_data = {'type': 'general', 'topic': topic}

    # ─── Puzzle Data ────────────────────────────────────────────────
    if 'math' in subject:
        num1 = random.randint(2, 9); num2 = random.randint(2, 9)
        op = random.choice(['+', '-', '×'])
        if op == '+':   ans = num1 + num2
        elif op == '-': num1 += num2; ans = num1 - num2
        else:           ans = num1 * num2
        p_items = [str(ans), str(ans+1), str(ans-1), str(ans+3), str(ans+5), str(ans-2)]
        p_answer = str(ans)
        p_question = f"What is {num1} {op} {num2} = ?"
        p_type = "math"
    elif 'english' in subject:
        words = [w.capitalize() for w in topic.split()] + ['Book', 'Read', 'Write', 'Word', 'Spell', 'Letter']
        random.shuffle(words)
        p_items = words[:6]
        p_answer = topic.split()[0].capitalize() if topic.split() else 'Word'
        p_question = f"Drag the word: '{topic.split()[0]}' to the answer box"
        p_type = "crossword"
    elif 'hindi' in subject:
        p_items = ['अनार', 'आम', 'बस', 'घर', 'मन','राम']
        p_answer = 'अनार'
        p_question = "कौन सा शब्द 'अ' से शुरू होता है?"
        p_type = "hindi_letters"
    else:
        extras = ['Knowledge', 'Victory', 'Science', 'Hero', topic.split()[0] if topic.split() else 'Star']
        random.shuffle(extras)
        p_items = extras[:5] + [topic]
        p_answer = topic
        p_question = f"Which word is today's topic?"
        p_type = "general"

    # ─── Voice Sentence ─────────────────────────────────────────────
    voice_map = {
        'math':     f"The answer is {p_answer}. Mathematics is my superpower!",
        'english':  f"I am reading about {topic}. Reading opens new worlds!",
        'hindi':    f"हिंदी पढ़ना बहुत मज़ेदार है। आज का विषय है: {topic}।",
        'bengali':  f"বাংলা শেখা মজার। আজকের বিষয় হলো: {topic}।",
        'science':  f"Science is amazing! Today we explore {topic}.",
        'evs':      f"Let us protect our earth. Today we learn about {topic}.",
        'sst':      f"History and geography teach us who we are. Topic: {topic}.",
        'gk':       f"General knowledge makes you amazing. Did you know about {topic}?",
        'computer': f"Computers are super smart. I am learning about {topic}.",
    }
    voice_sentence = voice_map.get(subject, f"Today I am learning about {topic}. It is so exciting!")

    # ─── Experiment Type & Steps ─────────────────────────────────────
    t_low = topic.lower()
    if any(k in t_low for k in ['water', 'rain', 'evapor', 'cloud']):
        exp_type = 'water_cycle'
        exp_steps = ['Water evaporates from the ocean','Water vapour rises and cools','Clouds form in the sky','Rain falls back to earth']
    elif any(k in t_low for k in ['plant', 'seed', 'grow', 'leaf', 'tree']):
        exp_type = 'plant_growth'
        exp_steps = ['Plant a seed in soil','Water it every day','Sunlight helps the seedling grow','The plant blooms!']
    elif any(k in t_low for k in ['magnet', 'attract', 'repel']):
        exp_type = 'magnetism'
        exp_steps = ['Hold two magnets close','Feel the attraction force','Flip one magnet — repulsion!','Draw the invisible field lines']
    elif any(k in t_low for k in ['light', 'shadow', 'mirror', 'reflect']):
        exp_type = 'light_shadow'
        exp_steps = ['Shine a torch on an object','Observe the shadow cast','Change the angle of light','The shadow moves with the light!']
    elif any(k in t_low for k in ['air', 'wind', 'atmospher', 'pressure']):
        exp_type = 'air_pressure'
        exp_steps = ['Blow air into a balloon','Feel the pressure inside','Release the balloon — it flies!','Air moves from high to low pressure']
    else:
        exp_type = 'chemical_reaction'
        exp_steps = ['Mix baking soda and vinegar','Watch the bubbles form','CO₂ gas is released!','The chemical reaction is complete']

    content = {
        'character': char,
        'storybook': {
            'text': story_text,
            'audio_text': audio_text
        },
        'adventure': {
            'objective': f"Collect items for {char['name']} while learning {topic}!",
            'game_data': game_data,
            'xp_reward': 50
        },
        'puzzle': {
            'type':     p_type,
            'question': p_question,
            'items':    p_items,
            'answer':   p_answer,
        },
        'experiment': {
            'name':         f"{topic} Simulation",
            'type':         exp_type,
            'instructions': f"Help {char['name']} run the {topic} experiment step by step!",
            'steps':        exp_steps,
        },
        'voice': {
            'sentence': voice_sentence,
            'hint':     f"It is about {topic}",
        }
    }

    return json.dumps(content)


@app.route('/complete_topic', methods=['POST'])
def complete_topic():
    """Mark a topic as completed and award XP."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    data = request.json
    subject = data.get('subject')
    topic = data.get('topic')
    mode = data.get('mode')
    xp_earned = data.get('xp', 20)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Record progress
    cursor.execute(
        'INSERT INTO learning_progress (user_id, subject, topic, mode) VALUES (?, ?, ?, ?)',
        (session['user_id'], subject, topic, mode)
    )
    
    # Update User XP
    cursor.execute('SELECT xp, streak FROM users WHERE id = ?', (session['user_id'],))
    user_data = cursor.fetchone()
    new_xp = user_data['xp'] + xp_earned
    new_level = calculate_level(new_xp)
    new_medal = get_medal(new_xp)
    new_streak = user_data['streak'] + 1
    
    cursor.execute(
        'UPDATE users SET xp = ?, level = ?, streak = ?, medals = ? WHERE id = ?',
        (new_xp, new_level, new_streak, new_medal, session['user_id'])
    )
    
    conn.commit()
    conn.close()
    
    return json.dumps({'status': 'success', 'new_xp': new_xp, 'level': new_level})

@app.route('/learn')
def learn():
    """Subject hub — lets the user pick which subject to study."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    board = user['board']
    board_key = 'CBSE' if 'CBSE' in board else ('ICSE' if 'ICSE' in board else 'WBSE')
    class_match = re.search(r'Class\s*(\d+)', user['class_level'])
    class_num = class_match.group(1) if class_match else '1'
    subjects = list(SYLLABUS_DB.get(board_key, {}).get(class_num, {}).keys())
    syllabus = SYLLABUS_DB.get(board_key, {}).get(class_num, {})

    next_level_xp = user['level'] * 100
    current_level_xp = (user['level'] - 1) * 100
    denom = next_level_xp - current_level_xp
    xp_progress = round(((user['xp'] - current_level_xp) / denom * 100)) if denom > 0 else 0
    xp_progress = max(0, min(100, xp_progress))

    return render_template('learn.html',
        user=user, subjects=subjects, syllabus=syllabus,
        xp_progress=xp_progress, next_level_xp=next_level_xp)


@app.route('/api/achievements')
def api_achievements():
    """JSON API: return current user's achievements."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT xp FROM users WHERE id = ?', (session['user_id'],))
    u = cursor.fetchone()
    conn.close()
    achievements = get_user_achievements(u['xp'], session['user_id'])
    return json.dumps(achievements)


@app.route('/api/leaderboard_position')
def api_leaderboard_position():
    """JSON API: return current user's rank on the leaderboard."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users ORDER BY xp DESC')
    ids = [r['id'] for r in cursor.fetchall()]
    conn.close()
    try:
        rank = ids.index(session['user_id']) + 1
    except ValueError:
        rank = None
    return json.dumps({'rank': rank, 'total': len(ids)})


@app.route('/api/complete_daily', methods=['POST'])
def api_complete_daily():
    """Mark daily challenge complete and award XP."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401
    today = datetime.date.today().isoformat()
    xp_reward = 25
    conn = get_db_connection()
    cursor = conn.cursor()
    # Guard: only allow once per day
    cursor.execute('SELECT id FROM daily_log WHERE user_id=? AND date=?', (session['user_id'], today))
    if cursor.fetchone():
        conn.close()
        return json.dumps({'status': 'already_done'})
    cursor.execute('INSERT INTO daily_log (user_id, date, xp_earned) VALUES (?,?,?)',
                   (session['user_id'], today, xp_reward))
    cursor.execute('SELECT xp FROM users WHERE id=?', (session['user_id'],))
    new_xp = cursor.fetchone()['xp'] + xp_reward
    cursor.execute('UPDATE users SET xp=?, level=?, medals=? WHERE id=?',
                   (new_xp, calculate_level(new_xp), get_medal(new_xp), session['user_id']))
    conn.commit()
    conn.close()
    return json.dumps({'status': 'success', 'xp_earned': xp_reward, 'new_xp': new_xp})


@app.route('/sw.js')
def service_worker():
    """Serve service worker from root path with correct scope header."""
    resp = make_response(send_from_directory('static', 'sw.js'))
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['Service-Worker-Allowed'] = '/'
    return resp


@app.route('/profile')
def profile():
    """User profile page with detailed stats."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    # Recent activity
    cursor.execute('SELECT * FROM learning_progress WHERE user_id=? ORDER BY completed_at DESC LIMIT 15', (session['user_id'],))
    recent = cursor.fetchall()
    # Subject progress
    cursor.execute('SELECT subject, COUNT(*) as cnt FROM learning_progress WHERE user_id=? GROUP BY subject', (session['user_id'],))
    subj_rows = cursor.fetchall()
    # Total lessons
    cursor.execute('SELECT COUNT(*) as cnt FROM learning_progress WHERE user_id=?', (session['user_id'],))
    total_lessons = cursor.fetchone()['cnt']
    # Rank
    cursor.execute('SELECT id FROM users ORDER BY xp DESC')
    ids = [r['id'] for r in cursor.fetchall()]
    conn.close()
    try: rank = ids.index(session['user_id']) + 1
    except ValueError: rank = '?'

    # Subject progress %
    board_key = 'CBSE' if 'CBSE' in user['board'] else ('ICSE' if 'ICSE' in user['board'] else 'WBSE')
    class_match = re.search(r'Class\s*(\d+)', user['class_level'])
    class_num = class_match.group(1) if class_match else '1'
    syllabus = SYLLABUS_DB.get(board_key, {}).get(class_num, {})
    subj_counts = {r['subject']: r['cnt'] for r in subj_rows}
    subject_progress = {}
    for subj, topics in syllabus.items():
        done = subj_counts.get(subj, 0)
        total = len(topics)
        subject_progress[subj] = min(100, round(done / total * 100)) if total else 0

    achievements = get_user_achievements(user['xp'], session['user_id'])
    badges_earned = sum(1 for a in achievements if a['earned'])
    subjects_studied = len(subj_counts)

    next_level_xp = user['level'] * 100
    current_level_xp = (user['level'] - 1) * 100
    denom = next_level_xp - current_level_xp
    xp_progress = round(((user['xp'] - current_level_xp) / denom * 100)) if denom > 0 else 0
    xp_progress = max(0, min(100, xp_progress))

    medal_map = {'None': '🔘', 'Bronze': '🥉', 'Silver': '🥈', 'Gold': '🥇', 'Platinum': '💎', 'Diamond': '🌟'}
    medal = medal_map.get(user['medals'] or 'None', '🔘')
    try:
        joined = (user['created_at'] or '2024')[:10]
    except (IndexError, TypeError):
        joined = '2024'

    return render_template('profile.html',
        user=user, recent=recent, subject_progress=subject_progress,
        achievements=achievements, badges_earned=badges_earned,
        subjects_studied=subjects_studied, total_lessons=total_lessons,
        rank=rank, xp_progress=xp_progress, next_level_xp=next_level_xp,
        medal=medal, joined=joined)


HINTS_DB = {
    'math': {
        'default': ['Break the problem into smaller parts!', 'Try drawing a picture to visualize.', 'Check your multiplication tables!', 'Remember: divide = share equally'],
        'Fractions': ['Think of a pizza divided into equal slices!', 'Numerator = top number, Denominator = bottom'],
        'Addition': ['Count on your fingers for smaller numbers!', 'Line up the ones, tens, hundreds columns'],
        'Multiplication': ['Remember: 9×n = 10n - n', 'Use repeated addition to check your answer'],
    },
    'english': {
        'default': ['Sound out each syllable!', 'Look for the root word inside.', 'Try using the word in a sentence.'],
        'Nouns': ['A noun is a person, place, animal, or thing!', 'Try: "The ___ is/was big"'],
        'Verbs': ['A verb shows action or state of being!', 'Try: "I ___ every day" — if it fits, it\'s a verb!'],
    },
    'science': {
        'default': ['Think about what you\'ve observed in nature!', 'Remember the water cycle!', 'All living things need food, water, and air.'],
        'Plants': ['Remember: leaves make food using sunlight!', 'Roots absorb water from soil.'],
    },
    'hindi': {'default': ['संज्ञा = नाम', 'क्रिया = काम करना', 'मात्राएँ ध्यान से देखें!']},
    'gk': {'default': ['Think about everyday life!', 'India has 28 states and 8 union territories.', 'The capital is always the seat of government.']},
    'default': {'default': ['Take it step by step!', 'Re-read the question carefully.', 'Eliminate wrong answers first.']},
}

@app.route('/api/hint')
def api_hint():
    """Return a hint for a given subject+topic."""
    subject = request.args.get('subject', 'default').lower()
    topic = request.args.get('topic', 'default')
    subj_hints = HINTS_DB.get(subject, HINTS_DB['default'])
    topic_hints = subj_hints.get(topic, subj_hints.get('default', ['You can do it! 💪']))
    import random
    return json.dumps({'hint': random.choice(topic_hints), 'subject': subject, 'topic': topic})


@app.route('/leaderboard')
def leaderboard():
    """Leaderboard with optional class filter."""
    class_filter = request.args.get('class', 'all')
    conn = get_db_connection()
    cursor = conn.cursor()
    if class_filter != 'all':
        cursor.execute('SELECT id, name, xp, level, medals, class_level, board FROM users WHERE class_level LIKE ? ORDER BY xp DESC',
                       (f'%{class_filter}%',))
    else:
        cursor.execute('SELECT id, name, xp, level, medals, class_level, board FROM users ORDER BY xp DESC')
    users = cursor.fetchall()
    conn.close()
    return render_template('leaderboard.html', users=users, class_filter=class_filter)




if __name__ == '__main__':
    init_db()
    app.run(debug=True)
