import tkinter as tk
from tkinter import ttk, scrolledtext
from scheduler import Scheduler
import os
import logging


class GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)

        # GUI 스레드에서 실행되도록 보장
        self.text_widget.after(0, append)


class DBFCMSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KD-Navien Alarm push Service")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        self.scheduler: Scheduler = None
        self.gui_handler = None

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

        self.setup_ui()

    def init_scheduler(self):
        if self.scheduler is None:
            self.scheduler = Scheduler()

    def destroy_scheduler(self):
        if self.scheduler is not None:
            self.scheduler = None

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

        info_text = "Host: http://kdnavien.iptime.org | User: root | Database: MariaDB"

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
            command=self.start_clicked,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=10, ipady=10)

        self.stop_button = ttk.Button(
            button_container,
            text="STOP",
            style='Stop.TButton',
            command=self.stop_clicked,
            state='disabled',
            width=15
        )
        self.stop_button.pack(side=tk.LEFT, padx=10, ipady=10)

    def start_clicked(self):
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.connection_status.config(text="● Running", foreground='#00ff00')

        # GUI 핸들러 설정
        if self.gui_handler is None:
            self.gui_handler = GuiLogHandler(self.log_text)
            self.gui_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',
                                                            datefmt='%H:%M:%S'))

        # 로깅 기본 설정 (Scheduler 생성 전에 설정)
        logging.basicConfig(level=logging.INFO, force=True)

        # 루트 로거를 먼저 설정
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(self.gui_handler)
        root_logger.setLevel(logging.INFO)

        # Scheduler 인스턴스 생성 (이미 로깅 설정이 완료된 상태)
        self.init_scheduler()

        # 각 로거에 핸들러 추가 (Scheduler 생성 후)
        scheduler_logger = logging.getLogger('scheduler')
        scheduler_logger.handlers.clear()  # 기존 핸들러 모두 제거
        scheduler_logger.addHandler(self.gui_handler)
        scheduler_logger.setLevel(logging.INFO)
        scheduler_logger.propagate = False  # 상위 로거로 전파 방지

        mysql_logger = logging.getLogger('mysql_connector')
        mysql_logger.handlers.clear()  # 기존 핸들러 모두 제거
        mysql_logger.addHandler(self.gui_handler)
        mysql_logger.setLevel(logging.INFO)
        mysql_logger.propagate = False  # 상위 로거로 전파 방지

        self.scheduler.start()

        # GUI 로그로 직접 출력 테스트
        logging.info('Start button clicked - Scheduler starting...')

    def stop_clicked(self):
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.connection_status.config(text="● Stopped", foreground='#ff0000')

        # GUI 로그로 직접 출력
        logging.info('Stop button clicked - Scheduler stopping...')

        # 스케줄러 중지
        if self.scheduler:
            self.scheduler.stop()

        # 핸들러 제거
        if self.gui_handler:
            scheduler_logger = logging.getLogger('scheduler')
            scheduler_logger.removeHandler(self.gui_handler)

            mysql_logger = logging.getLogger('mysql_connector')
            mysql_logger.removeHandler(self.gui_handler)

            root_logger = logging.getLogger()
            root_logger.removeHandler(self.gui_handler)

        self.destroy_scheduler()


def main():
    root = tk.Tk()
    DBFCMSchedulerApp(root)

    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()