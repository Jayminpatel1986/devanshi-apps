# -*- coding: utf-8 -*-
# =======================================================================================================================
# 👑 દેવાંશી મનસ્વી સોફ્ટવેર (DEVANSHI MANSVI MASTER ERP) - MAIN DESKTOP APP LAUNCHER & ZERO-TOUCH OTA ENGINE (app.py)
# માલિક અને આર્કિટેક્ટ: જયમીનભાઈ પટેલ (મો. 9725721215 | માસ્ટર PIN: 1986)
# ૧. મલ્ટી-વિન્ડો ડેસ્કટોપ એપ્લિકેશન મોડ: દુકાનદાર ૧ વાર કે ૪-૫ વાર ડબલ-ક્લિક કરે, કોઈ પોર્ટ એરર કે ટાસ્ક-કિલ વગર
#    દરેક ક્લિક પર તરત જ નવી સ્વતંત્ર ડેસ્કટોપ એપ્લિકેશન વિન્ડો ખુલશે (એકમાં ખરીદી ચાલુ રાખી બીજીમાં બિલ/પ્રિન્ટ કાઢી શકાશે)!
# ૨. ઝીરો-ટચ OTA ડાયનામિક હોટ-લોડર (DiskFirstOtaMetaFinder): દુકાનદારને ક્યારેય ફરીથી .exe ફાઇલ આપવી નહીં પડે!
#    જયમીનભાઈ એડમિન પેનલ (મોબાઈલ કે લેપટોપ) માંથી જેવું અપડેટ પુશ કરશે, .exe ફાઇલ અંદરના જૂના કોડને બદલે
#    OTA_Live_Updates ફોલ્ડરમાંથી નવો કોડ આપોઆપ લોડ અને હોટ-રીલોડ કરી લેશે!
# =======================================================================================================================
import os
import sys
import socket
import threading
import time
import webbrowser
import urllib.request
import subprocess
import importlib.abc
import importlib.util
import uvicorn
import io

class SafeWriter(io.StringIO):
    def write(self, s):
        return len(s)
    def flush(self):
        pass
    def isatty(self):
        return False

if sys.stdout is None:
    sys.stdout = SafeWriter()
if sys.stderr is None:
    sys.stderr = SafeWriter()

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if os.name == "nt":
    _app_d = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    OTA_DIR_HIDDEN = os.path.join(_app_d, "Devanshi_Mansvi_ERP", ".sys_ota_core")
else:
    OTA_DIR_HIDDEN = os.path.join("/tmp", "devanshi_mobile", "OTA_Live_Updates")
OTA_DIR_MAIN = os.path.join(BASE_DIR, "OTA_Live_Updates")
OTA_DIR_TMP = os.path.join("/tmp", "devanshi_mobile", "OTA_Live_Updates")
try:
    os.makedirs(OTA_DIR_HIDDEN, exist_ok=True)
except Exception:
    pass

CURRENT_BUILD_VERSION = "2026.11.12.001"

ERP_DYNAMIC_MODULES = {
    "part1_core",
    "part2_views",
    "part2_b_counters",
    "part2_c_counters_extra",
    "part2_d_sheets",
    "part3_routes",
    "part4_ai_import",
    "part5_saas_control",
    "part6_police_vault",
    "part7_eod_whatsapp",
    "part8_pwa_offline_sync",
    "part9_realtime_print_push",
    "part10_accessories_part2",
}

def _validate_and_clean_ota_cache():
    """જો .sys_ota_core ફોલ્ડરમાં જૂના વર્ઝનની કે અધૂરી .py ફાઇલો પડી હોય (જેમાં નવા ફંક્શન ન હોય), તો તેને આપોઆપ સાફ કરે છે જેથી .exe ક્યારેય ImportError થી ક્રેશ ન થાય!"""
    for ota_d in (OTA_DIR_HIDDEN, OTA_DIR_MAIN, OTA_DIR_TMP):
        try:
            p1_cand = os.path.join(ota_d, "part1_core.py")
            if os.path.isfile(p1_cand):
                with open(p1_cand, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                required_markers = [
                    "def is_jaymin_permanent_master_laptop",
                    "def register_jaymin_permanent_master_laptop",
                    "def api_qr_svg_endpoint",
                ]
                if not all(m in txt for m in required_markers):
                    for fn in os.listdir(ota_d):
                        if fn.endswith(".py") or fn.endswith(".json"):
                            try:
                                os.remove(os.path.join(ota_d, fn))
                            except Exception:
                                pass
        except Exception:
            pass

_validate_and_clean_ota_cache()

class DiskFirstOtaMetaFinder(importlib.abc.MetaPathFinder):
    """
    PyInstaller .exe ની અંદર રહેલા FrozenImporter કરતાં પહેલાં ડિસ્ક પરના
    OTA_Live_Updates/ અથવા BASE_DIR ના તાજા અને માન્ય .py મોડ્યુલ્સ લોડ કરે છે!
    """
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in ERP_DYNAMIC_MODULES:
            return None
        candidates = []
        for d in (OTA_DIR_HIDDEN, OTA_DIR_MAIN, OTA_DIR_TMP, BASE_DIR):
            cand = os.path.join(d, f"{fullname}.py")
            if os.path.exists(cand) and os.path.isfile(cand) and os.path.getsize(cand) > 100:
                try:
                    with open(cand, "r", encoding="utf-8") as cf:
                        src = cf.read()
                    compile(src, cand, "exec")
                    if fullname == "part1_core" and "def is_jaymin_permanent_master_laptop" not in src:
                        continue
                    candidates.append((os.path.getmtime(cand), cand))
                except Exception:
                    continue
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_py_path = candidates[0][1]
        return importlib.util.spec_from_file_location(fullname, best_py_path)

# Install DiskFirstOtaMetaFinder at index 0 BEFORE importing part1..part10!
if not any(type(f).__name__ == "DiskFirstOtaMetaFinder" for f in sys.meta_path):
    sys.meta_path.insert(0, DiskFirstOtaMetaFinder())

def open_standalone_desktop_window(url: str):
    """
    બ્રાઉઝરની ટેબ કે URL બાર વગર સીધી જ સ્વતંત્ર ડેસ્કટોપ એપ્લિકેશન વિન્ડો (--app=...) ખોલે છે.
    દુકાનદાર જેટલી વાર ડબલ-ક્લિક કરશે એટલી અલગ-અલગ વિન્ડો સાઈડ-બાય-સાઈડ ખુલશે!
    """
    app_opened = False
    if os.name == "nt":
        for browser_exe in [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        ]:
            if os.path.exists(browser_exe):
                try:
                    cflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                    subprocess.Popen([browser_exe, f"--app={url}", "--new-window"], creationflags=cflags)
                    app_opened = True
                    break
                except Exception:
                    pass
    if not app_opened:
        try:
            webbrowser.open_new(url)
        except Exception:
            pass

CURRENT_BUILD_VERSION = "2026.11.12.001"

def kill_old_server_on_port(port: int):
    """જો જૂની .exe પોર્ટ પર ચાલતી હોય તો તેને આપમેળે બંધ (Kill) કરે છે જેથી નવું સોફ્ટવેર તરત જ ચાલુ થઈ જાય!"""
    if os.name == "nt":
        try:
            cflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            out = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True, creationflags=cflags).decode("utf-8", errors="ignore")
            my_pid = os.getpid()
            for line in out.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and "LISTENING" in line.upper():
                    pid = int(parts[-1])
                    if pid != my_pid and pid > 0:
                        subprocess.run(f"taskkill /F /PID {pid} /T", shell=True, creationflags=cflags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        time.sleep(0.6)

def find_running_devanshi_server():
    """જો નવું જ વર્ઝન પહેલેથી ચાલુ હોય તો નવી મલ્ટી-વિન્ડો ખોલે છે, પણ જો જૂની કે ઝોમ્બી .exe ચાલતી હોય તો તેને બંધ કરી નવું વર્ઝન શરૂ કરે છે!"""
    import json as _json
    for p in range(8000, 8015):
        port_open = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.15)
                if s.connect_ex(("127.0.0.1", p)) == 0:
                    port_open = True
        except Exception:
            pass
        if port_open:
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{p}/api/ota-status", headers={"User-Agent": "DevanshiLauncher"})
                with urllib.request.urlopen(req, timeout=0.6) as resp:
                    if resp.status == 200:
                        raw = resp.read().decode("utf-8", errors="ignore")
                        data = _json.loads(raw) if raw else {}
                        if data.get("build_version") == CURRENT_BUILD_VERSION:
                            return p
                        else:
                            kill_old_server_on_port(p)
                    else:
                        kill_old_server_on_port(p)
            except Exception:
                kill_old_server_on_port(p)
    return None

# જો સર્વર પહેલેથી ચાલુ હોય અને કોઈ .exe પર બીજી/ત્રીજી/ચોથી વાર ડબલ-ક્લિક કરે -> તરત જ નવી વિન્ડો ખોલો!


if __name__ == "__main__":
    existing_port = find_running_devanshi_server()
    if existing_port is not None:
        open_standalone_desktop_window(f"http://127.0.0.1:{existing_port}/?multi_win={int(time.time())}")
        sys.exit(0)

from part1_core import (
    app, init_db, STORE_CFG, save_store_config,
    check_and_pull_ota_updates,
    start_ota_background_daemons,
    start_auto_cloud_tunnel_daemon, ensure_windows_firewall_unblocked
)

# સ્ટાર્ટઅપ વખતે જ ક્લાઉડ પરથી કોઈ નવું OTA અપડેટ હોય તો બેકગ્રાઉન્ડ થ્રેડમાં ચેક કરો જેથી સર્વર ૧ સેકન્ડમાં તુરંત પોર્ટ 8000 પર લાઈવ થઈ જાય!
try:
    if "fastapi.testclient" not in sys.modules:
        threading.Thread(target=check_and_pull_ota_updates, args=(True,), daemon=True).start()
except Exception:
    pass

import part2_views
import part2_b_counters
import part2_c_counters_extra
import part2_d_sheets
import part3_routes
import part4_ai_import
import part5_saas_control
import part6_police_vault
import part7_eod_whatsapp
import part8_pwa_offline_sync
import part9_realtime_print_push
import part10_accessories_part2

init_db()
start_ota_background_daemons()

from part1_core import get_local_lan_ip

def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        if s.connect_ex(("127.0.0.1", port)) == 0:
            return False
    for host in ("127.0.0.1", "0.0.0.0"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
            except OSError:
                return False
    return True

def find_available_port(start_port=8000, max_port=8100):
    for port in range(start_port, max_port + 1):
        if is_port_free(port):
            return port
    return start_port

def auto_open_first_window(port):
    url = f"http://127.0.0.1:{port}/login"
    for _ in range(50):
        time.sleep(0.2)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                break
    open_standalone_desktop_window(url)

if __name__ == "__main__":
    env_port = os.environ.get("PORT")
    if env_port:
        active_port = int(env_port)
    else:
        active_port = find_available_port(8000, 8100)
    STORE_CFG["active_port"] = active_port
    save_store_config(STORE_CFG)
    if os.name == "nt":
        ensure_windows_firewall_unblocked(active_port)
    start_auto_cloud_tunnel_daemon(active_port)
    lan_ip = get_local_lan_ip()

    print("=" * 82)
    print(f"🚀 દેવાંશી મનસ્વી સોફ્ટવેર (Devanshi Mansvi ERP) પોર્ટ {active_port} પર ચાલુ થઈ ગયું છે!")
    print(f"🗔 મલ્ટી-વિન્ડો મોડ સક્રિય: આઇકોન પર ફરીથી ડબલ-ક્લિક કરતાં ૨જી, ૩જી, ૪થી વિન્ડો ખુલશે!")
    print(f"☁️ ઝીરો-ટચ OTA એન્જિન સક્રિય: ફરીથી .exe આપ્યા વગર ઓટોમેટિક લાઈવ અપડેટ!")
    print(f"💻 કમ્પ્યુટર લિંક : http://127.0.0.1:{active_port}/login")
    print(f"📱 મોબાઈલ લિંક   : http://{lan_ip}:{active_port}/login")
    print("👑 સુપર એડમિન   : જયમીનભાઈ પટેલ (9725721215)")
    print("=" * 82)

    if not env_port and os.name == "nt":
        threading.Thread(target=auto_open_first_window, args=(active_port,), daemon=True).start()
    log_cfg = None if (sys.stdout is None or isinstance(sys.stdout, SafeWriter)) else uvicorn.config.LOGGING_CONFIG
    uvicorn.run(app, host="0.0.0.0", port=active_port, log_config=log_cfg)

