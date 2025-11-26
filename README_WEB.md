# 🎤 Voice Note Translator - Web Application

**Transform Nigerian Pidgin & Native Language Voice Notes to English Instantly**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Platform](https://img.shields.io/badge/platform-web-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Overview

A powerful web application that accurately translates voice notes from Nigerian Pidgin, Yoruba, Igbo, and Hausa to English. Perfect for WhatsApp voice notes, recordings, and any audio content in Nigerian languages.

### ✨ Key Features

- 🎯 **Accurate Translation** - Specialized for Nigerian languages
- ⚡ **Fast Processing** - Results in 10-30 seconds
- 📱 **Mobile Optimized** - Works on phones, tablets, and desktops
- 🔒 **Privacy First** - No permanent storage of your audio
- 💬 **WhatsApp Ready** - Easy integration with WhatsApp voice notes
- 🌐 **Web-Based** - No installation required
- 🎨 **Modern UI** - Beautiful, intuitive interface

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements_web.txt
```

2. **Start Backend Server**
```bash
python app.py
```
Server will start at: http://localhost:5000

3. **Open Frontend**
- Open `index.html` in your browser
- Or serve with Python: `python -m http.server 8000`
- Access at: http://localhost:8000

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t voice-translator .
docker run -p 5000:5000 voice-translator
```

## 📱 How to Use

### From WhatsApp:

1. **Save Voice Note**
   - Long press voice note in WhatsApp
   - Tap "Forward" or "Share"
   - Save to your device

2. **Upload & Translate**
   - Open the web app
   - Upload the saved audio file
   - Click "Translate Voice Note"
   - Get instant English translation

3. **Share Back**
   - Copy translation
   - Or use "Share to WhatsApp" button

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)      │
│         - Tailwind CSS              │
│         - Drag & Drop Upload        │
│         - Real-time Status          │
└──────────────┬──────────────────────┘
               │ REST API
┌──────────────▼──────────────────────┐
│         Backend (Flask)             │
│         - File Processing           │
│         - Speech Recognition        │
│         - Translation Engine        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      External Services              │
│      - Google Speech API            │
│      - Google Translate API         │
└─────────────────────────────────────┘
```

## 🌍 Supported Languages

✅ **Current Support:**
- Nigerian Pidgin (Naija)
- Yoruba
- Igbo
- Hausa
- English

🔜 **Coming Soon:**
- Edo (Bini)
- Efik
- Ibibio
- Ijaw
- More Nigerian languages

## 📋 Supported Audio Formats

- WAV (recommended)
- MP3
- M4A
- OGG
- FLAC
- OPUS
- WEBM

**Max file size:** 10MB

## 🌐 Deployment

### Heroku

```bash
# Login and create app
heroku login
heroku create your-app-name

# Add buildpack
heroku buildpacks:add heroku/python

# Deploy
git push heroku main

# Open app
heroku open
```

### Render.com

1. Connect GitHub repository
2. Select "Web Service"
3. Build Command: `pip install -r requirements_web.txt`
4. Start Command: `gunicorn app:app`
5. Deploy!

### DigitalOcean App Platform

1. Create new app
2. Link repository
3. Select Python app
4. Auto-deploy enabled
5. Access your URL

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
MAX_CONTENT_LENGTH=10485760
ALLOWED_ORIGINS=https://yourdomain.com
```

### API URL Configuration

Update `app.js` line 3:
```javascript
const API_URL = 'https://your-api-domain.com';
```

## 📱 WhatsApp Integration

### Current: Manual Upload
Users can save WhatsApp voice notes and upload them manually.

### Future: Business API
Full WhatsApp Business API integration planned:
- Automatic voice note detection
- Direct translation in chat
- No manual upload needed

[Read WhatsApp Integration Guide](./WHATSAPP_INTEGRATION.md)

## 🎨 Customization

### Change Colors (Tailwind CSS)
Edit `index.html` Tailwind classes:
- Primary: `purple-600` → your color
- Accent: `green-500` → your color

### Add Languages
1. Update `app.py` languages list
2. Add to dropdown in `index.html`
3. Test translation accuracy

### Custom Branding
- Replace title and logo
- Update color scheme
- Add your company info

## 🔒 Security

### Best Practices Implemented:
✅ File type validation
✅ File size limits
✅ Temporary file storage
✅ Secure file handling
✅ CORS protection
✅ Input sanitization

### Recommended Additions:
- Rate limiting
- API authentication
- Request logging
- SSL/TLS encryption
- Regular security audits

## ⚡ Performance

### Current Metrics:
- Audio upload: < 2 seconds
- Processing: 10-30 seconds
- Translation: 2-5 seconds

### Optimization Tips:
- Use CDN for static files
- Implement caching
- Add load balancer
- Use background workers

## 🧪 Testing

Run tests (if available):
```bash
pytest tests/
```

Manual testing checklist:
- [ ] Upload various audio formats
- [ ] Test different languages
- [ ] Try large files (near limit)
- [ ] Test error handling
- [ ] Check mobile responsiveness

## 📊 API Endpoints

### GET `/`
Returns API information

### GET `/api/health`
Health check endpoint

### POST `/api/translate`
Translate voice note
- **Body:** FormData with 'audio' file
- **Returns:** JSON with translation

### GET `/api/languages`
Get supported languages list

## 🛠️ Troubleshooting

### CORS Errors
Update `app.py` CORS settings to include your domain

### File Upload Fails
- Check file size (max 10MB)
- Verify file format is supported
- Check network connection

### Translation Errors
- Ensure clear audio quality
- Check internet connection
- Verify API services are running

### Deployment Issues
- Check all environment variables
- Verify Python version (3.8+)
- Ensure FFmpeg is installed

## 📚 Documentation

- [Web Deployment Guide](./WEB_DEPLOYMENT_GUIDE.txt)
- [WhatsApp Integration](./WHATSAPP_INTEGRATION.md)
- [API Documentation](./API_DOCS.md)
- [Contributing Guide](./CONTRIBUTING.md)

## 🗺️ Roadmap

### Version 2.0 (Current)
✅ Web application
✅ Modern UI with Tailwind CSS
✅ WhatsApp sharing
✅ Mobile optimization

### Version 2.5 (Next)
- [ ] User accounts
- [ ] Translation history
- [ ] Batch processing
- [ ] Browser extension

### Version 3.0 (Future)
- [ ] WhatsApp Business API
- [ ] Real-time recording
- [ ] Mobile apps (iOS/Android)
- [ ] Custom language models

## 💡 Use Cases

- **Personal:** Translate family WhatsApp voice notes
- **Business:** Customer service communications
- **Education:** Language learning and research
- **Content Creation:** Transcribe and translate content
- **Accessibility:** Make audio content accessible

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request

## 📄 License

MIT License - free to use and modify

## 🙏 Acknowledgments

Built with:
- Flask (Backend)
- Tailwind CSS (Frontend)
- Google Speech Recognition
- Google Translate API

## 📞 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join our community]
- 🐦 Twitter: [@voicetranslator]
- 📱 WhatsApp: Coming soon!

## ⭐ Star Us!

If you find this useful, please star the repository!

---

**Made with ❤️ for the Nigerian Community**

Translate voice notes. Break language barriers. Connect better.
