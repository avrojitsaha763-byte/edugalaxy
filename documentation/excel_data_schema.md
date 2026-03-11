# EduGalaxy Data Schema & Excel Export Guide

This document outlines the JSON/Python dictionary structures used in the EduGalaxy backend, serving as an "Excel Guide" for how the data is stored, managed, and structured for the application. 

It can be used to plan out larger database migrations or Excel sheets of content that you want to import later.

---

## 👥 1. Users Database (Leaderboard & Profiles)
**Backend Source:** `USERS_DB` (In-memory Python Dictionary simulating a DB Table)

| Column Name | Data Type | Description | Example Row Data |
| :--- | :--- | :--- | :--- |
| `username` | `String (Primary Key)` | Unique identifier for the cadet. | `"StarCadet"` |
| `class_level` | `String` | The student's grade/class. | `"Class 3"` |
| `board` | `String` | The curriculum board. | `"CBSE"` |
| `xp` | `Integer` | Total experience points accumulated. | `450` |
| `tier` | `Integer` | Current rank tier (calculated by XP). | `4` |
| `lessons_done` | `Integer` | Count of interactive lessons finished. | `12` |
| `activities` | `Integer` | Count of quizzes/puzzles solved. | `34` |
| `badges` | `List[String]` | Array of earned achievement IDs. | `["first_step", "math_whiz"]` |
| `subject_progress` | `Object` | JSON mapping subjects to completion %. | `{"math": 80, "science": 40}` |

---

## 📚 2. Syllabus Database (Subjects & Topics)
**Backend Source:** `SYLLABUS_DB` (Nested Dictionary Mapping)

| Class Level | Board | Subject | Topic 1 | Topic 2 | Topic 3 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Class 1 | CBSE | Math | Numbers 1-50 | Addition | Patterns |
| Class 1 | CBSE | English | Phonics | Simple Sentences | Rhyming Words |
| Class 3 | ICSE | Science | Plants & Environment | Human Body | Solar System |
| Class 5 | WBSE | Bengali | Vowels & Consonants | Short Stories | Grammar Rules |

---

## ❓ 3. Quizzes & Puzzles Database
**Backend Source:** `QUIZZES_DB`

| Subject | Topic | Question | Options (Array) | Correct Answer Index | Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Math | Addition | "What is 15 + 7?" | `["20", "22", "25", "21"]` | `1` | Multiple Choice |
| Science | Solar System | "Identify the red planet:" | `["Earth", "Jupiter", "Mars", "Venus"]` | `2` | Multiple Choice |
| English | Grammar | "Past tense of 'Run' is __?"| `["Runned", "Ran", "Running"]` | `1` | Fill in Blank |
| Math | *Random* | "9 x 9 = ?" | `["81"]` | `0` | Daily Challenge |

---

## 💡 4. Hints Database
**Backend Source:** `HINTS_DB`

| Subject | Topic | Hint Text |
| :--- | :--- | :--- |
| Math | Addition | "Count the tens first, then add the ones!" |
| Science | Plants | "Remember, photosynthesis requires sunlight and water." |
| English | Phonics | "Sound it out slowly, letter by letter." |

---

## 🏅 5. Achievements & Badges Schema
**Frontend/Backend Registry**

| Badge ID | Badge Name | Requirement | Icon/SVG |
| :--- | :--- | :--- | :--- |
| `first_step` | First Step | Complete 1 lesson | Rocket Ship |
| `math_whiz` | Math Explorer | Score 100 XP in Math | Calculator/Graph |
| `daily_streak` | Star Cadet | Complete 5 Daily Challenges | Glowing Star |
| `tier_5` | Galactic Lord | Reach Tier 5 Rank | Golden Crown |
