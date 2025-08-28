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
