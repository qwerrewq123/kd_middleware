# Event Processing Middleware

두 개의 데이터베이스 시스템(MSSQL과 MariaDB)을 연결하여 이벤트를 처리하는 Python 기반 미들웨어입니다.

## 주요 기능

- MariaDB의 `alram_event` 테이블에서 미처리 이벤트(`push_yn = 'N'`) 주기적 조회
- 미처리 이벤트를 MSSQL 데이터베이스로 전송
- 처리 완료된 이벤트 상태 업데이트 (`push_yn = 'Y'`)
- 스케줄러 기반 자동 실행
- 실시간 처리 상태 모니터링

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정 (`.env` 파일 수정):
```env
# MSSQL Configuration
MSSQL_HOST=kdnavien.iptime.org
MSSQL_PORT=1533
MSSQL_DATABASE=KDNAVIEN
MSSQL_USERNAME=navien
MSSQL_PASSWORD=your_password

# MariaDB Configuration  
MARIADB_HOST=kdnavien.iptime.org
MARIADB_PORT=3336
MARIADB_DATABASE=simbizlocal
MARIADB_USERNAME=root
MARIADB_PASSWORD=your_password

# Application Configuration
SCHEDULER_INTERVAL=60  # 체크 주기 (초)
BATCH_SIZE=100        # 한 번에 처리할 이벤트 수
LOG_LEVEL=INFO        # 로그 레벨
```

## 실행

```bash
python main.py
```

## 테스트

```bash
python test_middleware.py
```

## 프로젝트 구조

```
middleware/
│
├── main.py              # 메인 애플리케이션 진입점
├── config.py            # 설정 관리
├── db_connectors.py     # 데이터베이스 연결 클래스
├── event_processor.py   # 이벤트 처리 로직
├── scheduler.py         # 스케줄러 모듈
├── test_middleware.py   # 단위 테스트
├── requirements.txt     # 의존성 패키지
├── .env                # 환경 변수 설정
└── README.md           # 프로젝트 문서
```

## 모듈 설명

### db_connectors.py
- `MSSQLConnector`: MSSQL 데이터베이스 연결 및 쿼리 실행
- `MariaDBConnector`: MariaDB 데이터베이스 연결 및 이벤트 관리

### event_processor.py
- `EventProcessor`: 이벤트 조회, 처리, 전송 로직 구현
- 미처리 이벤트 카운트 확인
- 배치 단위 이벤트 처리
- 처리 통계 관리

### scheduler.py
- `EventScheduler`: 주기적 작업 실행 스케줄러
- 멀티스레드 기반 백그라운드 실행
- 작업 상태 모니터링

### config.py
- 환경 변수 로드 및 설정 관리
- 로깅 설정

## 로그

애플리케이션 로그는 콘솔과 `middleware.log` 파일에 동시에 기록됩니다.

## 종료

`Ctrl+C`를 눌러 안전하게 종료할 수 있습니다.