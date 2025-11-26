# 🔒 SECURITY BEST PRACTICES
## Voice Note Translator - Production Security Guide

═══════════════════════════════════════════════════════════════

This guide covers essential security measures to protect your application and users.

---

## 🛡️ FILE UPLOAD SECURITY

### 1. File Type Validation (✓ Implemented)

**Current Implementation:**
```python
# app.py - Line 21
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm', 'opus'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

**Enhanced Validation:**
```python
import magic  # python-magic library

def validate_file_type(file):
    """Validate file type using magic numbers, not just extension"""
    # Check file extension
    if not allowed_file(file.filename):
        return False

    # Check actual file content (magic numbers)
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer

    allowed_mimes = [
        'audio/wav',
        'audio/mpeg',
        'audio/mp4',
        'audio/ogg',
        'audio/flac',
        'audio/webm',
        'audio/opus'
    ]

    return file_type in allowed_mimes
```

**Why This Matters:**
- Prevents malicious files disguised with audio extensions
- Protects against file upload exploits
- Validates actual file content, not just the name

---

### 2. File Size Limits (✓ Implemented)

**Current Implementation:**
```python
# app.py - Line 22
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
```

**Enhanced Size Control:**
```python
@app.before_request
def check_file_size():
    """Check file size before processing"""
    if request.method == 'POST' and request.files:
        file = request.files.get('audio')
        if file:
            # Check size before saving
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > MAX_FILE_SIZE:
                return jsonify({
                    'success': False,
                    'error': f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB'
                }), 413
```

**Recommended Limits:**
- **Free tier:** 10MB
- **Basic tier:** 25MB
- **Premium tier:** 50MB
- **Enterprise:** 100MB+

---

### 3. Malware Scanning

**Integrate ClamAV for virus scanning:**
```python
import pyclamd

def scan_for_malware(filepath):
    """Scan uploaded file for malware"""
    try:
        cd = pyclamd.ClamdUnixSocket()

        # Scan the file
        scan_result = cd.scan_file(filepath)

        if scan_result:
            # File is infected
            return False, "Malware detected"

        return True, "Clean"

    except Exception as e:
        # If scanner fails, log and decide policy
        print(f"Malware scan failed: {e}")
        return False, "Unable to verify file safety"

# In translate_voice()
is_safe, message = scan_for_malware(filepath)
if not is_safe:
    return jsonify({
        'success': False,
        'error': message
    }), 400
```

**Installation:**
```bash
# Install ClamAV
sudo apt-get install clamav clamav-daemon
sudo systemctl start clamav-daemon

# Python library
pip install pyclamd
```

---

### 4. Secure File Storage

**Use Temporary Storage (✓ Implemented):**
```python
# app.py - Line 20
UPLOAD_FOLDER = tempfile.gettempdir()

# Files are deleted after processing (Line 214-218)
finally:
    if os.path.exists(filepath):
        os.remove(filepath)
    if converted_filepath and os.path.exists(converted_filepath):
        os.remove(converted_filepath)
```

**Enhanced Cleanup:**
```python
import atexit
import signal

# Store active files
active_files = set()

def cleanup_files():
    """Cleanup all temporary files on shutdown"""
    for filepath in active_files:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass

# Register cleanup handlers
atexit.register(cleanup_files)
signal.signal(signal.SIGTERM, lambda s, f: cleanup_files())
```

---

## 🔐 API SECURITY

### 1. Rate Limiting (✓ Implemented)

**Current Implementation:**
```python
# app.py - Line 30-36
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/translate', methods=['POST'])
@limiter.limit("10 per minute")
```

**Enhanced Rate Limiting:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Use Redis for distributed rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    default_limits=["200 per day", "50 per hour"],
    headers_enabled=True  # Return rate limit info in headers
)

# Different limits for different endpoints
@app.route('/api/translate', methods=['POST'])
@limiter.limit("10 per minute")  # Strict for translations

@app.route('/api/health')
@limiter.limit("100 per minute")  # Relaxed for health checks
```

**Custom Rate Limit Response:**
```python
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': e.description
    }), 429
```

---

### 2. API Authentication

**Implement API Key Authentication:**
```python
from functools import wraps
import secrets

# Generate API keys
def generate_api_key():
    return secrets.token_urlsafe(32)

# Store in database
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Decorator for API key validation
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 401

        # Validate key
        key = APIKey.query.filter_by(key=api_key, active=True).first()
        if not key:
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 403

        return f(*args, **kwargs)
    return decorated_function

# Protect endpoints
@app.route('/api/translate', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def translate_voice():
    # ... existing code ...
```

---

### 3. Input Validation

**Sanitize All Inputs:**
```python
from bleach import clean

def sanitize_input(text, max_length=5000):
    """Sanitize text input"""
    if not text:
        return ""

    # Remove HTML/script tags
    text = clean(text, tags=[], strip=True)

    # Limit length
    text = text[:max_length]

    # Remove null bytes
    text = text.replace('\x00', '')

    return text.strip()

# In translate_voice()
if 'language' in request.form:
    target_lang = sanitize_input(request.form['language'], max_length=10)
```

---

### 4. HTTPS Only

**Force HTTPS in Production:**
```python
from flask_talisman import Talisman

# Force HTTPS
Talisman(app,
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000
)

# Or with configuration
if not app.debug:
    @app.before_request
    def before_request():
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
```

**Update CORS for Production:**
```python
# Only allow specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com", "https://www.yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "X-API-Key"]
    }
})
```

---

## 🔑 DATA PRIVACY

### 1. No Permanent Storage (✓ Implemented)

**Best Practices:**
```python
# NEVER store audio files permanently
# NEVER log sensitive content
# ALWAYS delete files after processing

# Logging configuration
import logging

# Don't log sensitive data
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Filter sensitive data from logs
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Don't log actual text content
        if 'original_text' in str(record.msg):
            record.msg = 'Translation processed (content hidden)'
        return True

logging.getLogger().addFilter(SensitiveDataFilter())
```

---

### 2. Encryption at Rest

**Encrypt Sensitive Data:**
```python
from cryptography.fernet import Fernet
import os

# Generate encryption key (store securely!)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_text(text):
    """Encrypt sensitive text"""
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text):
    """Decrypt text"""
    return cipher.decrypt(encrypted_text.encode()).decode()

# Store encrypted in database
translation.original_text = encrypt_text(original_text)
```

---

### 3. Privacy Policy

**Create privacy policy page:**
```html
<!-- privacy.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Privacy Policy - Voice Note Translator</title>
</head>
<body>
    <h1>Privacy Policy</h1>

    <h2>Data Collection</h2>
    <p>We collect:</p>
    <ul>
        <li>Audio files (temporarily, deleted after processing)</li>
        <li>IP addresses (for rate limiting)</li>
        <li>Usage statistics (anonymized)</li>
    </ul>

    <h2>Data Storage</h2>
    <p>We DO NOT permanently store:</p>
    <ul>
        <li>Your audio files</li>
        <li>Transcribed text</li>
        <li>Translated content</li>
    </ul>

    <h2>Data Security</h2>
    <p>We protect your data with:</p>
    <ul>
        <li>HTTPS encryption</li>
        <li>Temporary file storage</li>
        <li>Automatic file deletion</li>
        <li>Rate limiting protection</li>
    </ul>

    <h2>Third-Party Services</h2>
    <p>We use:</p>
    <ul>
        <li>Google Speech Recognition API</li>
        <li>Google Translate API</li>
    </ul>

    <h2>Contact</h2>
    <p>Questions? Email: privacy@yourapp.com</p>
</body>
</html>
```

---

## 🛠️ SECURE CONFIGURATION

### 1. Environment Variables

**Never hardcode secrets:**
```python
# ❌ BAD - Don't do this
API_KEY = "sk_live_1234567890abcdef"

# ✅ GOOD - Use environment variables
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

**Create .env file (NEVER commit this!):**
```bash
# .env
SECRET_KEY=your-secret-key-here-generate-random
GOOGLE_CLOUD_API_KEY=your-key
AZURE_SPEECH_KEY=your-key
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
ENCRYPTION_KEY=your-encryption-key
```

**Add to .gitignore:**
```bash
# .gitignore
.env
*.pem
*.key
secrets/
```

---

### 2. Secure Headers

**Add security headers:**
```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# Security headers
Talisman(app,
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", 'cdn.tailwindcss.com', 'cdnjs.cloudflare.com'],
        'style-src': ["'self'", 'fonts.googleapis.com', "'unsafe-inline'"],
        'font-src': ["'self'", 'fonts.gstatic.com'],
        'img-src': ["'self'", 'data:'],
    },
    content_security_policy_nonce_in=['script-src']
)

# Additional headers
@app.after_request
def set_secure_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

---

### 3. Database Security

**Secure database connections:**
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,  # Verify connections
    'connect_args': {
        'sslmode': 'require',  # Require SSL for PostgreSQL
        'connect_timeout': 10
    }
}

# Prepare statements to prevent SQL injection
from sqlalchemy import text

# ❌ BAD - SQL injection vulnerable
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ GOOD - Parameterized query
query = text("SELECT * FROM users WHERE email = :email")
result = db.session.execute(query, {"email": email})
```

---

## 🚨 ERROR HANDLING

### 1. Don't Expose Sensitive Info

**Generic error messages:**
```python
@app.errorhandler(Exception)
def handle_error(error):
    """Generic error handler"""

    # Log detailed error (internal only)
    app.logger.error(f"Error: {str(error)}")
    app.logger.error(traceback.format_exc())

    # Return generic message to user
    if app.debug:
        # Development: show details
        return jsonify({
            'success': False,
            'error': str(error),
            'traceback': traceback.format_exc()
        }), 500
    else:
        # Production: hide details
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please try again later.'
        }), 500
```

---

### 2. Monitoring & Alerts

**Set up error monitoring:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment='production'
)

# Alert on suspicious activity
def alert_suspicious_activity(reason, details):
    """Send alert for security events"""
    # Send to Slack, email, etc.
    import requests

    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={
            'text': f'🚨 Security Alert: {reason}',
            'attachments': [{
                'color': 'danger',
                'fields': [
                    {'title': 'Details', 'value': details}
                ]
            }]
        })

# Use in code
if too_many_failed_attempts:
    alert_suspicious_activity(
        'Rate limit exceeded',
        f'IP: {request.remote_addr}'
    )
```

---

## 📋 SECURITY CHECKLIST

### Before Deployment:

- [ ] ✅ Enable HTTPS (SSL/TLS certificate)
- [ ] ✅ Set up rate limiting with Redis
- [ ] ✅ Validate file types using magic numbers
- [ ] ✅ Scan uploads for malware
- [ ] ✅ Use secure session cookies
- [ ] ✅ Implement API authentication
- [ ] ✅ Add security headers (CSP, HSTS, etc.)
- [ ] ✅ Configure CORS properly
- [ ] ✅ Hide error details in production
- [ ] ✅ Use environment variables for secrets
- [ ] ✅ Enable logging and monitoring
- [ ] ✅ Set up automatic file cleanup
- [ ] ✅ Create privacy policy
- [ ] ✅ Implement input validation
- [ ] ✅ Use parameterized database queries
- [ ] ✅ Enable database SSL connections
- [ ] ✅ Set up backup system
- [ ] ✅ Configure firewall rules
- [ ] ✅ Regular security updates
- [ ] ✅ Penetration testing

---

## 🔄 REGULAR MAINTENANCE

### Security Updates:
```bash
# Update dependencies monthly
pip list --outdated
pip install --upgrade package-name

# Check for vulnerabilities
pip install safety
safety check

# Audit npm packages (if using Node.js)
npm audit
npm audit fix
```

### Monitoring:
- Monitor failed login attempts
- Track unusual API usage
- Review error logs daily
- Check rate limit violations
- Audit file upload patterns

---

## 🆘 INCIDENT RESPONSE

### If Security Breach Occurs:

1. **Immediate Actions:**
   - Take affected systems offline
   - Preserve logs and evidence
   - Change all credentials
   - Notify affected users

2. **Investigation:**
   - Review logs for entry point
   - Assess damage scope
   - Document timeline

3. **Recovery:**
   - Patch vulnerabilities
   - Restore from backups
   - Monitor for reinfection

4. **Prevention:**
   - Update security measures
   - Conduct post-mortem
   - Improve monitoring

---

## 📚 ADDITIONAL RESOURCES

- **OWASP Top 10:** https://owasp.org/Top10/
- **Flask Security:** https://flask.palletsprojects.com/security/
- **Web Security Basics:** https://developers.google.com/web/fundamentals/security

---

**Security is not a feature, it's a requirement! 🔒**
