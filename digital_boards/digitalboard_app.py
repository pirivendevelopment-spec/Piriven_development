import sys
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import requests
import os
import datetime
import subprocess
import psutil 
import threading 
import pygetwindow as gw  
import json  
import cv2                 # 💡 සැබෑ පින්තූරයෙන් සිසුන් ගණන සෙවීමට
import winreg              # 💡 Windows Startup එකට ඇප් එක එකතු කිරීමට

# ⚠️ Firebase API URL
FIREBASE_URL = "https://pirivensmartboardmonitoring-default-rtdb.asia-southeast1.firebasedatabase.app/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPDATA_DIR = os.path.join(os.environ.get('APPDATA', os.environ.get('USERPROFILE', os.path.expanduser('~'))), 'PirivenSystem')
if not os.path.exists(APPDATA_DIR): os.makedirs(APPDATA_DIR)

CENSUS_FILE = os.path.join(APPDATA_DIR, "census_config.txt")
LAST_MSG_FILE = os.path.join(APPDATA_DIR, "last_msg_id.txt")
OFFLINE_LOG_FILE = os.path.join(APPDATA_DIR, "offline_logs.json")  

if getattr(sys, 'frozen', False): BASE_DIR = sys._MEIPASS
else: BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATE_LOGO_PATH = os.path.join(BASE_DIR, "statelogo.png")
PIRIVEN_LOGO_PATH = os.path.join(BASE_DIR, "pirivenlogo.png")

# OpenCV නිල Haar Cascade AI Face Model එක පද්ධතියට ලෝඩ් කිරීම
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

last_heartbeat_time = datetime.datetime.now()

# 💡 Windows Startup එකට ඇප් එක එකතු කරන ස්මාර්ට් එන්ජිම
def add_to_windows_startup():
    try:
        if getattr(sys, 'frozen', False):
            app_path = sys.executable 
        else:
            app_path = os.path.abspath(__file__)
            app_path = f'"{sys.executable}" "{app_path}"'
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as reg_key:
            winreg.SetValueEx(reg_key, "PirivenSmartBoardSystem", 0, winreg.REG_SZ, app_path)
        print("✅ Startup Registered!")
    except Exception as e:
        print(f"⚠️ Startup Error: {e}")

def detect_device_type():
    try:
        if psutil.sensors_battery() is not None: return "Laptop"
        output = subprocess.check_output("wmic computersystem get model", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().lower()
        if "smart" in output or "board" in output or "touch" in output: return "Smart Board"
    except: pass
    return "Desktop PC"

def get_board_location():
    try:
        res = requests.get('https://ipapi.co/json/', timeout=3)
        if res.status_code == 200:
            d = res.json()
            return {"lat": d.get("latitude", 7.8731), "lon": d.get("longitude", 80.7718), "city": d.get("city", "Unknown City")}
    except: pass
    return {"lat": 7.8731, "lon": 80.7718, "city": "Unknown City"}

def get_machine_serial():
    try:
        out = subprocess.check_output("wmic bios get serialnumber", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().strip().split('\n')
        if len(out) >= 2 and out[1].strip() and not any(x in out[1].lower() for x in ["default", "filled", "string", "none", "unknown"]): return out[1].strip()
        out_mb = subprocess.check_output("wmic baseboard get serialnumber", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().strip().split('\n')
        if len(out_mb) >= 2 and out_mb[1].strip() and not any(x in out_mb[1].lower() for x in ["default", "filled", "string", "none", "unknown"]): return out_mb[1].strip()
    except: pass
    return "SMART-BOARD-PC"

def get_advanced_device_specs():
    try:
        brand = subprocess.check_output("wmic computersystem get manufacturer", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().strip().split('\n')[1].strip()
        model = subprocess.check_output("wmic computersystem get model", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().strip().split('\n')[1].strip()
        processor = subprocess.check_output("wmic cpu get name", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().strip().split('\n')[1].strip()
        ram = f"{round(psutil.virtual_memory().total / (1024 ** 3))} GB"
        os_v = subprocess.check_output("wmic os get Caption", shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode().strip().split('\n')[1].strip()
        return {"brand": brand, "model": model, "chipset": "Intel/AMD", "processor": processor, "frequency": "Active", "cache": "N/A", "ram": ram, "harddisk": "512 GB", "os": os_v}
    except: return {"brand":"N/A","model":"N/A","chipset":"N/A","processor":"N/A","frequency":"N/A","cache":"N/A","ram":"N/A","harddisk":"N/A","os":"N/A"}

def send_live_ping(census_no):
    try:
        loc, dev, ser, specs = get_board_location(), detect_device_type(), get_machine_serial(), get_advanced_device_specs()
        ping_data = {"census_no": census_no, "device_type": dev, "device_serial": ser, "live_lat": loc["lat"], "live_lon": loc["lon"], "live_city": loc["city"], "status": "Active", "last_ping": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "spec_advanced": specs}
        requests.put(f"{FIREBASE_URL}live_boards/{census_no}/{ser}.json", json=ping_data, timeout=3)
    except: pass

def start_live_ping_watchdog(root, census_no):
    global last_heartbeat_time
    try:
        current_time = datetime.datetime.now()
        if (current_time - last_heartbeat_time).total_seconds() > 300:
            threading.Thread(target=lambda: send_live_ping(census_no), daemon=True).start()
        
        last_heartbeat_time = current_time
        loc, dev, ser, specs = get_board_location(), detect_device_type(), get_machine_serial(), get_advanced_device_specs()
        ping_data = {"census_no": census_no, "device_type": dev, "device_serial": ser, "live_lat": loc["lat"], "live_lon": loc["lon"], "live_city": loc["city"], "status": "Active", "last_ping": current_time.strftime("%Y-%m-%d %H:%M:%S"), "spec_advanced": specs}
        
        def target_ping():
            try: requests.put(f"{FIREBASE_URL}live_boards/{census_no}/{ser}.json", json=ping_data, timeout=3)
            except: pass
        threading.Thread(target=target_ping, daemon=True).start()
    except: pass
    root.after(30000, lambda: start_live_ping_watchdog(root, census_no))

def sync_offline_logs_to_cloud(census_no):
    if os.path.exists(OFFLINE_LOG_FILE):
        try:
            with open(OFFLINE_LOG_FILE, "r") as f: offline_data = json.load(f)
            if offline_data:
                for date_key, apps in offline_data.items():
                    for app_label, offline_minutes in apps.items():
                        res = requests.get(f"{FIREBASE_URL}software_analytics/{census_no}/{date_key}/{app_label}.json", timeout=3)
                        current_cloud_minutes = res.json() if res.status_code == 200 and res.json() else 0
                        total_minutes = current_cloud_minutes + offline_minutes
                        requests.put(f"{FIREBASE_URL}software_analytics/{census_no}/{date_key}/{app_label}.json", json=total_minutes, timeout=3)
                with open(OFFLINE_LOG_FILE, "w") as f: json.dump({}, f)
        except: pass

def track_software_usage_loop(root, census_no):
    try:
        active_win = gw.getActiveWindow()
        if active_win is not None:
            window_title = active_win.title.lower()
            window_pid = active_win._hWnd
            import ctypes
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(window_pid, ctypes.byref(pid))
            
            if pid.value > 0:
                process = psutil.Process(pid.value)
                exe_name = process.name().lower()
                
                if "youtube" in window_title: 
                    app_label = "YouTube (Educational Videos)"
                elif "powerpnt" in exe_name: app_label = "MS PowerPoint"
                elif "winword" in exe_name: app_label = "MS Word"
                elif "excel" in exe_name: app_label = "MS Excel"
                elif "vlc" in exe_name: app_label = "VLC Media Player"
                elif "chrome" in exe_name: app_label = "Google Chrome (General Browsing)"
                elif "msedge" in exe_name: app_label = "Web Browser (MS Edge)"
                elif "explorer" in exe_name: app_label = None
                else: app_label = exe_name.replace(".exe", "").capitalize()

                if app_label:
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    try:
                        res = requests.get(f"{FIREBASE_URL}software_analytics/{census_no}/{today_str}/{app_label}.json", timeout=3)
                        if res.status_code == 200:
                            sync_offline_logs_to_cloud(census_no)
                            curr = res.json() if res.json() else 0
                            requests.put(f"{FIREBASE_URL}software_analytics/{census_no}/{today_str}/{app_label}.json", json=curr + 1, timeout=3)
                    except:
                        local_data = {}
                        if os.path.exists(OFFLINE_LOG_FILE):
                            try:
                                with open(OFFLINE_LOG_FILE, "r") as f: local_data = json.load(f)
                            except: local_data = {}
                        
                        if today_str not in local_data: local_data[today_str] = {}
                        local_data[today_str][app_label] = local_data[today_str].get(app_label, 0) + 1
                        with open(OFFLINE_LOG_FILE, "w") as f: json.dump(local_data, f)
    except: pass
    root.after(60000, lambda: track_software_usage_loop(root, census_no))

def check_for_live_announcements(root, census_no):
    try:
        res = requests.get(f"{FIREBASE_URL}latest_announcement.json", timeout=3)
        if res.status_code == 200 and res.json():
            d = res.json()
            curr_id = str(hash(d.get("title","") + d.get("body","")))
            last_id = ""
            if os.path.exists(LAST_MSG_FILE):
                with open(LAST_MSG_FILE, "r", encoding="utf-8") as f: last_id = f.read().strip()
            if curr_id != last_id:
                with open(LAST_MSG_FILE, "w", encoding="utf-8") as f: f.write(curr_id)
                messagebox.showinfo(f"🔔 ALERT: {d.get('title')}", d.get('body'))
    except: pass
    root.after(10000, lambda: check_for_live_announcements(root, census_no))

def get_piriven_name_from_cloud(census_no):
    try:
        res = requests.get(f"{FIREBASE_URL}ministry_excel_registry.json", timeout=4)
        if res.status_code == 200 and res.json():
            registry = res.json()
            if isinstance(registry, list):
                for record in registry:
                    if not record: continue
                    if str(record.get("Census No", "")).split('.')[0].strip() == str(census_no).strip():
                        full_name = str(record.get("Piriven Name", "")).strip()
                        if full_name and full_name.lower() != "nan":
                            if "," in full_name: return full_name.split(",")[0].strip().upper()
                            return full_name.upper()
    except: pass
    return None

def launch_main_app(census_no):
    root = tk.Tk()
    root.title("Connecting to Ministry Network... ⏳")
    root.geometry("1050x740")
    root.configure(bg="#f8fafc")

    # 💡 Windows Startup එක සක්‍රිය කිරීම
    add_to_windows_startup()
    
    header_frame = tk.Frame(root, bg="#1e293b", pady=20); header_frame.pack(fill=tk.X)
    logo_container = tk.Frame(header_frame, bg="#1e293b"); logo_container.pack(side=tk.LEFT, padx=25)
    
    if os.path.exists(STATE_LOGO_PATH):
        try:
            state_hdr_img = tk.PhotoImage(file=STATE_LOGO_PATH).subsample(2, 2) 
            lbl_state = tk.Label(logo_container, image=state_hdr_img, bg="#1e293b")
            lbl_state.image = state_hdr_img; lbl_state.pack(side=tk.LEFT, padx=8)
        except: pass

    if os.path.exists(PIRIVEN_LOGO_PATH):
        try:
            piriven_hdr_img = tk.PhotoImage(file=PIRIVEN_LOGO_PATH).subsample(2, 2)
            lbl_piriven = tk.Label(logo_container, image=piriven_hdr_img, bg="#1e293b")
            lbl_piriven.image = piriven_hdr_img; lbl_piriven.pack(side=tk.LEFT, padx=8)
        except: pass

    text_container = tk.Frame(header_frame, bg="#1e293b"); text_container.pack(side=tk.LEFT, padx=15)
    title_label = tk.Label(text_container, text="PIRIVEN SMART BOARD SYSTEM", font=("Segoe UI", 22, "bold"), bg="#1e293b", fg="#f8fafc"); title_label.pack(anchor="w")
    subtitle_label = tk.Label(text_container, text=f"Census No: {census_no}  |  Live Network 🟢", font=("Segoe UI", 11), bg="#1e293b", fg="#94a3b8"); subtitle_label.pack(anchor="w")

    clock_label = tk.Label(header_frame, text="", font=("Consolas", 14, "bold"), bg="#1e293b", fg="#60a5fa", justify="right"); clock_label.pack(side=tk.RIGHT, padx=30)
    def update_live_clock():
        clock_label.config(text=datetime.datetime.now().strftime("%Y-%m-%d\n%H:%M:%S"))
        root.after(1000, update_live_clock)
    update_live_clock()

    def fetch_cloud_data_bg():
        send_live_ping(census_no)
        short_piriven_name = get_piriven_name_from_cloud(census_no)
        if short_piriven_name: root.title(f"{short_piriven_name} - Dashboard"); title_label.config(text=short_piriven_name)

    # සැබෑ මුහුණු ගණන මැන, සර්වර් එකේ සමස්ත ඓතිහාසික ශිෂ්‍ය සංඛ්‍යාව එකතු කරන එන්ජිම
    def trigger_interactive_camera_capture(is_automated=False):
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened(): cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

            if cap.isOpened():
                countdown = 1 if is_automated else 3
                start_time = datetime.datetime.now()
                
                while True:
                    succ, img = cap.read()
                    if not succ: break
                    
                    display_img = img.copy()
                    if not is_automated:
                        cv2.putText(display_img, f"LOOK AT THE CAMERA: {countdown}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                        cv2.putText(display_img, "Capturing class attendance...", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.imshow("🏫 PIRIVEN AI ATTENDANCE Desk", display_img)
                        cv2.waitKey(1)
                    else:
                        cv2.waitKey(10)
                    
                    if (datetime.datetime.now() - start_time).total_seconds() >= 1.0:
                        countdown -= 1
                        start_time = datetime.datetime.now()
                    
                    if countdown <= 0:
                        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                        student_count = len(faces)
                        
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        attendance_data = {"live_student_count": student_count, "last_captured": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                        requests.patch(f"{FIREBASE_URL}live_boards/{census_no}/attendance.json", json=attendance_data, timeout=3)
                        
                        try:
                            res_cum = requests.get(f"{FIREBASE_URL}live_boards/{census_no}/attendance/cumulative_student_lessons.json", timeout=3)
                            current_cumulative = res_cum.json() if res_cum.status_code == 200 and res_cum.json() else 0
                            new_cumulative = current_cumulative + student_count
                            requests.put(f"{FIREBASE_URL}live_boards/{census_no}/attendance/cumulative_student_lessons.json", json=new_cumulative, timeout=3)
                        except: pass
                        
                        if not is_automated:
                            messagebox.showinfo("📊 Attendance Logged", f"පන්තියේ පැමිණීම සාර්ථකව සටහන් විය!\n👨‍🎓 කැමරාවෙන් හඳුනාගත් සැබෑ සිසුන් ගණන: {student_count}")
                        break
                cap.release()
                cv2.destroyAllWindows()
        except: pass

    # 🤖 සෑම විනාඩි 15කට වරක්ම කැමරාව පණගන්වන එන්ජිම
    def automated_camera_scheduler_loop():
        trigger_interactive_camera_capture(is_automated=True)
        root.after(900000, automated_camera_scheduler_loop)

    root.after(1000, lambda: threading.Thread(target=fetch_cloud_data_bg, daemon=True).start())
    root.after(2000, lambda: check_for_live_announcements(root, census_no))
    root.after(4000, lambda: start_live_ping_watchdog(root, census_no)) 
    root.after(6000, lambda: track_software_usage_loop(root, census_no))
    root.after(10000, automated_camera_scheduler_loop)

    content_frame = tk.Frame(root, bg="#f8fafc", pady=35); content_frame.pack(expand=True, fill=tk.BOTH)

    def open_lessons():
        try:
            res = requests.get(f"{FIREBASE_URL}current_lesson.json", timeout=4)
            if res.status_code == 200 and res.json():
                data = res.json()
                link_type = data.get("type", "video")
                link_value = data.get("value", "").strip()
                if link_value:
                    if link_type == "video" and "youtube.com" not in link_value and "youtu.be" not in link_value:
                        webbrowser.open(f"https://www.youtube.com/watch?v={link_value}")
                    else: webbrowser.open(link_value)
                else: messagebox.showwarning("No Lessons", "අමාත්‍යාංශය විසින් දැනට සක්‍රිය පාඩම් මාලාවක් විකාශනය කර නොමැත.")
        except: messagebox.showerror("Error", "Cloud සර්වර් පද්ධතිය සමඟ සම්බන්ධ වීමට නොහැකි විය.")

    def open_syllabus(): webbrowser.open("http://www.edupub.gov.lk/")

    def open_messages():
        msg_win = tk.Toplevel(root); msg_win.title("Ministry Live Announcements"); msg_win.geometry("550x300"); msg_win.configure(bg="#ffffff")
        tk.Label(msg_win, text="📢 Ministry Official Broadcasts (පොදු නිවේදන)", font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#1e3a8a").pack(anchor="w", padx=20, pady=15)
        ann_box = tk.Text(msg_win, height=8, font=("Segoe UI", 11), bg="#f8fafc", fg="#1e293b", bd=0, highlightthickness=1, highlightbackground="#cbd5e1", padx=12, pady=12); ann_box.pack(fill=tk.X, padx=20)
        try:
            res = requests.get(f"{FIREBASE_URL}latest_announcement.json", timeout=3)
            if res.status_code == 200 and res.json():
                d = res.json(); ann_box.insert(tk.END, f"📌 {d.get('title', '')}\n\n{d.get('body', '')}")
            else: ann_box.insert(tk.END, "විශේෂ නිවේදන කිසිවක් නොමැත.")
        except: pass
        ann_box.config(state=tk.DISABLED)

    def open_bug_report():
        report_win = tk.Toplevel(root); report_win.title("Technical Support Desk & Private Chat"); report_win.geometry("1000x620"); report_win.configure(bg="#ffffff"); report_win.grab_set()
        left_frame = tk.Frame(report_win, bg="#ffffff", width=400, padx=20, pady=10); left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Label(left_frame, text="🛠️ Report New Issue", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#1e293b").pack(anchor="w", pady=10)
        
        ser_no = get_machine_serial()
        tk.Label(left_frame, text=f"Serial: {ser_no}", font=("Segoe UI", 9, "bold"), bg="#f1f5f9", fg="#475569", padx=8, pady=4).pack(anchor="w", pady=5)
        
        issue_type = tk.StringVar(left_frame); issue_type.set("Select Category")
        dropdown = tk.OptionMenu(left_frame, issue_type, "Audio/Sound Issue", "Display/Touch Issue", "Internet Connectivity", "Other Issue (වෙනත් ගැටලු)")
        dropdown.config(font=("Segoe UI", 10), bg="#f8fafc"); dropdown.pack(fill=tk.X, pady=8)
        
        tk.Label(left_frame, text="Describe your issue / ගැටලුවේ විස්තරය:", font=("Segoe UI", 10), bg="#ffffff", fg="#64748b").pack(anchor="w", pady=2)
        desc_box = tk.Text(left_frame, height=6, font=("Segoe UI", 10), bg="#f8fafc", highlightthickness=1, highlightbackground="#cbd5e1", padx=8, pady=8); desc_box.pack(fill=tk.X, pady=5)

        right_frame = tk.Frame(report_win, bg="#f8fafc", padx=20, pady=10); right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right_frame, text="💬 Private Chat & Ticket Status", font=("Segoe UI", 14, "bold"), bg="#f8fafc", fg="#b91c1c").pack(anchor="w", pady=10)
        
        tree = ttk.Treeview(right_frame, columns=("ID", "Category", "Status"), show="headings", height=4)
        tree.heading("ID", text="Ticket ID"); tree.heading("Category", text="Category"); tree.heading("Status", text="Status")
        tree.column("ID", width=70); tree.column("Category", width=140); tree.column("Status", width=120); tree.pack(fill=tk.X, pady=5)

        chat_text = tk.Text(right_frame, height=10, font=("Segoe UI", 10), bg="#ffffff", state=tk.DISABLED, padx=8, pady=8); chat_text.pack(fill=tk.BOTH, expand=True, pady=5)
        chat_input = tk.Entry(right_frame, font=("Segoe UI", 11)); chat_input.pack(fill=tk.X, pady=5)

        selected_ticket_id = [None]

        def load_ticket_chats(tid):
            selected_ticket_id[0] = tid
            chat_text.config(state=tk.NORMAL); chat_text.delete("1.0", tk.END)
            try:
                res = requests.get(f"{FIREBASE_URL}support_tickets/{tid}.json").json()
                chats = res.get("chats", {})
                status = res.get("status", "Pending")
                chat_text.insert(tk.END, f"=== [CHATS FOR TICKET: {tid}] ===\n👉 {res.get('description')}\n---------------------------------------\n")
                if chats:
                    for cid, c in chats.items():
                        sender = "🏛️ Ministry" if c.get("sender") == "ministry" else "🏫 You"
                        chat_text.insert(tk.END, f"[{c.get('time')[11:16]}] {sender}: {c.get('msg')}\n")
                if status == "Solved":
                    chat_input.config(state=tk.DISABLED); send_btn.config(state=tk.DISABLED, text="🔒 CHAT CLOSED (SOLVED)")
                    chat_text.insert(tk.END, "\n⚠️ [අමාත්‍යාංශ දැනුම්දීම]: මෙම තාක්ෂණික ගැටලුව නිරාකරණය කර ඇති බැවින් සජීවී චැට් පද්ධතිය වසා ඇත.")
                else: chat_input.config(state=tk.NORMAL); send_btn.config(state=tk.NORMAL, text="✉️ Send Reply / පිළිතුර යවන්න")
            except: pass
            chat_text.config(state=tk.DISABLED); chat_text.see(tk.END)

        def auto_refresh_chat_loop():
            if report_win.winfo_exists():
                tid = selected_ticket_id[0]
                if tid: load_ticket_chats(tid)
                report_win.after(3000, auto_refresh_chat_loop)

        def refresh_ticket_grid():
            for row in tree.get_children(): tree.delete(row)
            try:
                all_t = requests.get(f"{FIREBASE_URL}support_tickets.json").json()
                if all_t:
                    for tid, info in all_t.items():
                        if str(info.get("census_no")).strip() == str(census_no).strip(): tree.insert("", tk.END, values=(tid, info.get("issue_type"), info.get("status")))
            except: pass

        def submit_new_issue():
            if issue_type.get() == "Select Category" or not desc_box.get("1.0", tk.END).strip():
                messagebox.showwarning("Incomplete", "කරුණාකර සියලු විස්තර සපුරන්න.")
                return
            try:
                requests.post(f"{FIREBASE_URL}support_tickets.json", json={"census_no": census_no, "issue_type": issue_type.get(), "description": desc_box.get("1.0", tk.END).strip(), "device_serial": ser_no, "status": "Pending", "reported_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                messagebox.showinfo("✅ Success", "ගැටලුව සාර්ථකව අධ්‍යාපන අමාත්‍යාංශය වෙත යොමු වුණා!")
                desc_box.delete("1.0", tk.END); issue_type.set("Select Category"); refresh_ticket_grid()
            except: pass

        def send_chat_message():
            tid = selected_ticket_id[0]
            msg = chat_input.get().strip()
            if tid and msg:
                new_msg = {"sender": "piriven", "msg": msg, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                requests.post(f"{FIREBASE_URL}support_tickets/{tid}/chats.json", json=new_msg)
                chat_input.delete(0, tk.END); load_ticket_chats(tid)

        tree.bind("<<TreeviewSelect>>", lambda e: load_ticket_chats(tree.item(tree.selection()[0])['values'][0]) if tree.selection() else None)
        tk.Button(left_frame, text="📤 SUBMIT REPORT", bg="#ef4444", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=10, command=submit_new_issue).pack(fill=tk.X, pady=15)
        send_btn = tk.Button(right_frame, text="✉️ Send Reply / පිළිතුර යවන්න", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=send_chat_message)
        send_btn.pack(fill=tk.X, pady=5)
        auto_refresh_chat_loop(); refresh_ticket_grid()

    card_frame = tk.Frame(content_frame, bg="#f8fafc"); card_frame.pack()
    def create_modern_card(parent, text, color, cmd, row, col):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 13, "bold"), bg=color, fg="white", bd=0, width=24, height=8, cursor="hand2", command=cmd, relief="flat")
        btn.grid(row=row, column=col, padx=25, pady=25)

    create_modern_card(card_frame, "📺\n\nREMOTE LESSONS\n\n(Live Video Education)", "#ef4444", open_lessons, 0, 0)
    create_modern_card(card_frame, "📚\n\nSYLLABUS & BOOKS\n\n(Digital Library)", "#3b82f6", open_syllabus, 0, 1)
    create_modern_card(card_frame, "🔔\n\nMINISTRY MESSAGES\n\n(Announcements)", "#10b981", open_messages, 0, 2)

    tk.Button(root, text="📸    START AI CLASS ATTENDANCE DETECTOR (සජීවී සිසුන් සංඛ්‍යාව ගණනය කරන්න)", 
              font=("Segoe UI", 11, "bold"), bg="#dc2626", fg="white", bd=0, pady=16, cursor="hand2", 
              command=lambda: trigger_interactive_camera_capture(is_automated=False)).pack(pady=10, padx=85, fill=tk.X)

    tk.Button(root, text="🛠    REPORT TECHNICAL ISSUES & PRIVATE CHAT SYSTEM", font=("Segoe UI", 11, "bold"), bg="#475569", fg="white", bd=0, pady=16, cursor="hand2", command=open_bug_report).pack(pady=15, padx=85, fill=tk.X)
    
    # 💡 [නව ආරක්ෂිත රීතිය] ගුරුවරයා UI එක Close (X) කළත් ඇප් එක Kill නොකර බැක්ග්‍රවුන්ඩ් සඟවන ආරක්ෂිත රීතිය
    def on_ui_close_safeguard():
        root.withdraw() # UI එක පමණක් සඟවයි (Destroy නොකරයි)
        print("🔒 UI Hidden by user, but Piriven Core Service is still running in the background...")
        
    root.protocol("WM_DELETE_WINDOW", on_ui_close_safeguard)
    
    footer_frame = tk.Frame(root, bg="#1e293b", pady=18); footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
    footer_frame.columnconfigure(0, weight=1); footer_frame.columnconfigure(1, weight=2); footer_frame.columnconfigure(2, weight=1)
    tk.Label(footer_frame, text=f"Piriven Development Branch\n📧 info.pirivendevelopment@gmail.com\n© {datetime.datetime.now().year} | Ministry of Education, Sri Lanka.", font=("Segoe UI", 9), bg="#1e293b", fg="#cbd5e1", justify="center").grid(row=0, column=1, sticky="ew")
    root.mainloop()

def enable_windows_camera_permission():
    try:
        import winreg
        keys = [r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam", r"Software\Microsoft\Windows\CurrentVersion\DeviceAccess\Global\{E5323777-F976-4f5b-9B55-B94699C46E44}"]
        for key_path in keys:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Allow"); winreg.CloseKey(key)
    except: pass

def show_setup_screen():
    setup = tk.Tk(); setup.title("System Activation"); setup.geometry("460x320"); setup.configure(bg="#ffffff")
    setup.resizable(False, False)
    tk.Label(setup, text="⚙️ Board Initialization", font=("Segoe UI", 18, "bold"), bg="#ffffff", fg="#1e293b").pack(pady=20)
    tk.Label(setup, text="⚠️ IMPORTANT NOTICE:\nThis app requires Web Camera access for live class analysis.\nPlease ensure Windows Camera Privacy settings are allowed.", 
             font=("Segoe UI", 9, "bold"), bg="#fee2e2", fg="#991b1b", justify="center", pady=8, padx=10).pack(pady=5)
    tk.Label(setup, text="Enter Piriven Census Number:", font=("Segoe UI", 11), bg="#ffffff", fg="#64748b").pack(pady=5)
    entry = tk.Entry(setup, font=("Segoe UI", 14), width=18, justify="center", bg="#f1f5f9", bd=0, highlightthickness=1); entry.pack(pady=5)
    
    def save():
        c = entry.get().strip()
        if c:
            enable_windows_camera_permission()
            try:
                test_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if test_cap.isOpened(): test_cap.release()
            except: pass
            with open(CENSUS_FILE, "w") as f: f.write(c)
            setup.destroy(); launch_main_app(c)
        else: messagebox.showwarning("Incomplete", "Census number is required.")

    tk.Button(setup, text="ACTIVATE BOARD & ALLOW CAMERA", bg="#3b82f6", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=10, padx=25, command=save).pack(pady=15)
    setup.mainloop()

if __name__ == "__main__":
    if os.path.exists(CENSUS_FILE):
        with open(CENSUS_FILE, "r") as f: launch_main_app(f.read().strip())
    else: show_setup_screen()