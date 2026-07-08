import asyncio
import aiohttp
import json
import base64
import random
import re
import os
import string
import time
import sys
import hashlib
import uuid
import socket
import webbrowser
import subprocess
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import shutil

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
PURPLE = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"
CLEAR_LINE = "\033[K"

# Configuration
URL_FILE = ".session_url"
MAC_FILE = ".previous_mac"
TELEGRAM_ACC = "@aiden2410"
TELEGRAM_CHANNEL = "https://t.me/aiden_24"

KEY_HEX = "000102030405060708090a0b0c0d0e0f"
key = bytes.fromhex(KEY_HEX)

# Global state
CURRENT_SESSION_URL = None
KEEP_ALIVE_TASK = None

def decrypt_with_iv(iv_hex: str, encrypted_b64: str) -> str:
    try:
        iv = bytes.fromhex(iv_hex)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted_padded = cipher.decrypt(encrypted_bytes)
        pad_len = decrypted_padded[-1]
        return decrypted_padded[:-pad_len].decode('utf-8')
    except Exception as e:
        return None

def resolve_url_from_token(token: str) -> str:
    if token.startswith("token"):
        token = token[5:]
    else:
        return None
    
    if len(token) <= 42:
        return None
    
    token = token[10:]
    iv_hex = token[:32]
    encrypted_b64 = token[32:]
    
    return decrypt_with_iv(iv_hex, encrypted_b64)

def get_auto_mac():
    try:
        mac = hex(uuid.getnode())[2:].zfill(12)
        return ":".join(mac[i:i+2] for i in range(0, 12, 2))
    except:
        return "1c:8b:ef:99:12:65"

def modify_url_parameter(url: str, param: str, value: str) -> str:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs[param] = [value]
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params,
                       urlencode(qs, doseq=True), parsed.fragment))

def get_center(text):
    terminal_width = shutil.get_terminal_size().columns
    lines = text.split('\n')
    centered_lines = []
    for line in lines:
        clean_line = re.sub(r'\033\[[0-9;]*m', '', line)
        padding = (terminal_width - len(clean_line)) // 2
        centered_lines.append(" " * max(0, padding) + line)
    return "\n".join(centered_lines)

def print_banner(status=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    terminal_width = shutil.get_terminal_size().columns
    
    banner_art = f"""
{GREEN}{BOLD}
   _____   _  __ __     __   ____   __     __
  / ____| | |/ / \ \   / /  |  _ \  \ \   / /
 | (___   | ' /   \ \_/ /   | |_) |  \ \_/ / 
  \___ \  |  <     \   /    |  _ <    \   /  
  ____) | | . \     | |     | |_) |    | |   
 |_____/  |_|\_\    |_|     |____/     |_|   
{RESET}"""
    sub_text = f"\n{YELLOW}[ Voucher Code Bypass + Battery Saver ]{RESET}"
    welcome_text = f"\n{GREEN}Welcome to Voucher Bypass System!{RESET}"
    
    print(get_center(banner_art))
    print(get_center(sub_text))
    print(get_center(welcome_text))
    print(f"{YELLOW}{'-' * terminal_width}{RESET}")
    
    if status:
        print(f"{YELLOW}[*] Status      : {CYAN}{status}{RESET}")
        print(f"{YELLOW}{'-' * terminal_width}{RESET}")

async def keep_alive_ping(url):
    """
    Optimized background task to keep the session alive.
    - Uses a longer interval to save battery and reduce heat.
    - Uses HEAD request instead of GET to minimize data transfer.
    """
    # Use a single session to reuse connection (TCP Keep-Alive)
    connector = aiohttp.TCPConnector(limit=1, keepalive_timeout=60)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            try:
                # HEAD is lighter than GET, uses less CPU and data
                async with session.head(url, timeout=5) as response:
                    pass
            except Exception:
                # Fallback to GET if HEAD is not supported
                try:
                    async with session.get(url, timeout=5) as response:
                        pass
                except:
                    pass
            
            # Increased interval to 120 seconds (2 mins) to save battery
            # Most Wi-Fi sessions stay active for at least 5-10 mins of inactivity
            await asyncio.sleep(120)

async def main():
    global CURRENT_SESSION_URL, KEEP_ALIVE_TASK
    
    # Load persistent Session URL if it exists
    if CURRENT_SESSION_URL is None:
        if os.path.exists(URL_FILE):
            with open(URL_FILE, "r") as f:
                CURRENT_SESSION_URL = f.read().strip()

    # Main Menu
    print_banner()
    if CURRENT_SESSION_URL:
        print(f"{YELLOW}[*] Configuration loaded.{RESET}")
    else:
        print(f"{YELLOW}[*] Configuration: {RED}Not Set{RESET}")
    
    if KEEP_ALIVE_TASK and not KEEP_ALIVE_TASK.done():
        print(f"{GREEN}[*] Battery Saver: {BOLD}ON (Keep-Alive Active){RESET}")
    
    terminal_width = shutil.get_terminal_size().columns
    print(f"{YELLOW}{'-' * terminal_width}{RESET}")
    print(f"{GREEN}[1] Setup Configuration{RESET}")
    print(f"{YELLOW}[2] Browser Injection (Battery Optimized Mode){RESET}")
    print(f"{RED}[3] Exit{RESET}")
    print(f"{YELLOW}{'-' * terminal_width}{RESET}")
    
    main_choice = await asyncio.get_event_loop().run_in_executor(None, lambda: input(f"{CYAN}{BOLD}Select Option: {RESET}").strip())

    if main_choice == "1":
        print_banner(status="Setup Configuration")
        print(f"{YELLOW}[?] {CYAN}Enter your Secret Code:{RESET}")
        token = await asyncio.get_event_loop().run_in_executor(None, lambda: input(f"    {CYAN}> {RESET}").strip())
        if not token:
            print(f"{RED}❌ Token cannot be empty!{RESET}")
            await asyncio.sleep(1)
            return await main()
        
        resolved_url = resolve_url_from_token(token)
        
        if resolved_url:
            CURRENT_SESSION_URL = resolved_url
            with open(URL_FILE, "w") as f:
                f.write(CURRENT_SESSION_URL)
            print(f"\n{GREEN}[ ✔ ] Configuration saved!{RESET}")
            await asyncio.sleep(1)
        else:
            print(f"{RED}❌ Invalid Token or Decryption Failed!{RESET}")
            await asyncio.sleep(1)
        return await main()

    elif main_choice == "2":
        print_banner(status="Browser Injection Mode")
        if not CURRENT_SESSION_URL:
            print(f"{RED}❌ Configuration not loaded. Please use Option 1 first.{RESET}")
            await asyncio.sleep(2)
            return await main()

        print(f"{YELLOW}[*] Configuration loaded.{RESET}")
        print(f"{YELLOW}{'-' * terminal_width}{RESET}")

        # Handle Previous MAC
        prev_mac = None
        if os.path.exists(MAC_FILE):
            with open(MAC_FILE, "r") as f:
                prev_mac = f.read().strip()
        
        if prev_mac:
            print(f"{YELLOW}[*] Previous MAC: {CYAN}[ HIDDEN ]{RESET}")
            print(f"{YELLOW}{'-' * terminal_width}{RESET}")

        print(f"{CYAN}[?] Enter MAC Address:{RESET}")
        print(f"    {WHITE}Format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX{RESET}")
        if prev_mac:
            print(f"    {WHITE}(Press Enter to use previous MAC){RESET}")
        
        manual_mac = await asyncio.get_event_loop().run_in_executor(None, lambda: input(f"    {CYAN}> {RESET}").strip())

        mac_to_use = manual_mac if manual_mac else prev_mac
        
        if not mac_to_use:
            # If no previous MAC, use auto-detected
            mac_to_use = get_auto_mac()

        # Save current MAC as previous for next time
        with open(MAC_FILE, "w") as f:
            f.write(mac_to_use)

        print(f"\n{GREEN}[ ✔ ] MAC: {CYAN}{mac_to_use}{GREEN} saved!{RESET}")
        
        print(f"\n{GREEN}[ + ] Preparing battery-optimized injection...{RESET}")
        await asyncio.sleep(0.5)
        print(f"{YELLOW}[ * ] Opening in external browser...{RESET}")
        await asyncio.sleep(0.5)
        print(f"{GREEN}[ ✔ ] Browser launched!{RESET}")
        await asyncio.sleep(0.5)

        processed_url = modify_url_parameter(CURRENT_SESSION_URL, 'mac', mac_to_use)

        # Start Optimized Keep-Alive background task
        if KEEP_ALIVE_TASK:
            KEEP_ALIVE_TASK.cancel()
        KEEP_ALIVE_TASK = asyncio.create_task(keep_alive_ping(processed_url))
        
        print(f"{GREEN}[ ✔ ] Battery Saver active (Ping every 2 mins).{RESET}")
        print(f"{YELLOW}[ ! ] Keeping terminal open will maintain connection.{RESET}")

        try:
            # For Termux
            subprocess.run(["termux-open-url", processed_url], check=True, timeout=5)
        except:
            try:
                # For Standard Browsers
                webbrowser.open(processed_url)
            except:
                print(f"\n{YELLOW}အောက်ပါလင့်ခ်ကို ကိုယ်တိုင်ဖွင့်ပါ:\n{processed_url}{RESET}")
        
        await asyncio.get_event_loop().run_in_executor(None, lambda: input(f"\n{CYAN}Press Enter to return to menu...{RESET}"))
        return await main()

    elif main_choice == "3":
        if KEEP_ALIVE_TASK:
            KEEP_ALIVE_TASK.cancel()
        print(f"\n{YELLOW}Goodbye!{RESET}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if KEEP_ALIVE_TASK:
            KEEP_ALIVE_TASK.cancel()
        print(f"\n{RED}⚠ Stopped by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")
