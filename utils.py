import os
import sys
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import threading


class DateRotatingFileHandler(RotatingFileHandler):
    """날짜가 변경되면 자동으로 새 디렉토리에 로그를 생성하는 핸들러"""
    
    def __init__(self, base_path, *args, **kwargs):
        self.base_path = base_path
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.lock = threading.Lock()
        
        # 초기 로그 파일 설정
        log_file = self._get_log_file_path()
        super().__init__(log_file, *args, **kwargs)
        
    def _get_log_file_path(self):
        """현재 날짜에 맞는 로그 파일 경로 생성"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_dir = os.path.join(self.base_path, today)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 기존 로그 파일 개수 확인
        existing_logs = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        log_number = len(existing_logs) + 1
        
        return os.path.join(log_dir, f'{today}_log_{log_number}.log')
    
    def doRollover(self):
        """100MB 초과 시 새 파일로 로테이션 (순차 번호 보장)"""
        # 현재 스트림 닫기
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # 현재 날짜와 디렉토리 확인
        today = datetime.now().strftime('%Y-%m-%d')
        log_dir = os.path.join(self.base_path, today)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 다음 번호 찾기 (현재 파일은 이미 꽉 찬 상태)
        existing_logs = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        next_number = len(existing_logs) + 1
        
        # 새 파일명으로 변경
        new_log_file = os.path.join(log_dir, f'{today}_log_{next_number}.log')
        self.baseFilename = new_log_file
        
        # 새 스트림 열기
        self.stream = self._open()
    
    def emit(self, record):
        """로그 기록 시 날짜 체크"""
        with self.lock:
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 날짜가 변경되었는지 확인
            if current_date != self.current_date:
                # 기존 스트림 닫기
                if self.stream:
                    self.stream.close()
                    self.stream = None
                
                # 새 날짜로 업데이트
                self.current_date = current_date
                
                # 새 로그 파일 경로 설정
                new_log_file = self._get_log_file_path()
                self.baseFilename = new_log_file
                
                # 새 스트림 열기
                self.stream = self._open()
            
        # 부모 클래스의 emit 호출
        super().emit(record)


def get_resource_path(relative_path):
    """
    PyInstaller로 빌드된 실행 파일과 개발 환경 모두에서 
    올바른 리소스 파일 경로를 반환합니다.
    """
    try:
        # PyInstaller가 생성한 임시 폴더의 경로
        base_path = sys._MEIPASS
    except Exception:
        # 개발 환경에서 실행 중일 때
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_sync_rows(result,count):
    total_cnt = len(result)
    fetch_cnt = total_cnt - count
    total_list = []
    for i in range(fetch_cnt):
        total_list.append(result[-1-i])
    total_list.reverse()
    return total_list

def fix_kr(s):
    return s.encode('cp1252', errors='replace').decode('cp949', errors='replace')

def contains_leak(s):
    return '누수' in s

def process_to_tuple(results):
    for result in results:
        del result['idx']
        result['END_TIME'] = None
        result['TAG_DESC'] = fix_kr(result['TAG_DESC'])
        if contains_leak(result['TAG_DESC']):
            result['ALRAM_TP1_CD'] = 'TP002'
            result['ALRAM_TP1_NM'] = '누수'
        else:
            result['ALRAM_TP1_CD'] = 'TP001'
            result['ALRAM_TP1_NM'] = '가스'
        result['ALRAM_MEMO'] = None
        result['UPDATE_USER'] = None
        result['CHECK_YN'] = 'N'
        result['PUSH_YN'] = 'N'
        result['UPDATE_TIME'] = None

    return tuple(results)


def setup_logging():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 날짜가 변경되면 자동으로 새 디렉토리를 사용하는 커스텀 핸들러 사용
    handler = DateRotatingFileHandler(
        base_path=base_path,
        maxBytes=104857600,  # 100MB
        backupCount=999,
        encoding='utf-8'
    )

    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 기존 핸들러 제거
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # 새 핸들러 추가
    root_logger.addHandler(handler)

    # 콘솔 출력도 원한다면 추가
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 현재 날짜의 로그 디렉토리 반환
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(base_path, today)