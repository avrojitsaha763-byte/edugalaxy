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

# --- COMPREHENSIVE MULTI-BOARD SYLLABUS DATABASE (2025-26 Curriculum) ---
SYLLABUS_DB = {
    'CBSE': {
        '1': {
            'english': ['A Happy Child', 'Three Little Pigs', 'After a Bath', 'The Bubble, the Straw and the Shoe', 'One Little Kitten', 'Lalu and Peelu', 'Once I Saw a Little Bird', 'Mittu and the Yellow Mango', 'Merry-Go-Round', 'Circle', 'If I Were an Apple', 'Our Tree', 'A Kite', 'Sundari', 'A Little Turtle', 'The Tiger and the Mosquito', 'Alphabet and phonics', 'Vowels and consonants', 'Blending sounds', 'Two-letter words', 'Three-letter words', 'Naming words', 'Action words', 'Use of A / An', 'Simple sentences', 'Rhymes and short stories', 'Picture reading'],
            'hindi': ['झूला', 'आम की टोकरी', 'आम का पेड़', 'पत्ते ही पत्ते', 'पकौड़ी', 'छुक-छुक गाड़ी', 'रसोईघर', 'चूहों की सभा', 'बंदर और गिलहरी', 'पतंग', 'स्वर', 'व्यंजन', 'मात्राएँ', 'दो अक्षर के शब्द', 'तीन अक्षर के शब्द', 'शब्द निर्माण', 'सरल वाक्य', 'कविता'],
            'math': ['Shapes and Space', 'Numbers 1–9', 'Addition', 'Subtraction', 'Numbers 10–20', 'Time', 'Measurement', 'Numbers 21–50', 'Data Handling', 'Patterns', 'Numbers 1–100', 'Comparing numbers', 'Shapes and patterns', 'Measurement (long/short, heavy/light)', 'Time (day/night)', 'Money (basic idea)']
        },
        '2': {
            'english': ['First Day at School', 'Haldi’s Adventure', 'I Am Lucky', 'I Want', 'A Smile', 'The Wind and the Sun', 'Rain', 'Storm in the Garden', 'Zoo Manners', 'Funny Bunny', 'Mr Nobody', 'Curlylocks and the Three Bears', 'Nouns', 'Pronouns', 'Verbs', 'Adjectives', 'Articles (a, an, the)', 'Prepositions (in, on, under)', 'Sentence formation', 'Reading comprehension', 'Paragraph writing'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'लिंग', 'वचन', 'वाक्य रचना', 'कहानी और कविता'],
            'math': ['What is Long What is Round', 'Counting in Groups', 'How Much Can You Carry', 'Counting in Tens', 'Patterns', 'Footprints', 'Jugs and Mugs', 'Tens and Ones', 'My Funday', 'Add Our Points', 'Lines and Lines', 'Give and Take', 'The Longest Step', 'Numbers up to 1000', 'Addition and subtraction', 'Introduction to multiplication', 'Measurement (length, weight, capacity)', 'Time', 'Money', 'Data handling'],
            'evs': ['My family', 'My body', 'Food we eat', 'Clothes', 'Houses', 'Plants', 'Animals', 'Water and air', 'Transport', 'Festivals and seasons']
        },
        '3': {
            'english': ['Good Morning', 'The Magic Garden', 'Bird Talk', 'Nina and the Baby Sparrows', 'Little by Little', 'The Enormous Turnip', 'Sea Song', 'A Little Fish Story', 'The Balloon Man', 'The Yellow Butterfly', 'Nouns (types)', 'Pronouns', 'Verbs and tenses', 'Adjectives', 'Prepositions', 'Conjunctions', 'Paragraph writing', 'Story writing', 'Reading comprehension'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'विशेषण', 'लिंग और वचन', 'वाक्य निर्माण', 'अनुच्छेद लेखन'],
            'math': ['Where to Look From', 'Fun with Numbers', 'Give and Take', 'Long and Short', 'Shapes and Designs', 'Time Goes On', 'Who is Heavier', 'How Many Times', 'Play with Patterns', 'Jugs and Mugs', 'Can We Share', 'Smart Charts', 'Numbers up to 10,000', 'Addition and subtraction', 'Multiplication', 'Division', 'Fractions', 'Measurement', 'Time and money', 'Geometry'],
            'evs': ['Family and relationships', 'Food and cooking', 'Water', 'Plants', 'Animals', 'Work and occupations', 'Transport', 'Communication'],
            'gk': ['Animals and birds', 'Countries and flags', 'Famous personalities', 'Science facts', 'Sports']
        },
        '4': {
            'english': ['Wake Up', 'Neha’s Alarm Clock', 'Noses', 'The Little Fir Tree', 'Run', 'Nasruddin’s Aim', 'Why', 'Alice in Wonderland', 'Don’t Be Afraid of the Dark', 'Helen Keller', 'Kinds of Nouns (Proper, Common, Collective)', 'Pronouns (Personal, Possessive)', 'Verbs and continuous tenses', 'Adverbs of time and place', 'Prepositions of position', 'Conjunctions (and, but, because)', 'Formal and informal letter writing', 'Descriptive paragraph writing'],
            'hindi': ['संज्ञा के भेद (व्यक्तिवाचक, जातिवाचक, भाववाचक)', 'सर्वनाम के प्रकार', 'क्रिया और काल (वर्तमान, भूत, भविष्य)', 'विशेषण और उसके भेद', 'लिंग और वचन परिवर्तन के नियम', 'लोकोक्तियाँ और मुहावरे', 'रचनात्मक अनुच्छेद लेखन'],
            'math': ['Operations on Large numbers up to Lakhs', 'Advanced Multiplication Techniques', 'Long Division Methods', 'Equivalent Fractions and Addition/Subtraction of Fractions', 'Geometry: Lines, Rays, Angles, and Polygons', 'Measurement Conversions: Length, Mass, Capacity', 'Data handling: Tally Marks and Pictographs'],
            'evs': ['Plants: Structure, Function, and Adaptation', 'Animals: Habitats and Behaviors', 'Human Body: Food, Digestion, and Nutrition', 'Air, Water, and Weather Cycles', 'Our Environment and Ecosystems', 'Natural Resources: Renewable and Non-renewable'],
            'sst': ['The Earth, Globe, and Latitudes/Longitudes', 'Reading Maps and Directions', 'India: Physical Features and the 28 States', 'Environment Protection and Pollution Control'],
            'gk': ['Important National and International Days', 'Famous Historical Personalities', 'Great Inventions and Discoveries', 'World Geography Facts'],
            'computer': ['Introduction to Computers and Generations', 'Input, Output, and Storage Devices', 'Advanced Paint Program Tools', 'Word Processor: Formatting and Editing', 'Internet Basics and Web Browsers']
        },
        '5': {
            'english': ['Ice-Cream Man', 'Wonderful Waste', 'Teamwork', 'Flying Together', 'My Shadow', 'Robinson Crusoe', 'Crying', 'My Elder Brother', 'The Lazy Frog', 'Rip Van Winkle', 'Comprehensive Parts of Speech Revision', 'Perfect and Continuous Tenses', 'Adverbs of Manner, Degree, and Frequency', 'Coordinating and Subordinating Conjunctions', 'Prepositions of Time and Movement', 'Formal Letter and Email Writing', 'Creative Story Writing and Plot Formatting'],
            'hindi': ['संज्ञा और उसके सभी विस्तृत भेद', 'सर्वनाम के छह प्रकार और उनका प्रयोग', 'क्रिया और काल के सभी उपभेद', 'मुहावरों का वाक्यों में सटीक प्रयोग', 'गहन रचनात्मक अनुच्छेद लेखन', 'औपचारिक और अनौपचारिक पत्र लेखन की कला'],
            'math': ['Operations on Large numbers up to Crores', 'Multiplication and Division of Fractions', 'Decimals, Percentages, and their Applications', 'Advanced Geometry: Angles, Triangles, Circles, and Symmetry', 'Measurement: Area, Perimeter, and Volume Calculations', 'Data handling: Bar Graphs and Pie Charts'],
            'evs': ['Flora and Fauna: Interdependence of Plants and Animals', 'Conservation of Natural Resources and Fossil Fuels', 'Global Environment Issues and Solutions', 'Human Body Systems: Respiratory, Circulatory, and Nervous'],
            'sst': ['The Earth and our Solar System', 'The Early Human Civilizations: Indus Valley, Mesopotamia', 'India: Our Glorious Culture, Heritage, and Constitution', 'Conservation of Our Environment and Ecology'],
            'gk': ['World Geography and Continents', 'Space, Planets, and Universe', 'Famous Scientists and their Contributions', 'Global Sports and Tournaments'],
            'computer': ['Computer Hardware, Software, and Architecture', 'Understanding Operating Systems (Windows/Linux)', 'Word Processing: Tables, Mail Merge', 'Presentation Software: Slides, Animations, Transitions', 'Internet Safety, Netiquette, and Cyber Security']
        }
    },
    'ICSE': {
        '1': {
            'english': ['Alphabet and phonics', 'Naming words', 'Action words', 'Use of A / An', 'Simple sentences', 'Rhymes and stories'],
            'math': ['Numbers', 'Addition', 'Subtraction', 'Shapes', 'Measurement'],
            'evs': ['Myself', 'My family', 'Plants', 'Animals', 'Food']
        },
        '2': {
            'english': ['Nouns', 'Pronouns', 'Verbs', 'Adjectives', 'Sentences'],
            'math': ['Numbers up to 1000', 'Addition', 'Subtraction', 'Multiplication'],
            'evs': ['Body parts', 'Food', 'Plants', 'Animals'],
            'gk': ['Animals and birds', 'Countries', 'Sports']
        },
        '3': {
            'english': ['Parts of speech', 'Tenses', 'Adverbs', 'Composition', 'Letter writing'],
            'hindi': ['संज्ञा', 'सर्वनाम', 'क्रिया', 'विशेषण', 'अनुच्छेद'],
            'math': ['Numbers', 'Multiplication and division', 'Fractions', 'Geometry', 'Measurement'],
            'evs': ['Plants', 'Animals', 'Human body', 'Environment'],
            'sst': ['Earth and maps', 'History basics', 'India'],
            'gk': ['World knowledge', 'Science facts', 'Current affairs'],
            'computer': ['Computer basics', 'Paint', 'Word processing', 'Internet']
        },
        '4': {
            'english': ['Comprehensive Parts of Speech (Noun, Pronoun, Verb, Adjective, Adverb)', 'Tenses: Present, Past, Future', 'Adverbs of Time, Place, Manner', 'Structured Composition Writing', 'Formal and Informal Letter Writing'],
            'hindi': ['संज्ञा और उसके भेद', 'सर्वनाम के प्रकार', 'सकर्मक और अकर्मक क्रिया', 'विशेषण की विशेषताएँ', 'रचनात्मक अनुच्छेद लेखन'],
            'math': ['Advanced Numbers and Operations', 'Multiplication and Long Division', 'Introduction to Fractions and Equivalents', 'Geometry: Lines, Angles, Polygons', 'Measurement: Length, Mass, Capacity'],
            'evs': ['Plants: Photosynthesis and Parts', 'Animals: Habitats, Herbivores, Carnivores', 'Human Body: Organ Systems Overview', 'Environment: Ecosystems and Conservation'],
            'sst': ['Earth, Maps, Latitudes, and Longitudes', 'History basics: Early Man and Tools', 'India: Physical and Political Divisions'],
            'gk': ['World knowledge: Continents and Oceans', 'Science facts: Solar System and Energy', 'Current affairs and Important Events'],
            'computer': ['Computer Component basics (Hardware/Software)', 'Advanced Paint Tools', 'Word processing: Formatting text', 'Internet: Browsers and Searches']
        },
        '5': {
            'english': ['Detailed Study of Parts of Speech and Conjunctions', 'Perfect and Continuous Tenses', 'Adverbs of Frequency and Degree', 'Advanced Composition and Essay Writing', 'Official Letter Writing and Emails'],
            'hindi': ['संज्ञा, सर्वनाम, विशेषण और क्रिया का विस्तृत व्याकरण', 'काल के सभी भेद', 'मुहावरे और लोकोक्तियाँ', 'विस्तृत अनुच्छेद और निबंध लेखन', 'पत्र लेखन'],
            'math': ['Large Numbers, HCF, and LCM', 'Multiplication and Division Check Methods', 'Operations on Fractions and Decimals', 'Geometry: Properties of Triangles and Circles', 'Measurement: Area, Perimeter, and Volume'],
            'evs': ['Plants: Reproduction and Dispersal of Seeds', 'Animals: Interdependence and Food Chains', 'Human Body: Skeletal and Muscular Systems', 'Environment: Pollution, Global Warming, and Solutions'],
            'sst': ['Earth structure, Maps, and Map Reading', 'History: The Ancient Civilizations', 'India: Government, Constitution, and Culture'],
            'gk': ['World knowledge: Capitals, Currencies, and Landmarks', 'Science facts: Human Body and Physics basics', 'Current affairs affecting the World'],
            'computer': ['Computer Architecture basics', 'Flowcharts and Algorithms', 'Word processing: Advanced formatting', 'Internet Protocols and Cybersecurity']
        }
    },
    'WBSE': {
        '1': {
            'bengali': ['বর্ণমালা', 'স্বরবর্ণ', 'ব্যঞ্জনবর্ণ', 'শব্দ গঠন', 'ছড়া'],
            'math': ['সংখ্যা', 'যোগ', 'বিয়োগ', 'আকার'],
            'evs': ['আমার পরিবার', 'গাছপালা', 'প্রাণী']
        },
        '2': {
            'bengali': ['শব্দ গঠন', 'বাক্য গঠন', 'গল্প'],
            'math': ['সংখ্যা', 'যোগ ও বিয়োগ', 'গুণ'],
            'evs': ['গাছ', 'প্রাণী', 'জল'],
            'gk': ['পশু', 'পাখি', 'দেশ']
        },
        '3': {
            'bengali': ['বিশেষ্য', 'সর্বনাম', 'ক্রিয়া'],
            'english': ['Nouns', 'Verbs', 'Sentences'],
            'math': ['Numbers', 'Multiplication', 'Division'],
            'evs': ['Environment', 'Plants', 'Animals'],
            'gk': ['Countries', 'Famous people']
        },
        '4': {
            'bengali': ['পদ পরিচয় (বিশেষ্য, বিশেষণ, সর্বনাম, অব্যয়, ক্রিয়া)', 'সঠিক বাক্য রচনা ও গঠনশৈলী', 'বোধ পরীক্ষণ ও অনুচ্ছেদ লেখা'],
            'english': ['Parts of speech: Identification and Usage', 'Tenses: Simple and Continuous Forms', 'Guided Composition and Paragraph Writing'],
            'math': ['Fractions: Addition and Subtraction', 'Decimals: Introduction and Place Value', 'Geometry: Basic 2D Shapes and Angles'],
            'evs': ['Nature: Ecosystems and Weather', 'Animals: Diversity and Habitats', 'Environment: Pollution and Waste Management'],
            'sst': ['Geography of India: Mountains, Rivers, Plains', 'Reading Maps correctly', 'History basics: Independence Movement Overview'],
            'gk': ['Science facts: Basic Physics and Biology', 'Geography: Continents and Oceans'],
            'computer': ['Computer basics and working principles', 'MS Paint Drawing Options', 'Word processor text styling', 'Introduction to the Internet']
        },
        '5': {
            'bengali': ['বিস্তারিত পদ পরিচয় এবং সমাস', 'জটিল ও যৌগিক বাক্য রচনা', 'বিশ্লেষণমূলক অনুচ্ছেদ ও প্রবন্ধ লেখা'],
            'english': ['Parts of speech in complex sentences', 'Tenses: Perfect and Perfect Continuous', 'Creative Composition, Essays, and Letters'],
            'math': ['Fractions: Multiplication and Division', 'Decimals: Advanced Operations and Percentages', 'Geometry: Triangles, Circles, and Symmetry'],
            'evs': ['Nature: Conservation and Natural Resources', 'Animals: Food Web and Adaptations', 'Environment: Global Warming and Sustainability'],
            'sst': ['India: Government and Constitution Structure', 'Advanced Maps and Topography', 'History: Ancient Empires and Heritage'],
            'gk': ['Advanced Science facts and Space', 'World Geography and Political Boundaries'],
            'computer': ['Computer Memory and Generations', 'Multimedia and PowerPoint basics', 'Word processor Mail Merge', 'Internet Email and E-safety']
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
    if not user:
        session.clear()
        conn.close()
        return redirect(url_for('login'))

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
    if not user:
        session.clear()
        conn.close()
        return redirect(url_for('login'))
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
    
    t_low = topic.lower()

    # ─── STORYBOOK (Paginated) ──────────────────────────────────────
    story_pages = []
    if 'math' in subject:
        story_pages.append({"text": f"Welcome to the Math Dojo! Today {char['name']} is going to teach you all about {topic}.", "audio": f"Welcome to the Math Dojo! Today I will teach you about {topic}."})
        story_pages.append({"text": f"Did you know? Mathematics is the language of the universe. {topic} helps us solve real-world problems every single day!", "audio": f"Did you know? Mathematics is the language of the universe. {topic} helps us solve real problems!"})
        story_pages.append({"text": f"Let's look at an example. If you have 3 apples and you get 2 more, you use math to know you have 5! The concept of {topic} is just as powerful.", "audio": f"For example, if you have 3 apples and get 2 more, you have 5. {topic} is just as powerful!"})
        story_pages.append({"text": f"Now, let's practice! {char['catchphrase']} Always remember to double-check your work.", "audio": f"Now let's practice! {char['catchphrase']} Remember to double check your work."})
    elif 'english' in subject or 'hindi' in subject or 'bengali' in subject:
        story_pages.append({"text": f"Ahoy! {char['name']} is ready to explore the magic of words with you. Our treasure today is: {topic}.", "audio": f"Ahoy! I am ready to explore words with you. Today we learn {topic}."})
        story_pages.append({"text": f"Language helps us communicate our feelings and stories. A solid grasp of {topic} will make you a master storyteller!", "audio": f"Language helps us communicate. Learning {topic} makes you a master storyteller!"})
        story_pages.append({"text": f"For instance, every sentence needs structure. Understanding {topic} is like finding the map to the One Piece of grammar.", "audio": f"Every sentence needs structure. {topic} is the map to grammar."})
        story_pages.append({"text": f"Repeat out loud: '{topic}'! {char['catchphrase']} You're doing great.", "audio": f"Repeat out loud: {topic}. {char['catchphrase']} You're doing great."})
    elif 'science' in subject or 'evs' in subject:
        story_pages.append({"text": f"Get ready to power up! {char['name']} is here to guide you through the wonders of {topic}.", "audio": f"Get ready to power up! I will guide you through {topic}."})
        story_pages.append({"text": f"Science explains how everything around us works, from the smallest atom to the biggest star.", "audio": "Science explains how everything around us works."})
        story_pages.append({"text": f"When we study {topic}, we can predict what will happen in nature and even create new inventions!", "audio": f"Studying {topic} lets us predict nature and invent new things!"})
        story_pages.append({"text": f"Keep observing the world! {char['catchphrase']} Your curiosity is your greatest superpower.", "audio": f"Keep observing! {char['catchphrase']} Curiosity is your superpower."})
    else:
        story_pages.append({"text": f"{char['name']} says hello! Today's grand adventure is all about {topic}.", "audio": f"Hello! Today's adventure is {topic}."})
        story_pages.append({"text": f"Learning about {topic} helps us understand our world, our history, and our society better.", "audio": f"Learning {topic} helps us understand the world better."})
        story_pages.append({"text": f"Every fact you learn makes your brain stronger. So let's dive into {topic} together!", "audio": f"Every fact makes your brain stronger. Let's dive into {topic}!"})
        story_pages.append({"text": f"Fantastic! {char['catchphrase']} Let's keep moving forward!", "audio": f"Fantastic! {char['catchphrase']} Let's keep moving forward!"})


    # ─── ADVENTURE GAME ─────────────────────────────────────────────
    if 'math' in subject:
        num1 = random.randint(1, 10); num2 = random.randint(1, 10)
        game_data = {'type': 'math_catch', 'target': 'numbers', 'equation': f'{num1} + {num2} = ?', 'correct': str(num1+num2), 'wrong': [str(num1+num2+1), str(num1+num2-1), str(num1+num2+2)]}
    elif 'english' in subject:
        game_data = {'type': 'word_catch', 'target': 'letters', 'word': topic.split()[0].upper(), 'wrong': ['Z','X','Q', 'W']}
    elif 'science' in subject or 'evs' in subject:
        game_data = {'type': 'dodger', 'target': 'energy', 'avoid': 'pollution', 'topic': topic}
    else:
        game_data = {'type': 'collect', 'itemName': topic.split()[0], 'topic': topic}

    # ─── PUZZLE DATA ────────────────────────────────────────────────
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

    # ─── EXPERIMENT Type & Steps ─────────────────────────────────────
    if any(k in t_low for k in ['water', 'rain', 'evapor', 'cloud']):
        exp_type = 'water_cycle'
        exp_steps = ['Apply heat to the ocean to Evaporate', 'Cool the vapour to Condense into Clouds', 'Let it rain! (Precipitation)', 'Collect the water back.']
    elif any(k in t_low for k in ['plant', 'seed', 'grow', 'leaf', 'tree', 'photosynthesis']):
        exp_type = 'plant_growth'
        exp_steps = ['Plant seed in soil', 'Drag water can to soil', 'Drag sun to shine light', 'Watch the flower bloom!']
    elif any(k in t_low for k in ['magnet', 'attract', 'repel']):
        exp_type = 'magnetism'
        exp_steps = ['Place Magnet A', 'Drag Magnet B (North) close to A (South) -> Attract', 'Flip Magnet B (South) close to A (South) -> Repel', 'Observe magnetic fields.']
    elif 'math' in subject:
        exp_type = 'math_balance'
        exp_steps = ['Place 5 weights on the left scale', 'Place weights on right scale until balanced', 'Balance achieved!', 'Equation solved.']
    else:
        exp_type = 'chemical_reaction'
        exp_steps = ['Drag Flask A (Vinegar)', 'Pour Baking Soda into Flask A', 'Watch the chemical reaction!', 'Observe the CO2 Gas.']

    # ─── ORAL VOICE TEST ────────────────────────────────────────────
    voice_map = {
        'math':     f"Let's practice! What is 5 plus 5? Please say: The answer is 10.",
        'english':  f"Can you say this tongue twister? She sells seashells by the seashore.",
        'hindi':    f"कृपया कहें: मुझे {topic} पढ़ना पसंद है।",
        'bengali':  f"দয়া করে বলুন: আমি {topic} ভালোবাসি।",
        'science':  f"What gas do we breathe? Please say: Oxygen.",
        'evs':      f"How can we help the Earth? Please say: Plant more trees.",
        'sst':      f"What is the capital of India? Please say: New Delhi.",
        'gk':       f"Who is known as the Father of the Nation? Please say: Mahatma Gandhi.",
        'computer': f"What is the brain of the computer? Please say: The C P U.",
    }
    voice_question = voice_map.get(subject, f"Please say: I am learning about {topic}.")
    
    # Simple expected keyword matcher
    expected_words = []
    if 'math' in subject: expected_words = ['10', 'ten']
    elif 'english' in subject: expected_words = ['seashells', 'seashore']
    elif 'hindi' in subject: expected_words = ['पसंद']
    elif 'science' in subject: expected_words = ['oxygen']
    elif 'evs' in subject: expected_words = ['trees', 'plant']
    elif 'sst' in subject: expected_words = ['delhi']
    elif 'gk' in subject: expected_words = ['gandhi']
    elif 'computer' in subject: expected_words = ['cpu', 'processor']
    else: expected_words = [topic.split()[0].lower(), 'learning']


    # ─── 3D WORLD ASSESSMENT ────────────────────────────────────────
    three_d_test = {
        'mcq': [
            {'q': f"Which of the following belongs to {topic}?", 'options': [f"Concept of {topic}", "Something unrelated", "Another wrong answer"], 'ans': 0},
            {'q': f"Why is {topic} important?", 'options': ["It is not important", "It helps us understand the world", "To waste time"], 'ans': 1}
        ],
        'subjective': {
            'q': f"Explain in your own words what you learned about {topic} today."
        }
    }


    content = {
        'character': char,
        'topic': topic,
        'subject': subject,
        'storybook': {
            'pages': story_pages
        },
        'adventure': {
            'objective': f"Play the game for {topic}!",
            'game_data': game_data,
            'xp_reward': 50
        },
        'puzzle': {
            'p_type':     p_type,
            'question': p_question,
            'items':    p_items,
            'answer':   p_answer,
            'xp_reward': 40
        },
        'experiment': {
            'name':         f"{topic} Interactive Lab",
            'type':         exp_type,
            'instructions': f"Perform the experiment by following the interactive steps!",
            'steps':        exp_steps,
            'xp_reward': 60
        },
        'voice': {
            'sentence': voice_question,
            'expected_words': expected_words,
            'hint':     f"Speak clearly into the microphone.",
            'xp_reward': 30
        },
        'assessment': three_d_test
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
    if not user:
        session.clear()
        conn.close()
        return redirect(url_for('login'))
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
