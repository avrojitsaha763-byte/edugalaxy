import sqlite3

DATABASE = "database.db"

# Real curriculum syllabus for different classes, boards
SYLLABUS = [
    # Class 1 - CBSE
    ("1", "CBSE", "Math", "Numbers 1-10", "Count, recognize, read and write numbers 0-10", 3),
    ("1", "CBSE", "Math", "Addition Basics", "Simple addition with single digits", 4),
    ("1", "CBSE", "Math", "Subtraction Basics", "Simple subtraction with single digits", 4),
    ("1", "CBSE", "Math", "Shapes", "Recognition of basic shapes (circle, square, triangle)", 2),
    ("1", "CBSE", "Science", "Living and Non-Living", "Identify living and non-living things", 3),
    ("1", "CBSE", "Science", "Human Body", "Basic parts of human body", 2),
    ("1", "CBSE", "Science", "Animals Around Us", "Common animals and their features", 3),
    ("1", "CBSE", "English", "Alphabet", "Learn alphabet A-Z", 5),
    ("1", "CBSE", "English", "Simple Words", "Reading and writing simple words", 4),

    # Class 2 - CBSE
    ("2", "CBSE", "Math", "Numbers 1-100", "Count, read and write numbers up to 100", 4),
    ("2", "CBSE", "Math", "Addition and Subtraction", "Two-digit addition and subtraction", 5),
    ("2", "CBSE", "Math", "Multiplication Basics", "Introduction to multiplication tables 2-5", 4),
    ("2", "CBSE", "Math", "Measurement", "Length, weight, capacity basics", 3),
    ("2", "CBSE", "Science", "Plants Around Us", "Parts of plants and their functions", 4),
    ("2", "CBSE", "Science", "Weather and Seasons", "Different weather conditions and seasons", 3),
    ("2", "CBSE", "Science", "Water", "Where water comes from, its uses", 3),
    ("2", "CBSE", "English", "Nouns and Verbs", "Basic parts of speech", 4),
    ("2", "CBSE", "English", "Simple Sentences", "Reading and constructing simple sentences", 4),

    # Class 3 - CBSE
    ("3", "CBSE", "Math", "Numbers up to 999", "Three-digit numbers and place value", 5),
    ("3", "CBSE", "Math", "Multiplication", "Multiplication facts and problems", 6),
    ("3", "CBSE", "Math", "Division", "Division concepts and basic division facts", 5),
    ("3", "CBSE", "Math", "Fractions", "Half, quarter, three-quarters", 4),
    ("3", "CBSE", "Science", "Life Cycle of Animals", "Reproduction and growth in animals", 4),
    ("3", "CBSE", "Science", "Human Body and Health", "Health, hygiene, and nutrition", 5),
    ("3", "CBSE", "Science", "Natural Resources", "Water, air, soil conservation", 4),
    ("3", "CBSE", "English", "Comprehension", "Reading comprehension exercises", 5),
    ("3", "CBSE", "English", "Grammar Basics", "Nouns, verbs, adjectives, punctuation", 6),

    # Class 4 - CBSE
    ("4", "CBSE", "Math", "Large Numbers", "Numbers up to 10,000 and place value", 5),
    ("4", "CBSE", "Math", "Operations", "All four operations with multi-digit numbers", 6),
    ("4", "CBSE", "Math", "Factors and Multiples", "Factors, multiples, prime numbers", 5),
    ("4", "CBSE", "Math", "Decimals", "Introduction to decimal fractions", 4),
    ("4", "CBSE", "Science", "Photosynthesis", "How plants make food", 5),
    ("4", "CBSE", "Science", "Respiration", "Breathing and respiration in organisms", 4),
    ("4", "CBSE", "Science", "The Solar System", "Planets, sun, moon, stars", 5),
    ("4", "CBSE", "English", "Writing Skills", "Paragraph writing and creative writing", 6),
    ("4", "CBSE", "English", "Tenses", "Present, past, future tenses", 5),

    # Class 5 - CBSE
    ("5", "CBSE", "Math", "Percentages", "Understanding and calculating percentages", 5),
    ("5", "CBSE", "Math", "Geometry", "Shapes, angles, area, perimeter", 6),
    ("5", "CBSE", "Math", "Data Handling", "Graphs, charts, data interpretation", 5),
    ("5", "CBSE", "Math", "Algebra Basics", "Simple algebraic expressions", 5),
    ("5", "CBSE", "Science", "Cell Structure", "Plant and animal cell structures", 6),
    ("5", "CBSE", "Science", "Force and Motion", "Newton's laws and motion concepts", 6),
    ("5", "CBSE", "Science", "Electricity and Magnetism", "Basic electricity and magnetism", 5),
    ("5", "CBSE", "English", "Literature", "Reading and analyzing stories and poems", 6),
    ("5", "CBSE", "English", "Advanced Grammar", "Complex sentences and clauses", 6),

    # Class 1-2 ICSE (similar to CBSE with minor differences)
    ("1", "ICSE", "Math", "Number Recognition", "Numbers 1-20 and their order", 3),
    ("1", "ICSE", "Math", "Basic Operations", "Addition and subtraction basics", 4),
    ("2", "ICSE", "Math", "Two-digit Numbers", "Numbers 1-100 with place value", 4),
    ("2", "ICSE", "Math", "Multiplication Intro", "Introduction to multiplication", 5),

    # Class 3-5 ICSE
    ("3", "ICSE", "Math", "Three-digit Arithmetic", "Operations with 3-digit numbers", 5),
    ("3", "ICSE", "Science", "Living Organisms", "Classification and life processes", 5),
    ("4", "ICSE", "Math", "Advanced Operations", "All operations with larger numbers", 6),
    ("4", "ICSE", "Science", "Structure of Life", "Cells and organisms", 5),
    ("5", "ICSE", "Math", "Advanced Mathematics", "Percentages, ratios, geometry", 6),
    ("5", "ICSE", "Science", "Scientific Method", "Experiments and scientific inquiry", 6),

    # Class 1-2 WBSC
    ("1", "WBSC", "Math", "Counting Skills", "Counting and number formation 1-20", 3),
    ("2", "WBSC", "Math", "Basic Numeracy", "Numbers 1-100 and simple operations", 4),
    ("2", "WBSC", "Science", "Environment", "Living things around us", 3),

    # Class 3-5 WBSC
    ("3", "WBSC", "Math", "Three Digit Numbers", "Place value and operations", 5),
    ("3", "WBSC", "Science", "Nature Study", "Ecology and nature", 4),
    ("4", "WBSC", "Math", "Advanced Numeracy", "Operations with larger numbers", 6),
    ("4", "WBSC", "Science", "Life Processes", "Biology basics", 5),
    ("5", "WBSC", "Math", "Higher Mathematics", "Advanced topics", 6),
    ("5", "WBSC", "Science", "Scientific Concepts", "Physics and chemistry basics", 6),
]

def seed_syllabus():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for s in SYLLABUS:
        try:
            cursor.execute("""
            INSERT INTO syllabus (class_level, board, subject, chapter, topics, estimated_hours)
            VALUES (?, ?, ?, ?, ?, ?)
            """, s)
        except sqlite3.IntegrityError:
            pass  # Skip duplicates

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(SYLLABUS)} syllabus chapters into database")

if __name__ == "__main__":
    seed_syllabus()
