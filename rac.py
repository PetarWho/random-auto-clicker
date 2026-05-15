import threading
import time
import os
import sys
import random
import json
import tkinter as tk
import customtkinter as ctk
from pynput import keyboard, mouse

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".rac_config.json")

class AutoClicker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Random Auto Clicker")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        
        self.start_time = 0
        self.clicking = False
        self.capturing_key = False
        
        icon_path = ''
        if hasattr(sys, '_MEIPASS'):
            try:
                self.root.iconbitmap(os.path.join(sys._MEIPASS, 'rac.ico'))
            except Exception:
                pass
        elif os.path.exists('rac.ico'):
             try:
                self.root.iconbitmap('rac.ico')
             except Exception:
                pass

        self.load_config()

        # Create variables
        self.delay_from = tk.StringVar(value="0.5")
        self.delay_to = tk.StringVar(value="1.0")
        self.mouse_button = tk.StringVar(value="left")
        self.toggle_key_str = tk.StringVar(value=self.get_key_display(self.toggle_key))

        # Create widgets
        ctk.CTkLabel(self.root, text="Random Auto Clicker", font=(None, 24, "bold")).pack(pady=20)

        delay_frame = ctk.CTkFrame(self.root)
        delay_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(delay_frame, text="Click Delay (seconds):", font=(None, 14, "bold")).pack(pady=(10, 0))
        
        delay_input_frame = ctk.CTkFrame(delay_frame, fg_color="transparent")
        delay_input_frame.pack(pady=10)
        
        ctk.CTkLabel(delay_input_frame, text="From:", font=(None, 12)).pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(delay_input_frame, textvariable=self.delay_from, width=70).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(delay_input_frame, text="To:", font=(None, 12)).pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(delay_input_frame, textvariable=self.delay_to, width=70).pack(side=tk.LEFT, padx=5)

        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(button_frame, text="Mouse Button:", font=(None, 14, "bold")).pack(pady=5)
        
        radio_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        radio_frame.pack(pady=5)
        ctk.CTkRadioButton(radio_frame, text="Left Click", variable=self.mouse_button, value="left").pack(side=tk.LEFT, padx=20)
        ctk.CTkRadioButton(radio_frame, text="Right Click", variable=self.mouse_button, value="right").pack(side=tk.LEFT, padx=20)

        key_frame = ctk.CTkFrame(self.root)
        key_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(key_frame, text="Toggle Hotkey:", font=(None, 14, "bold")).pack(side=tk.LEFT, padx=15)
        self.key_button = ctk.CTkButton(key_frame, textvariable=self.toggle_key_str, width=120, 
                                        fg_color="#3b3b3b", hover_color="#4b4b4b",
                                        command=self.start_capturing)
        self.key_button.pack(side=tk.RIGHT, padx=15, pady=10)

        self.status_label = ctk.CTkLabel(self.root, text=f"Press {self.get_key_display(self.toggle_key)} to start/stop", 
                                         font=(None, 15, "bold"))
        self.status_label.pack(pady=(20, 0))
        
        self.timer_label = ctk.CTkLabel(self.root, text="Ready", font=(None, 13, "italic"), text_color="gray")
        self.timer_label.pack(pady=5)

        # Create listener for toggle key
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.auto_click_thread = None

    def on_closing(self):
        self.clicking = False
        if self.listener:
            self.listener.stop()
        self.root.quit()
        self.root.destroy()
        os._exit(0)

    def load_config(self):
        self.toggle_key = keyboard.Key.f10
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    key_val = config.get('toggle_key')
                    if key_val:
                        if key_val.startswith('Key.'):
                            self.toggle_key = getattr(keyboard.Key, key_val.split('.')[1])
                        else:
                            self.toggle_key = keyboard.KeyCode.from_char(key_val)
            except Exception:
                pass

    def save_config(self):
        try:
            key_val = str(self.toggle_key)
            if hasattr(self.toggle_key, 'name'):
                key_val = f"Key.{self.toggle_key.name}"
            else:
                key_val = self.toggle_key.char
                
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'toggle_key': key_val}, f)
        except Exception:
            pass

    def get_key_display(self, key):
        if hasattr(key, 'name'):
            return key.name.upper()
        return str(key).replace("'", "").upper()

    def start_capturing(self):
        self.capturing_key = True
        self.toggle_key_str.set("Press a key...")
        self.key_button.configure(state="disabled")

    def run(self):
        self.root.mainloop()

    def on_press(self, key):
        if self.capturing_key:
            self.root.after(0, lambda: self.finish_capturing(key))
            return

        if key == self.toggle_key:
            self.root.after(0, self.toggle_clicking)

    def toggle_clicking(self):
        if not self.clicking:
            self.start_clicking()
        else:
            self.stop_clicking()

    def finish_capturing(self, key):
        self.toggle_key = key
        self.capturing_key = False
        self.toggle_key_str.set(self.get_key_display(self.toggle_key))
        self.status_label.configure(text=f"Press {self.get_key_display(self.toggle_key)} to start/stop")
        self.key_button.configure(state="normal")
        self.save_config()

    def start_clicking(self):
        self.clicking = True
        self.start_time = time.time()
        self.status_label.configure(text="RAC running...", text_color="#57bb8a")
        self.timer_label.configure(text="")
        self.auto_click_thread = threading.Thread(target=self.auto_click)
        self.auto_click_thread.daemon = True
        self.auto_click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        elapsed_time = time.time() - self.start_time
        hours = int(elapsed_time / 3600)
        minutes = int((elapsed_time - hours * 3600) / 60)
        seconds = int(elapsed_time - hours * 3600 - minutes * 60)
        time_str = f"Ran for: {hours:02d}h:{minutes:02d}m:{seconds:02d}s"
        self.timer_label.configure(text=time_str)
        self.status_label.configure(text="RAC stopped.", text_color=None)

    def auto_click(self):
        mouse_ctrl = mouse.Controller()
        while self.clicking:
            try:
                df = float(self.delay_from.get())
                dt = float(self.delay_to.get())
                if df > dt:
                    df, dt = dt, df
                delay = random.uniform(df, dt)
            except Exception:
                delay = 0.5
            
            # Sleep in small increments to respond faster to stop
            stop_time = time.time() + delay
            while time.time() < stop_time:
                if not self.clicking:
                    return
                time.sleep(0.01)
                
            if not self.clicking:
                break
                
            button = mouse.Button.left if self.mouse_button.get() == "left" else mouse.Button.right
            mouse_ctrl.click(button)

if __name__ == "__main__":
    autoclicker = AutoClicker()
    autoclicker.run()
