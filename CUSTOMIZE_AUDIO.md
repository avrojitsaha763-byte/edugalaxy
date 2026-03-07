# 🎵 Customization Guide - Melodies & Voiceovers

## 🎙️ Change Voiceover Text

Edit `edugalaxy/ai_voice_service.py`:

```python
VOICEOVER_CONTENT = {
    "index": "Welcome to EduGalaxy...",  # ← Change this text
    "dashboard": "...",
    # ... etc
}
```

### Steps:
1. Find the page name in `VOICEOVER_CONTENT`
2. Edit the text string
3. Delete the corresponding MP3 file (triggers regeneration)
4. Refresh the page (new voiceover will be generated)

### Example:
```python
# Before
"index": "Welcome to EduGalaxy, your ultimate online learning platform..."

# After
"index": "Hola! Welcome to EduGalaxy, where you become a learning champion!"
```

---

## 🎼 Customize Melodies

Edit `edugalaxy/ai_voice_service.py`:

```python
MELODY_CONFIGS = {
    "index": {
        "notes": [264, 330, 392, 440],      # ← Frequencies (Hz)
        "durations": [0.5, 0.5, 0.5, 0.5],  # ← Length (seconds)
        "style": "uplifting"                 # ← Description
    }
}
```

### Musical Frequencies Reference

```
Octave 4:
C4: 261.63 Hz
D4: 293.66 Hz
E4: 329.63 Hz
F4: 349.23 Hz
G4: 392.00 Hz
A4: 440.00 Hz (concert pitch)
B4: 493.88 Hz

Octave 5:
C5: 523.25 Hz
D5: 587.33 Hz
E5: 659.25 Hz
F5: 698.46 Hz
G5: 783.99 Hz
A5: 880.00 Hz
B5: 987.77 Hz
```

### Melody Examples

#### Uplifting (Current Index)
```python
"notes": [264, 330, 392, 440],
"durations": [0.5, 0.5, 0.5, 0.5],
"style": "uplifting"
# Plays: C-E-G-A ascending (E major arpeggio)
```

#### Calm/Peaceful
```python
"notes": [264, 264, 330, 330],
"durations": [1.0, 0.5, 1.0, 0.5],
"style": "peaceful"
# Plays: Long C, Short C, Long E, Short E
```

#### Energetic/Fast
```python
"notes": [440, 494, 523, 587],
"durations": [0.25, 0.25, 0.25, 0.25],
"style": "energetic"
# Fast ascending high notes
```

#### Descending (Sad/Reflective)
```python
"notes": [523, 493, 440, 392],
"durations": [0.5, 0.5, 0.5, 0.5],
"style": "reflective"
# Plays: E-B-A-G descending
```

#### Triumph/Victory
```python
"notes": [523, 587, 659, 784],
"durations": [0.5, 0.5, 0.5, 0.8],
"style": "triumphant"
# Strong ascending E-B-E-G octave jump
```

### Create a Simple Melody

**Two-note bounce (Quiz page - fun/energetic)**:
```python
"quiz": {
    "notes": [440, 550, 440, 550],
    "durations": [0.3, 0.3, 0.3, 0.3],
    "style": "bouncy"
}
```

**Three-note progression (Learning)**:
```python
"materials": {
    "notes": [330, 392, 523],
    "durations": [0.6, 0.6, 0.8],
    "style": "progressive"
}
```

---

## 🔊 Voice Speed Control

Edit `ai_voice_service.py`, line ~114:

```python
def generate_ai_voiceover(self, page_name):
    """Generate AI voiceover using Google Text-to-Speech"""
    text = VOICEOVER_CONTENT[page_name]

    # slow=False (normal, ~150 wpm)
    # slow=True (slower, ~100 wpm)
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(audio_file)
```

### Options:
```python
# Fast (normal speed)
tts = gTTS(text=text, lang='en', slow=False)

# Slow (easier to understand)
tts = gTTS(text=text, lang='en', slow=True)
```

---

## 🌍 Support Multiple Languages

Create variants in `ai_voice_service.py`:

```python
# English
VOICEOVER_CONTENT_EN = {
    "index": "Welcome to EduGalaxy...",
    "dashboard": "Welcome to your dashboard...",
}

# Spanish
VOICEOVER_CONTENT_ES = {
    "index": "Bienvenido a EduGalaxy...",
    "dashboard": "Bienvenido a tu panel...",
}

# French
VOICEOVER_CONTENT_FR = {
    "index": "Bienvenue sur EduGalaxy...",
    "dashboard": "Bienvenue sur votre tableau de bord...",
}
```

Then update generation function:

```python
def generate_ai_voiceover(self, page_name, language='en'):
    if language == 'es':
        content = VOICEOVER_CONTENT_ES
    elif language == 'fr':
        content = VOICEOVER_CONTENT_FR
    else:
        content = VOICEOVER_CONTENT_EN

    text = content[page_name]
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(audio_file)
```

---

## 🎛️ Adjust Melody Volume/Duration

The melody durations are already customizable in `MELODY_CONFIGS`:

```python
"dashboard": {
    "notes": [330, 330, 392, 392],
    "durations": [0.75, 0.75, 0.75, 0.75],  # ← Make longer/shorter
    "style": "focused"
}
```

### Melody Generation Details

In `generate_melody_tone()`:
```python
# Adjust amplitude (loudness) - line ~163
wave = 0.3 * np.sin(...)  # 0.3 = 30% amplitude
                          # 0.5 = 50% (louder)
                          # 0.2 = 20% (quieter)

# Adjust fade in/out - line ~168
fade_samples = int(sample_rate * 0.05)  # 0.05 = 50ms fade
                                         # 0.1 = 100ms (longer)
                                         # 0.02 = 20ms (shorter)

# Adjust pause between notes - line ~177
pause = 0.1  # seconds between notes
```

---

## 🎵 Add Background Music (Advanced)

### Option 1: Use Free Music Resources

Download from:
- **Incompetech**: incompetech.com (creative commons)
- **YouTube Audio Library**: youtube.com/audiolibrary
- **Freesound**: freesound.org
- **Zapsplat**: zapsplat.com

Save to: `edugalaxy/static/music/`

### Option 2: Update Mixing Function

```python
def mix_voiceover_with_melody_and_music(self, page_name):
    """Mix voiceover with melody AND background music"""

    voiceover = AudioSegment.from_mp3(voiceover_file)
    melody = AudioSegment.from_wav(melody_file)
    music = AudioSegment.from_mp3(music_file)  # Load background music

    # Reduce volumes
    melody = melody - 12
    music = music - 18

    # Mix together
    mixed = music.overlay(melody).overlay(voiceover)

    return mixed
```

---

## 🚀 Quick Customization Examples

### Example 1: Make Quiz Faster/More Energetic

**Before:**
```python
"quiz": {
    "notes": [440, 494, 523, 587],
    "durations": [0.4, 0.4, 0.4, 0.4],
    "style": "energetic"
}
```

**After (Even Faster):**
```python
"quiz": {
    "notes": [440, 494, 523, 587, 440, 494, 523, 587],  # Repeat notes
    "durations": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],  # Shorter
    "style": "ultra_energetic"
}
```

### Example 2: Make Admin Page More Professional

**Before:**
```python
"admin": {
    "notes": [440, 440, 523, 523],
    "durations": [0.7, 0.7, 0.7, 0.7],
    "style": "professional"
}
```

**After (Deep & Authoritative):**
```python
"admin": {
    "notes": [196, 196, 220, 220],  # Lower notes
    "durations": [1.0, 0.5, 1.0, 0.5],  # Longer notes
    "style": "authoritative"
}
```

Note: 196 Hz is G3, 220 Hz is A3 (lower octave)

### Example 3: Change Login to More Welcoming

**Current voiceover:**
```
"login": "Welcome back to EduGalaxy. Enter your email and password to access your account and continue your learning journey."
```

**More enthusiastic:**
```
"login": "Welcome back to EduGalaxy! Ready to continue your learning adventure? Just enter your email and password and let's go!"
```

---

## 📝 Best Practices

### Voiceover Text Tips
- Keep under 20 seconds of speech
- Use clear, friendly language
- Start with action verbs (Welcome, Explore, View, etc.)
- End with a call to action or encouragement
- Test pronunciation (gTTS handles proper nouns well)

### Melody Design Tips
- Use 3-5 notes per melody (not too complex)
- Keep note durations between 0.3-1.0 seconds
- Use major chords for positive pages (C-E-G)
- Use minor/descending for serious pages
- Test on speaker (different devices sound different)

### Overall Sound Tips
- Voiceover should be 70% of mix volume
- Melody should accent, not dominate
- Keep total audio under 20 seconds
- Test on mobile speakers (may distort if too loud)
- Consider disabled users (should have text alternative too)

---

## 🧪 Testing Changes

1. **Edit file**
   ```
   edugalaxy/ai_voice_service.py
   ```

2. **Delete old files** (if changing voiceover text or melody)
   ```
   rm edugalaxy/static/voiceovers/index_ai_voiceover.mp3
   rm edugalaxy/static/voiceovers/index_melody.wav
   ```

3. **Refresh page** or call API
   ```
   GET /api/generate-all-voiceovers
   GET /api/generate-all-melodies
   ```

4. **Test in browser**
   - Open DevTools (F12)
   - Click speaker icon
   - Check console for generation status
   - Listen to audio

---

## 🎓 Master Musical Notes

For creating custom melodies:

```
C Major Scale: C(261), D(293), E(329), F(349), G(392), A(440), B(493)
G Major Scale: G(392), A(440), B(493), C(523), D(587), E(659), F#(740)
A Minor Scale: A(440), B(493), C(523), D(587), E(659), F(698), G(783)
```

**Creating triads (3-note chords):**
- C Major: C(261) + E(329) + G(392)
- G Major: G(392) + B(493) + D(587)
- A Minor: A(440) + C(523) + E(659)

---

## 💡 Pro Tips

1. **Use the same key for all melodies** → Cohesive sound
2. **Different tempos for different pages** → Faster for quiz, slower for profile
3. **Test on various devices** → Sound differs on phones vs laptops
4. **Keep voiceovers under 15 seconds** → Respects user time
5. **Use clear English** → Google TTS handles accents well
6. **Version your changes** → Keep backup copies

---

## ❓ Common Issues

### Melody Sounds Off-Pitch
- Check frequency values (should be in 200-700 Hz range)
- Test individual notes
- Use reference: A4 = 440 Hz is standard tuning

### Voiceover Sounds Robotic
- Shorter sentences = more natural
- Add pauses with punctuation
- Use simple, conversational language

### Audio Too Loud/Quiet
- Adjust amplitude: `wave = 0.X * np.sin(...)`
- X = 0.3 (30%) is default
- Increase/decrease by 0.1-0.2

---

Ready to customize? Edit `ai_voice_service.py` and enjoy creating your perfect audio experience! 🎵
