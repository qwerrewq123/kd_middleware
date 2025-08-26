# KD-Navien Alarm Push Service Middleware

경동나비엔 알람 푸시 서비스를 위한 Python 기반 미들웨어입니다. MariaDB를 실시간 모니터링하며 Firebase Cloud Messaging(FCM)을 통해 푸시 알림을 자동으로 전송합니다.

## 주요 기능

- **실시간 데이터베이스 모니터링**: MariaDB의 `alram_event` 테이블에서 미처리 이벤트(`push_yn = 'N'`) 주기적 조회
- **자동 알림 처리**: 미처리 이벤트를 FCM 테이블로 자동 전송
- **FCM 푸시 알림**: Firebase Cloud Messaging을 통한 모바일 푸시 알림 전송
- **상태 관리**: 처리 완료된 이벤트 상태 자동 업데이트 (`push_yn = 'Y'`)
- **GUI 인터페이스**: 실시간 로그 모니터링이 가능한 사용자 친화적인 GUI 제공
- **스케줄러 기반 자동화**: 설정 가능한 주기로 자동 실행 (기본 5초)


## install

1. install package:
```bash
pip install -r requirements.txt
```

2. set enviroment variable (`config.toml`):
```env
# MariaDB Configuration  
[database.mariadb]
host = 
port = 
database = 
username = 
password = 
```

## execute

```bash
python main.py
```



## project

```
middleware/
│
├── main.py           
├── mysql_connector.py
├── push_fcm.py    
├── push_sql.py   
├── scheduler.py  
├── requirements.txt
├── config.toml   
└── simbizmall-5717f-firebase-adminsdk-45is2-597a4fbefc.json          
```

