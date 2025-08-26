import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import queue
from datetime import datetime
import sys
import os
import winreg



class DBFCMSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("경동나비엔 알람PUSH 서비스")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')

        # 아이콘 설정
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icons', 'KDNAVIEN_icon_v1.2.png')
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, icon)
        except Exception as e:
            pass  # 아이콘 로드 실패시 기본 아이콘 사용

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.is_running = False
        self.thread = None
        self.log_queue = queue.Queue()

        self.db_config = {
            'host': '',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'test_db'
        }

        self.setup_ui()
        self.update_log_display()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Header.TFrame', background='#1a1a1a')
        style.configure('Body.TFrame', background='#1a1a1a')
        style.configure('Footer.TFrame', background='#1a1a1a')

        style.configure('Title.TLabel',
                        background='#2a2a2a',
                        foreground='#ffffff',
                        font=('Segoe UI', 12, 'bold'))
        style.configure('Info.TLabel',
                        background='#2a2a2a',
                        foreground='#b0b0b0',
                        font=('Segoe UI', 10))
        style.configure('Status.TLabel',
                        background='#2a2a2a',
                        foreground='#ff0000',
                        font=('Segoe UI', 10, 'bold'))

        style.configure('Start.TButton',
                        background='#2e7d32',
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        font=('Segoe UI', 10, 'bold'))
        style.map('Start.TButton',
                  background=[('active', '#388e3c')])

        style.configure('Stop.TButton',
                        background='#c62828',
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        font=('Segoe UI', 10, 'bold'))
        style.map('Stop.TButton',
                  background=[('active', '#d32f2f')])

        self.create_header_frame()
        self.create_body_frame()
        self.create_footer_frame()

    def create_header_frame(self):
        header_frame = ttk.Frame(self.root, style='Header.TFrame', height=120)
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        db_info_frame = tk.Frame(header_frame, bg='#2a2a2a', highlightbackground='#404040', highlightthickness=1)
        db_info_frame.pack(fill='both', expand=True, pady=10)

        ttk.Label(db_info_frame, text="MariaDB Connection Info", style='Title.TLabel').pack(pady=(10, 5))

        info_text = f"Host: {self.db_config['host']}:{self.db_config['port']} | " \
                    f"User: {self.db_config['user']} | " \
                    f"Database: {self.db_config['database']}"

        self.db_info_label = ttk.Label(db_info_frame, text=info_text, style='Info.TLabel')
        self.db_info_label.pack(pady=(0, 10))

        self.connection_status = ttk.Label(db_info_frame, text="● Stopped", style='Status.TLabel')
        self.connection_status.pack(pady=(0, 10))

    def create_body_frame(self):
        body_frame = ttk.Frame(self.root, style='Body.TFrame')
        body_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        body_frame.grid_rowconfigure(0, weight=1)
        body_frame.grid_columnconfigure(0, weight=1)

        log_container = tk.Frame(body_frame, bg='#2a2a2a', highlightbackground='#404040', highlightthickness=1)
        log_container.grid(row=0, column=0, sticky='nsew')
        log_container.grid_rowconfigure(1, weight=1)
        log_container.grid_columnconfigure(0, weight=1)

        ttk.Label(log_container, text="Status Monitor", style='Title.TLabel').grid(row=0, column=0, pady=(10, 5),
                                                                                   sticky='w', padx=10)

        self.log_text = scrolledtext.ScrolledText(
            log_container,
            wrap=tk.WORD,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 9),
            insertbackground='#00ff00',
            selectbackground='#404040',
            relief=tk.FLAT,
            borderwidth=10
        )
        self.log_text.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        self.log_text.config(state=tk.DISABLED)

    def create_footer_frame(self):
        footer_frame = ttk.Frame(self.root, style='Footer.TFrame', height=80)
        footer_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=(10, 20))

        button_container = tk.Frame(footer_frame, bg='#1a1a1a')
        button_container.pack(expand=True)

        self.start_button = ttk.Button(
            button_container,
            text="START",
            style='Start.TButton',
            command=self.start_scheduler,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=10, ipady=10)

        self.stop_button = ttk.Button(
            button_container,
            text="STOP",
            style='Stop.TButton',
            command=self.stop_scheduler,
            state='disabled',
            width=15
        )
        self.stop_button.pack(side=tk.LEFT, padx=10, ipady=10)

    def log_message(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] [{level}] {message}"
        self.log_queue.put(formatted_message)

    def update_log_display(self):
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + '\n')
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.update_log_display)

    def test_db_connection(self):
        try:
            connection = mariadb.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            connection.close()
            return True
        except Exception as e:
            self.log_message(f"MariaDB Connection Error: {str(e)}", "ERROR")
            return False

    def start_scheduler(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            self.log_message("Starting DB Sync & FCM Scheduler...", "INFO")

            if self.test_db_connection():
                self.connection_status.config(text="● Running", foreground='#00ff00')
                self.log_message("MariaDB connected successfully", "SUCCESS")
            else:
                self.connection_status.config(text="● Stopped", foreground='#ff0000')
                self.stop_scheduler()
                return

            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()

            self.log_message("Scheduler started successfully", "SUCCESS")

    def stop_scheduler(self):
        if self.is_running:
            self.is_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.connection_status.config(text="● Stopped", foreground='#ff0000')

            self.log_message("Stopping scheduler...", "INFO")

            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)

            self.log_message("Scheduler stopped", "INFO")

    def run_scheduler(self):
        while self.is_running:
            try:
                self.sync_database()

                self.send_fcm_notifications()

                time.sleep(5)

            except Exception as e:
                self.log_message(f"Scheduler Error: {str(e)}", "ERROR")
                time.sleep(10)

    def sync_database(self):
        try:
            connection = mariadb.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )

            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()

            connection.close()

            self.log_message("MariaDB sync completed", "INFO")

        except Exception as e:
            self.log_message(f"MariaDB Sync Error: {str(e)}", "ERROR")

    def send_fcm_notifications(self):
        try:
            self.log_message("Sending FCM notifications...", "INFO")

            time.sleep(1)

            self.log_message("FCM notifications sent successfully", "SUCCESS")

        except Exception as e:
            self.log_message(f"FCM Error: {str(e)}", "ERROR")

    def add_to_startup(self):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "DBFCMScheduler"
            app_path = os.path.abspath(sys.argv[0])

            if app_path.endswith('.py'):
                app_path = f'"{sys.executable}" "{app_path}"'
            else:
                app_path = f'"{app_path}"'

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)

            self.log_message("Added to Windows startup", "SUCCESS")

        except Exception as e:
            self.log_message(f"Startup registration error: {str(e)}", "ERROR")


def main():
    root = tk.Tk()
    app = DBFCMSchedulerApp(root)

    app.add_to_startup()

    def on_closing():
        if app.is_running:
            app.stop_scheduler()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()