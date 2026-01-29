import time
import re
import os
import sys
import ctypes
import pyperclip
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import wmi
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

# Configuration
API_URL = "https://cyberguard-backend-l2yo.onrender.com"
MONITOR_DIRS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop")
]

# ALLOW LISTS
ALLOWED_USB_SERIALS = ["1234567890"] # Example Serial
ALLOWED_INSTALLERS = ["updater.exe", "system_update.exe"]

# DLP Patterns - COMPREHENSIVE LIBRARY
PATTERNS = {
    # Identity Documents (India)
    "PAN_CARD": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
    "AADHAR_CARD": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "PASSPORT": r"\b[A-Z]{1}[0-9]{7}\b",
    "VOTER_ID": r"\b[A-Z]{3}[0-9]{7}\b",
    "DRIVING_LICENSE": r"\b(([A-Z]{2}[0-9]{2})( )|([A-Z]{2}-[0-9]{2}))((19|20)[0-9][0-9])[0-9]{7}\b",

    # Identity Documents (Global)
    "SSN_US": r"\b\d{3}-\d{2}-\d{4}\b",
    
    # Financial Data
    "CREDIT_CARD": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
    "IBAN": r"\b[A-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}\b",
    "GSTIN": r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b",
    "IFSC_CODE": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    "UPI_ID": r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b",
    
    # Contact Info (PII)
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE_INDIA": r"\b(?:\+91|91)?[6-9]\d{9}\b",
    
    # Technical Secrets & Keys
    "AWS_ACCESS_KEY": r"\bAKIA[0-9A-Z]{16}\b",
    "PRIVATE_KEY_HEADER": r"-----BEGIN PRIVATE KEY-----",
    "GOOGLE_API_KEY": r"AIza[0-9A-Za-z-_]{35}",
    "SLACK_TOKEN": r"xox[baprs]-([0-9a-zA-Z]{10,48})",
    
    # Network
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def block_usb_storage():
    """Monitor and unmount unauthorized USB drives"""
    print("   Monitoring USB Ports...")
    c = wmi.WMI()
    watcher = c.Win32_Volume.watch_for("operation")
    
    while True:
        try:
            # Wait for volume event (Mount/Unmount)
            event = watcher()
            if event.ClassName == "Win32_Volume" and event.DriveType == 2: # 2 = Removable
                drive_letter = event.Name
                print(f"[!] New USB Detected: {drive_letter}")
                
                # In a real scenario, we would map Drive Letter -> Device ID -> Serial
                # For this prototype, we will BLOCK ALL unless explicitly whitelisted in code
                
                authorized = False 
                # (Logic to check serial would go here - complex in Python WMI)
                
                if not authorized:
                    print(f"[!!!] BLOCKING UNAUTHORIZED USB: {drive_letter}")
                    os.system(f"mountvol {drive_letter} /D")
                    threading.Thread(
                        target=show_alert,
                        args=('CyberGuard Security', f'Blocked unauthorized USB device: {drive_letter}'),
                        daemon=True
                    ).start()
                    log_event("USB_BLOCKED", f"Unauthorized USB inserted: {drive_letter}", "BLOCKED")
        except Exception as e:
            pass

def block_installations():
    """Kill processes that look like installers"""
    print("   Monitoring Process List (Anti-Install)...")
    suspicious_keywords = ["setup", "install", "msi", "setup.exe", "installer"]
    
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    p_name = proc.info['name'].lower()
                    if any(kw in p_name for kw in suspicious_keywords):
                        if p_name not in ALLOWED_INSTALLERS:
                            print(f"[!!!] BLOCKING INSTALLATION: {p_name}")
                            proc.kill()
                            threading.Thread(
                                target=show_alert,
                                args=('CyberGuard Security', f'Blocked unauthorized installation: {p_name}'),
                                daemon=True
                            ).start()
                            log_event("INSTALL_BLOCKED", f"Blocked process: {p_name}", "KILLED")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            pass
        time.sleep(2)

import webbrowser

from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

def login_prompt():
    """Ask user for email/password and get token from backend"""
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    # Custom Login Dialog
    dialog = tk.Toplevel(root)
    dialog.title("CyberGuard Login")
    dialog.geometry("350x350") # Increased height for Google Button
    dialog.attributes("-topmost", True)
    
    # Variables
    email_var = tk.StringVar()
    password_var = tk.StringVar()
    result = {"token": None}
    
    def on_submit():
        email = email_var.get()
        password = password_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields", parent=dialog)
            return
            
        try:
            response = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
            
            if response.status_code == 200:
                data = response.json()
                is_paid = data.get("is_paid", False)
                token = data.get("access_token")
                
                if not is_paid:
                    messagebox.showwarning("Pro Subscription Required", "Your account is not a Pro subscriber.\nRedirecting to payment page...", parent=dialog)
                    webbrowser.open("https://cyberguard-dashboard.onrender.com/dashboard") # Redirect to payment/dashboard
                    return
                
                if token:
                    with open("token.txt", "w") as f:
                        f.write(token)
                    messagebox.showinfo("Success", "CyberGuard activated successfully!", parent=dialog)
                    result["token"] = token
                    dialog.destroy()
                    root.destroy()
            else:
                try:
                    detail = response.json().get("detail", "Login failed")
                except:
                    detail = "Login failed"
                messagebox.showerror("Error", detail, parent=dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}", parent=dialog)

    def on_google_login():
        # 1. Start Local Server to listen for token
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body style='font-family:sans-serif; text-align:center; padding-top:50px;'><h1>Login Successful!</h1><p>You can close this tab and return to the application.</p><script>window.close();</script></body></html>")
                
                # Extract token from query params: /?token=...
                if 'token=' in self.path:
                    token = self.path.split('token=')[1].split('&')[0]
                    result["token"] = token
                
                # Stop server
                threading.Thread(target=httpd.shutdown).start()

        # Find free port
        port = 5678
        server_address = ('localhost', port)
        httpd = HTTPServer(server_address, CallbackHandler)
        
        # Run server in a separate thread to avoid blocking UI
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # 2. Open Browser to Backend Google Auth Simulation
        webbrowser.open(f"{API_URL}/auth/google_login_simulation?callback_port={port}")
        
        # 3. Poll for result without blocking
        messagebox.showinfo("Google Login", "A browser window has opened.\nPlease complete the login there.", parent=dialog)
        
        def check_google_token():
            if result["token"]:
                with open("token.txt", "w") as f:
                    f.write(result["token"])
                messagebox.showinfo("Success", "CyberGuard activated successfully with Google!", parent=dialog)
                dialog.destroy()
                root.destroy()
            else:
                # Check again in 1 second
                dialog.after(1000, check_google_token)
        
        check_google_token()

    # UI Elements
    tk.Label(dialog, text="CyberGuard Professional", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Label(dialog, text="Sign in with your Pro account").pack(pady=5)
    
    tk.Label(dialog, text="Email:").pack(anchor="w", padx=20)
    tk.Entry(dialog, textvariable=email_var, width=30).pack(padx=20)
    
    tk.Label(dialog, text="Password:").pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(dialog, textvariable=password_var, show="*", width=30).pack(padx=20)
    
    tk.Button(dialog, text="Sign In", command=on_submit, bg="#007bff", fg="white", width=20).pack(pady=15)
    
    # Divider
    tk.Frame(dialog, height=1, bg="grey", width=200).pack(pady=5)
    
    # Google Button
    tk.Button(dialog, text="Sign in with Google", command=on_google_login, bg="white", fg="black", width=20).pack(pady=10)
    
    # Wait for dialog
    root.wait_window(dialog)
    return result["token"]

def get_token():
    """Load token from a local file or prompt login"""
    try:
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                return f.read().strip()
        else:
            # First run login
            return login_prompt()
    except:
        pass
    return None

def log_event(event_type, description, action):
    """Log event to the cloud backend"""
    print(f"[*] LOGGING: {event_type} - {description} - {action}")
    token = get_token()
    
    if not token:
        print("   [!] Warning: No 'token.txt' found. Log not sent to dashboard.")
        return

    try:
        payload = {
            "event_type": event_type,
            "description": description,
            "url": "Desktop Device",
            "action_taken": action
        }
        headers = {"Authorization": f"Bearer {token}"}
        requests.post(f"{API_URL}/events", json=payload, headers=headers)
        print("   [+] Log sent to dashboard!")
    except Exception as e:
        print(f"[!] Failed to log: {e}")

class DLPFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        self.scan_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory: return
        self.scan_file(event.src_path)

    def scan_file(self, filepath):
        """Read file and check for sensitive patterns"""
        # Skip large files or non-text files for prototype
        if not filepath.endswith(('.txt', '.csv', '.json', '.md', '.log')):
            return
            
        try:
            # Wait briefly for file write to complete
            time.sleep(0.5) 
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for p_type, pattern in PATTERNS.items():
                if re.search(pattern, content):
                    print(f"\n[!] ALERT: Found {p_type} in file: {filepath}")
                    threading.Thread(
                        target=show_alert,
                        args=('CyberGuard File Alert', f'Sensitive {p_type} found in {os.path.basename(filepath)}'),
                        daemon=True
                    ).start()
                    log_event("FILE_SCAN", f"Sensitive {p_type} found in {filepath}", "FLAGGED")
                    break
        except Exception as e:
            pass

def start_file_monitoring():
    observer = Observer()
    event_handler = DLPFileHandler()
    
    print("   Monitoring Folders for Sensitive Files:")
    for path in MONITOR_DIRS:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=False)
            print(f"    - {path}")
            
    observer.start()
    return observer

def show_alert(title, message):
    """Show a Windows message box in a separate thread to avoid blocking."""
    try:
        # 0x30 = MB_ICONWARNING, 0x40000 = MB_TOPMOST
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x30 | 0x40000)
    except:
        pass

def monitor_clipboard():
    if not is_admin():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Administrator Required", "CyberGuard Agent must be run as Administrator to function correctly.\n\nPlease right-click the app and select 'Run as Administrator'.")
        root.destroy()
        return

    # Ensure login happens on Main Thread before any monitoring starts
    print(">>> Checking Authentication...")
    if not get_token():
        print("   [!] Login required but cancelled/failed. Exiting.")
        return

    # In windowed mode (PyInstaller --noconsole), print() might fail or go nowhere.
    # We redirect stdout/stderr to null to prevent "Bad file descriptor" errors if they occur.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    print(">>> CyberGuard Desktop Agent Running (ADMIN MODE)...")
    print("   Monitoring Clipboard, Files, USB, and Processes...")
    
    # Start File Monitor
    observer = start_file_monitoring()
    
    # Start USB Monitor Thread
    threading.Thread(target=block_usb_storage, daemon=True).start()
    
    # Start Installation Monitor Thread
    threading.Thread(target=block_installations, daemon=True).start()
    
    print("   Press Ctrl+C to stop.")

    last_value = ""

    try:
        while True:
            # Clipboard Check
            try:
                current_value = pyperclip.paste()
            except:
                current_value = ""

            if current_value != last_value:
                last_value = current_value
                for p_type, pattern in PATTERNS.items():
                    if re.search(pattern, current_value):
                        print(f"\n[!] ALERT: Detected {p_type} in clipboard!")
                        pyperclip.copy("") 
                        last_value = "" 
                        threading.Thread(
                            target=show_alert, 
                            args=('CyberGuard DLP Alert', f'Blocked copy of sensitive {p_type} data!'), 
                            daemon=True
                        ).start()
                        log_event("CLIPBOARD_LEAK", f"User tried to copy {p_type}", "BLOCKED")
                        break
            
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[!] Agent Stopped.")
    observer.join()

if __name__ == "__main__":
    monitor_clipboard()