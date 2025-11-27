#!/usr/bin/env python3
"""
Voice Note Translator - Nigerian Pidgin & Native Languages
Translates voice notes to English with high accuracy using OpenAI Whisper
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from openai import OpenAI
from googletrans import Translator
import os
from pathlib import Path
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Note Translator - Nigerian Languages (Powered by Whisper)")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')

        # Initialize components
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.translator = Translator()
        self.audio_file_path = None

        # Check if API key is configured
        if not os.getenv('OPENAI_API_KEY'):
            messagebox.showwarning(
                "API Key Missing",
                "OpenAI API key not found!\n\n"
                "Please create a .env file with:\n"
                "OPENAI_API_KEY=your_api_key_here\n\n"
                "Get your API key from:\n"
                "https://platform.openai.com/api-keys"
            )

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

        tech_label = tk.Label(
            title_frame,
            text="⚡ Powered by OpenAI Whisper - Superior Accuracy",
            font=('Arial', 10, 'italic'),
            bg='#1a1a2e',
            fg='#4CAF50'
        )
        tech_label.pack(pady=5)
        
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
        """Transcribe and translate audio using OpenAI Whisper"""
        try:
            # Update UI
            self.root.after(0, self.update_status, "Processing audio file...")
            self.root.after(0, self.progress.start)
            self.root.after(0, lambda: self.translate_btn.config(state='disabled'))

            # Clear previous results
            self.root.after(0, lambda: self.original_text.delete('1.0', tk.END))
            self.root.after(0, lambda: self.translated_text.delete('1.0', tk.END))

            # Transcribe audio using Whisper
            self.root.after(0, self.update_status, "Transcribing with Whisper AI...")

            # Map Nigerian languages to Whisper language codes
            language_map = {
                "Nigerian Pidgin": None,      # Auto-detect (Whisper handles Pidgin better)
                "Yoruba": "yo",               # Yoruba
                "Igbo": "ig",                 # Igbo
                "Hausa": "ha",                # Hausa
                "Urhobo": None,               # Auto-detect (not officially supported)
                "Auto-detect": None           # Auto-detect
            }

            # Get selected language
            selected_lang = self.lang_var.get()
            whisper_language = language_map.get(selected_lang, None)

            # Transcribe using OpenAI Whisper API
            try:
                with open(self.audio_file_path, 'rb') as audio_file:
                    # Prepare transcription parameters
                    transcription_params = {
                        'file': audio_file,
                        'model': 'whisper-1',
                        'response_format': 'verbose_json',
                    }

                    # Add language parameter if specified
                    if whisper_language:
                        transcription_params['language'] = whisper_language

                    # Call Whisper API
                    response = self.openai_client.audio.transcriptions.create(**transcription_params)

                    original_text = response.text
                    detected_language = getattr(response, 'language', 'unknown')

                    # Map language codes to full names
                    language_names = {
                        'en': 'English',
                        'yo': 'Yoruba',
                        'ig': 'Igbo',
                        'ha': 'Hausa',
                        'pcm': 'Nigerian Pidgin'
                    }

                    detected_lang_name = language_names.get(detected_language, detected_language)

                    self.root.after(
                        0,
                        self.update_status,
                        f"Detected language: {detected_lang_name}"
                    )

                if not original_text or original_text.strip() == '':
                    raise ValueError("No speech detected in audio")

                self.root.after(0, lambda: self.original_text.insert('1.0', original_text))

            except Exception as e:
                error_msg = str(e)
                if 'api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
                    self.root.after(0, lambda: self.original_text.insert(
                        '1.0',
                        "API Key Error!\n\n"
                        "Please ensure you have:\n"
                        "1. Created a .env file in the project directory\n"
                        "2. Added: OPENAI_API_KEY=your_api_key_here\n"
                        "3. Get your API key from: https://platform.openai.com/api-keys\n\n"
                        f"Error details: {error_msg}"
                    ))
                else:
                    self.root.after(0, lambda: self.original_text.insert(
                        '1.0',
                        f"Transcription failed.\n\n"
                        f"Please ensure:\n"
                        f"- Audio file contains clear speech\n"
                        f"- You have internet connection\n"
                        f"- Your OpenAI API key is valid\n\n"
                        f"Error: {error_msg}"
                    ))
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.translate_btn.config(state='normal'))
                self.root.after(0, self.update_status, "Transcription failed")
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
