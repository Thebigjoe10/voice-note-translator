#!/usr/bin/env python3
"""
Voice Note Translator API
Flask backend for web application
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from googletrans import Translator
import os
import tempfile
from werkzeug.utils import secure_filename
import traceback
from pydub import AudioSegment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Set ffmpeg path explicitly
AudioSegment.converter = r"C:\Users\jojos\ffmpeg-8.0.1-essentials_build\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm', 'opus'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

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
recognizer = sr.Recognizer()
translator = Translator()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(input_path):
    """
    Convert any audio format to WAV format for speech recognition
    Returns the path to the converted WAV file
    """
    try:
        # Get file extension
        file_ext = os.path.splitext(input_path)[1].lower().replace('.', '')

        # If already WAV, return as is
        if file_ext == 'wav':
            return input_path

        # Load audio file using pydub
        if file_ext == 'mp3':
            audio = AudioSegment.from_mp3(input_path)
        elif file_ext == 'm4a':
            audio = AudioSegment.from_file(input_path, format='m4a')
        elif file_ext == 'ogg':
            audio = AudioSegment.from_ogg(input_path)
        elif file_ext == 'flac':
            audio = AudioSegment.from_file(input_path, format='flac')
        elif file_ext == 'webm':
            audio = AudioSegment.from_file(input_path, format='webm')
        elif file_ext == 'opus':
            audio = AudioSegment.from_file(input_path, format='opus')
        else:
            # Try generic approach
            audio = AudioSegment.from_file(input_path)

        # Convert to WAV format
        # Set parameters for speech recognition compatibility
        audio = audio.set_frame_rate(16000)  # 16kHz sample rate
        audio = audio.set_channels(1)  # Mono
        audio = audio.set_sample_width(2)  # 16-bit

        # Create output path
        output_path = os.path.splitext(input_path)[0] + '_converted.wav'

        # Export as WAV
        audio.export(output_path, format='wav')

        return output_path

    except Exception as e:
        print(f"Audio conversion error: {str(e)}")
        raise ValueError(f"Could not convert audio file: {str(e)}")

@app.route('/')
def index():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Voice Note Translator API',
        'version': '2.0',
        'endpoints': {
            '/api/translate': 'POST - Translate voice note',
            '/api/health': 'GET - Health check'
        }
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'speech_recognition': 'active',
            'translation': 'active'
        }
    })

@app.route('/api/translate', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit: 10 translations per minute
def translate_voice():
    """
    Translate voice note to English
    Accepts: audio file and optional language parameter
    Returns: JSON with original text and translation
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

        converted_filepath = None

        try:
            # Convert audio to WAV format if needed
            wav_filepath = convert_to_wav(filepath)
            if wav_filepath != filepath:
                converted_filepath = wav_filepath

            # Transcribe audio
            with sr.AudioFile(wav_filepath) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)

            # Map Nigerian languages to Google Speech Recognition language codes
            language_map = {
                'pidgin': 'en-NG',      # Nigerian English (Pidgin is English-based)
                'yoruba': 'yo-NG',      # Yoruba (Nigeria)
                'igbo': 'ig-NG',        # Igbo (Nigeria)
                'hausa': 'ha-NG',       # Hausa (Nigeria)
                'urhobo': 'en-NG',      # Urhobo (use Nigerian English as fallback)
                'auto': None            # Auto-detect
            }

            # Recognize speech with proper language support
            try:
                original_text = None
                error_messages = []

                if source_language == 'auto' or source_language not in language_map:
                    # Try multiple Nigerian languages
                    languages_to_try = ['en-NG', 'yo-NG', 'ig-NG', 'ha-NG', 'en-US']

                    for lang_code in languages_to_try:
                        try:
                            original_text = recognizer.recognize_google(
                                audio_data,
                                language=lang_code,
                                show_all=False
                            )
                            detected_language = lang_code
                            break
                        except sr.UnknownValueError:
                            error_messages.append(f"Failed with {lang_code}")
                            continue
                        except sr.RequestError as e:
                            error_messages.append(f"Service error with {lang_code}: {str(e)}")
                            continue

                    if not original_text:
                        return jsonify({
                            'success': False,
                            'error': 'Could not understand audio in any Nigerian language. Please ensure clear audio with minimal background noise.',
                            'details': error_messages
                        }), 400
                else:
                    # Use specified language
                    lang_code = language_map.get(source_language, 'en-NG')
                    original_text = recognizer.recognize_google(
                        audio_data,
                        language=lang_code,
                        show_all=False
                    )
                    detected_language = lang_code

            except sr.UnknownValueError:
                return jsonify({
                    'success': False,
                    'error': 'Could not understand audio. Please ensure clear audio with minimal background noise.'
                }), 400
            except sr.RequestError as e:
                return jsonify({
                    'success': False,
                    'error': f'Speech recognition service error: {str(e)}'
                }), 503
            
            # Detect language and translate
            try:
                detection = translator.detect(original_text)
                detected_language = detection.lang
                
                if detected_language == 'en':
                    translated_text = original_text
                    note = 'Text was already in English'
                else:
                    translation = translator.translate(original_text, dest='en')
                    translated_text = translation.text
                    note = None
                
                return jsonify({
                    'success': True,
                    'original_text': original_text,
                    'translated_text': translated_text,
                    'detected_language': detected_language,
                    'note': note
                })
                
            except Exception as e:
                # If translation fails, return original text
                return jsonify({
                    'success': True,
                    'original_text': original_text,
                    'translated_text': original_text,
                    'detected_language': 'unknown',
                    'note': 'Translation service unavailable, showing original text'
                })
        
        finally:
            # Clean up temporary files
            if os.path.exists(filepath):
                os.remove(filepath)
            if converted_filepath and os.path.exists(converted_filepath):
                os.remove(converted_filepath)
    
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
    print("=" * 60)
    print("Voice Note Translator API Server")
    print("=" * 60)
    print("\nServer starting...")
    print("API will be available at: http://localhost:5000")
    print("Documentation at: http://localhost:5000/")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
