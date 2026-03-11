# EduGalaxy — Technical Documentation & Submission Details
## Comprehensive Project Overview (Word Document Format)

### 1. Executive Summary
**EduGalaxy** is a next-generation, syllabus-driven educational platform designed to gamify the learning experience for students in Classes 1 through 5. By casting the student in the role of a "Protagonist Hero" defending their galaxy from alien invasion, the platform transforms mundane homework into an epic, interactive journey. 

Built with the speed of Python (Flask) on the backend and the visual supremacy of WebGL (Three.js) on the frontend, EduGalaxy offers a seamless, cinematic, and offline-capable (PWA) learning environment.

### 2. Core Problem & Solution
*   **The Problem:** Traditional digital learning is static. Students lose interest quickly when faced with flat UI and unengaging quizzes that do not reward continuous progress.
*   **The Solution:** An immersive 3D gamification loop where answering questions correctly (Math, Science, English, etc.) powers a planetary defense grid. Progression is tracked via visual "Mastery Rings," an evolving "Session XP" bar, and a global class-filtered leaderboard.

### 3. Key Technical Features
#### A. High-Fidelity 3D Environments
*   **Star Wars Galaxy Scroll:** The Home page utilizes extreme WebGL parallax and direct Z-axis depth scrolling. A massive 3D asteroid belt, animated glowing planets, and aggressively moving alien warships dominate the viewport.
*   **Lightspeed & Holo-Portal Logins:** The Authentication pages feature WebGL hyperspace tunnels and rotating wireframe torus knots with custom GLSL neon scanline shaders.

#### B. Gamification Engine
*   **Dynamic XP Tracking:** An animated Session XP bar provides real-time feedback with confetti bursts upon reaching daily goals.
*   **Achievement System:** A custom Mission Control Profile dashboard showcases earnable SVG badges (e.g., Star Cadet, Math Whiz).
*   **Contextual Hints:** An API endpoint (`/api/hint`) delivers specific syllabus hints when a student is stuck on an interactive task.

#### C. Performance & Accessibility
*   **Progressive Web App (PWA):** A fully configured Service Worker (`sw.js`) utilizing a cache-first strategy ensures that core assets (UI, 3D models, fonts) load instantly and work offline.
*   **Responsive Glassmorphism:** The UI uses CSS Level 4 features (backdrop-filter) and responsive breakpoints to deliver a premium "Glass" aesthetic across desktop and mobile devices.
*   **Generative Audio (Tone.js):** Instead of loading massive MP3 files, the background ambient music and interactive SFX (like laser blasts) are generated procedurally in the browser, saving bandwidth.

### 4. Setup & Deployment Instructions
To run this project locally for judging:
1.  **Prerequisites:** Ensure Python 3.8+ is installed.
2.  **Install Dependencies:** Run `pip install flask` (The project has zero other backend dependencies to maximize portability).
3.  **Run Application:** Execute `python app.py`.
4.  **Access:** Open any modern browser (Chrome/Edge recommended for WebGL) and navigate to `http://127.0.0.1:5000/`.

### 5. Future Roadmap
*   **AI Integration:** Implement LLM-generated dynamic quizzes based on the syllabus data rather than static dictionaries.
*   **Multiplayer Boss Fights:** Allow classes of students to pool their Session XP together to defeat massive weekly "Alien Boss" events.
*   **Expanded Syllabus:** Integrate higher classes (6-12) and additional regional boards.

---
*Created by [Your Team Name] for [Hackathon Name].*
