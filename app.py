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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm', 'opus'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize services
recognizer = sr.Recognizer()
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
def translate_voice():
    """
    Translate voice note to English
    Accepts: audio file
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
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Transcribe audio
            with sr.AudioFile(filepath) as source:
                audio_data = recognizer.record(source)
            
            # Recognize speech
            try:
                original_text = recognizer.recognize_google(audio_data)
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
            # Clean up temporary file
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
            {'code': 'yo', 'name': 'Yoruba'},
            {'code': 'ig', 'name': 'Igbo'},
            {'code': 'ha', 'name': 'Hausa'},
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
