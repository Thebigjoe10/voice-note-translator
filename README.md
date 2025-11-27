# Voice Note Translator - Nigerian Pidgin & Native Languages

## 🎯 Overview
This software **accurately** translates voice notes from Nigerian Pidgin and native Nigerian languages (Yoruba, Igbo, Hausa) into English using **state-of-the-art OpenAI Whisper AI** for superior transcription accuracy. Built specifically for Nigerian language translation with industry-leading accuracy.

## ⚡ v3.0 - Major Upgrade: OpenAI Whisper Integration
**NEW!** This version now uses OpenAI's Whisper API for transcription, providing:
- **Significantly improved accuracy** for Nigerian Pidgin
- **Better language detection** - correctly identifies Pidgin vs Igbo vs other languages
- **Superior noise handling** - works well even with background noise
- **Industry-leading transcription quality**

## ✨ Features
- 🎤 Upload voice notes in multiple formats (MP3, WAV, M4A, OGG, FLAC, WEBM, OPUS)
- 🧠 **State-of-the-art AI transcription** using OpenAI Whisper
- 🔄 **Highly accurate** transcription of Nigerian Pidgin and native languages
- 🎯 **Smart language detection** - correctly identifies Pidgin, Igbo, Yoruba, Hausa
- 🌐 Automatic translation to English
- 📋 Copy translations to clipboard
- 💾 Save translations to text files
- 🎨 User-friendly interface
- ⚡ Fast processing with superior results

## 📋 Requirements
- Python 3.8 or higher
- OpenAI API key (get from https://platform.openai.com/api-keys)
- Internet connection (for Whisper API and translation services)
- Audio files in supported formats

## 🚀 Installation

### Step 1: Install Python
Make sure Python 3.8+ is installed on your computer.
Download from: https://www.python.org/downloads/

### Step 2: Clone or Download This Repository
```bash
git clone <repository-url>
cd voice-note-translator
```

### Step 3: Install Required Packages
Open terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install flask flask-cors flask-limiter openai googletrans==4.0.0rc1 pydub werkzeug python-dotenv
```

### Step 4: Set Up OpenAI API Key
1. Get your API key from: https://platform.openai.com/api-keys
2. Create a `.env` file in the project directory:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

### Step 5: Install FFmpeg (Optional - for audio format conversion)
- **Windows**: Download from https://ffmpeg.org/download.html
- **Mac**: Run `brew install ffmpeg`
- **Linux**: Run `sudo apt install ffmpeg`

Note: Whisper API supports most audio formats directly, but ffmpeg helps with compatibility.

## 💻 How to Use

### Option 1: Desktop GUI Application
Run the GUI program:
```bash
python voice_translator.py
```

### Option 2: Web API Server
Run the Flask API server:
```bash
python app.py
```
Then access the web interface at `http://localhost:5000`

### Using the Translator (GUI)
1. **Upload Voice Note**: Click "📁 Upload Voice Note" and select your audio file
2. **Select Language**: Choose the source language (Nigerian Pidgin, Yoruba, Igbo, Hausa, or Auto-detect)
   - **Tip**: Use "Auto-detect" for best Pidgin recognition
3. **Translate**: Click "🔄 Transcribe & Translate" button
4. **Wait**: The Whisper AI will process your voice note (typically 5-15 seconds)
5. **View Results**:
   - Original transcription appears in the first text box
   - English translation appears in the second text box
   - Detected language is shown in the status bar
6. **Save or Copy**: Use the buttons to copy or save your translation

### Using the Web API
Send POST requests to `/api/translate`:
```bash
curl -X POST -F "audio=@yourfile.mp3" http://localhost:5000/api/translate
```

## 🎯 Best Practices for Accurate Results

### Audio Quality
✅ **DO:**
- **Whisper handles background noise well**, but clearer is still better
- Speak at a normal pace
- Most audio formats work great (MP3, WAV, M4A, etc.)
- Files up to 25MB are supported
- **Use "Auto-detect" mode for best Pidgin recognition**

❌ **AVOID:**
- Extremely loud background music
- Multiple people speaking simultaneously
- Audio files larger than 25MB (compress if needed)

### Supported Languages
- Nigerian Pidgin (Naija)
- Yoruba
- Igbo
- Hausa
- English

## 🔧 Troubleshooting

### "API Key Error" or "Authentication Failed"
- Ensure you've created a `.env` file with your OpenAI API key
- Verify your API key is correct at https://platform.openai.com/api-keys
- Make sure you have credits in your OpenAI account

### "Could not understand audio"
- Ensure audio file contains speech
- Check that the file isn't corrupted
- Try a different audio format
- Verify the audio isn't completely silent

### "Connection Error"
- Check your internet connection
- Verify firewall isn't blocking API requests
- Ensure OpenAI services are accessible from your location
- Try again after a few moments

### "Rate Limit Exceeded"
- The app has built-in rate limiting (10 requests/minute)
- Wait a minute and try again
- Check your OpenAI API usage limits

### Translation Issues
- The app uses Google's translation service for final translation
- Whisper provides the transcription (very accurate)
- For Pidgin, Whisper's auto-detect mode works best
- You can manually correct translations if needed

## 🌟 Features Coming Soon
- Real-time voice recording
- Support for more Nigerian languages
- Batch processing multiple files
- Integration with WhatsApp (future version)
- Offline mode
- Custom dictionary for local terms

## 📝 File Formats Supported
- WAV (recommended - best quality)
- MP3
- M4A
- OGG
- FLAC

## 💡 Tips
1. **Use "Auto-detect" mode** for best Pidgin recognition
2. Whisper handles various audio formats well - MP3, WAV, M4A all work great
3. Background noise is okay - Whisper is very robust
4. Speak at a normal, conversational pace
5. The app excels with Nigerian English, Pidgin, Yoruba, Igbo, and Hausa
6. Internet connection is required for OpenAI Whisper API
7. Keep your OpenAI API key secure in the `.env` file

## 🔒 Privacy & Security
- All transcription is done through secure OpenAI Whisper API
- Translation uses Google Translate API
- Audio files are temporarily stored during processing and immediately deleted
- Translations are not saved unless you explicitly save them
- Your OpenAI API key is stored locally in `.env` (never share this file)
- No data is permanently stored by this application

## 💰 Costs
- OpenAI Whisper API pricing: $0.006 per minute of audio (very affordable!)
- Example: A 5-minute voice note costs about $0.03 (3 cents)
- Google Translate API is free for personal use
- First-time OpenAI users often get free credits

## 🆘 Support
For issues or questions:
1. Check the Troubleshooting section above
2. Verify your OpenAI API key is set correctly in `.env`
3. Ensure all requirements are properly installed
4. Check your internet connection is stable
5. Verify you have OpenAI API credits

## 📜 License
This software is provided as-is for translation purposes.

## 🙏 Credits
Built using:
- **OpenAI Whisper** (State-of-the-art speech recognition)
- **Flask** (Web API framework)
- **GoogleTrans** (Translation API)
- **Python Tkinter** (Desktop GUI)
- **pydub** (Audio processing)

## 🔄 Version History
- **v3.0** - Major upgrade to OpenAI Whisper API for superior accuracy
- **v2.0** - Added web API and multiple Nigerian languages
- **v1.0** - Initial release with Google Speech Recognition

---

**Made with ❤️ for Nigerian language translation**
**Powered by OpenAI Whisper - The Future of Speech Recognition**
