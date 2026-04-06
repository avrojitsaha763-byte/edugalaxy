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
from typing import List, Dict, Any, Tuple, cast
import itertools
import pypdf

app = Flask(__name__)
app.secret_key = 'edugalaxy_secret_key_2024'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
# --- SCIFI GAMIFIED ACHIEVEMENTS (The Galactic Collection) ---
ACHIEVEMENTS = [
    {'id': 'first_step',   'name': 'Initiate Pilot',   'icon': '🛰️', 'desc': 'Complete your first galactic jump',     'xp_req': 1,    'color': '#00ff87'},
    {'id': 'bronze_mind',  'name': 'Cosmic Cadet',     'icon': '🥉', 'desc': 'Accumulate 100 Starlight XP',          'xp_req': 100,  'color': '#cd7f32'},
    {'id': 'silver_mind',  'name': 'Star Commander',   'icon': '🥈', 'desc': 'Accumulate 300 Starlight XP',          'xp_req': 300,  'color': '#c0c0c0'},
    {'id': 'gold_mind',    'name': 'Galactic Hero',    'icon': '🥇', 'desc': 'Accumulate 600 Starlight XP',          'xp_req': 600,  'color': '#ffd700'},
    {'id': 'diamond_mind', 'name': 'Universe Master',  'icon': '💎', 'desc': 'Accumulate 1000 Starlight XP',         'xp_req': 1000, 'color': '#a5f3fc'},
    {'id': 'streak_3',     'name': 'Hyper-Jump',       'icon': '🔥', 'desc': 'Execute 3 jumps in successsion',       'xp_req': 50,   'color': '#f97316'},
    {'id': 'polymath',     'name': 'Multi-Versal',     'icon': '🌌', 'desc': 'Research 3 distinct planets',          'xp_req': 150,  'color': '#a78bfa'},
    {'id': 'scientist',    'name': 'Tech Specialist',  'icon': '🤖', 'desc': 'Complete 5 virtual simulations',       'xp_req': 200,  'color': '#2dd4bf'},
    {'id': 'storyteller',  'name': 'Lore Keeper',      'icon': '📜', 'desc': 'Decode 5 history scrolls',             'xp_req': 50,   'color': '#60a5fa'},
    {'id': 'voice_hero',   'name': 'Wave Master',      'icon': '📡', 'desc': 'Complete 3 voice-sync codes',          'xp_req': 75,   'color': '#f472b6'},
    {'id': 'puzzle_master','name': 'Code Breaker',     'icon': '🔐', 'desc': 'De-encrypt 5 security puzzles',        'xp_req': 100,  'color': '#facc15'},
    {'id': 'explorer',     'name': 'Galaxy Explorer',  'icon': '🛸', 'desc': 'Navigate to Sector 7 Command',         'xp_req': 20,   'color': '#22d3ee'},
]

DAILY_CHALLENGES = [
    {'q': 'What is the speed of light approx? (km/s)',  'ans': '300000',     'subject': 'science', 'xp': 50},
    {'q': 'Complete the code: 1, 1, 2, 3, 5, ?',       'ans': '8',          'subject': 'math',    'xp': 40},
    {'q': 'Which element is needed for fusion?',       'ans': 'hydrogen',   'subject': 'science', 'xp': 40},
    {'q': 'Who wrote "A Brief History of Time"?',      'ans': 'stephen hawking','subject': 'gk',   'xp': 50},
    {'q': 'Synonym for "Vast" (Starts with E)',        'ans': 'enormous',   'subject': 'english', 'xp': 30},
    {'q': 'Square root of 144?',                       'ans': '12',         'subject': 'math',    'xp': 30},
    {'q': 'Nearest galaxy to Milky Way?',              'ans': 'andromeda',  'subject': 'science', 'xp': 50},
    {'q': 'Solve: 15% of 200?',                        'ans': '30',         'subject': 'math',    'xp': 40},
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
            medals TEXT DEFAULT 'None',
            inventory TEXT DEFAULT '[]',
            pet_data TEXT DEFAULT '{"type": "None", "level": 1, "xp": 0}',
            skill_tree TEXT DEFAULT '{}',
            avatar_url TEXT DEFAULT 'default_avatar.png'
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
        cursor.execute('ALTER TABLE users ADD COLUMN inventory TEXT DEFAULT "[]"')
        cursor.execute('ALTER TABLE users ADD COLUMN pet_data TEXT DEFAULT \'{"type": "None", "level": 1, "xp": 0}\'')
        cursor.execute('ALTER TABLE users ADD COLUMN skill_tree TEXT DEFAULT "{}"')
        cursor.execute('ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT "default_avatar.png"')
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

    # Parse JSON fields for template convenience
    try:
        pet_data = json.loads(user['pet_data'])
    except:
        pet_data = {"type": "None", "level": 1, "xp": 0}

    try:
        inventory = json.loads(user['inventory'])
    except:
        inventory = []

    return render_template('dashboard.html',
        user=user, subjects=subjects, progress=progress,
        achievements=achievements, daily_challenge=daily_challenge,
        daily_done=bool(daily_done), recent=recent, activity=activity,
        xp_progress=xp_progress, next_level_xp=next_level_xp,
        pet_data=pet_data, inventory=inventory)


@app.route('/syllabus/<class_level>/<subject>/<path:filename>')
def serve_syllabus(class_level, subject, filename):
    """Serve the PDF syllabus files safely."""
    directory = os.path.join(app.root_path, 'Syllabus', f'class{class_level}', subject)
    return send_from_directory(directory, filename)

@app.route('/serve_video/<class_level>/<subject>/<path:filename>')
def serve_video(class_level, subject, filename):
    """Serve the MP4 syllabus video files safely."""
    directory = os.path.join(app.root_path, 'Syllabus', f'class{class_level}', subject)
    # Ensure correct mime type for video streaming
    return send_from_directory(directory, filename, mimetype='video/mp4')

@app.route('/learn/interactive', methods=['GET', 'POST'])
def learn_interactive():
    """Main interactive learning portal - Storybook & Embedded Video View."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    subject = request.form.get('subject') if request.method == 'POST' else request.args.get('subject')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    if not user:
        session.clear()
        conn.close()
        return redirect(url_for('login'))
    conn.close()

    class_match = re.search(r'Class\s*(\d+)', user['class_level'])
    class_num = class_match.group(1) if class_match else '1'

    # Subject Folder Mapping (matching filesystem case)
    folder_map = {
        'math': 'Maths', 'english': 'English', 'hindi': 'Hindi', 
        'evs': 'EVS', 'science': 'EVS', 'arts': 'Arts', 'computer': 'Computer'
    }
    
    if not subject:
        subject = 'math'
        
    subject_folder = folder_map.get(subject.lower(), subject.title())
    syllabus_dir = os.path.join(app.root_path, 'Syllabus', f'class{class_num}', subject_folder)
    
    chapters: List[Dict[str, Any]] = []
    if os.path.exists(syllabus_dir):
        files = [f for f in os.listdir(syllabus_dir) if f.endswith('.pdf')]
        # Sort files assuming names like "chapter 1.pdf", "chapter 2.pdf"
        files.sort(key=lambda x: int(match.group()) if (match := re.search(r'\d+', x)) else 0)
        
        # Vetted, Ultra-Reliable Global Video IDs (Math test cases)
        yt_map = {
            'math': ['jNQXAC9IVRw', 'ncORPosDrjI', 'X0eRtvhS04g'],
            'english': ['bellPQKxH0M', 'W3LqD9-3yFk', 'r5z-l8U2874'],
            'hindi': ['zMiyG7CIn8o', 'M6i-2U0HjW4', 'B2A6b4X1K7Q'],
            'evs': ['f-lIup36jEY', 'WfGZ5v1X1_o', 'uabXGf1hmsU']
        }
        video_id_list = yt_map.get(subject.lower(), ['jNQXAC9IVRw']) # 'Me at the zoo' fallback explicitly allows embedding
        
        all_videos = [f for f in os.listdir(syllabus_dir) if f.lower().endswith('.mp4')]
        
        for idx, f in enumerate(files):
            # Extract number from PDF name like "chapter  (1).pdf" or "unit 1.pdf"
            num_match = re.search(r'\d+', f)
            num = num_match.group() if num_match else str(idx + 1)
            
            # Find all local videos related to this chapter number
            chapter_vids = []
            
            # Robust pattern: matches "chapter{num}" exactly at start of filename
            # Handles: chapter1.mp4, chapter1 part1.mp4, chapter1 part (1).mp4, chapter10.mp4
            # Uses word-boundary approach: chapter{num} must be followed by end, space, dot, or '('
            padded_num = str(int(num))  # normalise e.g. "01" -> "1"
            # Pattern: (chapter|unit|lesson) + optional-space + exact-number + (end|space|dot|'(')
            exact_pattern = re.compile(
                rf'^(?:chapter|unit|lesson|videoplayback)\s*0*{padded_num}(?:\s|\.|_|\(|$)',
                re.I
            )
            
            matches = []
            for v_name in all_videos:
                v_lower = v_name.lower().strip()
                if exact_pattern.match(v_lower):
                    matches.append(v_name)
            
            # Sort so part1 < part2 etc. Natural sort by embedded numbers
            def _nat_sort_key(s):
                return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]
            matches.sort(key=_nat_sort_key)
            
            for v_name in matches:
                chapter_vids.append({
                    'url': url_for('serve_video', class_level=class_num, subject=subject_folder, filename=v_name),
                    'is_local': True,
                    'title': v_name.replace('.mp4', '').replace('(', '').replace(')', '').title()
                })
            
            # Fallback to YouTube if no local videos found
            if not chapter_vids:
                # Use a specific index safely
                v_idx = idx % len(video_id_list)
                # Cast to Any to prevent "non-class" indexing error in some linters
                vid_id = cast(Any, video_id_list)[v_idx]
                chapter_vids.append({
                    'url': f"https://www.youtube.com/embed/{vid_id}",
                    'is_local': False,
                    'title': "Global Transmission"
                })
            
            chapters.append({
                'title': f.replace('.pdf', '').title(),
                'filename': f,
                'pdf_url': url_for('serve_syllabus', class_level=class_num, subject=subject_folder, filename=f),
                'videos': chapter_vids,
                'video_url': chapter_vids[0]['url'],
                'is_local': chapter_vids[0]['is_local']
            })
    
    if not chapters:
        # Fallback if no PDFs found
        chapters = [{'title': 'Chapter 1: Basics', 'filename': '', 'pdf_url': '', 'video_id': 'Y7zZ4Tzhj7Q'}]

    return render_template('learn_interactive.html', user=user, subject=subject, chapters=chapters)

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

    # ─── STORYBOOK (Paginated & Narrative) ──────────────────────────
    story_pages = []

    # Base Narrative Template based on Subject
    if 'math' in subject:
        intro = f"Welcome to the Math Dojo! {char['name']} is ready to master {topic} with you."
        story_pages.append({"text": intro, "audio": intro})
        story_pages.append({"text": f"In the world of numbers, {topic} is a powerful tool. It lets us measure, calculate, and build amazing things!", "audio": f"In the world of numbers, {topic} is a powerful tool!"})
        story_pages.append({"text": f"Imagine you are an architect. To build a skyscraper, you'd need the logic of {topic} to ensure every floor is perfect!", "audio": f"To build a skyscraper, you'd need the logic of {topic}."})
        story_pages.append({"text": f"Let's dive into some calculations. {char['catchphrase']} Focus your mind, Cadet!", "audio": f"Let's dive in. {char['catchphrase']} Focus your mind!"})
    elif 'science' in subject or 'evs' in subject:
        intro = f"Power up! {char['name']} is taking you to the Science Lab to explore {topic}."
        story_pages.append({"text": intro, "audio": intro})
        story_pages.append({"text": f"The universe is full of mysteries, and {topic} is one of the most fascinating ones!", "audio": f"The universe is full of mysteries, and {topic} is fascinating!"})
        story_pages.append({"text": f"Whether it's the atoms in your body or the stars in the sky, everything follows the laws of {topic}.", "audio": f"Everything follows the laws of {topic}."})
        story_pages.append({"text": f"Observe closely. {char['catchphrase']} Science is all about discovery!", "audio": f"Observe closely. {char['catchphrase']} Science is about discovery!"})
    elif 'english' in subject or 'hindi' in subject or 'bengali' in subject:
        intro = f"Ahoy! {char['name']} is your guide through the Enchanted Library. Today's book: {topic}."
        story_pages.append({"text": intro, "audio": intro})
        story_pages.append({"text": f"Words are like magic spells. Using {topic} correctly makes you a powerful wizard of communication!", "audio": f"Words are like spells. {topic} makes you a wizard of communication!"})
        story_pages.append({"text": f"Each sentence we build with {topic} tells a part of our story. Let's make it a masterpiece!", "audio": f"Each sentence with {topic} tells a story. Let's make it a masterpiece!"})
        story_pages.append({"text": f"Say it with me! {char['catchphrase']} You're becoming a master linguist.", "audio": f"Say it with me! {char['catchphrase']}"})
    else:
        intro = f"Greetings! {char['name']} is here for our daily briefing on {topic}."
        story_pages.append({"text": intro, "audio": intro})
        story_pages.append({"text": f"Understanding {topic} gives you a window into how the world works and our place in it.", "audio": f"Understanding {topic} shows how the world works."})
        story_pages.append({"text": f"Every great hero in history started by learning the basics, just like you are doing with {topic}.", "audio": f"Every hero started by learning basics, like {topic}."})
        story_pages.append({"text": f"Stay curious! {char['catchphrase']} The more you know, the further you'll go!", "audio": f"Stay curious! {char['catchphrase']}"})


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
        p_items = words[:6]  # type: ignore
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
        p_items = extras[:5] + [topic]  # type: ignore
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

@app.route('/skill_tree')
def skill_tree():
    """Skill Tree progression page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('skill_tree.html', user=user)


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


@app.route('/api/skill_tree', methods=['GET', 'POST'])
def api_skill_tree():
    """Manage user skill tree progression."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.json
        skill_id = data.get('skill_id')
        cursor.execute('SELECT skill_tree, xp FROM users WHERE id = ?', (session['user_id'],))
        user_row = cursor.fetchone()
        skill_tree = json.loads(user_row['skill_tree'])

        # Simple unlocking logic - can be expanded
        if skill_id not in skill_tree:
            skill_tree[skill_id] = {'unlocked_at': datetime.datetime.now().isoformat()}
            cursor.execute('UPDATE users SET skill_tree = ? WHERE id = ?', (json.dumps(skill_tree), session['user_id']))
            conn.commit()
        conn.close()
        return json.dumps({'status': 'success', 'skill_tree': skill_tree})

    cursor.execute('SELECT skill_tree FROM users WHERE id = ?', (session['user_id'],))
    tree = cursor.fetchone()['skill_tree']
    conn.close()
    return json.dumps(json.loads(tree))

@app.route('/api/claim_reward', methods=['POST'])
def api_claim_reward():
    """Grant random items/rewards from treasure chests."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401

    rewards = [
        {'id': 'starlight_fragment', 'name': 'Starlight Fragment', 'icon': '✨', 'xp': 20},
        {'id': 'cosmic_shard', 'name': 'Cosmic Shard', 'icon': '💎', 'xp': 50},
        {'id': 'warp_fuel', 'name': 'Warp Fuel', 'icon': '🚀', 'xp': 30},
    ]
    reward = random.choice(rewards)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT inventory, xp FROM users WHERE id = ?', (session['user_id'],))
    user_data = cursor.fetchone()
    inventory = json.loads(user_data['inventory'])
    inventory.append(reward)

    new_xp = user_data['xp'] + reward['xp']
    cursor.execute('UPDATE users SET inventory = ?, xp = ?, level = ? WHERE id = ?',
                   (json.dumps(inventory), new_xp, calculate_level(new_xp), session['user_id']))
    conn.commit()
    conn.close()

    return json.dumps({'status': 'success', 'reward': reward, 'new_xp': new_xp})

@app.route('/api/pet/interact', methods=['POST'])
def api_pet_interact():
    """Interact with the learning pet (feed, train)."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401

    data = request.json
    action = data.get('action') # 'feed' or 'train'
    item_id = data.get('item_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT pet_data, inventory FROM users WHERE id = ?', (session['user_id'],))
    user_row = cursor.fetchone()
    pet_data = json.loads(user_row['pet_data'])
    inventory = json.loads(user_row['inventory'])

    if action == 'feed':
        # Check if item exists in inventory
        item_index = next((i for i, item in enumerate(inventory) if item['id'] == item_id), None)
        if item_index is not None:
            item = inventory.pop(item_index)
            pet_data['xp'] += 20
            if pet_data['xp'] >= 100:
                pet_data['level'] += 1
                pet_data['xp'] = 0
                # Evolution Logic
                if pet_data['level'] == 5: pet_data['type'] = 'Alpha'
                elif pet_data['level'] == 10: pet_data['type'] = 'Omega'

            cursor.execute('UPDATE users SET pet_data = ?, inventory = ? WHERE id = ?',
                           (json.dumps(pet_data), json.dumps(inventory), session['user_id']))
            conn.commit()
            conn.close()
            return json.dumps({'status': 'success', 'pet_data': pet_data, 'reward': 'Pet grew stronger!'})
        else:
            conn.close()
            return json.dumps({'status': 'error', 'message': 'Item not found in inventory'})

    conn.close()
    return json.dumps({'status': 'error', 'message': 'Invalid action'})

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


# --- CHAPTER-SPECIFIC DYNAMIC PARSER ---
class ChapterParser:
    @staticmethod
    def parse_pdf(file_path):
        """Extract all text from a PDF file."""
        if not os.path.exists(file_path):
            return ""
        
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
            return ""
        return text

    @staticmethod
    def parse_txt(file_path):
        """Extract structured game data from a chapter text file or PDF."""
        if not os.path.exists(file_path):
            return None
        
        if file_path.lower().endswith('.pdf'):
            text = ChapterParser.parse_pdf(file_path)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
        
        if not text:
            return None

        data = {
            'terms': [],
            'facts': [],
            'tf': [],
            'fill': []
        }
        
        # 1. Extract terms (New words / vocabulary)
        # Look for "New words" or "vocabulary" or "words to know" or "keywords"
        term_sections = re.findall(r'(?:New words|vocabulary|words to know|keywords|Let us speak)\s*[:\-]*\s*(.*?)(?:\n\n|\r\n\r\n|\n[A-Z]|\Z)', text, re.DOTALL | re.IGNORECASE)
        for section in term_sections:
            # Clean up the section
            section = re.sub(r'[\r\n]+', ' ', section)
            # Split by various delimiters common in lists
            words = re.split(r'[|,\t•●○■]', section)
            for w in words:
                w = w.strip().replace('*', '').replace('•', '').replace('●', '').replace('○', '').replace('■', '')
                # Filter for clean words/terms
                if 2 < len(w) < 40 and any(c.isalpha() for c in w):
                    data['terms'].append(w)
        
        # 2. Extract facts/sentences for MCQs
        # For PDF, we just take clean sentences from the whole text if not too many
        sentences = re.split(r'[.!?](?:\s|\n|\r)', text)
        for s in sentences:
            # Clean up the sentence (remove page numbers, weird symbols etc)
            s = s.strip()
            s = re.sub(r'\s+', ' ', s)
            if 30 < len(s) < 200:
                if any(x in s.lower() for x in ['teacher', 'note', 'indd', 'reprint', 'page', 'mridang', 'ncert', 'editor']):
                    continue
                
                # Simple Fact Extraction (avoid questions)
                if not s.strip().endswith('?'):
                    # Check for simple "A is B" patterns
                    is_match = re.search(r'^(.*?)\s+(is|are|was|were|means|has|consists of)\s+(.*)$', s, re.I)
                    if is_match:
                        data['facts'].append((is_match.group(1).strip(), is_match.group(3).strip()))
                    else:
                        if len(data['facts']) < 25:
                            data['facts'].append((s, "True"))

        # 3. Extract Workbook Exercises (Fill in the blanks / True False)
        # Look for patterns like "1. ...", "A. ...", or lines with "/"
        exercise_lines = re.findall(r'(?:[A-Z0-9]\.\s*|●\s*|•\s*)(.*?)(?:\n|\Z)', text)
        for line in exercise_lines:
            line = line.strip()
            if not line: continue
            
            # True/False detection
            if '?' in line:
                data['tf'].append((line, True))
            
            # Fill in the blank detection (Look for underscores or slash options)
            if '___' in line or '/' in line:
                if '/' in line and len(line) < 80:
                    parts = re.split(r'[ /]', line)
                    answer = next((p for p in parts if len(p) > 2), "Answer")
                    data['fill'].append((line, answer))
                else:
                    data['fill'].append((line, "___"))

        # Deduplicate
        data['terms'] = list(dict.fromkeys(data['terms']))
        return data

class UniversalMapper:
    @staticmethod
    def get_asset_path(subject, chapter_name, chapter_index, board='CBSE', class_num='1'):
        """Locate the best available text asset for a given chapter."""
        # Clean inputs
        subject = subject.lower()
        chapter_index = int(chapter_index)
        
        # Priority 1: Syllabus recursive search (Class-specific)
        target_class = f"class{class_num}"
        for root, dirs, files in os.walk('Syllabus'):
            # Path parts like ['Syllabus', 'class5', 'Maths']
            path_parts = [p.lower() for p in root.split(os.sep)]
            
            # Ensure we are in the correct class folder AND subject folder (looser check for subject)
            if target_class in path_parts and any(subject.lower() in p for p in path_parts):
                for f in files:
                    f_low = f.lower()
                    if not (f_low.endswith('.pdf') or f_low.endswith('.txt')):
                        continue
                    
                    # Regex match to find the chapter number
                    # Supports: "chapter (1)", "chapter 1", "chapter  (10)", "unit 1", "1.pdf"
                    target_idx = str(chapter_index + 1)
                    if re.search(rf'(?:chapter|unit|ch|[\s\(])\s*0*{target_idx}(?:[\.\)\s]|$)', f_low) or f_low.startswith(f"{target_idx}."):
                        return os.path.join(root, f)
                    
                    if chapter_name.lower() in f_low:
                        return os.path.join(root, f)
        
        # Priority 2: Fallback to root-level common files (only as legacy support)
        subj_map = {'english': 'eng', 'maths': 'math', 'math': 'math', 'hindi': 'hindi', 'evs': 'evs', 'science': 'sci'}
        prefix = subj_map.get(subject, subject[:3])
        root_file = f"{prefix}_ch{chapter_index + 1}.txt"
        if os.path.exists(root_file) and class_num == '1': # Only for Class 1 fallbacks
            return root_file
        
        return None
        
        return None
        
        return None

CHAPTER_KNOWLEDGE = {
    'math': {
        'Shapes and Space': {
            'terms': ['inside', 'outside', 'above', 'below', 'near', 'far', 'on', 'under', 'top', 'bottom'],
            'facts': [('The cat is sleeping ___ the bed','under'),('Where do you put shoes?','Outside the room'),('The ball is ___ the basket','inside'),('Birds are ___ the tree','on')],
            'tf': [('The red ball is under the bed',True),('We throw garbage inside the dustbin',True),('A furry cat hides below the mat',True),('Above and below are positional words',True)],
            'fill': [('Draw a smile ___ the nose','below'),('Draw eyebrows ___ the eyes','above'),('The furry cat is at the ___ of the car','top')]
        },
        'What is Long? What is Round?': {
            'terms': ['long', 'round', 'roll', 'slide', 'dholak', 'pencil box', 'ball', 'tower'],
            'facts': [('A pencil box is','long'),('A ball is','round'),('A dholak can','roll'),('A striker in carrom','slides')],
            'tf': [('A ball is long',False),('The dholak rolled fast',True),('A pencil box is round',False),('A striker slides on the board',True)],
            'fill': [('The grandmother put the lamb into a ___','dholak'),('My ___ box is long','pencil'),('A ___ is round','ball')]
        },
        'Numbers 1–9': {
            'terms': ['one','two','three','four','five','six','seven','eight','nine','count'],
            'facts': [('1 + 1 =','2'),('2 + 3 =','5'),('The number after 7 is','8'),('5 - 2 =','3'),('4 + 4 =','8')],
            'tf': [('3 + 2 = 5',True),('7 is less than 5',False),('1 is the smallest single digit',True),('9 comes before 8',False)],
            'fill': [('3 + ___ = 7','4'),('___ - 2 = 3','5'),('The number before 6 is ___','5')]
        },
        'Addition': {
            'terms': ['add','sum','plus','total','more','count','together','combine','equal','answer'],
            'facts': [('5 + 3 =','8'),('2 + 7 =','9'),('Adding zero gives','same number'),('4 + 4 =','8'),('6 + 3 =','9')],
            'tf': [('5 + 0 = 5',True),('3 + 4 = 8',False),('Addition makes numbers bigger',True),('2 + 2 = 5',False)],
            'fill': [('7 + ___ = 10','3'),('___ + 5 = 9','4'),('8 + 2 = ___','10')]
        },
        'Subtraction': {
            'terms': ['subtract','minus','less','take away','difference','remain','left','reduce','fewer','remove'],
            'facts': [('9 - 4 =','5'),('7 - 3 =','4'),('Subtracting zero gives','same number'),('10 - 5 =','5'),('8 - 2 =','6')],
            'tf': [('10 - 3 = 7',True),('5 - 5 = 1',False),('Subtraction makes numbers smaller',True),('6 - 2 = 3',False)],
            'fill': [('10 - ___ = 6','4'),('___ - 3 = 5','8'),('9 - 4 = ___','5')]
        },
        'Multiplication': {
            'terms':['multiply','times','product','groups','of','repeated','addition','table','double','triple'],
            'facts':[('3 × 4 =','12'),('5 × 2 =','10'),('Any number × 1 =','same number'),('6 × 0 =','0'),('7 × 3 =','21')],
            'tf':[('5 × 5 = 25',True),('3 × 0 = 3',False),('Multiplication is repeated addition',True),('4 × 2 = 6',False)],
            'fill':[('6 × ___ = 18','3'),('___ × 5 = 25','5'),('8 × 2 = ___','16')]
        },
        'Fractions': {
            'terms':['half','quarter','fraction','numerator','denominator','part','whole','equal','divide','piece'],
            'facts':[('½ means','1 out of 2 parts'),('¼ means','1 out of 4 parts'),('The top number is called','numerator'),('The bottom number is called','denominator'),('2/4 is the same as','1/2')],
            'tf':[('½ is greater than ¼',True),('The denominator is the top number',False),('1/3 means 1 part of 3 equal parts',True),('½ + ½ = ¼',False)],
            'fill':[('In ¾, the numerator is ___','3'),('½ of 10 is ___','5'),('A fraction shows ___ of a whole','part')]
        },
        'Time': {
            'terms':['clock','hour','minute','second','morning','afternoon','evening','night','watch','hands'],
            'facts':[('1 hour has','60 minutes'),('1 day has','24 hours'),('The short hand shows','hours'),('The long hand shows','minutes'),('Noon means','12 PM')],
            'tf':[('1 hour = 60 minutes',True),('The long hand shows hours',False),('Morning comes before afternoon',True),('1 day = 12 hours',False)],
            'fill':[('1 hour = ___ minutes','60'),('The short hand shows the ___','hour'),('12 PM is called ___','noon')]
        },
    },
    'english': {
        'Greetings': {
            'terms': ['morning', 'afternoon', 'evening', 'night', 'namaste', 'hello', 'goodbye', 'meet', 'greet'],
            'facts': [('When I meet someone in the morning, I say','Good morning'),('When I go to bed, I say','Good night'),('When I meet someone in the evening, I say','Good evening'),('Namaste is a','greeting')],
            'tf': [('We say Good Morning at night',False),('Namaste is used to greet others',True),('Good Night is said before sleeping',True),('We say Good Afternoon in the morning',False)],
            'fill': [('When I meet someone in the afternoon, I say Good ___','afternoon'),('When I meet someone, I say ___','Namaste'),('I go to ___ at night','bed')]
        },
        'My Family': {
            'terms': ['mother', 'father', 'brother', 'sister', 'grandmother', 'grandfather', 'aunt', 'uncle', 'sparrow', 'nest'],
            'facts': [('Mama and Papa sparrow were making a','nest'),('Mama sparrow laid','three small eggs'),('Papa sparrow brought','food for babies'),('We are a','family')],
            'tf': [('There were five baby sparrows',False),('A sparrow family lives in a nest',True),('Father sparrow brought food',True),('A family includes brother and sister',True)],
            'fill': [('The baby sparrows grew ___ and bigger','bigger'),('They flew up into the big blue ___','sky'),('Mama sparrow laid three small ___','eggs')]
        },
        'Hop a Little': {
            'terms': ['hop', 'jump', 'stamp', 'skip', 'tap', 'dance', 'twist', 'shake', 'yawn', 'sleep'],
            'facts': [('Hop a little, jump a little, one two','three'),('Stamp a little, skip a little, tap one','knee'),('Dance a little, twist a little, shake your','hand'),('Yawn a little, sleep a little, in your','bed')],
            'tf': [('We tap our knee in the poem',True),('We jump with ten feet',False),('We sleep in our bed',True),('We shake our hand',True)],
            'fill': [('One, two, ___','three'),('Tap one ___','knee'),('Shake your ___','hand')]
        },
        'Nouns': {
            'terms':['noun','name','person','place','animal','thing','proper','common','boy','girl'],
            'facts':[('A noun is a','naming word'),('Dog is a','common noun'),('India is a','proper noun'),('Nouns can be','person, place, animal or thing'),('Common nouns are','general names')],
            'tf':[('A noun is an action word',False),('Delhi is a proper noun',True),('Cat is a common noun',True),('Verbs are naming words',False)],
            'fill':[('A ___ is a naming word','noun'),('India is a ___ noun','proper'),('A ___ names a general thing','common')]
        },
        'Verbs': {
            'terms':['verb','action','run','jump','eat','sleep','play','write','read','sing'],
            'facts':[('A verb is an','action word'),('Run, jump, eat are','verbs'),('Verbs tell us','what someone does'),('Is, am, are are also','verbs'),('Every sentence needs a','verb')],
            'tf':[('A verb shows action',True),('Table is a verb',False),('Run is a verb',True),('Nouns tell what someone does',False)],
            'fill':[('A ___ is an action word','verb'),('The girl ___s to school','walk'),('Birds ___ in the sky','fly')]
        },
        'Adjectives': {
            'terms':['adjective','big','small','tall','short','beautiful','ugly','fast','slow','color'],
            'facts':[('An adjective','describes a noun'),('Big, small, tall are','adjectives'),('Adjectives tell us','more about nouns'),('Colors are','adjectives'),('Adjectives answer','what kind, how many')],
            'tf':[('An adjective describes a noun',True),('Run is an adjective',False),('Red is an adjective',True),('Adjectives are action words',False)],
            'fill':[('An ___ describes a noun','adjective'),('The ___ ball is round','big'),('She has a ___ dress','beautiful')]
        },
        'Pronouns': {
            'terms':['pronoun','he','she','it','they','we','I','you','him','her'],
            'facts':[('A pronoun','replaces a noun'),('He, she, it are','pronouns'),('I and we are','first person pronouns'),('You is a','second person pronoun'),('They is a','third person pronoun')],
            'tf':[('A pronoun replaces a noun',True),('Cat is a pronoun',False),('She is a pronoun',True),('Pronouns are naming words',False)],
            'fill':[('A ___ replaces a noun','pronoun'),('___ is going to school (boy)','He'),('___ are playing (children)','They')]
        },
    },
    'hindi': {
        'स्वर': {
            'terms':['अ','आ','इ','ई','उ','ऊ','ए','ऐ','ओ','औ'],
            'facts':[('हिंदी में स्वर','11 होते हैं'),('अ, आ, इ, ई','स्वर हैं'),('स्वर स्वतंत्र रूप से','बोले जा सकते हैं'),('ऋ भी एक','स्वर है'),('अं और अः','अयोगवाह हैं')],
            'tf':[('हिंदी में 11 स्वर हैं',True),('क एक स्वर है',False),('अ पहला स्वर है',True),('स्वर 5 होते हैं',False)],
            'fill':[('हिंदी में ___ स्वर हैं','11'),('अ, आ, इ ये ___ हैं','स्वर'),('पहला स्वर ___ है','अ')]
        },
        'व्यंजन': {
            'terms':['क','ख','ग','घ','च','छ','ज','झ','ट','ठ'],
            'facts':[('हिंदी में व्यंजन','33 होते हैं'),('क से ज्ञ तक','व्यंजन हैं'),('व्यंजन बिना स्वर के','नहीं बोले जा सकते'),('क ख ग घ ङ','कवर्ग है'),('च छ ज झ ञ','चवर्ग है')],
            'tf':[('हिंदी में 33 व्यंजन हैं',True),('अ एक व्यंजन है',False),('क पहला व्यंजन है',True),('व्यंजन अकेले बोले जा सकते हैं',False)],
            'fill':[('हिंदी में ___ व्यंजन हैं','33'),('क, ख, ग ये ___ हैं','व्यंजन'),('पहला व्यंजन ___ है','क')]
        },
        'संज्ञा': {
            'terms':['संज्ञा','नाम','व्यक्ति','स्थान','वस्तु','जातिवाचक','व्यक्तिवाचक','भाववाचक','गाय','दिल्ली'],
            'facts':[('संज्ञा का अर्थ है','नाम'),('राम, दिल्ली','व्यक्तिवाचक संज्ञा'),('लड़का, नदी','जातिवाचक संज्ञा'),('ईमानदारी, सुंदरता','भाववाचक संज्ञा'),('संज्ञा के','तीन भेद होते हैं')],
            'tf':[('संज्ञा एक नाम है',True),('दौड़ना एक संज्ञा है',False),('गंगा व्यक्तिवाचक संज्ञा है',True),('संज्ञा के दो भेद हैं',False)],
            'fill':[('किसी व्यक्ति, स्थान या वस्तु के नाम को ___ कहते हैं','संज्ञा'),('राम एक ___ संज्ञा है','व्यक्तिवाचक'),('संज्ञा के ___ भेद होते हैं','तीन')]
        },
    },
    'evs': {
        'Plants': {
            'terms':['plant','root','stem','leaf','flower','seed','water','sunlight','soil','grow'],
            'facts':[('Plants need','water and sunlight'),('Roots absorb','water from soil'),('Leaves make','food for the plant'),('The process is called','photosynthesis'),('Seeds grow into','new plants')],
            'tf':[('Plants need sunlight to grow',True),('Roots are above the ground',False),('Leaves make food for plants',True),('Plants dont need water',False)],
            'fill':[('Plants need water and ___','sunlight'),('___ absorb water from soil','Roots'),('Leaves make ___ for the plant','food')]
        },
        'Animals': {
            'terms':['animal','herbivore','carnivore','omnivore','habitat','pet','wild','domestic','bird','fish'],
            'facts':[('Herbivores eat','only plants'),('Carnivores eat','only meat'),('Omnivores eat','both plants and meat'),('A habitat is','where an animal lives'),('Birds have','feathers and wings')],
            'tf':[('A lion is a herbivore',False),('A cow eats only plants',True),('Fish live in water',True),('All animals can fly',False)],
            'fill':[('Animals that eat only plants are called ___','herbivores'),('A ___ eats both plants and meat','omnivore'),('Where an animal lives is called its ___','habitat')]
        },
        'Water': {
            'terms':['water','rain','river','ocean','ice','steam','cloud','evaporation','condensation','precipitation'],
            'facts':[('Water exists in','3 states'),('Ice is','solid water'),('Steam is','water vapor'),('Evaporation turns water to','vapor'),('Rain comes from','clouds')],
            'tf':[('Water can be solid liquid and gas',True),('Ice is a liquid',False),('Rain comes from clouds',True),('The ocean has fresh water',False)],
            'fill':[('Water in solid form is called ___','ice'),('Water vapor forms ___','clouds'),('Rain is also called ___','precipitation')]
        },
    },
    'science': {
        'Plants': {
            'terms':['plant','root','stem','leaf','flower','seed','water','sunlight','soil','photosynthesis'],
            'facts':[('Plants make food through','photosynthesis'),('Roots anchor the plant in','soil'),('The green pigment in leaves is','chlorophyll'),('Plants release','oxygen'),('Seeds contain','baby plants')],
            'tf':[('Photosynthesis needs sunlight',True),('Plants breathe in oxygen',False),('Chlorophyll is green',True),('Roots grow towards light',False)],
            'fill':[('Plants make food through ___','photosynthesis'),('The green color in leaves is due to ___','chlorophyll'),('Plants release ___ gas','oxygen')]
        },
    },
    'gk': {
        'default': {
            'terms':['India','Delhi','Earth','planet','country','capital','flag','river','mountain','ocean'],
            'facts':[('Capital of India is','New Delhi'),('India has','28 states'),('The longest river in India is','Ganga'),('Earth is the','3rd planet from Sun'),('The national bird of India is','Peacock')],
            'tf':[('Delhi is the capital of India',True),('India has 30 states',False),('The Peacock is our national bird',True),('Earth is the 5th planet',False)],
            'fill':[('The capital of India is ___','New Delhi'),('India has ___ states','28'),('The national bird is ___','Peacock')]
        },
    },
    'computer': {
        'default': {
            'terms':['computer','keyboard','mouse','monitor','CPU','printer','internet','software','hardware','memory'],
            'facts':[('CPU stands for','Central Processing Unit'),('A keyboard is an','input device'),('A monitor is an','output device'),('The brain of computer is','CPU'),('Software are','programs and applications')],
            'tf':[('CPU is the brain of computer',True),('Mouse is an output device',False),('Monitor displays information',True),('Keyboard is an output device',False)],
            'fill':[('CPU stands for Central ___ Unit','Processing'),('A ___ is used to type','keyboard'),('The ___ displays output','monitor')]
        },
    },
    'sst': {
        'default': {
            'terms':['Earth','globe','map','continent','ocean','country','India','direction','north','south'],
            'facts':[('There are','7 continents'),('There are','5 oceans'),('India is in','Asia'),('A globe is a','model of Earth'),('Maps show','directions and places')],
            'tf':[('There are 7 continents',True),('India is in Europe',False),('A globe is round',True),('There are 3 oceans',False)],
            'fill':[('There are ___ continents','7'),('India is in the continent of ___','Asia'),('A ___ is a model of Earth','globe')]
        },
    },
}

def get_chapter_game_data(subject, chapter_name, chapter_index=0, board='CBSE', class_num='1'):
    """Get game content for a specific chapter using dynamic parsing or fallbacks."""
    
    # 1. Try to find and parse a text asset
    asset_path = UniversalMapper.get_asset_path(subject, chapter_name, chapter_index, board, class_num)
    if asset_path:
        dynamic_data = ChapterParser.parse_txt(asset_path)
        if dynamic_data and (dynamic_data['terms'] or dynamic_data['facts']):
            return dynamic_data

    # 2. Fall back to existing CHAPTER_KNOWLEDGE
    subj_data = CHAPTER_KNOWLEDGE.get(subject.lower(), {})
    data = subj_data.get(chapter_name)
    if not data:
        for key in subj_data:
            if key.lower() in chapter_name.lower() or chapter_name.lower() in key.lower():
                data = subj_data[key]
                break
    if not data:
        data = subj_data.get('default')
        
    # 3. Last resort: Smart Fallback using chapter name
    if not data:
        words = [w for w in chapter_name.split() if len(w) > 2]
        # Basic context for math/language
        data = {
            'terms': words + ['concept', 'logic', 'practice', 'study'],
            'facts': [
                (f"We are learning {chapter_name} in", f"{subject.capitalize()}"),
                (f"The main focus of this chapter is", chapter_name),
                (f"Practicing {chapter_name} helps with", "subject mastery")
            ],
            'tf': [
                (f"{chapter_name} is part of the {board} syllabus", True),
                (f"{chapter_name} is a very easy topic", True),
                (f"We should skip studying {chapter_name}", False)
            ],
            'fill': [
                (f"Current Chapter: ___", chapter_name),
                (f"Subject of study: ___", subject.capitalize())
            ]
        }
    return data


@app.route('/games/<subject>/<int:chapter_index>')
def games(subject, chapter_index):
    """Game Arcade Hub — chapter-specific interactive games."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    if not user:
        session.clear()
        return redirect(url_for('login'))

    board_key = 'CBSE' if 'CBSE' in user['board'] else ('ICSE' if 'ICSE' in user['board'] else 'WBSE')
    class_match = re.search(r'Class\s*(\d+)', user['class_level'])
    class_num = class_match.group(1) if class_match else '1'
    chapters_list = SYLLABUS_DB.get(board_key, {}).get(class_num, {}).get(subject.lower(), [])
    
    if chapter_index < 0 or chapter_index >= len(chapters_list):
        chapter_index = 0
    chapter_name = chapters_list[chapter_index] if chapters_list else 'General'
    
    return render_template('games.html',
        user=user, subject=subject, chapter_name=chapter_name,
        chapter_index=chapter_index, class_num=class_num, board=board_key)


@app.route('/api/game_data')
def api_game_data():
    """Return chapter-specific game content with dynamic mapping."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401
    
    subject = request.args.get('subject', 'math').lower()
    chapter = request.args.get('chapter', 'General')
    chapter_idx = int(request.args.get('chapter_idx', 0))
    board = request.args.get('board', 'CBSE')
    class_num = request.args.get('class_num', '1')
    
    data = get_chapter_game_data(subject, chapter, chapter_idx, board, class_num)
    terms = data.get('terms', [])
    facts = data.get('facts', [])
    tf_qs = data.get('tf', [])
    fill_qs = data.get('fill', [])
    
    # Build MCQ questions from facts
    mcqs = []
    facts_list: List[Tuple[Any, Any]] = cast(List[Tuple[Any, Any]], list(facts)) if facts else []  # type: ignore
    for q, a in facts_list:
        all_wrong = [str(f[1]) for f in facts_list if cast(Tuple[Any, Any], f)[1] != a]
        # Use cast to satisfy Pyre slicing
        wrong = cast(List[Any], list(itertools.islice(all_wrong, 3)))
        while len(wrong) < 3:
            wrong.append('None of these')
        opts = [a] + wrong
        random.shuffle(opts)
        mcqs.append({'q': q + '?', 'options': opts, 'answer': a})
    
    # Build True/False
    tf_list: List[Tuple[str, Any]] = list(tf_qs) if tf_qs else [] # type: ignore
    tfs = [{'q': q, 'answer': a} for q, a in tf_list]
    
    # Build Fill-in-the-Blanks
    fill_list: List[Tuple[str, Any]] = list(fill_qs) if fill_qs else [] # type: ignore
    fills = [{'q': q, 'answer': a} for q, a in fill_list]
    
    # Word builder data
    terms_list: List[str] = terms  # type: ignore
    word = random.choice(terms_list) if terms_list else 'learn'
    scrambled = list(str(word).upper())
    random.shuffle(scrambled)
    
    # Match pairs from facts using islice
    facts_for_pairs: List[Tuple[Any, Any]] = list(itertools.islice(facts_list, 6))
    pairs = [{'left': q, 'right': a} for q, a in facts_for_pairs]
    
    return json.dumps({
        'chapter': chapter, 'subject': subject,
        'terms': terms, 'mcqs': mcqs, 'tfs': tfs,
        'fills': fills, 'word': word.upper(),
        'scrambled': ''.join(scrambled),
        'pairs': pairs
    })


@app.route('/api/game_complete', methods=['POST'])
def api_game_complete():
    """Record game completion, award XP."""
    if 'user_id' not in session:
        return json.dumps({'error': 'Not logged in'}), 401
    data = request.json
    subject = data.get('subject', 'math')
    chapter = data.get('chapter', 'General')
    game_type = data.get('game_type', 'quiz')
    score = data.get('score', 0)
    
    xp_map = {'mcq': 30, 'tf': 25, 'fill': 30, 'word_builder': 35,
              'match': 35, 'drag_drop': 35, 'boss_battle': 60,
              'timed': 40, 'spin': 30, 'streak': 50, 'survival': 60,
              'memory': 35, 'word_scramble': 30, 'word_search': 40, 'picture': 30}
    base_xp = xp_map.get(game_type, 25)
    xp_earned = int(base_xp * min(score / 100, 1)) if score > 0 else 10
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO learning_progress (user_id, subject, topic, mode) VALUES (?,?,?,?)',
                   (session['user_id'], subject, chapter, game_type))
    cursor.execute('SELECT xp, streak FROM users WHERE id=?', (session['user_id'],))
    u = cursor.fetchone()
    new_xp = u['xp'] + xp_earned
    cursor.execute('UPDATE users SET xp=?, level=?, streak=?, medals=? WHERE id=?',
                   (new_xp, calculate_level(new_xp), u['streak'] + 1, get_medal(new_xp), session['user_id']))
    conn.commit()
    conn.close()
    return json.dumps({'status': 'success', 'xp_earned': xp_earned, 'new_xp': new_xp})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
