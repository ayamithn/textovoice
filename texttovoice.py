import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyttsx3
import threading
import json
import os
from datetime import datetime
import time

voices = []
current_voice_index = 0
current_speed = 200
is_dark_mode = True

def initialize_voices():
    global voices
    try:
        temp_engine = pyttsx3.init()
        voices = temp_engine.getProperty('voices')
        temp_engine.stop()
        del temp_engine
        save_preferences()
    except:
        voices = []

def save_preferences():
    try:
        preferences = {
            'voice_index': current_voice_index,
            'speed': current_speed,
            'dark_mode': is_dark_mode,
            'last_used': datetime.now().isoformat()
        }
        with open('tts_preferences.json', 'w') as f:
            json.dump(preferences, f)
    except:
        pass

def load_preferences():
    global current_voice_index, current_speed, is_dark_mode
    try:
        if os.path.exists('tts_preferences.json'):
            with open('tts_preferences.json', 'r') as f:
                preferences = json.load(f)
            current_voice_index = preferences.get('voice_index', 0)
            current_speed = preferences.get('speed', 200)
            is_dark_mode = preferences.get('dark_mode', True)
    except:
        pass

def animate_button(button):
    original_bg = button.cget('bg')
    def pulse():
        colors = ['#00ff88', '#00cc66', '#009944', original_bg]
        for color in colors:
            button.configure(bg=color)
            root.update()
            time.sleep(0.075)
    thread = threading.Thread(target=pulse)
    thread.daemon = True
    thread.start()

def update_progress_bar(progress):
    progress_var.set(progress)
    progress_label.configure(text=f"⚡ Progression: {int(progress)}%")
    root.update()

def speak():
    global voices, current_voice_index, current_speed
    text = text_area.get("1.0", tk.END).strip()
    if text:
        animate_button(button)
        def speak_thread():
            try:
                engine = pyttsx3.init()
                if len(voices) > 0:
                    engine.setProperty('voice', voices[current_voice_index].id)
                engine.setProperty('rate', current_speed)
                
                words = text.split()
                total_words = len(words)
                for i, word in enumerate(words):
                    if i % 10 == 0:
                        progress = (i / total_words) * 100
                        root.after(0, lambda p=progress: update_progress_bar(p))
                
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                del engine
                root.after(0, lambda: update_progress_bar(100))
                root.after(1000, lambda: update_progress_bar(0))
            except Exception as e:
                print(f"Error: {e}")
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()

def change_voice():
    global voices, current_voice_index
    try:
        if len(voices) > 0:
            current_voice_index = (current_voice_index + 1) % len(voices)
            voice_name = voices[current_voice_index].name.split(' - ')[0] if ' - ' in voices[current_voice_index].name else voices[current_voice_index].name
            voice_button.configure(text=f"🎤 {voice_name}")
            animate_button(voice_button)
            save_preferences()
        else:
            voice_button.configure(text="🎤 No voices available")
    except:
        current_voice_index = 0
        voice_button.configure(text="🎤 Default")

def set_voice_speed(speed):
    global current_speed
    try:
        current_speed = speed
        speed_label.configure(text=f"⚡ Speed: {speed} WPM")
        save_preferences()
    except:
        pass

def typing_effect(widget, text):
    def type_char(index=0):
        if index <= len(text):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", text[:index] + "█")
            if index < len(text):
                root.after(30, lambda: type_char(index + 1))
            else:
                widget.delete("1.0", tk.END)
                widget.insert("1.0", text)
    type_char()

def import_document():
    file_path = filedialog.askopenfilename(
        title="🚀 Sélectionner un document texte",
        filetypes=[
            ("Fichiers texte", "*.txt"),
            ("Fichiers PDF", "*.pdf"),
            ("Fichiers Word", "*.docx"),
            ("Tous les fichiers", "*.*")
        ]
    )
    
    if file_path:
        try:
            animate_button(import_button)
            encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is not None:
                text_area.delete("1.0", tk.END)
                if len(content) > 10000:
                    content = content[:10000] + "..."
                    messagebox.showinfo("Information", "Le texte a été tronqué à 10000 caractères.")
                
                typing_effect(text_area, content)
                messagebox.showinfo("Succès", f"Document importé!\nFichier: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Erreur", "Impossible de lire le fichier.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")

def clear_text():
    animate_button(clear_button)
    def clear_animation():
        current_text = text_area.get("1.0", tk.END)
        for i in range(len(current_text), 0, -1):
            text_area.delete("1.0", tk.END)
            text_area.insert("1.0", current_text[:i])
            root.update()
            time.sleep(0.01)
        text_area.delete("1.0", tk.END)
    thread = threading.Thread(target=clear_animation)
    thread.daemon = True
    thread.start()

def toggle_dark_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    save_preferences()
    
    if is_dark_mode:
        bg_color = '#0a0a0a'
        fg_color = '#00ff88'
        secondary_bg = '#1a1a1a'
        button_bg = '#2a2a2a'
        button_hover = '#3a3a3a'
        
        root.configure(bg=bg_color)
        for widget in [label, speed_label, progress_label]:
            try:
                widget.configure(bg=bg_color, fg=fg_color, font=("Helvetica", 12, "bold"))
            except:
                pass
        
        text_area.configure(bg=secondary_bg, fg=fg_color, insertbackground=fg_color,
                           font=("Consolas", 11), selectbackground='#004400')
        
        for btn in [button, voice_button, import_button, clear_button, theme_button,
                   speed_slow, speed_normal, speed_fast]:
            try:
                btn.configure(bg=button_bg, fg=fg_color, activebackground=button_hover,
                             font=("Helvetica", 10, "bold"), relief='flat', borderwidth=2)
            except:
                pass

        theme_button.configure(text="☀️ Light Mode")
        for frame in [speed_frame, action_frame, text_frame, progress_frame]:
            try:
                frame.configure(bg=bg_color)
            except:
                pass
    else:
        bg_color = '#f0f0f0'
        fg_color = '#000000'
        
        root.configure(bg=bg_color)
        for widget in [label, speed_label, progress_label]:
            try:
                widget.configure(bg=bg_color, fg=fg_color, font=("Helvetica", 12))
            except:
                pass
        
        text_area.configure(bg='#ffffff', fg=fg_color, insertbackground=fg_color,
                           font=("Helvetica", 11), selectbackground='#b3d9ff')
        
        for btn in [button, voice_button, import_button, clear_button, theme_button,
                   speed_slow, speed_normal, speed_fast]:
            try:
                btn.configure(bg='#e0e0e0', fg=fg_color, activebackground='#d0d0d0',
                             font=("Helvetica", 10), relief='raised', borderwidth=1)
            except:
                pass

        theme_button.configure(text="🌙 Dark Mode")
        for frame in [speed_frame, action_frame, text_frame, progress_frame]:
            try:
                frame.configure(bg=bg_color)
            except:
                pass
load_preferences()
initialize_voices()

root = tk.Tk()
root.title("🚀 TestoVoice Engine")
root.geometry("900x700")
root.configure(bg='#0a0a0a')
root.resizable(True, True)

progress_var = tk.DoubleVar()

label = tk.Label(root, text="🎯 TESTOVOICE ENGINE", 
                font=("Helvetica", 16, "bold"), bg='#0a0a0a', fg='#00ff88')
label.pack(pady=15)


text_frame = tk.Frame(root, bg='#0a0a0a')
text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

text_area = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 12), bg='#1a1a1a', 
                   fg='#00ff88', height=12, width=80, relief=tk.FLAT, borderwidth=0,
                   insertbackground='#00ff88', selectbackground='#004400')
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview,
                        bg='#2a2a2a', troughcolor='#1a1a1a', activebackground='#00ff88')
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_area.config(yscrollcommand=scrollbar.set)

action_frame = tk.Frame(root, bg='#0a0a0a')
action_frame.pack(pady=10)

import_button = tk.Button(action_frame, text="📁 IMPORT DOCUMENT", command=import_document, 
                         font=("Helvetica", 11, "bold"), bg='#2a2a2a', fg='#00ff88',
                         relief='flat', borderwidth=2, pady=8, padx=15)
import_button.pack(side=tk.LEFT, padx=10)

clear_button = tk.Button(action_frame, text="🗑️ CLEAR ALL", command=clear_text, 
                        font=("Helvetica", 11, "bold"), bg='#2a2a2a', fg='#ff4444',
                        relief='flat', borderwidth=2, pady=8, padx=15)
clear_button.pack(side=tk.LEFT, padx=10)

button = tk.Button(root, text="🎵 TESTOVOICE SPEAK", command=speak, 
                  font=("Helvetica", 14, "bold"), bg='#2a2a2a', fg='#00ff88',
                  relief='flat', borderwidth=3, pady=12, padx=25)
button.pack(pady=15)

voice_button = tk.Button(root, text="🎤 Voice: Default", command=change_voice, 
                        font=("Helvetica", 10, "bold"), bg='#2a2a2a', fg='#00ff88',
                        relief='flat', borderwidth=2, pady=6)
voice_button.pack(pady=8)

progress_frame = tk.Frame(root, bg='#0a0a0a')
progress_frame.pack(pady=10, padx=20, fill=tk.X)

progress_label = tk.Label(progress_frame, text="⚡ Progression: 0%", 
                         font=("Helvetica", 10, "bold"), bg='#0a0a0a', fg='#00ff88')
progress_label.pack()

progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100,
                              style="Futuristic.Horizontal.TProgressbar")
progress_bar.pack(fill=tk.X, pady=5)

theme_button = tk.Button(root, text="☀️ Light Mode", command=toggle_dark_mode, 
                        font=("Helvetica", 10, "bold"), bg='#2a2a2a', fg='#ffaa00',
                        relief='flat', borderwidth=2, pady=6)
theme_button.pack(pady=8)

speed_frame = tk.Frame(root, bg='#0a0a0a')
speed_frame.pack(pady=15)

speed_label = tk.Label(speed_frame, text="⚡ Speed: 200 WPM", 
                      font=("Helvetica", 12, "bold"), bg='#0a0a0a', fg='#00ff88')
speed_label.pack(pady=5)

speed_controls = tk.Frame(speed_frame, bg='#0a0a0a')
speed_controls.pack()

speed_slow = tk.Button(speed_controls, text="🐌 SLOW", command=lambda: set_voice_speed(100), 
                      font=("Helvetica", 9, "bold"), bg='#2a2a2a', fg='#ffaa00',
                      relief='flat', borderwidth=2, padx=12, pady=4)
speed_slow.pack(side=tk.LEFT, padx=8)

speed_normal = tk.Button(speed_controls, text="⚡ NORMAL", command=lambda: set_voice_speed(200), 
                        font=("Helvetica", 9, "bold"), bg='#2a2a2a', fg='#00ff88',
                        relief='flat', borderwidth=2, padx=12, pady=4)
speed_normal.pack(side=tk.LEFT, padx=8)

speed_fast = tk.Button(speed_controls, text="🚀 FAST", command=lambda: set_voice_speed(300), 
                      font=("Helvetica", 9, "bold"), bg='#2a2a2a', fg='#ff4444',
                      relief='flat', borderwidth=2, padx=12, pady=4)
speed_fast.pack(side=tk.LEFT, padx=8)

style = ttk.Style()
style.theme_use('clam')
style.configure("Futuristic.Horizontal.TProgressbar",
                background='#00ff88', troughcolor='#2a2a2a', borderwidth=0)

toggle_dark_mode()
root.mainloop()