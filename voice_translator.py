#!/usr/bin/env python3
"""
Voice Note Translator - Nigerian Pidgin & Native Languages
Translates voice notes to English with high accuracy
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import speech_recognition as sr
from googletrans import Translator
import os
from pathlib import Path
import threading

class VoiceTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Note Translator - Nigerian Languages")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.audio_file_path = None
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#1a1a2e')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🎤 Voice Note Translator",
            font=('Arial', 24, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Nigerian Pidgin & Native Languages to English",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        subtitle_label.pack()
        
        # File selection frame
        file_frame = tk.Frame(self.root, bg='#16213e')
        file_frame.pack(pady=20, padx=40, fill='x')
        
        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=('Arial', 11),
            bg='#16213e',
            fg='#ffffff',
            wraplength=600
        )
        self.file_label.pack(pady=10)
        
        btn_frame = tk.Frame(file_frame, bg='#16213e')
        btn_frame.pack(pady=10)
        
        self.upload_btn = tk.Button(
            btn_frame,
            text="📁 Upload Voice Note",
            command=self.upload_file,
            font=('Arial', 12, 'bold'),
            bg='#00d4ff',
            fg='#000000',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        self.upload_btn.pack(side='left', padx=5)
        
        self.translate_btn = tk.Button(
            btn_frame,
            text="🔄 Transcribe & Translate",
            command=self.start_translation,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.translate_btn.pack(side='left', padx=5)
        
        # Language selection
        lang_frame = tk.Frame(self.root, bg='#16213e')
        lang_frame.pack(pady=10, padx=40, fill='x')
        
        tk.Label(
            lang_frame,
            text="Source Language:",
            font=('Arial', 11, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        ).pack(side='left', padx=10)
        
        self.lang_var = tk.StringVar(value="Auto-detect")
        languages = [
            "Auto-detect",
            "Nigerian Pidgin",
            "Yoruba",
            "Igbo",
            "Hausa",
            "Urhobo"
        ]
        
        self.lang_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=languages,
            font=('Arial', 10),
            state='readonly',
            width=20
        )
        self.lang_dropdown.pack(side='left', padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=800
        )
        self.progress.pack(pady=10)
        
        # Results frame
        results_frame = tk.Frame(self.root, bg='#1a1a2e')
        results_frame.pack(pady=10, padx=40, fill='both', expand=True)
        
        # Original transcription
        tk.Label(
            results_frame,
            text="📝 Original Transcription:",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        ).pack(anchor='w', pady=(5, 5))
        
        self.original_text = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            font=('Arial', 11),
            bg='#16213e',
            fg='#ffffff',
            insertbackground='#ffffff',
            wrap='word'
        )
        self.original_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # English translation
        tk.Label(
            results_frame,
            text="🌐 English Translation:",
            font=('Arial', 12, 'bold'),
            bg='#1a1a2e',
            fg='#4CAF50'
        ).pack(anchor='w', pady=(5, 5))
        
        self.translated_text = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            font=('Arial', 11),
            bg='#16213e',
            fg='#ffffff',
            insertbackground='#ffffff',
            wrap='word'
        )
        self.translated_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Copy and Save buttons
        action_frame = tk.Frame(self.root, bg='#1a1a2e')
        action_frame.pack(pady=10)
        
        self.copy_btn = tk.Button(
            action_frame,
            text="📋 Copy Translation",
            command=self.copy_translation,
            font=('Arial', 10),
            bg='#ff6b6b',
            fg='#ffffff',
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.copy_btn.pack(side='left', padx=5)
        
        self.save_btn = tk.Button(
            action_frame,
            text="💾 Save Translation",
            command=self.save_translation,
            font=('Arial', 10),
            bg='#ff6b6b',
            fg='#ffffff',
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            state='disabled'
        )
        self.save_btn.pack(side='left', padx=5)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready to translate voice notes",
            font=('Arial', 9),
            bg='#16213e',
            fg='#ffffff',
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_label.pack(side='bottom', fill='x')
        
    def upload_file(self):
        """Upload audio file"""
        file_types = [
            ("Audio Files", "*.wav *.mp3 *.m4a *.ogg *.flac"),
            ("All Files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Voice Note",
            filetypes=file_types
        )
        
        if filepath:
            self.audio_file_path = filepath
            filename = os.path.basename(filepath)
            self.file_label.config(text=f"Selected: {filename}")
            self.translate_btn.config(state='normal')
            self.status_label.config(text=f"File loaded: {filename}")
            
    def start_translation(self):
        """Start translation in separate thread"""
        if not self.audio_file_path:
            messagebox.showwarning("No File", "Please upload a voice note first!")
            return
            
        # Start translation in background thread
        thread = threading.Thread(target=self.translate_audio, daemon=True)
        thread.start()
        
    def translate_audio(self):
        """Transcribe and translate audio"""
        try:
            # Update UI
            self.root.after(0, self.update_status, "Processing audio file...")
            self.root.after(0, self.progress.start)
            self.root.after(0, lambda: self.translate_btn.config(state='disabled'))
            
            # Clear previous results
            self.root.after(0, lambda: self.original_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.translated_text.delete('1.0', tk.END))
            
            # Transcribe audio
            self.root.after(0, self.update_status, "Transcribing voice note...")

            with sr.AudioFile(self.audio_file_path) as source:
                # Adjust for ambient noise to improve recognition
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)

            # Map Nigerian languages to Google Speech Recognition language codes
            language_map = {
                "Nigerian Pidgin": "en-NG",   # Nigerian English (Pidgin is English-based)
                "Yoruba": "yo-NG",             # Yoruba (Nigeria)
                "Igbo": "ig-NG",               # Igbo (Nigeria)
                "Hausa": "ha-NG",              # Hausa (Nigeria)
                "Urhobo": "en-NG",             # Urhobo (use Nigerian English as fallback)
                "Auto-detect": None            # Auto-detect
            }

            # Get selected language
            selected_lang = self.lang_var.get()

            # Try to recognize speech
            try:
                original_text = None

                if selected_lang == "Auto-detect":
                    # Try multiple Nigerian languages
                    languages_to_try = [
                        ("en-NG", "Nigerian English/Pidgin"),
                        ("yo-NG", "Yoruba"),
                        ("ig-NG", "Igbo"),
                        ("ha-NG", "Hausa"),
                        ("en-US", "English")
                    ]

                    for lang_code, lang_name in languages_to_try:
                        try:
                            self.root.after(0, self.update_status, f"Trying {lang_name}...")
                            original_text = self.recognizer.recognize_google(
                                audio_data,
                                language=lang_code
                            )
                            self.root.after(0, self.update_status, f"Recognized as {lang_name}")
                            break
                        except sr.UnknownValueError:
                            continue

                    if not original_text:
                        raise sr.UnknownValueError()
                else:
                    # Use specific language
                    lang_code = language_map.get(selected_lang, "en-NG")
                    original_text = self.recognizer.recognize_google(
                        audio_data,
                        language=lang_code
                    )

                self.root.after(0, lambda: self.original_text.insert('1.0', original_text))

            except sr.UnknownValueError:
                self.root.after(0, lambda: self.original_text.insert(
                    '1.0',
                    "Could not understand audio. Please ensure:\n"
                    "- Audio is clear with minimal background noise\n"
                    "- Speaking in one of the supported languages\n"
                    "- File format is supported (WAV works best)\n"
                    "- Try 'Auto-detect' mode for best results"
                ))
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.translate_btn.config(state='normal'))
                self.root.after(0, self.update_status, "Transcription failed")
                return

            except sr.RequestError as e:
                self.root.after(0, lambda: self.original_text.insert(
                    '1.0',
                    f"Could not connect to speech recognition service.\n"
                    f"Please check your internet connection."
                ))
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.translate_btn.config(state='normal'))
                self.root.after(0, self.update_status, "Connection error")
                return
            
            # Translate to English
            self.root.after(0, self.update_status, "Translating to English...")
            
            try:
                # Detect if text needs translation
                detection = self.translator.detect(original_text)
                
                if detection.lang == 'en':
                    # Already in English
                    translated = original_text
                    self.root.after(0, lambda: self.translated_text.insert(
                        '1.0',
                        f"{translated}\n\n[Note: Text was already in English]"
                    ))
                else:
                    # Translate to English
                    translation = self.translator.translate(original_text, dest='en')
                    translated = translation.text
                    self.root.after(0, lambda: self.translated_text.insert('1.0', translated))
                    
            except Exception as e:
                self.root.after(0, lambda: self.translated_text.insert(
                    '1.0',
                    f"Translation service unavailable.\n"
                    f"Showing original transcription only."
                ))
                translated = original_text
            
            # Update UI
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.translate_btn.config(state='normal'))
            self.root.after(0, lambda: self.copy_btn.config(state='normal'))
            self.root.after(0, lambda: self.save_btn.config(state='normal'))
            self.root.after(0, self.update_status, "Translation complete! ✓")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.translate_btn.config(state='normal'))
            self.root.after(0, self.update_status, f"Error occurred: {str(e)}")
            
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        
    def copy_translation(self):
        """Copy translation to clipboard"""
        translated = self.translated_text.get('1.0', 'end-1c')
        if translated:
            self.root.clipboard_clear()
            self.root.clipboard_append(translated)
            messagebox.showinfo("Copied", "Translation copied to clipboard!")
            
    def save_translation(self):
        """Save translation to file"""
        translated = self.translated_text.get('1.0', 'end-1c')
        original = self.original_text.get('1.0', 'end-1c')
        
        if not translated:
            messagebox.showwarning("Nothing to Save", "No translation to save!")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Translation"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=== ORIGINAL TRANSCRIPTION ===\n\n")
                    f.write(original)
                    f.write("\n\n=== ENGLISH TRANSLATION ===\n\n")
                    f.write(translated)
                    
                messagebox.showinfo("Saved", f"Translation saved to:\n{filepath}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")

def main():
    root = tk.Tk()
    app = VoiceTranslatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
