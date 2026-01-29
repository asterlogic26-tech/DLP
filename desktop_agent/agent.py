import time
import re
import os
import sys
import ctypes
import pyperclip
from plyer import notification
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
                    notification.notify(
                        title='CyberGuard Security',
                        message=f'Blocked unauthorized USB device: {drive_letter}',
                        app_name='CyberGuard',
                        timeout=5
                    )
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
                            notification.notify(
                                title='CyberGuard Security',
                                message=f'Blocked unauthorized installation: {p_name}',
                                app_name='CyberGuard',
                                timeout=5
                            )
                            log_event("INSTALL_BLOCKED", f"Blocked process: {p_name}", "KILLED")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            pass
        time.sleep(2)

def login_prompt():
    """Ask user for email and get token from backend"""
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    # Make sure it's on top
    root.attributes("-topmost", True)
    
    email = simpledialog.askstring("CyberGuard Login", "Please enter your registered email address to activate CyberGuard:", parent=root)
    
    if email:
        try:
            response = requests.post(f"{API_URL}/auth/simple", json={"email": email})
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    with open("token.txt", "w") as f:
                        f.write(token)
                    messagebox.showinfo("Success", "CyberGuard activated successfully!")
                    return token
            else:
                messagebox.showerror("Error", "Login failed. Please check your email.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")
            
    root.destroy()
    return None

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
                    notification.notify(
                        title='CyberGuard File Alert',
                        message=f'Sensitive {p_type} found in {os.path.basename(filepath)}',
                        app_name='CyberGuard',
                        timeout=5
                    )
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

def monitor_clipboard():
    if not is_admin():
        print("\n[!] ERROR: This agent must be run as ADMINISTRATOR to block USB/Installs.")
        print("    Right-click -> Run as Administrator")
        input("Press Enter to exit...")
        return

    print("🛡️  CyberGuard Desktop Agent Running (ADMIN MODE)...")
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
                        notification.notify(
                            title='CyberGuard DLP Alert',
                            message=f'Blocked copy of sensitive {p_type} data!',
                            app_name='CyberGuard',
                            timeout=5
                        )
                        log_event("CLIPBOARD_LEAK", f"User tried to copy {p_type}", "BLOCKED")
                        break
            
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Agent Stopped.")
    observer.join()

if __name__ == "__main__":
    monitor_clipboard()