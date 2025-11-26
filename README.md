# Voice Note Translator - Nigerian Pidgin & Native Languages

## 🎯 Overview
This software accurately translates voice notes from Nigerian Pidgin and native Nigerian languages (Yoruba, Igbo, Hausa) into English. Built specifically for accurate Nigerian language translation.

## ✨ Features
- 🎤 Upload voice notes in multiple formats (MP3, WAV, M4A, OGG, FLAC)
- 🔄 Accurate transcription of Nigerian Pidgin and native languages
- 🌐 Automatic translation to English
- 📋 Copy translations to clipboard
- 💾 Save translations to text files
- 🎨 User-friendly interface
- ⚡ Fast processing

## 📋 Requirements
- Python 3.8 or higher
- Internet connection (for speech recognition and translation services)
- Audio files in supported formats

## 🚀 Installation

### Step 1: Install Python
Make sure Python 3.8+ is installed on your computer.
Download from: https://www.python.org/downloads/

### Step 2: Install Required Packages
Open terminal/command prompt and run:

```bash
pip install speechrecognition pydub pillow googletrans==4.0.0rc1
```

### Step 3: Install FFmpeg (for audio processing)
- **Windows**: Download from https://ffmpeg.org/download.html
- **Mac**: Run `brew install ffmpeg`
- **Linux**: Run `sudo apt install ffmpeg`

## 💻 How to Use

### Starting the Application
Run the program:
```bash
python voice_translator.py
```

### Using the Translator
1. **Upload Voice Note**: Click "📁 Upload Voice Note" and select your audio file
2. **Select Language**: Choose the source language (Nigerian Pidgin, Yoruba, Igbo, Hausa, or Auto-detect)
3. **Translate**: Click "🔄 Transcribe & Translate" button
4. **Wait**: The software will process your voice note
5. **View Results**: 
   - Original transcription appears in the first text box
   - English translation appears in the second text box
6. **Save or Copy**: Use the buttons to copy or save your translation

## 🎯 Best Practices for Accurate Results

### Audio Quality
✅ **DO:**
- Use clear recordings with minimal background noise
- Speak at a normal pace
- Use WAV format for best results
- Keep audio files under 1 minute for faster processing

❌ **AVOID:**
- Very noisy recordings
- Multiple people speaking at once
- Very low volume recordings
- Heavily compressed audio files

### Supported Languages
- Nigerian Pidgin (Naija)
- Yoruba
- Igbo
- Hausa
- English

## 🔧 Troubleshooting

### "Could not understand audio"
- Check audio quality
- Ensure minimal background noise
- Try converting to WAV format
- Speak more clearly in the recording

### "Connection Error"
- Check your internet connection
- Ensure firewall isn't blocking the app
- Try again after a few moments

### Translation Issues
- The app uses Google's translation service
- For Pidgin, results may vary based on dialect
- You can manually correct translations

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
1. For best results, use WAV format audio files
2. Keep recordings clear and without background noise
3. Speak at a normal, conversational pace
4. The app works best with Nigerian English, Pidgin, and major native languages
5. Internet connection is required for processing

## 🔒 Privacy
- All processing is done through secure Google services
- No audio files are stored by the application
- Translations are not saved unless you explicitly save them

## 🆘 Support
For issues or questions:
1. Check the Troubleshooting section above
2. Ensure all requirements are properly installed
3. Verify your internet connection is stable

## 📜 License
This software is provided as-is for translation purposes.

## 🙏 Credits
Built using:
- SpeechRecognition (Google Speech API)
- GoogleTrans (Translation API)
- Python Tkinter (GUI)

---

**Made with ❤️ for Nigerian language translation**
