import os
import sys

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