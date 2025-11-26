# ⚡ PERFORMANCE OPTIMIZATION GUIDE
## Voice Note Translator - Speed & Scale

═══════════════════════════════════════════════════════════════

This guide covers techniques to make your application faster, more efficient, and ready to scale.

---

## 🚀 CACHING STRATEGIES

### 1. Translation Cache

**Cache common phrases to avoid repeated API calls:**

```python
from functools import lru_cache
from datetime import datetime, timedelta
import hashlib

# In-memory cache for recent translations
translation_cache = {}
CACHE_EXPIRY = 3600  # 1 hour

def get_cache_key(text):
    """Generate cache key from text"""
    return hashlib.md5(text.encode()).hexdigest()

def get_cached_translation(text):
    """Get translation from cache"""
    key = get_cache_key(text)

    if key in translation_cache:
        cached_data, timestamp = translation_cache[key]

        # Check if cache is still valid
        if datetime.now() - timestamp < timedelta(seconds=CACHE_EXPIRY):
            return cached_data

        # Remove expired cache
        del translation_cache[key]

    return None

def cache_translation(text, translation_data):
    """Store translation in cache"""
    key = get_cache_key(text)
    translation_cache[key] = (translation_data, datetime.now())

# In translate_voice()
cached = get_cached_translation(original_text)
if cached:
    return jsonify({
        'success': True,
        'cached': True,
        **cached
    })

# After successful translation
cache_translation(original_text, {
    'original_text': original_text,
    'translated_text': translated_text,
    'detected_language': detected_language
})
```

---

### 2. Redis Cache

**Use Redis for persistent, distributed caching:**

```python
import redis
import json

# Connect to Redis
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=6379,
    db=0,
    decode_responses=True
)

def get_redis_translation(text):
    """Get translation from Redis"""
    key = f"translation:{get_cache_key(text)}"

    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)

    return None

def cache_redis_translation(text, translation_data, ttl=3600):
    """Store translation in Redis with TTL"""
    key = f"translation:{get_cache_key(text)}"
    redis_client.setex(
        key,
        ttl,
        json.dumps(translation_data)
    )

# In translate_voice()
cached = get_redis_translation(original_text)
if cached:
    return jsonify({
        'success': True,
        'cached': True,
        **cached
    })

# After translation
cache_redis_translation(original_text, {
    'original_text': original_text,
    'translated_text': translated_text,
    'detected_language': detected_language
})
```

---

### 3. CDN for Static Files

**Serve static files from CDN:**

```html
<!-- Instead of local files -->
<script src="app.js"></script>

<!-- Use CDN (after uploading to CDN) -->
<script src="https://cdn.yourapp.com/app.js"></script>
```

**Popular CDN Options:**
- **Cloudflare:** Free tier, easy setup
- **AWS CloudFront:** Scalable, integrates with S3
- **Fastly:** High performance
- **BunnyCDN:** Affordable

**Setup with Cloudflare:**
1. Sign up at cloudflare.com
2. Add your domain
3. Update nameservers
4. Enable caching rules
5. Assets automatically cached

---

## 🔄 ASYNC PROCESSING

### 1. Background Jobs with Celery

**Offload heavy tasks to background workers:**

```python
# Install Celery
# pip install celery redis

from celery import Celery

# Configure Celery
celery = Celery(
    'tasks',
    broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Define background task
@celery.task(name='translate_audio_async')
def translate_audio_async(filepath, user_id=None):
    """Process audio translation in background"""
    try:
        # Convert to WAV
        wav_filepath = convert_to_wav(filepath)

        # Transcribe
        with sr.AudioFile(wav_filepath) as source:
            audio_data = recognizer.record(source)

        original_text = recognizer.recognize_google(audio_data)

        # Translate
        translation = translator.translate(original_text, dest='en')

        result = {
            'success': True,
            'original_text': original_text,
            'translated_text': translation.text,
            'detected_language': translation.src
        }

        # Cleanup
        os.remove(filepath)
        if wav_filepath != filepath:
            os.remove(wav_filepath)

        # Store result in cache or database
        if user_id:
            store_translation_result(user_id, result)

        return result

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# In Flask app
@app.route('/api/translate_async', methods=['POST'])
@limiter.limit("20 per minute")  # Higher limit for async
def translate_voice_async():
    """Submit translation job to queue"""
    # Save file
    file = request.files['audio']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Submit to queue
    task = translate_audio_async.delay(filepath, user_id=get_current_user_id())

    return jsonify({
        'success': True,
        'task_id': task.id,
        'status': 'processing',
        'message': 'Translation job submitted'
    })

# Check job status
@app.route('/api/translate_status/<task_id>')
def check_translation_status(task_id):
    """Check translation job status"""
    task = translate_audio_async.AsyncResult(task_id)

    if task.ready():
        result = task.get()
        return jsonify({
            'status': 'completed',
            'result': result
        })
    elif task.failed():
        return jsonify({
            'status': 'failed',
            'error': str(task.info)
        })
    else:
        return jsonify({
            'status': 'processing',
            'progress': task.info.get('progress', 0) if task.info else 0
        })
```

**Start Celery worker:**
```bash
celery -A app.celery worker --loglevel=info
```

---

### 2. WebSocket for Real-Time Updates

**Push updates to clients without polling:**

```python
# Install Flask-SocketIO
# pip install flask-socketio python-socketio

from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('translate_request')
def handle_translate_request(data):
    """Handle translation request via WebSocket"""
    # Process in background
    task = translate_audio_async.delay(data['filepath'])

    # Monitor task and emit updates
    while not task.ready():
        emit('translation_progress', {
            'status': 'processing',
            'progress': 50
        })
        socketio.sleep(1)

    # Send result
    result = task.get()
    emit('translation_complete', result)

# Run with socketio
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

**Frontend JavaScript:**
```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('translation_progress', (data) => {
    // Update progress bar
    document.getElementById('progress').style.width = data.progress + '%';
});

socket.on('translation_complete', (data) => {
    // Display results
    displayResults(data);
});

// Send translation request
socket.emit('translate_request', {
    filepath: '/path/to/file'
});
```

---

## 🗄️ DATABASE OPTIMIZATION

### 1. Connection Pooling

**Reuse database connections:**

```python
from sqlalchemy.pool import QueuePool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,          # Max connections
    'pool_recycle': 3600,     # Recycle after 1 hour
    'pool_pre_ping': True,    # Verify connections
    'max_overflow': 10,       # Extra connections when needed
    'pool_timeout': 30        # Wait timeout
}
```

---

### 2. Query Optimization

**Use indexes and efficient queries:**

```python
from sqlalchemy import Index

class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    original_text = db.Column(db.Text)
    translated_text = db.Column(db.Text)

    # Composite index for common queries
    __table_args__ = (
        Index('ix_user_created', 'user_id', 'created_at'),
    )

# Efficient query with pagination
@app.route('/api/history')
def get_history():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    translations = Translation.query\
        .filter_by(user_id=current_user.id)\
        .order_by(Translation.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'translations': [t.to_dict() for t in translations.items],
        'total': translations.total,
        'pages': translations.pages,
        'current_page': page
    })
```

---

### 3. Lazy Loading

**Load data only when needed:**

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Lazy load translations
    translations = db.relationship('Translation', lazy='dynamic', backref='user')

# Query only what you need
recent_count = user.translations.filter(
    Translation.created_at >= datetime.now() - timedelta(days=7)
).count()
```

---

## 🎯 FRONTEND OPTIMIZATION

### 1. Lazy Loading Images

```html
<img src="placeholder.jpg" data-src="actual-image.jpg" loading="lazy">

<script>
// Intersection Observer for lazy loading
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            observer.unobserve(img);
        }
    });
});

document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});
</script>
```

---

### 2. Minify Assets

**Compress JavaScript and CSS:**

```bash
# Install minifier
npm install -g terser clean-css-cli

# Minify JavaScript
terser app.js -o app.min.js -c -m

# Minify CSS (if you have custom CSS)
cleancss -o styles.min.css styles.css
```

**Update HTML to use minified files:**
```html
<script src="app.min.js"></script>
```

---

### 3. Service Workers for Offline Support

```javascript
// service-worker.js
const CACHE_NAME = 'voice-translator-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/app.js',
    '/styles.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
```

**Register in app.js:**
```javascript
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
        .then(reg => console.log('Service Worker registered'))
        .catch(err => console.log('Service Worker registration failed'));
}
```

---

## 📊 SCALING STRATEGIES

### 1. Load Balancer

**Use Nginx as reverse proxy:**

```nginx
# /etc/nginx/sites-available/voice-translator

upstream voice_translator {
    least_conn;  # Use least connections algorithm
    server 127.0.0.1:5000 weight=1;
    server 127.0.0.1:5001 weight=1;
    server 127.0.0.1:5002 weight=1;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://voice_translator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Cache static files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Run multiple Flask instances:**
```bash
# Terminal 1
gunicorn -w 4 -b 127.0.0.1:5000 app:app

# Terminal 2
gunicorn -w 4 -b 127.0.0.1:5001 app:app

# Terminal 3
gunicorn -w 4 -b 127.0.0.1:5002 app:app
```

---

### 2. Horizontal Scaling

**Deploy multiple instances:**

```yaml
# docker-compose.yml for multiple instances
version: '3'
services:
  app1:
    build: .
    environment:
      - FLASK_ENV=production
    ports:
      - "5000:5000"

  app2:
    build: .
    environment:
      - FLASK_ENV=production
    ports:
      - "5001:5000"

  app3:
    build: .
    environment:
      - FLASK_ENV=production
    ports:
      - "5002:5000"

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2
      - app3

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

---

### 3. Auto-Scaling with Kubernetes

**Basic Kubernetes deployment:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-translator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: voice-translator
  template:
    metadata:
      labels:
        app: voice-translator
    spec:
      containers:
      - name: app
        image: your-registry/voice-translator:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: voice-translator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: voice-translator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 🔧 APPLICATION OPTIMIZATION

### 1. Gzip Compression

**Enable compression in Flask:**

```python
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'text/javascript',
    'application/json',
    'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6  # 1-9, higher = more compression
app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress if >500 bytes
```

---

### 2. Database Query Caching

**Cache expensive queries:**

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/stats')
@cache.cached(timeout=600)  # Cache for 10 minutes
def get_stats():
    """Get usage statistics"""
    total_translations = Translation.query.count()
    total_users = User.query.count()

    return jsonify({
        'total_translations': total_translations,
        'total_users': total_users
    })

# Invalidate cache when data changes
@app.route('/api/translate', methods=['POST'])
def translate_voice():
    # ... translation code ...

    # Invalidate stats cache
    cache.delete('view//api/stats')

    return jsonify(result)
```

---

### 3. Optimize Audio Processing

**Process audio more efficiently:**

```python
# Use faster audio processing settings
def convert_to_wav_optimized(input_path):
    """Fast audio conversion"""
    file_ext = os.path.splitext(input_path)[1].lower().replace('.', '')

    if file_ext == 'wav':
        return input_path

    # Load audio
    audio = AudioSegment.from_file(input_path)

    # Optimize for speech recognition
    audio = audio.set_frame_rate(16000)  # Lower sample rate = faster
    audio = audio.set_channels(1)        # Mono
    audio = audio.set_sample_width(2)    # 16-bit

    # Export with faster settings
    output_path = os.path.splitext(input_path)[0] + '_converted.wav'
    audio.export(
        output_path,
        format='wav',
        parameters=["-ac", "1", "-ar", "16000"]  # FFmpeg optimization
    )

    return output_path
```

---

## 📈 MONITORING & METRICS

### 1. Application Monitoring

**Track performance metrics:**

```python
import time
from functools import wraps

def track_time(f):
    """Decorator to track function execution time"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start

        # Log slow requests
        if duration > 5.0:  # 5 seconds
            app.logger.warning(f"Slow request: {f.__name__} took {duration:.2f}s")

        return result
    return wrapper

@app.route('/api/translate', methods=['POST'])
@track_time
def translate_voice():
    # ... existing code ...
```

---

### 2. Performance Dashboard

**Create metrics endpoint:**

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Track custom metrics
translation_counter = metrics.counter(
    'translations_total',
    'Total number of translations'
)

translation_duration = metrics.histogram(
    'translation_duration_seconds',
    'Translation processing time'
)

@app.route('/api/translate', methods=['POST'])
def translate_voice():
    with translation_duration.time():
        # ... translation code ...
        translation_counter.inc()
        return jsonify(result)

# Metrics available at /metrics endpoint
```

---

## ⚡ PERFORMANCE CHECKLIST

### Before Deployment:

- [ ] ✅ Enable caching (Redis)
- [ ] ✅ Set up CDN for static files
- [ ] ✅ Implement async processing (Celery)
- [ ] ✅ Optimize database queries
- [ ] ✅ Add database indexes
- [ ] ✅ Enable Gzip compression
- [ ] ✅ Minify JavaScript/CSS
- [ ] ✅ Set up load balancer
- [ ] ✅ Configure connection pooling
- [ ] ✅ Implement lazy loading
- [ ] ✅ Add monitoring/metrics
- [ ] ✅ Set up auto-scaling
- [ ] ✅ Optimize audio processing
- [ ] ✅ Cache common translations
- [ ] ✅ Use WebSockets for real-time updates

---

## 🎯 PERFORMANCE TARGETS

### Response Times:
- **API Health Check:** < 50ms
- **File Upload:** < 100ms
- **Audio Conversion:** < 2 seconds
- **Speech Recognition:** < 5 seconds
- **Translation:** < 1 second
- **Total Process:** < 10 seconds

### Throughput:
- **Free Tier:** 100 requests/day per user
- **Basic Tier:** 1,000 requests/day per user
- **Premium Tier:** 10,000 requests/day per user

---

**Make it fast, make it scale! ⚡**
