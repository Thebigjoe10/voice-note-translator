// Voice Note Translator - Frontend JavaScript
// API Configuration
const API_URL = 'http://localhost:5000';  // Change this to your deployed API URL

// Global variables
let selectedFile = null;
let currentTranslation = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('Voice Note Translator loaded');
    setupDragAndDrop();
});

// Setup drag and drop
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('border-purple-500', 'bg-purple-50');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('border-purple-500', 'bg-purple-50');
        });
    });
    
    uploadArea.addEventListener('drop', handleDrop);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const file = files[0];
        document.getElementById('audioFile').files = files;
        handleFileSelect({ target: { files: [file] } });
    }
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/mp4', 'audio/ogg', 'audio/flac', 'audio/webm', 'audio/opus'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm', 'opus'];
    
    if (!allowedExtensions.includes(fileExtension)) {
        showToast('Invalid file type. Please upload an audio file.', 'error');
        return;
    }
    
    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('File too large. Maximum size is 10MB.', 'error');
        return;
    }
    
    selectedFile = file;
    
    // Display file info
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileInfo').classList.remove('hidden');
    
    // Enable translate button
    document.getElementById('translateBtn').disabled = false;
    
    showToast('File uploaded successfully!', 'success');
}

// Clear file
function clearFile() {
    selectedFile = null;
    document.getElementById('audioFile').value = '';
    document.getElementById('fileInfo').classList.add('hidden');
    document.getElementById('translateBtn').disabled = true;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Translate audio
async function translateAudio() {
    if (!selectedFile) {
        showToast('Please select an audio file first', 'error');
        return;
    }
    
    // Show processing status
    document.getElementById('processingStatus').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('translateBtn').disabled = true;
    
    // Create form data
    const formData = new FormData();
    formData.append('audio', selectedFile);
    
    try {
        // Call API
        const response = await fetch(`${API_URL}/api/translate`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store translation
            currentTranslation = data;
            
            // Display results
            displayResults(data);
            
            // Hide processing, show results
            document.getElementById('processingStatus').classList.add('hidden');
            document.getElementById('resultsSection').classList.remove('hidden');
            
            showToast('Translation complete!', 'success');
        } else {
            throw new Error(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        document.getElementById('processingStatus').classList.add('hidden');
        document.getElementById('translateBtn').disabled = false;
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Display results
function displayResults(data) {
    // Original text
    document.getElementById('originalText').textContent = data.original_text;
    
    // Translated text
    document.getElementById('translatedText').textContent = data.translated_text;
    
    // Detected language
    const languageNames = {
        'en': 'English',
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'ha': 'Hausa',
        'pidgin': 'Nigerian Pidgin'
    };
    
    const langName = languageNames[data.detected_language] || data.detected_language;
    document.getElementById('langName').textContent = langName;
    
    // Note (if any)
    if (data.note) {
        document.getElementById('noteText').textContent = data.note;
        document.getElementById('translationNote').classList.remove('hidden');
    } else {
        document.getElementById('translationNote').classList.add('hidden');
    }
}

// Copy translation
function copyTranslation() {
    if (!currentTranslation) return;
    
    const textToCopy = currentTranslation.translated_text;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        showToast('Translation copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Failed to copy. Please try again.', 'error');
    });
}

// Download translation
function downloadTranslation() {
    if (!currentTranslation) return;
    
    const content = `VOICE NOTE TRANSLATION
${'='.repeat(60)}

ORIGINAL TRANSCRIPTION
Language: ${currentTranslation.detected_language}
${'-'.repeat(60)}
${currentTranslation.original_text}

ENGLISH TRANSLATION
${'-'.repeat(60)}
${currentTranslation.translated_text}

${'='.repeat(60)}
Generated by Voice Note Translator
Date: ${new Date().toLocaleString()}
`;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translation_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Translation downloaded!', 'success');
}

// Share to WhatsApp
function shareToWhatsApp() {
    if (!currentTranslation) return;
    
    const text = encodeURIComponent(
        `Translation:\n\n${currentTranslation.translated_text}\n\n---\nOriginal: ${currentTranslation.original_text}`
    );
    
    // Check if mobile
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    if (isMobile) {
        // Open WhatsApp app
        window.location.href = `whatsapp://send?text=${text}`;
    } else {
        // Open WhatsApp Web
        window.open(`https://web.whatsapp.com/send?text=${text}`, '_blank');
    }
}

// Reset translator
function resetTranslator() {
    clearFile();
    currentTranslation = null;
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('processingStatus').classList.add('hidden');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Show help modal
function showHelp() {
    document.getElementById('helpModal').classList.remove('hidden');
}

// Close help modal
function closeHelp() {
    document.getElementById('helpModal').classList.add('hidden');
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    
    // Set icon and color based on type
    if (type === 'success') {
        toastIcon.className = 'fas fa-check-circle text-green-500 text-xl mr-3';
    } else if (type === 'error') {
        toastIcon.className = 'fas fa-exclamation-circle text-red-500 text-xl mr-3';
    } else if (type === 'info') {
        toastIcon.className = 'fas fa-info-circle text-blue-500 text-xl mr-3';
    }
    
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + V to paste (for future implementation)
    if ((e.ctrlKey || e.metaKey) && e.key === 'v' && currentTranslation) {
        // Could implement paste functionality
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        closeHelp();
    }
});
