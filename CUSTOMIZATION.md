# 🎨 CUSTOMIZATION GUIDE
## Voice Note Translator - Make It Your Own

═══════════════════════════════════════════════════════════════

This guide will help you customize the Voice Note Translator to match your brand, add new features, and extend functionality.

---

## 📱 BRANDING CUSTOMIZATION

### 1. Colors & Theme

The app uses Tailwind CSS. To change colors, update these classes in `index.html`:

**Primary Color (Purple → Your Color):**
```html
<!-- Find and replace these classes: -->
bg-purple-600     → bg-blue-600
text-purple-600   → text-blue-600
border-purple-300 → border-blue-300
hover:bg-purple-700 → hover:bg-blue-700
```

**Gradient Background:**
```html
<!-- Line 21-23 in index.html -->
<style>
    .gradient-bg {
        background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
    }
</style>
```

**Popular Color Schemes:**
- **Blue Professional:** `#3B82F6` → `#1E40AF`
- **Green Fresh:** `#10B981` → `#059669`
- **Orange Energetic:** `#F59E0B` → `#D97706`
- **Pink Modern:** `#EC4899` → `#DB2777`

---

### 2. Logo & Branding

**Update the Logo Icon:**
```html
<!-- Line 76 in index.html -->
<i class="fas fa-microphone-alt text-purple-600 text-2xl mr-3"></i>
```

Replace with your own:
- Use Font Awesome icons: https://fontawesome.com/icons
- Or add your own logo image:
```html
<img src="logo.png" alt="Logo" class="h-8 w-8 mr-3">
```

**Update Title & Tagline:**
```html
<!-- Line 77 in index.html -->
<span class="text-xl font-bold text-gray-800">Your App Name</span>

<!-- Line 94-99 -->
<h1 class="text-4xl font-extrabold text-white mb-4">
    🎤 Your Custom Tagline
</h1>
<p class="text-xl text-white opacity-90">
    Your custom description here
</p>
```

---

### 3. Fonts

**Change Default Font:**
```html
<!-- Line 15 in index.html -->
@import url('https://fonts.googleapis.com/css2?family=YourFont:wght@300;400;500;600;700;800&display=swap');

<style>
    body {
        font-family: 'YourFont', sans-serif;
    }
</style>
```

**Popular Font Choices:**
- **Poppins:** Modern & Friendly
- **Roboto:** Clean & Professional
- **Montserrat:** Bold & Impactful
- **Open Sans:** Versatile & Readable

---

## 🌍 LANGUAGE CUSTOMIZATION

### 1. Add More Nigerian Languages

**Update `app.py` (Line 159-171):**
```python
@app.route('/api/languages')
def get_languages():
    return jsonify({
        'supported_languages': [
            {'code': 'pidgin', 'name': 'Nigerian Pidgin'},
            {'code': 'yo', 'name': 'Yoruba'},
            {'code': 'ig', 'name': 'Igbo'},
            {'code': 'ha', 'name': 'Hausa'},
            {'code': 'fuv', 'name': 'Fulfulde'},  # NEW
            {'code': 'kcg', 'name': 'Tyap'},      # NEW
            {'code': 'en', 'name': 'English'},
            {'code': 'auto', 'name': 'Auto-detect'}
        ]
    })
```

**Update Language Names in `app.js` (Line 164-170):**
```javascript
const languageNames = {
    'en': 'English',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'ha': 'Hausa',
    'fuv': 'Fulfulde',  // NEW
    'kcg': 'Tyap',      // NEW
    'pidgin': 'Nigerian Pidgin'
};
```

---

### 2. Change Target Translation Language

**In `app.py` (Line 124):**
```python
# Change from English to another language
translation = translator.translate(original_text, dest='fr')  # French
translation = translator.translate(original_text, dest='es')  # Spanish
translation = translator.translate(original_text, dest='ar')  # Arabic
```

**Common Language Codes:**
- `en` - English
- `fr` - French
- `es` - Spanish
- `ar` - Arabic
- `pt` - Portuguese
- `zh-cn` - Chinese (Simplified)

---

### 3. Multi-Target Translation

**Add multiple translation targets:**
```python
@app.route('/api/translate_multi', methods=['POST'])
@limiter.limit("5 per minute")
def translate_voice_multi():
    """Translate to multiple languages"""
    # ... existing code ...

    target_languages = ['en', 'fr', 'es']  # English, French, Spanish
    translations = {}

    for lang in target_languages:
        translation = translator.translate(original_text, dest=lang)
        translations[lang] = translation.text

    return jsonify({
        'success': True,
        'original_text': original_text,
        'translations': translations
    })
```

---

## ✨ FEATURE ADDITIONS

### 1. User Accounts & Authentication

**Add Flask-Login for user management:**

```bash
pip install flask-login flask-sqlalchemy
```

**Create user model:**
```python
from flask_login import LoginManager, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    translations = db.relationship('Translation', backref='user')

class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    original_text = db.Column(db.Text)
    translated_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 2. Translation History

**Add history tracking:**
```python
@app.route('/api/history')
@login_required
def get_history():
    """Get user's translation history"""
    user_id = current_user.id
    translations = Translation.query.filter_by(user_id=user_id)\
                                   .order_by(Translation.created_at.desc())\
                                   .limit(50).all()

    return jsonify({
        'success': True,
        'history': [{
            'id': t.id,
            'original': t.original_text,
            'translated': t.translated_text,
            'date': t.created_at.isoformat()
        } for t in translations]
    })
```

---

### 3. Batch Processing

**Process multiple files at once:**
```python
@app.route('/api/translate_batch', methods=['POST'])
@limiter.limit("3 per hour")
def translate_batch():
    """Translate multiple voice notes"""
    files = request.files.getlist('audio')
    results = []

    for file in files[:5]:  # Limit to 5 files
        # Process each file
        # ... existing translation code ...
        results.append({
            'filename': file.filename,
            'original': original_text,
            'translated': translated_text
        })

    return jsonify({
        'success': True,
        'results': results
    })
```

**Frontend HTML:**
```html
<input type="file" id="audioFiles" accept="audio/*" multiple>
```

---

### 4. Real-Time Recording

**Add browser audio recording:**
```html
<!-- Add to index.html -->
<button onclick="startRecording()">
    <i class="fas fa-microphone"></i> Record
</button>
<button onclick="stopRecording()">
    <i class="fas fa-stop"></i> Stop
</button>
```

**JavaScript in app.js:**
```javascript
let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioChunks = [];

        // Upload to API
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        // ... send to API
    };

    mediaRecorder.start();
}

function stopRecording() {
    mediaRecorder.stop();
}
```

---

### 5. Voice Playback

**Add audio playback for original:**
```html
<!-- Add to results section -->
<audio id="audioPlayer" controls class="w-full mt-4">
    <source id="audioSource" type="audio/wav">
</audio>
```

```javascript
function displayResults(data) {
    // ... existing code ...

    // If you saved the audio file URL
    document.getElementById('audioSource').src = data.audio_url;
    document.getElementById('audioPlayer').load();
}
```

---

### 6. Text-to-Speech for Translation

**Add speech synthesis:**
```javascript
function speakTranslation() {
    const text = document.getElementById('translatedText').textContent;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    speechSynthesis.speak(utterance);
}
```

```html
<button onclick="speakTranslation()">
    <i class="fas fa-volume-up"></i> Listen to Translation
</button>
```

---

## 🎯 ADVANCED CUSTOMIZATION

### 1. Custom Language Models

**Use custom speech recognition:**
```python
# For better Nigerian language support
# Use Azure Speech Services or Google Cloud Speech-to-Text with custom models

from azure.cognitiveservices.speech import SpeechConfig, AudioConfig

speech_config = SpeechConfig(subscription="YOUR_KEY", region="YOUR_REGION")
speech_config.speech_recognition_language = "yo-NG"  # Yoruba Nigeria

# Or train custom model on Google Cloud
```

---

### 2. Accuracy Improvements

**Add confidence scoring:**
```python
# In app.py, update recognition
try:
    result = recognizer.recognize_google(audio_data, show_all=True)

    if result and 'alternative' in result:
        alternatives = result['alternative']
        best_match = alternatives[0]

        return jsonify({
            'success': True,
            'original_text': best_match['transcript'],
            'confidence': best_match.get('confidence', 0),
            'alternatives': [alt['transcript'] for alt in alternatives[:3]]
        })
except:
    pass
```

---

### 3. Custom UI Components

**Add dark mode:**
```html
<button onclick="toggleDarkMode()">
    <i class="fas fa-moon"></i>
</button>

<script>
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    // Update colors accordingly
}
</script>

<style>
.dark-mode {
    background: #1a1a1a;
    color: #ffffff;
}
.dark-mode .glass-effect {
    background: rgba(30, 30, 30, 0.95);
}
</style>
```

---

### 4. Analytics Integration

**Add Google Analytics:**
```html
<!-- Add to index.html head -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

**Track events:**
```javascript
function translateAudio() {
    // Track translation event
    gtag('event', 'translation_started', {
        'event_category': 'engagement',
        'event_label': selectedFile.name
    });

    // ... existing code ...
}
```

---

## 🔧 Configuration Files

### Create config.py

```python
import os

class Config:
    # App settings
    APP_NAME = "Voice Note Translator"
    APP_VERSION = "2.0"

    # File upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm', 'opus'}

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day"

    # API keys (store in environment variables)
    GOOGLE_CLOUD_API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY')
    AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')

    # Feature flags
    ENABLE_USER_ACCOUNTS = False
    ENABLE_TRANSLATION_HISTORY = False
    ENABLE_BATCH_PROCESSING = False
```

---

## 📦 DEPLOYMENT CUSTOMIZATION

### Environment Variables

Create `.env` file:
```bash
# App Configuration
APP_NAME="My Translator"
DEBUG=False
SECRET_KEY=your-secret-key-here

# API Keys
GOOGLE_CLOUD_API_KEY=your-key
AZURE_SPEECH_KEY=your-key

# Rate Limiting
REDIS_URL=redis://localhost:6379

# Feature Flags
ENABLE_ACCOUNTS=true
ENABLE_HISTORY=true
```

Load in app.py:
```python
from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
```

---

## 🎨 STYLE PRESETS

### Preset 1: Corporate Professional
```css
/* Blue gradient, clean lines */
.gradient-bg {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
}
```

### Preset 2: Creative & Vibrant
```css
/* Colorful gradient */
.gradient-bg {
    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);
}
```

### Preset 3: Minimalist Dark
```css
/* Dark theme */
.gradient-bg {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}
```

---

## 📝 SUMMARY CHECKLIST

- [ ] Update colors in `index.html`
- [ ] Change logo and branding
- [ ] Customize fonts
- [ ] Add/remove supported languages
- [ ] Implement desired features (accounts, history, etc.)
- [ ] Configure environment variables
- [ ] Set up analytics
- [ ] Test all customizations
- [ ] Update documentation

---

## 💡 NEED HELP?

- Check the main README.md for basic setup
- Review SECURITY.md for security best practices
- See PERFORMANCE.md for optimization tips
- Read MONETIZATION.md for business features

---

**Happy Customizing! 🚀**
