import sqlite3
import random

DATABASE = "database.db"

def get_random_questions(class_level, board, subject, limit=10):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM questions
        WHERE class_level=? AND board=? AND subject=?
    """, (class_level, board, subject))

    questions = cursor.fetchall()
    conn.close()

    random.shuffle(questions)
    return questions[:limit]
