import sqlite3

DATABASE = "database.db"

# Comprehensive questions for different classes, boards, and subjects
QUESTIONS = [
    # Class 1-2 (CBSE, ICSE, WBSC) - Math
    ("1", "CBSE", "Math", "Easy", "What is 2 + 3?", "5", "4", "6", "3", "A"),
    ("1", "CBSE", "Math", "Easy", "How many sides does a triangle have?", "3", "4", "5", "6", "A"),
    ("1", "ICSE", "Math", "Easy", "What is 10 - 5?", "5", "6", "4", "7", "A"),
    ("2", "CBSE", "Math", "Easy", "What is 3 × 4?", "12", "8", "15", "10", "A"),
    ("2", "WBSC", "Math", "Medium", "What is 20 ÷ 4?", "5", "4", "6", "7", "A"),

    # Class 1-2 Science
    ("1", "CBSE", "Science", "Easy", "How many legs does a dog have?", "4", "2", "6", "8", "A"),
    ("1", "ICSE", "Science", "Easy", "What color is the sky on a clear day?", "Blue", "Red", "Green", "Yellow", "A"),
    ("2", "CBSE", "Science", "Easy", "Which planet is closest to the Sun?", "Mercury", "Venus", "Mars", "Earth", "A"),
    ("2", "WBSC", "Science", "Medium", "What do plants use from the sun?", "Energy", "Water", "Air", "Soil", "A"),

    # Class 1-2 English
    ("1", "CBSE", "English", "Easy", "What is the opposite of 'happy'?", "Sad", "Mad", "Bad", "Glad", "A"),
    ("2", "ICSE", "English", "Easy", "Which is a verb?", "Run", "Happy", "Blue", "Big", "A"),

    # Class 3-4 Math
    ("3", "CBSE", "Math", "Medium", "What is 15 × 12?", "180", "160", "200", "150", "A"),
    ("3", "ICSE", "Math", "Medium", "What is the perimeter of a square with side 5cm?", "20", "15", "25", "30", "A"),
    ("4", "CBSE", "Math", "Medium", "What is 100 ÷ 25?", "4", "5", "3", "6", "A"),
    ("4", "WBSC", "Math", "Hard", "What is 45% of 200?", "90", "80", "100", "110", "A"),

    # Class 3-4 Science
    ("3", "CBSE", "Science", "Medium", "What is the process by which plants make food?", "Photosynthesis", "Respiration", "Digestion", "Fermentation", "A"),
    ("3", "ICSE", "Science", "Medium", "Which gas do humans breathe in?", "Oxygen", "Carbon Dioxide", "Nitrogen", "Argon", "A"),
    ("4", "CBSE", "Science", "Medium", "How many bones are in the adult human body?", "206", "186", "220", "250", "A"),
    ("4", "WBSC", "Science", "Hard", "What is the speed of light?", "3 × 10^8 m/s", "3 × 10^7 m/s", "3 × 10^9 m/s", "3 × 10^6 m/s", "A"),

    # Class 3-4 English
    ("3", "CBSE", "English", "Medium", "What is a noun?", "A person, place, or thing", "An action", "A quality", "A connection", "A"),
    ("4", "ICSE", "English", "Medium", "Which is an adjective?", "Beautiful", "Quickly", "Running", "Thinking", "A"),

    # Class 5 (Advanced) Math
    ("5", "CBSE", "Math", "Hard", "What is the square root of 144?", "12", "13", "11", "14", "A"),
    ("5", "ICSE", "Math", "Hard", "What is 25% of 1000?", "250", "200", "300", "350", "A"),
    ("5", "WBSC", "Math", "Hard", "What is the area of a circle with radius 7cm?", "154", "144", "164", "134", "A"),

    # Class 5 Science (Biology)
    ("5", "CBSE", "Science", "Hard", "What are proteins made of?", "Amino acids", "Glucose", "Lipids", "Nucleotides", "A"),
    ("5", "ICSE", "Science", "Hard", "What is the function of mitochondria?", "Energy production", "Protein synthesis", "Photosynthesis", "Waste removal", "A"),
    ("5", "CBSE", "Science", "Hard", "What is the life cycle of a star?", "Birth, main sequence, death", "Formation, maturity, decline", "Beginning, middle, end", "All of the above", "A"),

    # Class 5 English
    ("5", "CBSE", "English", "Hard", "What is the theme of a literary work?", "The main idea or message", "The title", "The author", "The setting", "A"),
    ("5", "ICSE", "English", "Hard", "What is alliteration?", "Repetition of initial sounds", "Repetition of words", "Repetition of lines", "Repetition of thoughts", "A"),

    # Class 5 Social Studies
    ("5", "CBSE", "Social Studies", "Medium", "Who was the first President of India?", "Dr. Rajendra Prasad", "Jawaharlal Nehru", "Sardar Vallabhbhai Patel", "B.R. Ambedkar", "A"),
    ("5", "ICSE", "Social Studies", "Medium", "In which year did India gain independence?", "1947", "1946", "1948", "1945", "A"),
]

def seed_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for q in QUESTIONS:
        try:
            cursor.execute("""
            INSERT INTO questions (class_level, board, subject, difficulty, question, optionA, optionB, optionC, optionD, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, q)
        except sqlite3.IntegrityError:
            pass  # Skip duplicates

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(QUESTIONS)} questions into database")

if __name__ == "__main__":
    seed_db()
