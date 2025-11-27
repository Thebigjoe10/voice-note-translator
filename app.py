#!/usr/bin/env python3
"""
Voice Note Translator API
Flask backend for web application
Upgraded to use OpenAI Whisper API for superior transcription accuracy
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from googletrans import Translator
import os
import tempfile
from werkzeug.utils import secure_filename
import traceback
from pydub import AudioSegment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set ffmpeg path explicitly (cross-platform support)
ffmpeg_path = os.getenv('FFMPEG_PATH')
if ffmpeg_path and os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
elif os.path.exists(r"C:\Users\jojos\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"):
    AudioSegment.converter = r"C:\Users\jojos\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm', 'opus'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (Whisper API supports up to 25MB)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize rate limiter for API security
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize services
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
translator = Translator()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Voice Note Translator API - Powered by OpenAI Whisper',
        'version': '3.0',
        'transcription_engine': 'OpenAI Whisper API',
        'endpoints': {
            '/api/translate': 'POST - Translate voice note',
            '/api/health': 'GET - Health check',
            '/api/languages': 'GET - Get supported languages'
        },
        'features': [
            'High-accuracy transcription using OpenAI Whisper',
            'Superior support for Nigerian Pidgin and native languages',
            'Automatic language detection',
            'Translation to English'
        ]
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    # Check if OpenAI API key is configured
    has_openai_key = bool(os.getenv('OPENAI_API_KEY'))

    return jsonify({
        'status': 'healthy' if has_openai_key else 'degraded',
        'services': {
            'whisper_api': 'active' if has_openai_key else 'missing API key',
            'translation': 'active'
        },
        'transcription_engine': 'OpenAI Whisper',
        'version': '3.0'
    })

@app.route('/api/translate', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit: 10 translations per minute
def translate_voice():
    """
    Translate voice note to English using OpenAI Whisper API
    Accepts: audio file and optional language parameter
    Returns: JSON with original text, translation, and detected language
    """
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400

        file = request.files['audio']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Get source language from form data (optional)
        source_language = request.form.get('language', 'auto')

        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Map Nigerian languages to Whisper language codes
            language_map = {
                'pidgin': None,          # Auto-detect (Whisper handles Pidgin better in auto mode)
                'yoruba': 'yo',          # Yoruba
                'igbo': 'ig',            # Igbo
                'hausa': 'ha',           # Hausa
                'urhobo': None,          # Auto-detect (not officially supported, use auto)
                'auto': None             # Auto-detect
            }

            # Get language code for Whisper
            whisper_language = language_map.get(source_language, None)

            # Transcribe audio using OpenAI Whisper API
            print(f"Transcribing audio with Whisper API...")

            with open(filepath, 'rb') as audio_file:
                # Use Whisper API for transcription
                transcription_params = {
                    'file': audio_file,
                    'model': 'whisper-1',
                    'response_format': 'verbose_json',
                }

                # Add language parameter if specified (not auto)
                if whisper_language:
                    transcription_params['language'] = whisper_language

                # Call Whisper API
                response = openai_client.audio.transcriptions.create(**transcription_params)

                original_text = response.text
                detected_language = getattr(response, 'language', 'unknown')

                print(f"Transcription successful: {original_text[:100]}...")
                print(f"Detected language: {detected_language}")

            if not original_text or original_text.strip() == '':
                return jsonify({
                    'success': False,
                    'error': 'Could not transcribe audio. Please ensure the audio contains clear speech.'
                }), 400

            # Detect language and translate to English
            try:
                # Map Whisper language codes to full names
                language_names = {
                    'en': 'English',
                    'yo': 'Yoruba',
                    'ig': 'Igbo',
                    'ha': 'Hausa',
                    'pcm': 'Nigerian Pidgin'
                }

                detected_lang_name = language_names.get(detected_language, detected_language)

                # Check if already in English
                if detected_language == 'en' or detected_language == 'english':
                    translated_text = original_text
                    note = 'Text is already in English'
                else:
                    # Translate to English using Google Translate
                    translation = translator.translate(original_text, dest='en')
                    translated_text = translation.text
                    note = None

                return jsonify({
                    'success': True,
                    'original_text': original_text,
                    'translated_text': translated_text,
                    'detected_language': detected_language,
                    'detected_language_name': detected_lang_name,
                    'note': note,
                    'transcription_engine': 'OpenAI Whisper'
                })

            except Exception as e:
                # If translation fails, return original text
                print(f"Translation error: {str(e)}")
                return jsonify({
                    'success': True,
                    'original_text': original_text,
                    'translated_text': original_text,
                    'detected_language': detected_language,
                    'detected_language_name': detected_lang_name,
                    'note': 'Translation service unavailable, showing original text only',
                    'transcription_engine': 'OpenAI Whisper'
                })

        finally:
            # Clean up temporary files
            if os.path.exists(filepath):
                os.remove(filepath)

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/languages')
def get_languages():
    """Get supported languages"""
    return jsonify({
        'supported_languages': [
            {'code': 'pidgin', 'name': 'Nigerian Pidgin'},
            {'code': 'yoruba', 'name': 'Yoruba'},
            {'code': 'igbo', 'name': 'Igbo'},
            {'code': 'hausa', 'name': 'Hausa'},
            {'code': 'urhobo', 'name': 'Urhobo'},
            {'code': 'en', 'name': 'English'},
            {'code': 'auto', 'name': 'Auto-detect'}
        ]
    })

if __name__ == '__main__':
    # Run in development mode
    print("=" * 70)
    print("🎤 Voice Note Translator API Server v3.0")
    print("Powered by OpenAI Whisper - Superior Transcription Accuracy")
    print("=" * 70)
    print("\n✨ Features:")
    print("  • High-accuracy transcription using OpenAI Whisper API")
    print("  • Excellent support for Nigerian Pidgin and native languages")
    print("  • Automatic language detection")
    print("  • Translation to English")
    print("\n🌐 Server Information:")
    print("  • API available at: http://localhost:5000")
    print("  • Documentation at: http://localhost:5000/")
    print("  • Health check: http://localhost:5000/api/health")

    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment variables!")
        print("  • Create a .env file with: OPENAI_API_KEY=your_api_key_here")
        print("  • Get your API key from: https://platform.openai.com/api-keys")
    else:
        print("\n✅ OpenAI API key configured")

    print("\nPress CTRL+C to stop the server")
    print("=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
